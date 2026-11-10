def entry_probability(r_new: float | None, rbar: float, theta: float) -> float:
    """min{1, theta max(0, r_new - rbar) / rbar}; 0 when r_new is None."""
    if r_new is None:
        return 0.0
    return min(1.0, theta * max(0.0, r_new - rbar) / rbar)
