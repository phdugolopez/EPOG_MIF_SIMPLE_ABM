def technique_cost(ucs: float, kappa: float, hurdle: float, delta: float) -> float:
    """ucs + (delta + h) kappa."""
    return ucs + (delta + hurdle) * kappa


def choose_technique(menu: list, hurdle: float, delta: float):
    """The technique with the lowest cost at h; exact ties go to the lower kappa, then the
    lower ucs."""
    return min(menu, key=lambda t: (technique_cost(t.ucs, t.kappa, hurdle, delta), t.kappa, t.ucs))
