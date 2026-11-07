FLIP = {"shaikh": "okishio", "okishio": "shaikh"}


def inherit(types: list[str], shares: list[float], mutation: float, rng) -> tuple[str, int, bool]:
    """h_e = h_j with Pr(j) = f_j,t: the entrant copies the rule of an incumbent drawn by
    market share, and switches to the other rule with probability m.

    Returns the entrant's type, the index of the incumbent drawn and whether it mutated.
    Drawing the index rather than the type uses the random stream identically.
    """
    parent = rng.choices(range(len(types)), weights=shares, k=1)[0]
    mutated = rng.random() < mutation
    return (FLIP[types[parent]] if mutated else types[parent]), parent, mutated


def inherited_type(types: list[str], shares: list[float], mutation: float, rng) -> str:
    """The entrant's type alone (see inherit)."""
    return inherit(types, shares, mutation, rng)[0]
