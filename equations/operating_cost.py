def operating_cost(
    ucs: list[float],
    normal: list[float],
    overtime: list[float],
    overtime_premium: float,
) -> float:
    """Wages and materials: ucs_v on normal output, (1 + premium) ucs_v on overtime."""
    return sum(
        c * (n + (1.0 + overtime_premium) * o) for c, n, o in zip(ucs, normal, overtime)
    )
