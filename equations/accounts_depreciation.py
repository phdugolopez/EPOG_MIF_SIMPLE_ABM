def depreciation(cost: float, book_value: float, delta: float) -> float:
    """delta x purchase cost a period, at most the remaining book value."""
    return min(delta * cost, book_value)
