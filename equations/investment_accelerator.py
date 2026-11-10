from math import ceil

from parameters import EPS


def plants_wanted(notional: float, u_target: float, capacity: float, on_order: float,
                  size: float) -> int:
    """ceil((notional / u* - capacity - on order) / S), at least 0."""
    return max(0, ceil((notional / u_target - capacity - on_order) / size - EPS))
