from equations.merit_order import plant_segments


def offered_capacity(
    ucs: list[float],
    capacity: list[float],
    price: float,
    u_max: float,
    overtime_premium: float,
) -> float:
    """Output the firm is willing to sell at its price: segments whose cost is covered.

    A plant runs only if the price covers its operating cost (brief, Scrapping, decision 1).
    """
    return sum(
        size
        for cost, _, size, _ in plant_segments(ucs, capacity, u_max, overtime_premium)
        if cost <= price
    )
