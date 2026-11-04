def firm_profit(
    revenue: float, operating_cost: float, depreciation: float, interest: float
) -> float:
    """Pi_i,t = p x - ucs x (+ overtime premium) - delta kappa qbar - rho B_i,t-1."""
    return revenue - operating_cost - depreciation - interest
