def dispatch(ucs: list[float], ages: list[int], capacity: list[float], quantity: float) -> list[float]:
    """Plants run lowest operating cost first, then youngest, each up to its normal capacity."""
    outputs = [0.0] * len(ucs)
    for i in sorted(range(len(ucs)), key=lambda i: (ucs[i], ages[i])):
        outputs[i] = min(capacity[i], quantity)
        quantity -= outputs[i]
    return outputs
