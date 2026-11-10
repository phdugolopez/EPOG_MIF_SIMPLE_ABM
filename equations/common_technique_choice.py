def technique_cost(ucs: float, kappa: float, hurdle: float, delta: float) -> float:
    """ucs + (delta + h) kappa."""
    return ucs + (delta + hurdle) * kappa


def choose_technique(menu: list, hurdle: float, delta: float):
    """The technique with the lowest cost at h; exact ties go to the lower kappa, then the
    lower ucs."""
    return min(menu, key=lambda t: (technique_cost(t.ucs, t.kappa, hurdle, delta), t.kappa, t.ucs))


def frontier(menu: list, delta: float) -> list:
    """The techniques no other beats on both unit cost and kappa. At any h >= 0 neither rule
    chooses a beaten technique, and none sets the hurdle: dropping them changes no choice."""
    points = [(t.ucs + delta * t.kappa, t.kappa) for t in menu]
    return [t for t, (c, k) in zip(menu, points)
            if not any(c2 <= c and k2 <= k and (c2, k2) != (c, k) for c2, k2 in points)]
