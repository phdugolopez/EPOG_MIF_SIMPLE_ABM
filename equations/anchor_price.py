def target_return_price(uc: float, kappa: float, rbar: float) -> float:
    """p^N_i = uc_i + rbar kappa_i: the firm's own price of production at normal output."""
    return uc + rbar * kappa


def markup_price(uc: float, markup: float) -> float:
    """Alternative anchor: (1 + mu) uc_i. It favours the lowest unit cost by construction."""
    return (1.0 + markup) * uc
