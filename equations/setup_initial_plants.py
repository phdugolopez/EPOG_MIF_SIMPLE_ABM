"""Initial plants of a firm: their number and their staggered ages.

    n = normal output / S, rounded half up, at least 1
    age of plant k = floor(k T / n),  k = 0 ... n - 1

Source: v4-final-model.md, "Initial industry". The ages spread the first retirements over
the first T periods.
"""
from math import floor


def initial_ages(output: float, size: float, life: int) -> list[int]:
    """The ages of the plants a firm starts with, youngest first."""
    n = max(1, floor(output / size + 0.5))
    return [k * life // n for k in range(n)]
