def reserve_released(r_new: float | None, rbar: float) -> bool:
    """True when new plants earn the general rate, r_new >= rbar, and when no plant is in the
    window of r_new: the reserve of a plant that leaves then joins the funds (A7)."""
    return r_new is None or r_new >= rbar
