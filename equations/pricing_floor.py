"""The floor of a firm's price: the lowest price it may cut to.

    unit-cost floor (default):  the lowest unit cost among the firm's plants
    operating-cost floor:       the highest operating cost among the plants that ran last
                                period; the lowest operating cost it owns if none ran
    mean-unit-cost floor:       the mean unit cost of the firm's plants, weighted by their
                                normal capacity

Source: v4-final-model.md, "Schedule", step 1, and the option `price_floor`; v4-choices.md,
decision 19; the mean-unit-cost floor is a departure asked on 12 Nov (v4-choices.md,
"Departures from the specification"). Under either other floor the cost edge is still read
on the unit cost of the best plant.
"""


def unit_cost_floor(unit_costs: list[float]) -> float:
    """The unit cost of the firm's best plant."""
    return min(unit_costs)


def operating_cost_floor(ucs_ran: list[float], ucs_owned: list[float]) -> float:
    """The operating cost of the dearest plant that ran, or of the cheapest plant owned."""
    if ucs_ran:
        return max(ucs_ran)
    return min(ucs_owned)


def mean_unit_cost_floor(unit_costs: list[float], capacities: list[float]) -> float:
    """The mean unit cost of the firm's plants, weighted by their normal capacity."""
    total = sum(capacities)
    if total <= 0.0:
        return min(unit_costs)
    return sum(cost * capacity for cost, capacity in zip(unit_costs, capacities)) / total
