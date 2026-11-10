"""The tally of a period's flows and the period table (v4-plan.md, sections 4 and 8).

The table has one row per period and label, in industry.rows. It observes and never decides:
it draws no random number and writes nothing a rule reads. Undefined values are None.

The tally is a list with one entry a flow, kept by firm. The table sums the entries of a
label; the run viewer sums those of a firm. A firm that left at step 6 is still in the tally
of its last period.
"""
from math import fsum, isclose
from typing import NamedTuple

from equations.common_unit_cost import unit_cost
from parameters import LABELS

# The flows of a period, in the order of their columns in the period table.
KEYS = ("dividends", "cap_retired", "cap_retired_age", "cap_retired_cost", "cap_retired_idle",
        "cap_released", "withdrawn", "cap_ordered", "cap_exit", "cap_entry",
        "orders", "orders_dearer", "drawn", "kept", "entries", "exits")


class Flow(NamedTuple):
    """One flow of the period."""
    firm_id: int           # the serial number of the firm
    label: str             # its label
    key: str               # one of KEYS
    amount: float


def count(industry, firm, key: str, amount: float) -> None:
    """Add a flow of this period to the tally, under the firm that made it."""
    assert key in KEYS, key
    industry.tally.append(Flow(firm.id, firm.label, key, amount))


def sum_flows(entries: list[Flow]) -> dict:
    """The total of each flow over some entries of the tally.

    The sums are exact (math.fsum), so no total depends on the order of the firms.
    """
    amounts = {key: [] for key in KEYS}
    for flow in entries:
        amounts[flow.key].append(flow.amount)
    totals = {}
    for key in KEYS:
        totals[key] = fsum(amounts[key])
    return totals


def ratio(numerator: float, denominator: float) -> float | None:
    """A ratio, undefined when its denominator is not positive."""
    if denominator > 0.0:
        return numerator / denominator
    return None


def weighted_mean(values: list[float], weights: list[float]) -> float | None:
    """A mean with weights, undefined when the weights sum to nothing."""
    total = fsum(value * weight for value, weight in zip(values, weights))
    return ratio(total, fsum(weights))


def plant_unit_cost(plant, p) -> float:
    """The unit cost of a plant's technique."""
    return unit_cost(plant.technique.ucs, plant.technique.kappa, p.delta)


def record_production(industry) -> None:
    """The two rows of the period, written at the end of step 3: before any plant or firm
    leaves. The industry columns are the same on both rows."""
    shared = industry_columns(industry)
    for label in LABELS:
        row = label_columns(industry, label)
        row.update(shared)
        industry.rows.append(row)


def industry_columns(industry) -> dict:
    """The columns that describe the whole industry at step 3."""
    p = industry.params
    firms = industry.firms
    # The firms with a plant in operation: those that have a unit cost and a profit rate.
    active = [firm for firm in firms if firm.plants]

    # The lowest price posted by a firm in operation, and the lowest unit cost among the
    # best plants of those firms.
    prices = [firm.price for firm in active]
    costs = [min(plant_unit_cost(plant, p) for plant in firm.plants) for firm in active]
    low_price = min(prices, default=None)
    low_cost = min(costs, default=None)
    # Whether a firm that posts the lowest price also has the lowest unit cost.
    leaders = [isclose(price, low_price) and isclose(cost, low_cost)
               for price, cost in zip(prices, costs)]

    # The price of the industry is weighted by sales; undefined when nothing is sold.
    price = weighted_mean([firm.price for firm in firms], [firm.sales for firm in firms])
    price_over_reg = None
    if price is not None and industry.reg_price > 0.0:
        price_over_reg = price / industry.reg_price

    # The realised rate of each firm in operation: profit over the purchase cost of its plants.
    rates = [firm.profit / fsum(plant.cost for plant in firm.plants) for firm in active]
    return {
        "demand": industry.demand,
        "lost": industry.lost,
        "low_price": low_price,
        "reg_price": industry.reg_price,
        "price_over_reg": price_over_reg,
        "r_new": industry.r_new,
        "war": int(any(firm.cut for firm in firms)),
        "leader_cheapest": int(any(leaders)),
        "rate_low": min(rates, default=None),
        "rate_high": max(rates, default=None),
    }


def label_columns(industry, label: str) -> dict:
    """The columns that describe the firms of one label at step 3."""
    p = industry.params
    # The firms that carry this label, and their plants in operation.
    group = [firm for firm in industry.firms if firm.label == label]
    plants = [plant for firm in group for plant in firm.plants]
    sizes = [plant.capacity for plant in plants]

    capacity = fsum(sizes)
    sales = fsum(firm.sales for firm in group)
    sold = fsum(firm.sales for firm in industry.firms)
    profit = fsum(firm.profit for firm in group)
    capital = fsum(plant.cost for plant in plants)

    # The price of the label is weighted by sales, or by capacity when it sells nothing.
    weights = [firm.capacity for firm in group]
    if sales > 0.0:
        weights = [firm.sales for firm in group]
    return {
        "t": industry.time,
        "label": label,
        "rule": getattr(p, "rule_" + label),
        "firms": len(group),
        "capacity": capacity,
        "share": fsum(firm.share for firm in group),
        "notional": fsum(firm.notional for firm in group),
        "sales": sales,
        "sales_share": ratio(sales, sold),
        "util": ratio(sales, capacity),
        "price": weighted_mean([firm.price for firm in group], weights),
        "ucs": weighted_mean([plant.technique.ucs for plant in plants], sizes),
        "kappa": weighted_mean([plant.technique.kappa for plant in plants], sizes),
        "unit_cost": weighted_mean([plant_unit_cost(plant, p) for plant in plants], sizes),
        "cuts": sum(firm.cut for firm in group),
        "profit": profit,
        "capital": capital,
        "profit_rate": ratio(profit, capital),
        "overtime": fsum(max(0.0, plant.output - plant.capacity) for plant in plants),
    }


def record_end(industry) -> None:
    """The two rows of the period are completed after step 6.

    They gain the flows of the tally, next period's capacity and the closing stocks.
    """
    for row in industry.rows[-len(LABELS):]:
        # The flows of the label's firms, those that left this period included.
        entries = [flow for flow in industry.tally if flow.label == row["label"]]
        row.update(sum_flows(entries))

        # Next period's capacity: what is in operation, less what left, plus what is on order.
        row["capacity_next"] = (row["capacity"] - row["cap_retired"] - row["cap_exit"]
                                + row["cap_ordered"] + row["cap_entry"])

        # The closing stocks of the firms that carry the label and are still in the industry.
        group = [firm for firm in industry.firms if firm.label == row["label"]]
        row["share_end"] = fsum(firm.share for firm in group)
        row["cash"] = fsum(firm.cash for firm in group)
        row["funds"] = fsum(firm.funds for firm in group)
        row["write_offs"] = fsum(firm.write_offs for firm in group)

        # Their mean hurdle; undefined without a firm.
        row["hurdle"] = None
        if group:
            row["hurdle"] = fsum(firm.hurdle for firm in group) / len(group)
