"""The period table: one row per period and label, kept in industry.rows (plan, section 6).
It observes and never decides: it draws no random number and writes nothing a rule reads.
A value that is not defined (a label without firms, capacity or sales) is None."""
from math import fsum, isclose

from equations.common_unit_cost import unit_cost
from parameters import LABELS

KEYS = ("dividends", "cap_retired", "cap_retired_age", "cap_retired_cost", "cap_retired_idle",
        "cap_released", "withdrawn", "cap_ordered", "cap_exit", "cap_entry",
        "orders", "orders_dearer", "drawn", "kept", "entries", "exits")


def reset_tally(industry) -> None:
    """A new tally of the period's flows, by label."""
    industry.tally = {label: {key: [] for key in KEYS} for label in LABELS}


def count(industry, firm, key: str, amount: float) -> None:
    """Add a flow of this period to the tally of the firm's label."""
    industry.tally[firm.label][key].append(amount)


def flows(industry, label: str) -> dict:
    """The period's flows of a label, summed exactly: no total depends on the order of firms."""
    return {key: fsum(amounts) for key, amounts in industry.tally[label].items()}


def ratio(a: float, b: float) -> float | None:
    return a / b if b > 0.0 else None


def mean(values: list[float], weights: list[float]) -> float | None:
    return ratio(fsum(v * w for v, w in zip(values, weights)), fsum(weights))


def record_production(industry) -> None:
    """The two rows of period t, written at the end of step 3: before any plant or firm leaves.
    The last columns describe the industry and are the same on both rows."""
    p, firms = industry.params, industry.firms
    active = [firm for firm in firms if firm.plants]
    best = [min(unit_cost(q.technique.ucs, q.technique.kappa, p.delta) for q in firm.plants)
            for firm in active]
    rates = [firm.profit / fsum(q.cost for q in firm.plants) for firm in active]
    low = min((firm.price for firm in active), default=None)
    price = mean([firm.price for firm in firms], [firm.sales for firm in firms])
    sold = fsum(firm.sales for firm in firms)
    shared = {
        "demand": industry.demand, "lost": industry.lost, "low_price": low,
        "reg_price": industry.reg_price,
        "price_over_reg": price / industry.reg_price if price and industry.reg_price else None,
        "r_new": industry.r_new, "war": int(any(firm.cut for firm in firms)),
        "leader_cheapest": int(any(isclose(firm.price, low) and isclose(cost, min(best))
                                   for firm, cost in zip(active, best))),
        "rate_low": min(rates, default=None), "rate_high": max(rates, default=None),
    }
    for label in LABELS:
        group = [firm for firm in firms if firm.label == label]
        plants = [q for firm in group for q in firm.plants]
        sizes = [q.capacity for q in plants]
        sales, profit = fsum(firm.sales for firm in group), fsum(firm.profit for firm in group)
        capacity, capital = fsum(sizes), fsum(q.cost for q in plants)
        weights = [firm.sales if sales > 0.0 else firm.capacity for firm in group]
        row = {
            "t": industry.time, "label": label, "rule": getattr(p, "rule_" + label),
            "firms": len(group), "capacity": capacity,
            "share": fsum(firm.share for firm in group),
            "notional": fsum(firm.notional for firm in group),
            "sales": sales, "sales_share": ratio(sales, sold), "util": ratio(sales, capacity),
            "price": mean([firm.price for firm in group], weights),
            "ucs": mean([q.technique.ucs for q in plants], sizes),
            "kappa": mean([q.technique.kappa for q in plants], sizes),
            "unit_cost": mean([unit_cost(q.technique.ucs, q.technique.kappa, p.delta)
                               for q in plants], sizes),
            "cuts": sum(firm.cut for firm in group),
            "profit": profit, "capital": capital, "profit_rate": ratio(profit, capital),
        }
        row.update(shared)
        industry.rows.append(row)


def record_end(industry) -> None:
    """Completes the two rows of t after step 6: the flows of the tally, next period's capacity
    and the stocks of the label's firms at the end of the period."""
    for row in industry.rows[-len(LABELS):]:
        group = [firm for firm in industry.firms if firm.label == row["label"]]
        row.update(flows(industry, row["label"]))
        row["capacity_next"] = (row["capacity"] - row["cap_retired"] + row["cap_ordered"]
                                - row["cap_exit"] + row["cap_entry"])
        row["share_end"] = fsum(firm.share for firm in group)
        row["cash"] = fsum(firm.cash for firm in group)
        row["funds"] = fsum(firm.funds for firm in group)
        row["write_offs"] = fsum(firm.write_offs for firm in group)
        row["hurdle"] = mean([firm.hurdle for firm in group], [1.0] * len(group))
