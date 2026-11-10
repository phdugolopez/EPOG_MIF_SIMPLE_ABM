"""The plants of an entrant: entry_size x mean capacity / S, rounded half up, at least 1.

Source: v4-final-model.md, "Schedule", step 6; v4-choices.md, the row Q8 kept from v3. The
mean is over the firms that stay after the exits of the period, on their capacity in
operation.
"""
from math import floor, fsum


def entrant_plants(capacities: list[float], entry_size: float, size: float) -> int:
    """The number of plants an entrant orders."""
    mean_capacity = fsum(capacities) / len(capacities)
    return max(1, floor(entry_size * mean_capacity / size + 0.5))
