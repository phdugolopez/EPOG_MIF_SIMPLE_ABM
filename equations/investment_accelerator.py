"""The plants a firm lacks for the demand addressed to it:
ceil((notional - capacity - on order) / S), at least 0.

Source: v4-final-model.md, "Schedule", step 5, the rule "Accelerator". There is no target
utilisation: overtime is the buffer. A tolerance keeps rounding from adding a plant.
"""
from math import ceil

from parameters import EPS


def plants_wanted(notional: float, capacity: float, on_order: float, size: float) -> int:
    """The plants missing to serve the notional demand at normal capacity."""
    return max(0, ceil((notional - capacity - on_order) / size - EPS))
