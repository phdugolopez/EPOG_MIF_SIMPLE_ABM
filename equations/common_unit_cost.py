def unit_cost(ucs: float, kappa: float, delta: float) -> float:
    """uc = ucs + delta kappa, the cost per unit of normal output."""
    return ucs + delta * kappa
