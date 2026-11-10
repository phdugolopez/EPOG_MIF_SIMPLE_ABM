"""The plants a sum of money pays for: floor(funds / plant cost), at least 0.

Source: v4-final-model.md, "Schedule", step 5, the rule "Retained earnings". The step passes
the smaller of the firm's funds and its cash; the accelerator passes its cash. A tolerance
keeps rounding from costing a plant.
"""
from math import floor

from parameters import EPS


def plants_affordable(funds: float, plant_cost: float) -> int:
    """The whole plants the funds buy; none on negative funds."""
    return max(0, floor((funds + EPS) / plant_cost))
