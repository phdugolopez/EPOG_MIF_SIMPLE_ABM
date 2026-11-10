"""Choice of a technique at a hurdle, and the frontier of a menu.

    j* = argmin over the menu of  ucs_j + (delta + h) kappa_j

Source: v4-final-model.md, "The one rule that differs". A tie goes to the lower kappa, then
to the lower operating cost. The frontier is for speed only, as in version 3 (v4-plan.md,
section 6): a technique that another beats on both unit cost and kappa is chosen at no hurdle
and never sets the hurdle, so dropping it changes no choice.
"""
from equations.common_unit_cost import unit_cost


def technique_cost(ucs: float, kappa: float, hurdle: float, delta: float) -> float:
    """What a technique costs per unit of normal output to a firm with this hurdle."""
    return ucs + (delta + hurdle) * kappa


def choose_technique(menu: list, hurdle: float, delta: float):
    """The technique of the menu with the lowest cost at the hurdle."""
    # Lowest cost first; a tie goes to the lower kappa, then to the lower operating cost.
    return min(menu, key=lambda technique: (
        technique_cost(technique.ucs, technique.kappa, hurdle, delta),
        technique.kappa,
        technique.ucs,
    ))


def frontier(menu: list, delta: float) -> list:
    """The techniques of the menu that no other beats on both unit cost and kappa."""
    points = [(unit_cost(technique.ucs, technique.kappa, delta), technique.kappa)
              for technique in menu]
    # A technique stays unless another point of the menu beats its own.
    return [technique for technique, point in zip(menu, points) if not is_beaten(point, points)]


def is_beaten(point: tuple, points: list) -> bool:
    """Whether another point has at most this unit cost and at most this kappa."""
    cost, kappa = point
    # Two techniques on the same point do not beat each other.
    return any(other[0] <= cost and other[1] <= kappa for other in points if other != point)
