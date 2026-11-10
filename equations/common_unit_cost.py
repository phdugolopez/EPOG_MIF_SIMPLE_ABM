"""Unit cost of a technique: uc = ucs + delta kappa.

Source: v4-final-model.md, "Setting". The operating cost ucs is Shaikh's prime cost; the unit
cost adds depreciation, delta = 1 / T.
"""


def unit_cost(ucs: float, kappa: float, delta: float) -> float:
    """The cost per unit of normal output: operating cost plus depreciation."""
    return ucs + delta * kappa
