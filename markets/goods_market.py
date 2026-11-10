"""The goods market: sales, one re-allocation of unserved demand, and the demand lost
(v4-final-model.md, "Schedule", step 2).
"""
from math import fsum


def allocate(demand: float, shares: list[float], limits: list[float]) -> tuple[list[float], float]:
    """The sales of each firm and the demand lost.

    A firm sells its share of demand up to its limit, u_max times the capacity it offers.
    What is not served is shared once among the firms, pro rata to the room each has left;
    the rest is lost.
    """
    wanted = [share * demand for share in shares]
    sales = [min(want, limit) for want, limit in zip(wanted, limits)]
    unserved = fsum(want - sold for want, sold in zip(wanted, sales))
    room = [limit - sold for limit, sold in zip(limits, sales)]
    total_room = fsum(room)
    extra = min(unserved, total_room)
    if extra > 0.0:
        sales = [min(limit, sold + extra * spare / total_room)
                 for limit, sold, spare in zip(limits, sales, room)]
    return sales, unserved - extra
