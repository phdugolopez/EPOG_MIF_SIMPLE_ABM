"""The cost a price must cover, and the periods a plant has spent below it.

    cost = ucs                    under scrap_cost = "operating_cost" (default)
    cost = ucs + delta kappa      under scrap_cost = "unit_cost"
    periods = previous + 1  if the owner's price is below the cost, else 0

Source: v4-final-model.md, "Schedule", step 4. The periods are consecutive: one period at or
above the cost starts the count again.
"""


def scrap_cost(ucs: float, kappa: float, delta: float, rule: str) -> float:
    """The cost of a plant that its owner's price must cover."""
    if rule == "unit_cost":
        return ucs + delta * kappa
    return ucs


def periods_below_cost(previous: int, price: float, cost: float) -> int:
    """Consecutive periods with the price below the cost, this period included."""
    if price < cost:
        return previous + 1
    return 0
