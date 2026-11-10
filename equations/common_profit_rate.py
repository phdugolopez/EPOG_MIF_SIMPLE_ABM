from equations.common_unit_cost import unit_cost


def profit_rate_at_price(price: float, ucs: float, kappa: float, delta: float) -> float:
    """(p - uc) / kappa at normal output."""
    return (price - unit_cost(ucs, kappa, delta)) / kappa
