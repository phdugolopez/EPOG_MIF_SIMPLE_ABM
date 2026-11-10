"""The price of a firm under universal undercutting (leader-follow in v2 and the notebook).

    a firm alone:       min((1 + z) previous, cap x floor)
    after a shortage:   (1 + z) L
    otherwise:          (1 - c) L, or the floor if that is higher

Source: v4-final-model.md, "Schedule", step 1, the paragraph "Universal undercutting";
v4-choices.md, decisions 9 and 17. L is the lowest price posted last period by a firm with a
plant in operation. Every firm cuts, whatever its utilisation and its cost. The floor
applies to a cut only: after a shortage, and for a firm alone, a price can be below it.
"""


def universal_price(previous: float, lowest: float, floor: float, excess: float, alone: bool,
                    cut: float, rise: float, cap: float) -> tuple[float, bool]:
    """The price the firm posts, and whether it cut."""
    if alone:
        return min((1.0 + rise) * previous, cap * floor), False
    if excess > 0.0:
        return (1.0 + rise) * lowest, False
    target = (1.0 - cut) * lowest
    if target >= floor:
        return target, True
    return floor, False
