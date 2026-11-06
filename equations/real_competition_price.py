import math


def real_competition_price(
    previous_price: float,
    rival_prices: list[float],
    rival_costs: list[float],
    own_cost: float,
    floor: float,
    spare: bool,
    excess_share: float,
    cut: float,
    shortage_response: float,
) -> tuple[float, bool]:
    """Pricing without an anchor or a war trigger (PRICING_RULE = "real_competition").

    Checked in order, with R = the lowest rival price last period and uc = unit costs
    (ucs + delta kappa) of each firm's best plant:

    1. Shortage: last period's demand exceeded industry supply (EXCESS_DEMAND: normal
       capacity, or all output with overtime). Move up to the next higher rival price; a
       firm with no rival above it raises by shortage_response x the excess-demand share.
    2. Undercut: the firm has spare capacity and a cost edge, i.e. its uc is below the cut
       price (1 - c) R and below the uc of at least one rival posting R. It posts (1 - c) R,
       never raising its own price. Cuts come from cost differences, not from a trigger.
    3. Follow: the lowest price posted last period (its own included), never below its floor.

    Returns (price, undercut).
    """
    lowest_rival = min(rival_prices) if rival_prices else previous_price
    if excess_share > 0.0:
        higher = [
            p for p in rival_prices
            if p > previous_price and not math.isclose(p, previous_price)
        ]
        if higher:
            return min(higher), False
        return previous_price * (1.0 + shortage_response * excess_share), False
    cut_price = (1.0 - cut) * lowest_rival
    at_lowest = [
        c for p, c in zip(rival_prices, rival_costs) if math.isclose(p, lowest_rival)
    ]
    edge = own_cost < cut_price and bool(at_lowest) and own_cost < max(at_lowest)
    if spare and edge:
        return min(previous_price, cut_price), True
    return max(min(lowest_rival, previous_price), floor), False
