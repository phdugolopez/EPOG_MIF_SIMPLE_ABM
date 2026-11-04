from dataclasses import asdict


class StockFlowError(AssertionError):
    """Raised when the accounts of a period do not add up."""


def after_step(industry, step: int) -> None:
    """Copy into the period record what a later step overwrites. Called by run_period
    after each step; it reads the state and never writes to anything a mechanism reads.
    """
    if step == 1:
        industry.record = {"t": industry.time, "firms": {}}
    record = industry.record
    if step == 2:
        shares = [f.share for f in industry.firms]
        record["share_sum_demand"] = sum(shares)
        record["share_min_demand"] = min(shares, default=0.0)


def _tolerance(scale: float) -> float:
    return 1e-9 * max(1.0, scale)


def residuals(industry) -> tuple[dict, list[str]]:
    """Every check of the period as a residual, and a message for each one that fails.

    Money checks use the tolerance 1e-9 * max(1, scale), scale = 1 + the sum of absolute
    flows + money; quantity checks use 1e-9 * max(1, demand); share checks 1e-9.
    """
    config = industry.parameters
    scale = 1.0 + sum(
        abs(v) for row in industry.flows.values() for v in row.values()
    ) + abs(industry.money)
    tol = _tolerance(scale)
    tol_q = _tolerance(industry.demand())
    tol_share = 1e-9
    fails = []
    out = {"check_tol": tol}

    # 1. Money is conserved: firms' cash plus the rest of the economy's cash is constant.
    money = industry.roe.cash + sum(f.cash for f in industry.firms)
    out["money_resid"] = money - industry.money
    if abs(out["money_resid"]) > tol:
        fails.append(f"money {money} != {industry.money}")

    # 2. Firms' debt equals the loans held by the rest of the economy.
    debt = sum(f.debt for f in industry.firms)
    out["debt_resid"] = debt - industry.roe.loans
    if abs(out["debt_resid"]) > tol:
        fails.append(f"debt {debt} != loans {industry.roe.loans}")

    # 3. For every firm, the change in net worth equals profit - dividends - write-offs
    #    (+ equity brought in at entry). Stored: the largest residual in absolute value.
    worst, worst_firm = 0.0, None
    for firm in industry.firms:
        change = firm.net_worth - firm.net_worth_start
        expected = firm.profit - firm.dividends - firm.write_offs + firm.equity_in
        if abs(change - expected) > abs(worst):
            worst, worst_firm = change - expected, firm
    out["nw_resid"] = worst
    if abs(worst) > tol:
        fails.append(
            f"firm {worst_firm.firm_id} net worth moved by "
            f"{worst_firm.net_worth - worst_firm.net_worth_start}, residual {worst}"
        )

    # 4. Every row of the transaction-flow matrix sums to zero, and each column sums to
    #    the change in that sector's cash.
    row_resid = {item: sum(row.values()) for item, row in industry.flows.items()}
    worst_item = max(row_resid, key=lambda k: abs(row_resid[k]), default=None)
    out["tfm_row_resid"] = row_resid[worst_item] if worst_item else 0.0
    if abs(out["tfm_row_resid"]) > tol:
        fails.append(f"row {worst_item} sums to {out['tfm_row_resid']}")
    columns = {"firms": 0.0, "roe": 0.0}
    for row in industry.flows.values():
        for sector, value in row.items():
            columns[sector] += value
    cash_now = {"firms": sum(f.cash for f in industry.firms), "roe": industry.roe.cash}
    col_resid = {s: total - (cash_now[s] - industry.cash_start[s])
                 for s, total in columns.items()}
    worst_sector = max(col_resid, key=lambda k: abs(col_resid[k]))
    out["tfm_col_resid"] = col_resid[worst_sector]
    if abs(out["tfm_col_resid"]) > tol:
        fails.append(
            f"column {worst_sector} sums to {columns[worst_sector]}, cash moved by "
            f"{cash_now[worst_sector] - industry.cash_start[worst_sector]}"
        )

    # 5. Shares sum to one after step 2 and after step 6; none is negative.
    end_shares = [f.share for f in industry.firms]
    out["share_resid_demand"] = industry.record.get("share_sum_demand", 1.0) - 1.0
    out["share_resid_end"] = sum(end_shares) - 1.0
    out["share_min"] = min(
        industry.record.get("share_min_demand", 0.0), min(end_shares, default=0.0)
    )
    for name in ("share_resid_demand", "share_resid_end"):
        if abs(out[name]) > tol_share:
            fails.append(f"{name} = {out[name]}")
    if out["share_min"] < -tol_share:
        fails.append(f"negative share {out['share_min']}")

    # 6. Sales plus unserved demand equal demand; no firm produces above u_max capacity.
    producers = industry.producers
    out["sales_resid"] = (
        sum(f.sales for f in producers) + industry.unserved - industry.demand()
    )
    if abs(out["sales_resid"]) > tol_q:
        fails.append(f"sales_resid = {out['sales_resid']}")
    over = [
        f for f in producers
        if sum(p.output for p in f.producing_plants)
        > config.U_MAX * f.producing_capacity + tol_q
    ]
    out["util_max_viol"] = len(over)
    if over:
        fails.append(f"firm {over[0].firm_id} produces above u_max capacity")

    # 7. Capacity identity, plant by plant (K = producing capacity at the start):
    #    K_t - retired - exit + ordered + entry - cancelled = K_{t+1}.
    flows = capacity_flows(industry)
    out["cap_resid"] = (
        flows["k_start"] - flows["retired"] - flows["exit"] + flows["ordered"]
        + flows["entry"] - flows["cancelled"] - flows["k_next"]
    )
    if abs(out["cap_resid"]) > tol_q:
        fails.append(f"cap_resid = {out['cap_resid']}")

    # 8. No posted price below the firm's floor.
    below = [
        f for f in producers
        if f.producing_plants and f.price < f.p_floor - _tolerance(f.p_floor)
    ]
    out["floor_viol"] = len(below)
    if below:
        fails.append(f"firm {below[0].firm_id} priced {below[0].price} below its floor")

    out["check_fail"] = len(fails)
    return out, fails


def _capacity(plants) -> float:
    return sum(p.capacity for p in plants)


def capacity_flows(industry, firms=None) -> dict:
    """The terms of the capacity identity for the period, over `firms` (default: all
    firms that produced this period, plus the entrants).

    k_start: capacity in operation at the start of the period; retired: plants scrapped
    at step 4 (replacements included); exit: plants still in operation at firms that
    leave at step 6; ordered: plants ordered at steps 4 and 5 by every incumbent;
    cancelled: the part of `ordered` placed by firms that leave, written off at exit;
    entry: entrants' plants; k_next: capacity in operation at the start of next period.
    """
    producers = industry.producers if firms is None else [
        f for f in industry.producers if f in firms
    ]
    entries = industry.entries if firms is None else [
        f for f in industry.entries if f in firms
    ]
    exited = {id(f) for f, _ in industry.exits}
    retired = {id(p) for p in industry.retired}
    leavers = [f for f in producers if id(f) in exited]
    stayers = [f for f in producers if id(f) not in exited]
    return {
        "k_start": sum(f.producing_capacity for f in producers),
        "retired": sum(
            p.capacity for f in producers for p in f.producing_plants if id(p) in retired
        ),
        "exit": sum(f.capacity for f in leavers),
        "ordered": sum(_capacity(f.pending_plants) for f in producers),
        "cancelled": sum(_capacity(f.pending_plants) for f in leavers),
        "entry": sum(_capacity(f.pending_plants) for f in entries),
        "k_next": sum(f.capacity + _capacity(f.pending_plants) for f in stayers)
        + sum(_capacity(f.pending_plants) for f in entries),
    }


def check_stock_flow(industry) -> None:
    """Compute every check of the period, store the residuals in the period's macro row,
    then raise StockFlowError on the first failure (CHECKS_RAISE) or count the period in
    industry.n_check_fail.

    Checks: money conserved; debt = loans; for every firm the change in net worth equals
    profit - dividends - write-offs (+ equity at entry); rows of the flow matrix sum to
    zero and columns to the change in cash; shares sum to one after steps 2 and 6;
    sales + unserved = demand; output within u_max capacity; the capacity identity;
    no price below its floor.
    """
    out, fails = residuals(industry)
    if industry.history and industry.history[-1]["time"] == industry.time:
        industry.history[-1].update(out)
    if not fails:
        return
    if industry.parameters.CHECKS_RAISE:
        raise StockFlowError(f"t={industry.time}: {fails[0]}")
    industry.n_check_fail += 1


def collect(industry) -> None:
    """Record macro, per-firm, per-plant and flow-matrix rows for the period.

    Rows cover every firm that produced this period, including those that left at its
    end, and the entrants of the period (whose first plant arrives next period).
    """
    industry.history.append(collect_macro_data(industry))
    for firm in industry.producers + industry.entries:
        industry.firm_history.append(firm_row(industry, firm))
        for plant in firm.producing_plants:
            industry.plant_history.append(plant_row(industry, firm, plant))
    for item, row in industry.flows.items():
        industry.flow_history.append({"time": industry.time, "item": item, **row})
    industry.previous_profit = sum(f.profit for f in industry.producers)
    industry.previous_investment = sum(f.investment for f in industry.producers)


def firm_uc(firm, delta: float) -> float:
    """Capacity-weighted unit cost of the plants that produced this period."""
    plants = firm.producing_plants
    return _weighted([p.ucs + delta * p.kappa for p in plants], [p.capacity for p in plants])


def firm_row(industry, firm) -> dict:
    plants = firm.plants + firm.pending_plants
    newest = max(plants, key=lambda p: p.vintage, default=None)
    return {
        "time": industry.time,
        "firm_id": firm.firm_id,
        "type": firm.type,
        "hurdle": firm.hurdle,
        "price": firm.price,
        "share": firm.share,
        "sales": firm.sales,
        "util": firm.util,
        "unmet": firm.unmet,
        "capacity": firm.producing_capacity,
        "capacity_next": sum(p.capacity for p in plants),
        "uc": firm_uc(firm, industry.parameters.DELTA),
        "n_plants": len(firm.producing_plants),
        "newest_technique": newest.technique if newest else "",
        "cash": firm.cash,
        "debt": firm.debt,
        "book_value": firm.book_value,
        "net_worth": firm.net_worth,
        "profit": firm.profit,
        "profit_rate": firm.profit_rate,
        "margin": firm.price - firm_uc(firm, industry.parameters.DELTA),
        "dividends": firm.dividends,
        "write_offs": firm.write_offs,
        "investment": firm.investment,
        "at_war": firm.at_war,
        "born": firm.born,
        "exit_reason": firm.exit_reason,
    }


def plant_row(industry, firm, plant) -> dict:
    row = asdict(plant)
    row["time"] = industry.time
    row["firm_id"] = firm.firm_id
    row["firm_type"] = firm.type
    row["profit_rate"] = plant.profit / plant.purchase_cost
    row["retired"] = plant in industry.retired
    return row


def _weighted(values, weights) -> float:
    total = sum(weights)
    return sum(v * w for v, w in zip(values, weights)) / total if total > 0.0 else 0.0


def _cv(values) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return var ** 0.5 / mean if mean else 0.0


def collect_macro_data(industry) -> dict:
    firms = industry.producers
    delta = industry.parameters.DELTA
    plants = [p for f in firms for p in f.producing_plants]
    techniques = list(industry.techniques)
    capital = [sum(p.purchase_cost for p in f.producing_plants) for f in firms]
    priced = [f for f in firms if f.producing_plants]
    leader = min(priced, key=lambda f: f.price) if priced else None
    lowest_cost = min(priced, key=lambda f: firm_uc(f, delta)) if priced else None
    newest = max((p.vintage for p in plants), default=0)
    newest_plants = [p for p in plants if p.vintage == newest]
    profit = sum(f.profit for f in firms)
    row = {
        "time": industry.time,
        "demand": industry.demand(),
        "sales": sum(f.sales for f in firms),
        "unserved": industry.unserved,
        "unmet": sum(f.unmet for f in firms),
        "hhi": sum(f.share ** 2 for f in industry.firms),
        "n_firms": len(industry.firms),
        "mean_price": _weighted([f.price for f in firms], [f.sales for f in firms]),
        "min_price": min(f.price for f in firms),
        "max_price": max(f.price for f in firms),
        "leader_price": industry.leader_price,
        "price_cv": _cv([f.price for f in priced]),
        "uc_cv": _cv([firm_uc(f, delta) for f in priced]),
        "leader_is_lowest_cost": leader is lowest_cost,
        "n_at_war": sum(f.at_war for f in firms),
        "capacity": sum(p.capacity for p in plants),
        "util": _weighted([f.util for f in firms], [f.producing_capacity for f in firms]),
        "profit": profit,
        "profit_rate": _weighted([f.profit_rate for f in firms], capital),
        "profit_rate_newest": _weighted(
            [p.profit / p.purchase_cost for p in newest_plants],
            [p.capacity for p in newest_plants],
        ),
        "incremental_rate": (
            (profit - industry.previous_profit) / industry.previous_investment
            if industry.previous_investment > 0.0 else None
        ),
        "r_new": industry.r_new,
        "cash": sum(f.cash for f in industry.firms),
        "debt": sum(f.debt for f in industry.firms),
        "net_worth": sum(f.net_worth for f in industry.firms),
        "dividends": sum(f.dividends for f in firms),
        "write_offs": sum(f.write_offs for f in firms),
        "investment": sum(f.investment for f in firms + industry.entries),
        "capacity_retired": sum(p.capacity for p in industry.retired),
        "replacements": industry.replacements,
        "entries": len(industry.entries),
        "entries_shaikh": sum(f.type == "shaikh" for f in industry.entries),
        "entries_okishio": sum(f.type == "okishio" for f in industry.entries),
        "exits": len(industry.exits),
        "exits_bankruptcy": sum(r == "bankruptcy" for _, r in industry.exits),
        "exits_share": sum(r == "share" for _, r in industry.exits),
        "exits_non_renewal": sum(r == "non-renewal" for _, r in industry.exits),
        "roe_cash": industry.roe.cash,
        "roe_loans": industry.roe.loans,
        "loan_losses": industry.roe.loan_losses,
    }
    for firm_type in ("shaikh", "okishio"):
        group = [f for f in firms if f.type == firm_type]
        row[f"n_{firm_type}"] = sum(f.type == firm_type for f in industry.firms)
        row[f"share_{firm_type}"] = sum(f.share for f in industry.firms if f.type == firm_type)
        row[f"sales_{firm_type}"] = sum(f.sales for f in group)
        row[f"capacity_{firm_type}"] = sum(f.producing_capacity for f in group)
        row[f"profit_rate_{firm_type}"] = _weighted(
            [f.profit_rate for f in group],
            [sum(p.purchase_cost for p in f.producing_plants) for f in group],
        )
        for name in techniques:
            row[f"capacity_{firm_type}_{name}"] = sum(
                p.capacity for f in group for p in f.producing_plants if p.technique == name
            )
    for name in techniques:
        row[f"capacity_{name}"] = sum(p.capacity for p in plants if p.technique == name)
    return row
