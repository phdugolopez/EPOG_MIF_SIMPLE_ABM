from parameters import EPS


def periods_idle(previous: int, output: float) -> int:
    """Consecutive periods without output."""
    return previous + 1 if output <= EPS else 0
