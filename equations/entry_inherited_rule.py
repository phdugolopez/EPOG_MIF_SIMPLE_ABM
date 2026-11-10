"""The label of an entrant: that of an incumbent drawn by weight, flipped with probability mu.

Source: v4-final-model.md, "Schedule", step 6, and the option `entry_label`; v4-choices.md,
decision 11. The weights are the market shares (default) or one vote a firm. The incumbents
are read in the order given, which the market fixes by serial number, so the draw does not
depend on a firm's place in the industry's list.
"""
from itertools import accumulate

from parameters import LABELS


def inherited_label(labels: list[str], weights: list[float], mutation: float,
                    u_parent: float, u_flip: float) -> str:
    """The label copied from the incumbent that u_parent draws, or the other one if u_flip
    falls below the mutation probability."""
    bounds = list(accumulate(weights))
    target = u_parent * bounds[-1]
    parent = labels[-1]
    # The first incumbent whose cumulated weight passes the draw; the last one by rounding.
    for label, bound in zip(labels, bounds):
        if target < bound:
            parent = label
            break
    if u_flip >= mutation:
        return parent
    if parent == LABELS[0]:
        return LABELS[1]
    return LABELS[0]
