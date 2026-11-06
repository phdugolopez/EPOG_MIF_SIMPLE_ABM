def cost_gated_war_price(
    previous_price: float,
    lowest_rival_price: float,
    best_unit_cost: float,
    floor: float,
    cut: float,
) -> float:
    """Alternative price-war rule (PRICE_WAR = "cost_gated"):

    p_i,t = max{floor_i, min{p_i,t-1, R~_i,t}}, with R_i,t the lowest rival price last period,
    R~ = (1 - c) R_i,t  if the firm's best unit cost min_v uc_v is below (1 - c) R_i,t,
    R~ = R_i,t          otherwise.

    Only a firm with a cost edge can sustain a cut below its rivals (Shaikh 2016, Table 7.3);
    the others match the lowest price. A war then moves customers toward the low-cost firm
    instead of lowering every price together. Prices never rise during a war.
    """
    undercut = (1.0 - cut) * lowest_rival_price
    target = undercut if best_unit_cost < undercut else lowest_rival_price
    return max(floor, min(previous_price, target))
