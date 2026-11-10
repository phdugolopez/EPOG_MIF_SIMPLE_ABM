"""Profit rate of a technique at a price: r = (p - uc) / kappa.

Source: v4-final-model.md, "The one rule that differs". It is the rate at normal output,
after depreciation, on the capital per unit of normal output.
"""
from equations.common_unit_cost import unit_cost


def profit_rate_at_price(price: float, ucs: float, kappa: float, delta: float) -> float:
    """The rate a technique earns at normal output when it sells at this price."""
    return (price - unit_cost(ucs, kappa, delta)) / kappa
