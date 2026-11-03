from dataclasses import asdict


class StockFlowError(AssertionError):
    """Raised when the accounts of a period do not add up."""


def _close(a: float, b: float, scale: float) -> bool:
    return abs(a - b) <= 1e-9 * max(1.0, scale)


def check_stock_flow(industry) -> None:
    """Assert stock-flow consistency for the period just run.

    1. Money is conserved: firms' cash plus the rest of the economy's cash is constant.
    2. Firms' debt equals the loans held by the rest of the economy.
    3. For every firm, the change in net worth equals profit - dividends - write-offs
       (+ equity brought in at entry).
    4. Every row of the transaction-flow matrix sums to zero, and each column sums to
       the change in that sector's cash.
    """
    scale = 1.0 + sum(
        abs(v) for row in industry.flows.values() for v in row.values()
    ) + abs(industry.money)
    money = industry.roe.cash + sum(f.cash for f in industry.firms)
    if not _close(money, industry.money, scale):
        raise StockFlowError(f"t={industry.time}: money {money} != {industry.money}")

    debt = sum(f.debt for f in industry.firms)
    if not _close(debt, industry.roe.loans, scale):
        raise StockFlowError(f"t={industry.time}: debt {debt} != loans {industry.roe.loans}")

    for firm in industry.firms:
        change = firm.net_worth - firm.net_worth_start
        expected = firm.profit - firm.dividends - firm.write_offs + firm.equity_in
        if not _close(change, expected, scale):
            raise StockFlowError(
                f"t={industry.time}: firm {firm.firm_id} net worth moved by {change}, "
                f"expected {expected}"
            )

    for item, row in industry.flows.items():
        if not _close(sum(row.values()), 0.0, scale):
            raise StockFlowError(f"t={industry.time}: row {item} does not sum to zero")
    columns = {"firms": 0.0, "roe": 0.0}
    for row in industry.flows.values():
        for sector, value in row.items():
            columns[sector] += value
    cash_now = {"firms": sum(f.cash for f in industry.firms), "roe": industry.roe.cash}
    for sector, total in columns.items():
        if not _close(total, cash_now[sector] - industry.cash_start[sector], scale):
            raise StockFlowError(
                f"t={industry.time}: column {sector} sums to {total}, cash moved by "
                f"{cash_now[sector] - industry.cash_start[sector]}"
            )


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
