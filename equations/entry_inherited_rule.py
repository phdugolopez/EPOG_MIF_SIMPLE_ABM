from itertools import accumulate

from parameters import LABELS


def inherited_label(labels: list[str], shares: list[float], mutation: float,
                    u_parent: float, u_flip: float) -> str:
    """The label of an incumbent drawn by share (u_parent, over the incumbents in the order
    given), flipped with probability mu (u_flip)."""
    bounds = list(accumulate(shares))
    parent = next((label for label, bound in zip(labels, bounds) if u_parent * bounds[-1] < bound),
                  labels[-1])
    other = LABELS[1] if parent == LABELS[0] else LABELS[0]
    return other if u_flip < mutation else parent
