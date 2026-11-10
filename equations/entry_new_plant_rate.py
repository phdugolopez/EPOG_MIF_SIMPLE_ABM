from math import fsum


def new_plant_rate(rates: list[float], capacities: list[float]) -> float | None:
    """r_new: capacity-weighted realised profit rate (plant profit / purchase cost) of the
    plants built in the window; None without one."""
    total = fsum(capacities)
    if total <= 0.0:
        return None
    return fsum(r * q for r, q in zip(rates, capacities)) / total
