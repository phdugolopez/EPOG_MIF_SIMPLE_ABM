from math import isclose


def posted_price(previous: float, rival_prices: list[float], rival_costs: list[float],
                 own_cost: float, spare: bool, excess: float, cost_edge: bool, cut: float,
                 shortage_step: float) -> tuple[float, bool]:
    """After a shortage: the next higher rival price, or previous x (1 + step x excess) with
    none above. Otherwise (1 - c) x the lowest rival price if the firm has spare capacity and,
    under cost-edge cutting, a unit cost below that of a rival posting that price; else the
    lowest price posted, its own included. Never above its previous price without a shortage,
    never below own_cost, its floor. Returns the price and whether the firm cut."""
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
