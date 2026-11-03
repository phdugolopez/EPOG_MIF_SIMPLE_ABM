def interest_payment(debt: float, rho: float) -> float:
    """rho B_i,t-1: interest on last period's debt."""
    return rho * debt
