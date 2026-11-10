"""Regulating technique and price of production.

    R   = the technique in operation with the lowest unit cost
    p_R = uc_R + rbar kappa_R

Source: v4-final-model.md, "Setting" and "The one rule that differs". A tie between two
techniques goes to the lower kappa.
"""
from equations.common_unit_cost import unit_cost


def regulating_technique(techniques: list, delta: float):
    """The technique with the lowest unit cost among those given."""
    # Lowest unit cost first; a tie goes to the lower kappa.
    return min(techniques, key=lambda technique: (
        unit_cost(technique.ucs, technique.kappa, delta),
        technique.kappa,
    ))


def price_of_production(ucs: float, kappa: float, delta: float, rbar: float) -> float:
    """The price at which a technique earns the general rate at normal output."""
    return unit_cost(ucs, kappa, delta) + rbar * kappa
