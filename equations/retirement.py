def periods_below_cost(previous_count: int, price: float, ucs: float) -> int:
    """Consecutive periods in which the price stayed below the plant's scrap cost: its
    operating cost ucs, or its unit cost ucs + delta kappa (SCRAP_COST, see scrap_cost)."""
    return previous_count + 1 if price < ucs else 0


def scrap_cost(ucs: float, kappa: float, delta: float, rule: str) -> float:
    """The cost the price must cover for a plant to stay: ucs (quasi-rent, Salter 1966) or
    the unit cost ucs + delta kappa (SCRAP_COST = "unit_cost")."""
    return ucs + delta * kappa if rule == "unit_cost" else ucs


def retirement_reason(
    age: int, plant_life: int | None, below_cost: int, obsolescence_periods: int,
    periods_idle: int = 0, idle_periods: int | None = None,
) -> str | None:
    """A plant leaves for good at its maximum age T (none if plant_life is None), once the
    price has been below its scrap cost for N periods, or (idle_periods set) once the firm
    has not needed it for that many periods. The same rule for both types."""
    if plant_life is not None and age >= plant_life:
        return "age"
    if below_cost >= obsolescence_periods:
        return "obsolescence"
    if idle_periods is not None and periods_idle >= idle_periods:
        return "idle"
    return None
