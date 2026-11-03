from equations.profit_rate_at_price import profit_rate_at_price
from equations.unit_cost import unit_cost


def best_profit_rate(price: float, menu, delta: float) -> float:
    """Highest profit rate on the menu at the given price, at normal output."""
    return max(
        profit_rate_at_price(price, unit_cost(t.ucs, t.kappa, delta), t.kappa) for t in menu
    )


def hurdle(rule: str, price: float, menu, delta: float, floor_at_zero: bool) -> float:
    """h_i: 0 under the unit-cost rule (Shaikh); the best profit rate on offer at the
    firm's own current price under the profit-rate rule (Okishio).

    This is the only equation that differs between the two types. With floor_at_zero,
    h never falls below 0 in a deep price war.
    """
    if rule == "unit_cost":
        return 0.0
    if rule == "profit_rate":
        h = best_profit_rate(price, menu, delta)
        return max(0.0, h) if floor_at_zero else h
    raise ValueError(f"unknown hurdle rule {rule!r}")
