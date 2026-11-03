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
    """Record macro, per-firm, per-plant and flow-matrix rows for the period."""
    industry.history.append(collect_macro_data(industry))
    for firm in industry.firms:
        industry.firm_history.append(firm_row(industry, firm))
        for plant in firm.plants:
            industry.plant_history.append(plant_row(industry, firm, plant))
    for item, row in industry.flows.items():
        industry.flow_history.append({"time": industry.time, "item": item, **row})


def firm_row(industry, firm) -> dict:
    newest = max(firm.plants + firm.pending_plants, key=lambda p: p.vintage, default=None)
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
        "capacity": firm.capacity,
        "n_plants": len(firm.plants),
        "newest_technique": newest.technique if newest else "",
        "cash": firm.cash,
        "debt": firm.debt,
        "book_value": firm.book_value,
        "net_worth": firm.net_worth,
        "profit": firm.profit,
        "profit_rate": firm.profit_rate,
        "dividends": firm.dividends,
        "write_offs": firm.write_offs,
        "investment": firm.investment,
        "at_war": firm.at_war,
        "born": firm.born,
    }


def plant_row(industry, firm, plant) -> dict:
    row = asdict(plant)
    row["time"] = industry.time
    row["firm_id"] = firm.firm_id
    row["firm_type"] = firm.type
    row["profit_rate"] = plant.profit / plant.purchase_cost
    return row


def _weighted(values, weights) -> float:
    total = sum(weights)
    return sum(v * w for v, w in zip(values, weights)) / total if total > 0.0 else 0.0


def collect_macro_data(industry) -> dict:
    firms = industry.firms
    techniques = list(industry.techniques)
    row = {
        "time": industry.time,
        "demand": industry.demand(),
        "sales": sum(f.sales for f in firms),
        "unserved": industry.unserved,
        "unmet": sum(f.unmet for f in firms),
        "hhi": sum(f.share**2 for f in firms),
        "n_firms": len(firms),
        "mean_price": _weighted([f.price for f in firms], [f.sales for f in firms]),
        "min_price": min(f.price for f in firms),
        "max_price": max(f.price for f in firms),
        "profit": sum(f.profit for f in firms),
        "profit_rate": _weighted(
            [f.profit_rate for f in firms], [f.capital for f in firms]
        ),
        "cash": sum(f.cash for f in firms),
        "debt": sum(f.debt for f in firms),
        "net_worth": sum(f.net_worth for f in firms),
        "dividends": sum(f.dividends for f in firms),
        "write_offs": sum(f.write_offs for f in firms),
        "investment": sum(f.investment for f in firms),
        "roe_cash": industry.roe.cash,
        "roe_loans": industry.roe.loans,
        "loan_losses": industry.roe.loan_losses,
    }
    for firm_type in ("shaikh", "okishio"):
        group = [f for f in firms if f.type == firm_type]
        row[f"n_{firm_type}"] = len(group)
        row[f"share_{firm_type}"] = sum(f.share for f in group)
        row[f"sales_{firm_type}"] = sum(f.sales for f in group)
        row[f"capacity_{firm_type}"] = sum(f.capacity for f in group)
        row[f"profit_rate_{firm_type}"] = _weighted(
            [f.profit_rate for f in group], [f.capital for f in group]
        )
        for name in techniques:
            row[f"capacity_{firm_type}_{name}"] = sum(
                p.capacity for f in group for p in f.plants if p.technique == name
            )
    for name in techniques:
        row[f"capacity_{name}"] = sum(
            p.capacity for f in firms for p in f.plants if p.technique == name
        )
    return row
