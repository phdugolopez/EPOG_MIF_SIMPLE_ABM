def technique_cost(ucs: float, kappa: float, hurdle: float, delta: float, tau: float) -> float:
    """(1 + h tau) ucs_j + (delta + h) kappa_j."""
    return (1.0 + hurdle * tau) * ucs + (delta + hurdle) * kappa


def choose_technique(menu, hurdle: float, delta: float, tau: float):
    """j* = argmin_j [(1 + h tau) ucs_j + (delta + h) kappa_j].

    With h = 0 it picks the lowest unit cost; with h equal to the best profit rate at the
    current price, the highest profit rate. Exact ties go to the first technique listed.
    """
    return min(menu, key=lambda t: technique_cost(t.ucs, t.kappa, hurdle, delta, tau))
