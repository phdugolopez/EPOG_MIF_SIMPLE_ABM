import math


def allocate(
    demand: float, shares: list[float], prices: list[float], offered: list[float]
) -> tuple[list[float], list[float], float]:
    """Each firm sells its share of demand up to the output it offers; the overflow goes
    to the cheapest firms with spare capacity, shared in proportion to spare capacity
    when prices tie. Returns sales, each firm's unmet demand, and demand left unserved.
    """
    wanted = [f * demand for f in shares]
    sales = [min(w, o) for w, o in zip(wanted, offered)]
    unmet = [w - s for w, s in zip(wanted, sales)]
    overflow = sum(unmet)
    while overflow > 1e-12:
        spare = {i: offered[i] - sales[i] for i in range(len(sales))}
        spare = {i: s for i, s in spare.items() if s > 1e-12}
        if not spare:
            break
        cheapest = min(prices[i] for i in spare)
        group = [i for i in spare if math.isclose(prices[i], cheapest)]
        room = sum(spare[i] for i in group)
        take = min(overflow, room)
        for i in group:
            sales[i] += take * spare[i] / room
        overflow -= take
    return sales, unmet, max(0.0, overflow)
