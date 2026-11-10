"""Merit order of a firm's plants, overtime included.

    plants run lowest operating cost first, then youngest, each to its normal capacity;
    what is left runs in the same order, each plant to u_max times its normal capacity

Source: v4-final-model.md, "Schedule", step 3, and "Overtime, in one place". The plants
given are those the firm offered at step 2: a plant that was not offered does not run
(v4-choices.md, decision 18). Overtime has the same operating cost. u_max = 1 gives none.
"""


def dispatch(ucs: list[float], ages: list[int], capacity: list[float], quantity: float,
             u_max: float) -> list[float]:
    """The output of each plant when the firm produces this quantity."""
    outputs = [0.0] * len(ucs)
    # The merit order: lowest operating cost first, then youngest.
    order = sorted(range(len(ucs)), key=lambda i: (ucs[i], ages[i]))
    # A first round up to normal capacity, a second up to the overtime limit.
    for limit in (1.0, u_max):
        for i in order:
            extra = min(limit * capacity[i] - outputs[i], quantity)
            outputs[i] += extra
            quantity -= extra
    return outputs
