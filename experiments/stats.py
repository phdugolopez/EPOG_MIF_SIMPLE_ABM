"""Shares of seeds won: the Wilson interval, the test "beyond drift", and a mean with its
interval (v4-final-model.md, "Winner")."""
from math import fsum, nan, sqrt


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95 % Wilson interval for a share of k successes in n trials; (nan, nan) for n = 0."""
    if n == 0:
        return nan, nan
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def disjoint(a: tuple[float, float], b: tuple[float, float]) -> bool:
    """Two intervals that do not overlap; False when either is not defined."""
    return a[1] < b[0] or b[1] < a[0]


def beyond_drift(mixed: tuple[float, float], *controls: tuple[float, float]) -> bool:
    """The interval of the mixed population is disjoint from the interval of every control."""
    return all(disjoint(mixed, control) for control in controls)


def mean_interval(values: list[float], z: float = 1.96) -> tuple[float, float, float]:
    """Mean of the values and its 95 % interval, mean -/+ z s / sqrt(n); nan without a value."""
    n = len(values)
    if n == 0:
        return nan, nan, nan
    mean = fsum(values) / n
    if n == 1:
        return mean, mean, mean
    half = z * sqrt(fsum((value - mean) ** 2 for value in values) / (n - 1) / n)
    return mean, mean - half, mean + half
