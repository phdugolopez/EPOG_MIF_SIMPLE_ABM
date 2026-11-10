from math import floor


def initial_ages(output: float, size: float, life: int) -> list[int]:
    """n = normal output / S rounded half up (at least 1) plants, of ages floor(i T / n)."""
    n = max(1, floor(output / size + 0.5))
    return [i * life // n for i in range(n)]
