def depreciation(kappa: float, capacity: float, delta: float, book_value: float) -> float:
    """Straight line: delta kappa_v qbar_v per period, until the book value reaches zero."""
    return min(book_value, delta * kappa * capacity)
