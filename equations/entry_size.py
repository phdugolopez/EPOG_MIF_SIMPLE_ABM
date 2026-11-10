from math import floor, fsum


def entrant_plants(capacities: list[float], entry_size: float, size: float) -> int:
    """entry_size x the average incumbent capacity, in plants of size S, rounded half up, at
    least 1."""
    return max(1, floor(entry_size * fsum(capacities) / len(capacities) / size + 0.5))
