from math import cos, pi, sin


def draw_neutral(ucs_o: float, kappa_o: float, u: float, v: float,
                 step: float) -> tuple[float, float]:
    """A design of the neutral set: direction uniform on the circle in the plane (change of
    ucs / ucs, change of kappa / kappa), of size u x step (u in (0, 1], v in [0, 1))."""
    size, angle = u * step, 2.0 * pi * v
    return (1.0 + size * cos(angle)) * ucs_o, (1.0 + size * sin(angle)) * kappa_o
