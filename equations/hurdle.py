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


def hurdle_at_general_rate(rule: str, rbar: float) -> float:
    """HURDLE_TARGET = "rbar": h = 0 under the unit-cost rule; h = rbar, the general rate of
    profit, under the profit-rate rule. The technique then minimises uc + rbar kappa, the
    price of production at the ruling rate (Sraffa's criterion, Shaikh 2016, p. 320 n. 36):
    the profit-rate rule evaluated at prices of production, the target-return reading of
    the hurdle (the K+S payback rule with b read as 1 / (delta + h)). It is no longer the
    best rate on offer at the current price."""
    if rule == "unit_cost":
        return 0.0
    if rule == "profit_rate":
        return rbar
    raise ValueError(f"unknown hurdle rule {rule!r}")
