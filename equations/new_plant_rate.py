def new_plant_rate(rates: list[float], capacities: list[float]) -> float | None:
    """r^new_t: capacity-weighted realised profit rate, this period, of the plants built in
    the last k periods. An industry signal, the same for every candidate entrant. None
    when no plant was built in the window."""
    total = sum(capacities)
    if total <= 0.0:
        return None
    return sum(r * q for r, q in zip(rates, capacities)) / total
