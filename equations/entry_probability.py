def entry_probability(r_new: float | None, rbar: float, theta: float) -> float:
    """Pr(entry_t) = min{1, theta max(0, r^new_t - rbar) / rbar}; at most one entrant."""
    if r_new is None:
        return 0.0
    return min(1.0, theta * max(0.0, r_new - rbar) / rbar)
