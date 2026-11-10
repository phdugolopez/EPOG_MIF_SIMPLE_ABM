def scrap_cost(ucs: float, kappa: float, delta: float, rule: str) -> float:
    """The cost the price must cover: ucs, or ucs + delta kappa under "unit_cost"."""
    return ucs + delta * kappa if rule == "unit_cost" else ucs


def periods_below_cost(previous: int, price: float, cost: float) -> int:
    """Consecutive periods with the price below the scrap cost."""
    return previous + 1 if price < cost else 0
