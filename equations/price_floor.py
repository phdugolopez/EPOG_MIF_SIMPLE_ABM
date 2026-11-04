from equations.merit_order import dispatch


def price_floor(
    ucs: list[float],
    capacity: list[float],
    last_sales: float,
    u_max: float,
    overtime_premium: float,
) -> float:
    """ucs of the most expensive plant the firm needs to run to produce last period's sales.

    Depreciation is sunk in the short run (Shaikh 2016, p. 316). A firm with no sales
    needs only its cheapest plant.
    """
    if not ucs:
        return 0.0
    normal, overtime = dispatch(ucs, capacity, last_sales, u_max, overtime_premium)
    running = [c for c, n, o in zip(ucs, normal, overtime) if n + o > 1e-12]
    return max(running) if running else min(ucs)
