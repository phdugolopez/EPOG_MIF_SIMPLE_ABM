def profit_rate_at_price(price: float, uc: float, kappa: float) -> float:
    """r(p) = (p - uc) / kappa: profit rate at normal output, no debt (Shaikh 2016, eq. 7.11)."""
    return (price - uc) / kappa
