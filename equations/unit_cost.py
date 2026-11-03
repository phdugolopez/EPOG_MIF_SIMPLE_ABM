def unit_cost(ucs: float, kappa: float, delta: float) -> float:
    """uc_v = ucs_v + delta kappa_v (Shaikh 2016, p. 316)."""
    return ucs + delta * kappa
