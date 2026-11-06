def depreciation(kappa: float, capacity: float, delta: float, book_value: float) -> float:
    """Straight line: delta kappa_v qbar_v per period, until the book value reaches zero."""
    return min(book_value, delta * kappa * capacity)


def depreciation_by_use(kappa: float, output: float, delta: float, book_value: float) -> float:
    """By use (DEPRECIATION = "use"): delta kappa_v x_v, overtime included, until the book
    value reaches zero. The purchase cost kappa_v qbar_v is spread over a lifetime output of
    qbar_v / delta, so at normal output the charge equals the straight-line one and the
    capital charge per unit of output is delta kappa_v in both rules: uc = ucs + delta kappa
    is unchanged. An idle plant does not depreciate."""
    return min(book_value, delta * kappa * output)
