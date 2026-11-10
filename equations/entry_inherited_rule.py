from math import fsum

from parameters import LABELS


def inherited_label(labels: list[str], shares: list[float], mutation: float,
                    u_parent: float, u_flip: float) -> str:
    """The label of an incumbent drawn by share (u_parent, over the incumbents in the order
    given), flipped with probability mu (u_flip)."""
    target, reached, parent = u_parent * fsum(shares), 0.0, labels[-1]
    for label, share in zip(labels, shares):
        reached += share
        if target < reached:
            parent = label
            break
    if u_flip < mutation:
        return LABELS[1] if parent == LABELS[0] else LABELS[0]
    return parent
