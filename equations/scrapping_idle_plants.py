"""The periods a plant has spent without output: previous + 1 if it did not run, else 0.

Source: v4-final-model.md, "Schedule", step 4. The periods are consecutive. The idle test is
a device of the model, without a source.
"""
from parameters import EPS


def periods_idle(previous: int, output: float) -> int:
    """Consecutive periods without output, this period included."""
    if output <= EPS:
        return previous + 1
    return 0
