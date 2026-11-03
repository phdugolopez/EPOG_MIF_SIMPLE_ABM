def posted_price(
    previous_price: float,
    anchor: float,
    leader_price: float,
    floor: float,
    at_war: bool,
    speed: float,
    band: float,
    cut: float,
) -> float:
    """p_i,t = max{floor_i, p~_i,t}, with
    p~ = (1 - c) p_i,t-1                                         in a price war,
    p~ = min{p_i,t-1 + lambda (p^N_i - p_i,t-1), (1 + b) p^lead_t-1}  otherwise.
    """
    if at_war:
        candidate = (1.0 - cut) * previous_price
    else:
        candidate = min(
            previous_price + speed * (anchor - previous_price),
            (1.0 + band) * leader_price,
        )
    return max(floor, candidate)
