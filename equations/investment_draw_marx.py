from math import exp


def draw_marx(ucs_o: float, kappa_o: float, u: float, z: float, step: float, bias: float,
              spread: float) -> tuple[float, float]:
    """A Marx-biased design from the reference o: ucs_n = (1 - a) ucs_o, kappa_n = (1 + k a)
    kappa_o, with a = u x step (u in (0, 1]) and k = bias x exp(spread z) (z standard normal)."""
    a = u * step
    return (1.0 - a) * ucs_o, (1.0 + bias * exp(spread * z) * a) * kappa_o
