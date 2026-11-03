def periods_below_cost(previous_count: int, price: float, ucs: float) -> int:
    """Consecutive periods in which the price stayed below the plant's operating cost."""
    return previous_count + 1 if price < ucs else 0


def retirement_reason(
    age: int, plant_life: int, below_cost: int, obsolescence_periods: int
) -> str | None:
    """A plant leaves for good at its maximum age T, or once its quasi-rent has been
    negative for N periods (Salter 1966). The same rule for both types."""
    if age >= plant_life:
        return "age"
    if below_cost >= obsolescence_periods:
        return "obsolescence"
    return None
