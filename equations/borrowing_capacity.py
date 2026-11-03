def borrowing_capacity(debt: float, revenue: float, debt_cap: float) -> float:
    """New borrowing for plants allowed while debt stays below Lambda times sales revenue."""
    return max(0.0, debt_cap * revenue - debt)
