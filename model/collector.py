"""Outputs of the model and the checks of every period.

The collector observes and never decides: it never draws from industry.rng and never
writes to state a mechanism reads. after_step copies into industry.record what later
steps overwrite; collect builds the rows of the period at step 7 from that record and
from the state; check_stock_flow stores the residuals of every check in the macro row.

Firm aggregates over plants (vintages), each with its weight:
  ucs     output-weighted over the plants that ran (output > 0) this period;
  kappa   capacity-weighted over the plants in operation this period;
  uc      capacity-weighted ucs + delta kappa over the plants in operation;
  k_cost  sum of kappa_v * capacity_v over the plants in operation (= Firm.capital at
          step 3, so that r_avg = profit / k_cost);
  k_book  sum of book values of plants in operation and on order, after step 6;
  r_newest  capacity-weighted (price - uc_v) / kappa_v over the plants in operation
          with the highest vintage, at normal output.
"""

import json
import math

from equations.desired_capacity import desired_capacity
from equations.entry_probability import entry_probability
from equations.exit_conditions import EXIT_CAUSES
from equations.hurdle import best_profit_rate, hurdle
from equations.technique_choice import choose_technique
from equations.unit_cost import unit_cost

# The pair of rules a firm can apply; tech_other is the choice of the other one.
OTHER_RULE = {"unit_cost": "profit_rate", "profit_rate": "unit_cost"}


class StockFlowError(AssertionError):
    """Raised when the accounts of a period do not add up."""


def after_step(industry, step: int) -> None:
    """Copy into the period record what a later step overwrites. Called by run_period
    after each step; it reads the state and never writes to anything a mechanism reads.

    1: debt and the trailing count of periods below U_WAR (before step 2 appends);
    2: the replicator shares, before step 6 rescales them;
    3: debt after the overdraft, book value of each plant before write-offs;
    4: capacity on order after scrapping (replacement orders);
    5: debt after investment.
    """
    record = industry.record
    if step == 1:
        u_war = industry.parameters.U_WAR
        record.clear()
        record.update({"t": industry.time, "firms": {}, "book": {},
                       "events_start": len(industry.events)})
        for firm in industry.firms:
            low = 0
            for u in reversed(firm.util_history):
                if u >= u_war:
                    break
                low += 1
            record["firms"][firm.firm_id] = {"debt_start": firm.debt, "low_util": low}
    elif step == 2:
        shares = [f.share for f in industry.firms]
        record["share_sum_demand"] = sum(shares)
        record["share_min_demand"] = min(shares, default=0.0)
        for firm in industry.firms:
            record["firms"][firm.firm_id]["share_demand"] = firm.share
    elif step == 3:
        for firm in industry.firms:
            record["firms"][firm.firm_id]["debt_3"] = firm.debt
            for plant in firm.plants:
                record["book"][plant.plant_id] = plant.book_value
    elif step == 4:
        for firm in industry.firms:
            record["firms"][firm.firm_id]["cap_replace"] = _capacity(firm.pending_plants)
    elif step == 5:
        for firm in industry.firms:
            record["firms"][firm.firm_id]["debt_5"] = firm.debt


# --- Event log -----------------------------------------------------------------------

EVENT_COLUMNS = (
    "t", "step", "event", "firm_id", "plant_id", "group", "rule", "hurdle", "tech",
    "other_tech", "capacity", "value", "cause", "other_id",
)
ORDER_STEP = {"replacement": 4, "expansion": 5, "entry": 6}


def log_event(industry, event: str, step: int, firm=None, plant=None, **fields) -> None:
    """Append one row to industry.events. firm and plant fill the id, label, rule,
    hurdle, technique and capacity columns; fields fill or override the others.
    Missing ids are -1."""
    rules = industry.parameters.HURDLE_RULES
    row = {
        "t": industry.time, "step": step, "event": event,
        "firm_id": firm.firm_id if firm is not None else -1,
        "plant_id": plant.plant_id if plant is not None else -1,
        "group": firm.type if firm is not None else "",
        "rule": rules[firm.type] if firm is not None else "",
        "hurdle": firm.hurdle if firm is not None else None,
        "tech": plant.technique if plant is not None else "",
        "other_tech": "",
        "capacity": plant.capacity if plant is not None else None,
        "value": None, "cause": "", "other_id": -1,
    }
    row.update(fields)
    industry.events.append(row)


def log_order(industry, firm, plant, cost: float, cause: str) -> None:
    """An order: technique chosen, the other rule's choice at the same price, cost.
    An entrant's hurdle and known techniques are set before its order (create_entrant)."""
    log_event(industry, "order", ORDER_STEP[cause], firm, plant,
              other_tech=tech_other(industry, firm), value=cost, cause=cause)


def log_exit(industry, firm, reason: str) -> None:
    """Called by remove_firm before anything is paid or written off: the exit with the
    firm's net worth and capacity left; the bills it could not pay, if any (negative
    cash, CASH_SHORTFALL = "bankruptcy"); the default, if any, with the debt the firm
    cannot repay (credit_market.default repays min(cash, debt) and writes off the rest);
    then one retire (cause "exit") per plant in operation and one cancel per plant on
    order, valued at the book value written off."""
    log_event(industry, "exit", 6, firm, value=firm.net_worth, cause=reason,
              capacity=firm.capacity)
    if firm.cash < 0.0:
        log_event(industry, "unpaid_bills", 6, firm, value=-firm.cash)
    loss = firm.debt - max(0.0, min(firm.cash, firm.debt))
    if loss > 0.0:
        log_event(industry, "default", 6, firm, value=loss)
    for plant in firm.plants:
        log_event(industry, "retire", 6, firm, plant, value=plant.book_value, cause="exit")
    for plant in firm.pending_plants:
        log_event(industry, "cancel", 6, firm, plant, value=plant.book_value, cause="exit")


def _episodes(flags):
    """Maximal runs of True in a list of (t, flag): [(first t, last t), ...]."""
    runs, start, last = [], None, None
    for t, flag in flags:
        if flag and start is None:
            start = t
        if not flag and start is not None:
            runs.append((start, last))
            start = None
        last = t
    if start is not None:
        runs.append((start, last))
    return runs


def episode_events(industry) -> list[dict]:
    """War and cutting episodes, derived after the run from the macro and firm rows.

    An industry war is a maximal run of periods with war_on (at least one firm
    cutting): war_start at its first period s, value = price_avg at s - 1 (None at
    s = 0); war_end at its last period e, value = the lowest price_avg over s..e,
    cause "censored" if the war is still on in the last period. other_id numbers the
    episodes from 1. A firm's cutting episode is the same from its cutting flag:
    cut_start / cut_end with value = its price, cut_end cause "exit" when the firm
    leaves while cutting and "censored" when it still cuts in the last period.
    """
    rows = []
    if not industry.history:
        return rows
    last = industry.history[-1]["t"]
    price = {r["t"]: r["price_avg"] for r in industry.history}
    blank = {"firm_id": -1, "plant_id": -1, "group": "", "rule": "", "hurdle": None,
             "tech": "", "other_tech": "", "capacity": None}
    flags = [(r["t"], r["war_on"]) for r in industry.history]
    for n, (s, e) in enumerate(_episodes(flags), start=1):
        rows.append({"t": s, "step": 1, "event": "war_start", **blank,
                     "value": price.get(s - 1), "cause": "", "other_id": n})
        rows.append({"t": e, "step": 1, "event": "war_end", **blank,
                     "value": min(price[t] for t in range(s, e + 1)),
                     "cause": "censored" if e == last else "", "other_id": n})
    by_firm = {}
    for r in industry.firm_history:
        by_firm.setdefault(r["firm_id"], []).append(r)
    for firm_id, firm_rows in by_firm.items():
        at = {r["t"]: r for r in firm_rows}
        for s, e in _episodes([(r["t"], r["cutting"]) for r in firm_rows]):
            for t, event in ((s, "cut_start"), (e, "cut_end")):
                r = at[t]
                cause = ""
                if event == "cut_end":
                    cause = "exit" if r["exited"] else "censored" if e == last else ""
                rows.append({
                    "t": t, "step": 1, "event": event, "firm_id": firm_id,
                    "plant_id": -1, "group": r["group"], "rule": r["rule"],
                    "hurdle": r["hurdle"], "tech": "", "other_tech": "", "capacity": None,
                    "value": r["price"], "cause": cause, "other_id": -1,
                })
    return rows


def events_table(industry) -> list[dict]:
    """The event log of the run: logged events plus war and cutting episodes, sorted by
    (t, step, event, firm_id, plant_id)."""
    rows = industry.events + episode_events(industry)
    return sorted(rows, key=lambda r: (r["t"], r["step"], r["event"], r["firm_id"],
                                       r["plant_id"]))


def _tolerance(scale: float) -> float:
    return 1e-9 * max(1.0, scale)


def residuals(industry) -> tuple[dict, list[str]]:
    """Every check of the period as a residual, and a message for each one that fails.

    Money checks use the tolerance 1e-9 * max(1, scale), scale = 1 + the sum of absolute
    flows + money + the cash and debt stocks (rounding grows with the stocks over long
    runs, version 2); quantity checks use 1e-9 * max(1, demand); share checks 1e-12.
    """
    config = industry.parameters
    scale = 1.0 + sum(
        abs(v) for row in industry.flows.values() for v in row.values()
    ) + abs(industry.money) + abs(industry.roe.cash) + abs(industry.roe.loans) + sum(
        abs(f.cash) + abs(f.debt) for f in industry.firms
    )
    tol = _tolerance(scale)
    tol_q = _tolerance(industry.demand())
    tol_share = 1e-12  # brief, section 3.7
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
    out["cap_resid"] = _identity_resid(flows)
    if abs(out["cap_resid"]) > tol_q:
        fails.append(f"cap_resid = {out['cap_resid']}")
    #    The same identity group by group; stored: the largest residual in absolute
    #    value, read from the group flows collect computed (recomputed when residuals is
    #    called on its own, before collect).
    group_flows = industry.record.get("group_flows")
    if group_flows is None:
        group_flows = {
            label: capacity_flows(industry, firms) for label, firms
            in _by_label(industry, industry.producers + industry.entries).items()
        }
    out["cap_resid_group"] = max(
        (abs(_identity_resid(flows)) for flows in group_flows.values()), default=0.0
    )
    if out["cap_resid_group"] > tol_q:
        fails.append(f"cap_resid_group = {out['cap_resid_group']}")

    # 8. No posted price below the firm's floor. Only the anchor rule enforces its floor in
    #    every branch; the version 2 rules undercut or rise relative to rivals and can post
    #    below the floor they used (a shortage under "leader_follow", a floor that rose
    #    with scrapping), so there the count is reported but is not a failure.
    below = [
        f for f in producers
        if f.producing_plants and f.price < f.p_floor - _tolerance(f.p_floor)
    ]
    out["floor_viol"] = len(below)
    if below and config.PRICING_RULE == "anchor":
        fails.append(f"firm {below[0].firm_id} priced {below[0].price} below its floor")

    out["check_fail"] = len(fails)
    return out, fails


def _capacity(plants) -> float:
    return sum(p.capacity for p in plants)


def _identity_resid(flows: dict) -> float:
    return (flows["k_start"] - flows["retired"] - flows["exit"] + flows["ordered"]
            + flows["entry"] - flows["cancelled"] - flows["k_next"])


def _by_label(industry, firms) -> dict:
    """firms split by label, one entry per key of HURDLE_RULES in sorted order (empty
    groups included). Grouping outputs by label is the only use of firm.type here."""
    groups = {label: [] for label in sorted(industry.parameters.HURDLE_RULES)}
    for firm in firms:
        groups[firm.type].append(firm)
    return groups


def capacity_flows(industry, firms=None) -> dict:
    """The terms of the capacity identity for the period, over `firms` (default: all
    firms that produced this period, plus the entrants).

    k_start: capacity in operation at the start of the period; retired: plants scrapped
    at step 4 (replacements included); exit: plants still in operation at firms that
    leave at step 6; ordered: plants ordered at steps 4 and 5 by every incumbent;
    cancelled: the part of `ordered` placed by firms that leave, written off at exit;
    entry: entrants' plants; k_next: capacity in operation at the start of next period.
    """
    producers, entries = industry.producers, industry.entries
    if firms is not None:
        wanted = {id(f) for f in firms}
        producers = [f for f in producers if id(f) in wanted]
        entries = [f for f in entries if id(f) in wanted]
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
    if industry.history and industry.history[-1]["t"] == industry.time:
        industry.history[-1].update(out)
    if not fails:
        return
    if industry.parameters.CHECKS_RAISE:
        raise StockFlowError(f"t={industry.time}: {fails[0]}")
    industry.n_check_fail += 1


def collect(industry) -> None:
    """Record macro, per-group, per-firm, per-plant and flow-matrix rows for the period.

    Rows cover every firm that produced this period, including those that left at its
    end, and the entrants of the period (whose first plant arrives next period). The
    plants table has a row for every plant in operation at the start of the period,
    those retired at step 4 included.
    """
    delta = industry.parameters.DELTA
    uc = {id(f): firm_uc(f, delta) for f in industry.producers + industry.entries}
    industry.history.append(collect_macro_data(industry, uc))
    exited = {id(f) for f, _ in industry.exits}
    retired = {id(p) for p in industry.retired}
    causes = {
        e["plant_id"]: e["cause"]
        for e in industry.events[industry.record.get("events_start", 0):]
        if e["event"] == "retire"
    }
    for firm in industry.producers + industry.entries:
        industry.firm_history.append(firm_row(industry, firm, retired, uc[id(firm)]))
        for plant in firm.producing_plants:
            industry.plant_history.append(plant_row(
                industry, firm, plant, id(plant) in retired, id(firm) in exited,
                causes.get(plant.plant_id, ""),
            ))
    for item, row in industry.flows.items():
        industry.flow_history.append({"t": industry.time, "item": item, **row})
    industry.group_history.extend(group_rows(industry))
    industry.previous_profit = sum(f.profit for f in industry.producers)
    industry.previous_investment = sum(f.investment for f in industry.producers)


def firm_uc(firm, delta: float) -> float:
    """Capacity-weighted unit cost of the plants that produced this period."""
    plants = firm.producing_plants
    return _weighted([p.ucs + delta * p.kappa for p in plants], [p.capacity for p in plants])


def _weighted_or_none(values, weights):
    total = sum(weights)
    return sum(v * w for v, w in zip(values, weights)) / total if total > 0.0 else None


def r_newest(firm, delta: float):
    """Rate at normal output, (price - uc_v) / kappa_v, on the plants in operation with
    the highest vintage, capacity-weighted. None for a firm with no plant in operation."""
    plants = firm.producing_plants
    if not plants:
        return None
    newest = max(p.vintage for p in plants)
    top = [p for p in plants if p.vintage == newest]
    return _weighted_or_none(
        [(firm.price - unit_cost(p.ucs, p.kappa, delta)) / p.kappa for p in top],
        [p.capacity for p in top],
    )


def tech_other(industry, firm) -> str:
    """Technique the other rule of the pair would pick at the firm's price, now, among
    the techniques the firm knows (the menu, plus its adopted designs under TECH_DRAWS)."""
    config = industry.parameters
    other = OTHER_RULE[config.HURDLE_RULES[firm.type]]
    known = firm.known or industry.menu
    h = hurdle(other, firm.price, known, config.DELTA, config.HURDLE_FLOOR_AT_ZERO)
    return choose_technique(known, h, config.DELTA, config.TAU).name


def firm_row(industry, firm, retired, uc: float | None = None) -> dict:
    """uc: the firm's capacity-weighted unit cost, computed once per period by collect.
    exp_sales and cap_desired are None for an entrant and for a firm that invest()
    skips on non-renewal, since neither reaches the investment rule this period."""
    config = industry.parameters
    delta = config.DELTA
    plants = firm.plants + firm.pending_plants
    newest = max(plants, key=lambda p: p.vintage, default=None)
    producing = firm.producing_plants
    running = [p for p in producing if p.output > 0.0]
    record = industry.record["firms"].get(firm.firm_id)  # None for an entrant
    if uc is None:
        uc = firm_uc(firm, delta)
    ucs_running = [p.ucs for p in running]
    expected = None
    if record is not None and not firm.non_renewal:
        expected = firm.previous_sales if config.INVESTMENT_SALES_LAG else firm.sales
    on_order = _capacity(firm.pending_plants)
    exited = firm.exit_reason != ""
    return {
        "t": industry.time,
        "firm_id": firm.firm_id,
        "type": firm.type,
        "group": firm.type,
        "rule": config.HURDLE_RULES[firm.type],
        "hurdle": firm.hurdle,
        "born": firm.born,
        "price": firm.price,
        "p_normal": firm.p_normal if record is not None else None,
        "p_floor": firm.p_floor if record is not None else None,
        "cutting": firm.at_war,
        "low_util": record["low_util"] if record is not None else None,
        "share": firm.share,
        "share_demand": record["share_demand"] if record is not None else None,
        "share_end": 0.0 if exited else firm.share,
        "sales": firm.sales,
        "util": firm.util,
        "unmet": firm.unmet,
        "capacity": firm.producing_capacity,
        "capacity_next": sum(p.capacity for p in plants),
        "output": sum(p.output for p in producing),
        "ucs": _weighted_or_none(ucs_running, [p.output for p in running]),
        "kappa": _weighted_or_none(
            [p.kappa for p in producing], [p.capacity for p in producing]
        ),
        "uc": uc,
        "margin": firm.price - uc,
        "revenue": firm.revenue,
        "op_cost": firm.operating_cost,
        "gos": firm.revenue - firm.operating_cost,
        "depreciation": firm.depreciation,
        "interest": firm.interest,
        "profit": firm.profit,
        "dividends": firm.dividends,
        "r_avg": firm.profit_rate,
        "r_newest": r_newest(firm, delta),
        "r_best": best_profit_rate(firm.price, firm.known or industry.menu, delta),
        "n_plants": len(producing),
        "oldest_vintage": min((p.vintage for p in producing), default=None),
        "newest_vintage": max((p.vintage for p in producing), default=None),
        "ucs_spread": max(ucs_running) / min(ucs_running) if ucs_running else None,
        "newest_technique": newest.technique if newest else "",
        "cap_retired": sum(p.capacity for p in producing if id(p) in retired),
        "write_off": firm.write_offs,
        "exp_sales": expected,
        "cap_desired": (
            None if expected is None
            else desired_capacity(expected, config.EXPECTED_GROWTH)
        ),
        "cap_ordered": on_order if record is not None else 0.0,
        "cap_replace": record["cap_replace"] if record is not None else 0.0,
        "tech_new": "+".join(sorted({p.technique for p in firm.pending_plants})),
        "tech_other": tech_other(industry, firm),
        "invest_spend": firm.investment,
        # New debt of the period's financing decisions, before any exit settlement:
        # borrow = debt after step 5 - debt at the start (overdraft, repayment and
        # plant finance); borrow_plants = the part taken at steps 4 and 5 for plants.
        "borrow": _borrow(firm, record),
        "borrow_plants": (
            record["debt_5"] - record["debt_3"] if record is not None else firm.debt
        ),
        "cash": firm.cash,
        "debt": firm.debt,
        "retained_earnings": firm.retained_earnings,
        "k_book": firm.book_value,
        "k_cost": sum(p.purchase_cost for p in producing),
        "net_worth": firm.net_worth,
        "n_known": len(firm.known),
        "exited": exited,
        "exit_cause": firm.exit_reason,
    }


def _borrow(firm, record) -> float:
    """Debt after step 5 - debt at the start of the period; an entrant's debt."""
    return record["debt_5"] - record["debt_start"] if record is not None else firm.debt




def group_rows(industry) -> list[dict]:
    """One row per label (key of HURDLE_RULES, sorted), empty groups included.

    Members: the firms that produced this period (step 1) plus the period's entrants.
    Capacity terms are those of the capacity identity (capacity_flows) over the group;
    share_demand sums the step 2 shares of its producers, share_end the shares after
    step 6 of its firms still in the industry (entrants included); cash, debt and
    net_worth are after step 6 (0 for leavers); hurdle_mean is weighted by producing
    capacity (None when the group produced nothing).
    """
    config = industry.parameters
    record = industry.record["firms"]
    exits = {id(f): reason for f, reason in industry.exits}
    producers = _by_label(industry, industry.producers)
    entrants = _by_label(industry, industry.entries)
    remaining = _by_label(industry, industry.firms)
    replaced = {}  # firm_id -> hurdle replacements this period, from the retire events
    for e in industry.events[industry.record.get("events_start", 0):]:
        if e["event"] == "retire" and e["cause"] == "replacement":
            replaced[e["firm_id"]] = replaced.get(e["firm_id"], 0) + 1
    industry.record["group_flows"] = {}  # read by residuals (cap_resid_group)
    rows = []
    for label, firms in producers.items():
        new = entrants[label]
        flows = {k: float(v) for k, v in capacity_flows(industry, firms + new).items()}
        industry.record["group_flows"][label] = flows
        left = [exits[id(f)] for f in firms if id(f) in exits]
        row = {
            "t": industry.time,
            "group": label,
            "rule": config.HURDLE_RULES[label],
            "n_firms": len(firms),
            "capacity": flows["k_start"],
            "capacity_next": flows["k_next"],
            "sales": sum(f.sales for f in firms),
            "share_demand": sum(record[f.firm_id]["share_demand"] for f in firms),
            "share_end": sum(f.share for f in remaining[label]),
            "cap_retired": flows["retired"],
            "cap_replace": float(sum(record[f.firm_id]["cap_replace"] for f in firms)),
            "cap_ordered": flows["ordered"],
            "cap_entry": flows["entry"],
            "cap_exit": flows["exit"],
            "cap_cancelled": flows["cancelled"],
            "cap_resid": _identity_resid(flows),
            "n_replace": sum(replaced.get(f.firm_id, 0) for f in firms),
            "n_entry": len(new),
            "n_exit": len(left),
        }
        for cause in EXIT_CAUSES:
            row[f"n_exit_{cause.replace('-', '_')}"] = left.count(cause)
        row.update({
            "profit": sum(f.profit for f in firms),
            "gos": sum(f.revenue - f.operating_cost for f in firms),
            "invest_spend": sum(f.investment for f in firms + new),
            "borrow": sum(_borrow(f, record.get(f.firm_id)) for f in firms + new),
            "cash": sum(f.cash for f in remaining[label]),
            "debt": sum(f.debt for f in remaining[label]),
            "net_worth": sum(f.net_worth for f in remaining[label]),
            "hurdle_mean": _weighted_or_none(
                [f.hurdle for f in firms], [f.producing_capacity for f in firms]
            ),
        })
        for name in industry.techniques:
            row[f"capacity_{name}"] = sum(
                p.capacity for f in firms for p in f.producing_plants if p.technique == name
            )
        row["capacity_designs"] = sum(
            p.capacity for f in firms for p in f.producing_plants
            if p.technique not in industry.techniques
        )
        rows.append(row)
    return rows


def plant_row(industry, firm, plant, retired: bool, exited: bool, cause: str) -> dict:
    """cause: the retire event's cause this period (age, obsolescence, replacement,
    exit), "" for a plant still in operation."""
    config = industry.parameters
    uc = unit_cost(plant.ucs, plant.kappa, config.DELTA)
    # Field by field rather than dataclasses.asdict, which deep-copies every value.
    row = {
        "plant_id": plant.plant_id,
        "ucs": plant.ucs,
        "kappa": plant.kappa,
        "capacity": plant.capacity,
        "vintage": plant.vintage,
        "initial": plant.initial,
        "age": plant.age,
        "output": plant.output,
        "overtime_output": plant.overtime_output,
        "profit": plant.profit,
        "lifetime_profit": plant.lifetime_profit,
        "tech": plant.technique,
        "k_book": plant.book_value,
        "below_cost": plant.periods_below_cost,
        "periods_idle": plant.periods_idle,
        "wear": plant.wear,
    }
    row.update({
        "t": industry.time,
        "firm_id": firm.firm_id,
        "firm_type": firm.type,
        "group": firm.type,
        "uc": uc,
        "running": plant.output > 0.0,
        "r_plant": (firm.price - uc) / plant.kappa,
        "profit_rate": plant.profit / plant.purchase_cost,
        "retired": retired,
        "retire_cause": cause,
        "exited_with_firm": exited,
        "write_off": industry.record["book"].get(plant.plant_id, 0.0) - plant.book_value,
    })
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


def _cv_weighted(values, weights):
    """Weighted coefficient of variation; None when the weights sum to zero."""
    total = sum(weights)
    if total <= 0.0:
        return None
    mean = sum(v * w for v, w in zip(values, weights)) / total
    var = sum(w * (v - mean) ** 2 for v, w in zip(values, weights)) / total
    return var ** 0.5 / mean if mean else None


def tied_ids(firms, key) -> list[int]:
    """Ids of every firm whose key equals the minimum (math.isclose): ties are kept,
    never broken by firm order."""
    if not firms:
        return []
    best = min(key(f) for f in firms)
    return sorted(f.firm_id for f in firms if math.isclose(key(f), best))


def collect_macro_data(industry, uc: dict | None = None) -> dict:
    """uc: id(firm) -> capacity-weighted unit cost, computed once per period by collect."""
    firms = industry.producers
    config = industry.parameters
    delta = config.DELTA
    if uc is None:
        uc = {id(f): firm_uc(f, delta) for f in firms}
    plants = [p for f in firms for p in f.producing_plants]
    techniques = list(industry.techniques)
    capital = [sum(p.purchase_cost for p in f.producing_plants) for f in firms]
    priced = [f for f in firms if f.producing_plants]
    leaders = tied_ids(priced, lambda f: f.price)
    lowest = tied_ids(priced, lambda f: uc[id(f)])
    newest = max((p.vintage for p in plants), default=0)
    newest_plants = [p for p in plants if p.vintage == newest]
    profit = sum(f.profit for f in firms)
    gos = sum(f.revenue - f.operating_cost for f in firms)
    sales = sum(f.sales for f in firms)
    invest_total = sum(f.investment for f in firms + industry.entries)
    previous = industry.history[-1] if industry.history else None
    n_cutting = sum(f.at_war for f in firms)
    row = {
        "t": industry.time,
        "demand": industry.demand(),
        "sales_total": sales,
        "unmet_total": industry.unserved,
        "unmet": sum(f.unmet for f in firms),
        "hhi": sum(f.share ** 2 for f in industry.firms),
        "hhi_sales": sum((f.sales / sales) ** 2 for f in firms) if sales > 0.0 else None,
        "n_firms": len(industry.firms),
        "n_active": len(firms),
        "price_avg": _weighted([f.price for f in firms], [f.sales for f in firms]),
        "min_price": min(f.price for f in firms),
        "max_price": max(f.price for f in firms),
        "price_lead": industry.leader_price,
        "leader_ids": json.dumps(leaders),
        "n_leaders": len(leaders),
        "leader_id": leaders[0] if len(leaders) == 1 else -1,
        "lowest_uc_ids": json.dumps(lowest),
        "n_lowest_uc": len(lowest),
        "lowest_uc_id": lowest[0] if len(lowest) == 1 else -1,
        "price_cv": _cv([f.price for f in priced]),
        "uc_cv": _cv([uc[id(f)] for f in priced]),
        "price_cv_w": _cv_weighted([f.price for f in firms], [f.sales for f in firms]),
        "uc_cv_w": _cv_weighted(
            [uc[id(f)] for f in priced], [f.producing_capacity for f in priced]
        ),
        "leader_is_lowest_cost": bool(set(leaders) & set(lowest)),
        "war_on": n_cutting > 0,
        "n_cutting": n_cutting,
        "capacity_total": sum(p.capacity for p in plants),
        "util": _weighted([f.util for f in firms], [f.producing_capacity for f in firms]),
        "profit": profit,
        "gos_total": gos,
        "profit_rate": _weighted([f.profit_rate for f in firms], capital),
        "profit_rate_newest": _weighted(
            [p.profit / p.purchase_cost for p in newest_plants],
            [p.capacity for p in newest_plants],
        ),
        "incremental_rate": (
            (profit - industry.previous_profit) / industry.previous_investment
            if industry.previous_investment > 0.0 else None
        ),
        "incremental_rate_gross": (
            (gos - previous["gos_total"]) / previous["invest_total"]
            if previous is not None and previous["invest_total"] > 0.0 else None
        ),
        "r_new": industry.r_new,
        "p_entry": entry_probability(industry.r_new, config.RBAR, config.ENTRY_SPEED),
        "cash": sum(f.cash for f in industry.firms),
        "debt": sum(f.debt for f in industry.firms),
        "net_worth": sum(f.net_worth for f in industry.firms),
        "dividends": sum(f.dividends for f in firms),
        "write_offs": sum(f.write_offs for f in firms),
        "invest_total": invest_total,
        "capacity_retired": sum(p.capacity for p in industry.retired),
        "replacements": industry.replacements,
        "entries": len(industry.entries),
        "entries_shaikh": sum(f.type == "shaikh" for f in industry.entries),
        "entries_okishio": sum(f.type == "okishio" for f in industry.entries),
        "exits": len(industry.exits),
        "exits_bankruptcy": sum(r == "bankruptcy" for _, r in industry.exits),
        "exits_share": sum(r == "share" for _, r in industry.exits),
        "exits_non_renewal": sum(r == "non-renewal" for _, r in industry.exits),
        "roe_balance": industry.roe.cash,
        "roe_loans": industry.roe.loans,
        "loan_losses": industry.roe.loan_losses,
        "unpaid_bills": industry.roe.unpaid_bills,
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
        row[f"unit_cost_{firm_type}"] = _weighted(
            [p.ucs + delta * p.kappa for f in group for p in f.producing_plants],
            [p.capacity for f in group for p in f.producing_plants],
        )
        for name in techniques:
            row[f"capacity_{firm_type}_{name}"] = sum(
                p.capacity for f in group for p in f.producing_plants if p.technique == name
            )
    for name in techniques:
        row[f"capacity_{name}"] = sum(p.capacity for p in plants if p.technique == name)
    # Capacity of plants built with designs drawn under TECH_DRAWS (not on the menu).
    row["capacity_designs"] = sum(
        p.capacity for p in plants if p.technique not in industry.techniques
    )
    row["designs_offered"] = sum(
        e["event"] == "design" for e in industry.events[industry.record.get("events_start", 0):]
    )
    row["designs_adopted"] = sum(
        e["event"] == "adopt" for e in industry.events[industry.record.get("events_start", 0):]
    )
    return row
