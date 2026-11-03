def replacement_pays(
    ucs_old: float, ucs_new: float, kappa_new: float, delta: float, hurdle: float
) -> bool:
    """Replace working plant v by technique n when ucs_v > ucs_n + (delta + h) kappa_n.

    The old plant's capital is sunk; h is the same hurdle as in investment.
    """
    return ucs_old > ucs_new + (delta + hurdle) * kappa_new
