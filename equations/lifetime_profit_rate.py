def lifetime_profit_rate(lifetime_profit: float, capital_periods: float) -> float:
    """Average profit rate over a plant's life, before interest:
    sum of its profits / (purchase cost x periods of operation)."""
    return lifetime_profit / capital_periods if capital_periods > 0.0 else 0.0
