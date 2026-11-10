"""Rate of new plants: r_new = sum of rate_k x capacity_k / sum of capacity_k.

Source: v4-final-model.md, "Schedule", step 3. The plants are those aged entry_window
periods or less; the rate of a plant is its realised profit, after depreciation, over its
purchase cost. r_new is undefined, None, when no plant is in the window. It opens the entry
gate at step 6 and releases the reserve at step 4.
"""
from math import fsum


def new_plant_rate(rates: list[float], capacities: list[float]) -> float | None:
    """The capacity-weighted mean of the plants' rates; None without a plant."""
    total = fsum(capacities)
    if total <= 0.0:
        return None
    weighted = fsum(rate * capacity for rate, capacity in zip(rates, capacities))
    return weighted / total
