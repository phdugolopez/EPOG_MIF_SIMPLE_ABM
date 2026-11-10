def dividends(profit: float, payout: float) -> float:
    """d x max(0, profit)."""
    return payout * max(0.0, profit)
