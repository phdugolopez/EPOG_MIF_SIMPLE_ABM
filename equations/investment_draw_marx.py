"""A Marx-biased design drawn from a technique o.

    ucs_n = (1 - a) ucs_o,   kappa_n = (1 + k a) kappa_o,   a = u A,   k = beta e^(sigma z)

Source: v4-final-model.md, "Technical change", and the second formula below the schedule.
u is uniform on (0, 1] and z standard normal: the design saves operating cost and, with
beta above 0, costs more capital per unit.
"""
from math import exp


def draw_marx(ucs_o: float, kappa_o: float, u: float, z: float, step: float, bias: float,
              spread: float) -> tuple[float, float]:
    """The design as (ucs, kappa)."""
    saving = u * step
    k = bias * exp(spread * z)
    return (1.0 - saving) * ucs_o, (1.0 + k * saving) * kappa_o
