FLIP = {"shaikh": "okishio", "okishio": "shaikh"}


def inherited_type(types: list[str], shares: list[float], mutation: float, rng) -> str:
    """h_e = h_j with Pr(j) = f_j,t: the entrant copies the rule of an incumbent drawn by
    market share, and switches to the other rule with probability m."""
    parent = rng.choices(types, weights=shares, k=1)[0]
    return FLIP[parent] if rng.random() < mutation else parent
