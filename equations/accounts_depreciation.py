"""Depreciation of a plant in a period: min(delta x purchase cost, book value).

Source: v4-final-model.md, "Schedule", step 3. Straight-line over T periods, delta = 1 / T,
by time and not by output: a plant depreciates whether it runs or not.
"""


def depreciation(cost: float, book_value: float, delta: float) -> float:
    """The charge of the period, at most what is left of the book value."""
    return min(delta * cost, book_value)
