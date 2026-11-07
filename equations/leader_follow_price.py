def markup_floor(unit_costs: list[float], capacities: list[float], markup: float) -> float:
    """Floor of the leader-follow rule: (1 + m) x the capacity-weighted average unit cost
    uc = ucs + delta kappa of the firm's plants."""
    total = sum(capacities)
    average = sum(c * q for c, q in zip(unit_costs, capacities)) / total
    return (1.0 + markup) * average


def leader_follow_price(
    previous_price: float,
    leader_price: float,
    floor: float,
    excess_share: float,
    only_firm: bool,
    cut: float,
    rise: float,
    monopoly_cap: float,
) -> tuple[float, bool]:
    """PRICING_RULE = "leader_follow" (the group notebook's rule), with L = the lowest price
    posted last period:
    1. Only firm in the industry: raise the own price by `rise`, up to monopoly_cap x floor.
    2. Shortage (last period's excess-demand share > 0): post (1 + rise) L.
    3. Otherwise: undercut the leader, max{floor, (1 - cut) L}. Every firm cuts whenever
       capacity is not short, so prices fall until they reach the floors.
    Returns (price, undercut).
    """
    if only_firm:
        return min(previous_price * (1.0 + rise), monopoly_cap * floor), False
    if excess_share > 0.0:
        return (1.0 + rise) * leader_price, False
    cut_price = (1.0 - cut) * leader_price
    if cut_price >= floor:
        return cut_price, True
    return floor, False
