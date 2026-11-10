from equations.common_unit_cost import unit_cost


def regulating_technique(techniques: list, delta: float):
    """The technique in operation with the lowest unit cost; exact ties go to the lower kappa."""
    return min(techniques, key=lambda t: (unit_cost(t.ucs, t.kappa, delta), t.kappa))


def price_of_production(ucs: float, kappa: float, delta: float, rbar: float) -> float:
    """uc + rbar kappa."""
    return unit_cost(ucs, kappa, delta) + rbar * kappa
