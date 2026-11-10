from math import floor

from parameters import EPS


def plants_affordable(funds: float, plant_cost: float) -> int:
    """floor(funds / plant cost), 0 if funds are negative."""
    return max(0, floor((funds + EPS) / plant_cost))
