"""Probability of an entrant in a period: min{1, theta max(0, r_new - rbar) / rbar}.

Source: v4-final-model.md, "Schedule", step 6, and the third formula below the schedule. No
entrant while r_new is undefined: without a plant in its window nothing says what a new
plant earns.
"""


def entry_probability(r_new: float | None, rbar: float, theta: float) -> float:
    """The probability that one firm enters this period."""
    if r_new is None:
        return 0.0
    return min(1.0, theta * max(0.0, r_new - rbar) / rbar)
