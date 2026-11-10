from math import fsum


def allocate(demand: float, shares: list[float], offered: list[float]) -> tuple[list[float], float]:
    """Each firm sells min(share x D, offered capacity); the demand left over is shared once,
    pro rata to spare offered capacity; the rest is lost (A6). Returns (sales, lost)."""
    wanted = [share * demand for share in shares]
    sales = [min(w, o) for w, o in zip(wanted, offered)]
    overflow = fsum(w - s for w, s in zip(wanted, sales))
    spare = [o - s for o, s in zip(offered, sales)]
    room = fsum(spare)
    extra = min(overflow, room)
    if extra > 0.0:
        sales = [min(o, s + extra * x / room) for o, s, x in zip(offered, sales, spare)]
    return sales, overflow - extra
