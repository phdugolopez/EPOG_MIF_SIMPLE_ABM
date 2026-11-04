def profit_rate(profit: float, capital: float) -> float:
    """r_i,t = Pi_i,t / (kappa qbar): net profit over capital at purchase cost."""
    return profit / capital if capital > 0.0 else 0.0
