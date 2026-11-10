"""A design of the neutral set, drawn from a technique o.

    ucs_n = (1 + s cos w) ucs_o,   kappa_n = (1 + s sin w) kappa_o,   s = u A,   w = 2 pi v

Source: v4-final-model.md, "Technical change", the option `tech_change = "neutral"`. The
direction is uniform on the circle in the plane of the two proportional changes, so no
direction of technical change is favoured. u is uniform on (0, 1] and v on [0, 1).
"""
from math import cos, pi, sin


def draw_neutral(ucs_o: float, kappa_o: float, u_step: float, u_direction: float,
                 step: float) -> tuple[float, float]:
    """The design as (ucs, kappa)."""
    size = u_step * step
    angle = 2.0 * pi * u_direction
    return (1.0 + size * cos(angle)) * ucs_o, (1.0 + size * sin(angle)) * kappa_o
