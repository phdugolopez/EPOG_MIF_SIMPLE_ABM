def dividends(profit: float, payout: float) -> float:
    """Div_i,t = d max{0, Pi_i,t}, the same payout d for both types."""
    return payout * max(0.0, profit)
