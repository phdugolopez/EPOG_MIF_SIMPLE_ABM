import math


def plant_number(capacity: float, plant_size: float, rounding: str = "nearest") -> int:
    """Whole plants of size plant_size for a capacity: the nearest number, at least one
    ("nearest", initial firms and entrants), or enough to cover it ("up", investment)."""
    if rounding == "up":
        return max(0, math.ceil(capacity / plant_size - 1e-9))
    return max(1, round(capacity / plant_size))
