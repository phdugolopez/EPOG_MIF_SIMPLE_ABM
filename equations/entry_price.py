"""The price an entrant posts.

    undercut (default):  max((1 - c) x lowest, floor)
    lowest:              lowest

Source: v4-final-model.md, "Schedule", step 6, and the option `entry_price`. `lowest` is the
lowest price posted by a firm with a plant in operation; the floor is the unit cost of the
entrant's own plants. Under "lowest" the entrant posts that price, as in version 3.
"""


def entrant_price(lowest: float, floor: float, cut: float, rule: str) -> float:
    """The price of the entrant in its first period."""
    if rule == "lowest":
        return lowest
    return max((1.0 - cut) * lowest, floor)
