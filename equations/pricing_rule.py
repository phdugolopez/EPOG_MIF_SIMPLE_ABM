from math import isclose


def posted_price(previous: float, rival_prices: list[float], rival_costs: list[float],
                 own_cost: float, spare: bool, excess: float, cost_edge: bool, cut: float,
                 shortage_step: float) -> tuple[float, bool]:
    """After a shortage (excess > 0): the next higher rival price, or previous x (1 + step x
    excess) with no rival above. Otherwise the firm undercuts to (1 - c) x the lowest rival
    price if it has spare capacity and, under cost-edge cutting, a unit cost below that of a
    rival posting that price; else it follows the lowest price posted, its own included. It
    never raises its price without a shortage, except to its floor: own_cost, the unit cost of
    its best plant in operation. Returns the price and whether the firm cut: it was entitled
    and its price fell below the lowest rival price."""
    if excess > 0.0:
        higher = [p for p in rival_prices if p > previous and not isclose(p, previous)]
        target = min(higher) if higher else previous * (1.0 + shortage_step * excess)
        return max(target, own_cost), False
    if not rival_prices:
        return max(previous, own_cost), False
    low_rival = min(rival_prices)
    at_low = [c for p, c in zip(rival_prices, rival_costs) if isclose(p, low_rival)]
    entitled = spare and (not cost_edge or own_cost < max(at_low))
    target = (1.0 - cut) * low_rival if entitled else low_rival
    price = max(min(previous, target), own_cost)
    fell = price < min(previous, low_rival) and not isclose(price, min(previous, low_rival))
    return price, entitled and fell
