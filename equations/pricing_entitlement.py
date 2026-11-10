"""Who may undercut the lowest price P of its rivals, under each cutting rule.

    cost edge (default):  spare capacity, and a unit cost below that of a rival posting P
    normal price:         spare capacity, and P above the firm's own price of production
                          or the cost edge
    systematic:           spare capacity

Source: v4-final-model.md, "Schedule", step 1, the paragraphs "Cost-edge cutting",
"Normal-price cutting" and "Systematic cutting"; v4-choices.md, decision 16. Spare capacity
is a last utilisation below u_full. Equal unit costs give no edge.
"""
from math import isclose


def entitled_cost_edge(spare: bool, own_cost: float, costs_at_lowest: list[float]) -> bool:
    """Spare capacity and a unit-cost edge over a rival that posts the lowest price."""
    return spare and own_cost < max(costs_at_lowest)


def entitled_normal_price(spare: bool, own_cost: float, costs_at_lowest: list[float],
                          lowest_rival: float, own_normal_price: float) -> bool:
    """While the lowest rival price is above the firm's price of production spare capacity
    is enough; at or below it the firm also needs the cost edge."""
    above = lowest_rival > own_normal_price and not isclose(lowest_rival, own_normal_price)
    return spare and (above or own_cost < max(costs_at_lowest))


def entitled_systematic(spare: bool) -> bool:
    """Spare capacity alone, at any price."""
    return spare
