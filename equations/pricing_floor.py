"""The floor of a firm's price: the lowest price it may cut to.

    unit-cost floor (default):  the lowest unit cost among the firm's plants
    operating-cost floor:       the highest operating cost among the plants that ran last
                                period; the lowest operating cost it owns if none ran

Source: v4-final-model.md, "Schedule", step 1, and the option `price_floor`; v4-choices.md,
decision 19. Under the operating-cost floor the cost edge is still read on the unit cost.
"""


def unit_cost_floor(unit_costs: list[float]) -> float:
    """The unit cost of the firm's best plant."""
    return min(unit_costs)


def operating_cost_floor(ucs_ran: list[float], ucs_owned: list[float]) -> float:
    """The operating cost of the dearest plant that ran, or of the cheapest plant owned."""
    if ucs_ran:
        return max(ucs_ran)
    return min(ucs_owned)
