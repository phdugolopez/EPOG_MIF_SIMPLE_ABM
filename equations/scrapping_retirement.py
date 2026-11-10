def retirement_reason(age: int, life: int, below_cost: int, idle: int, periods: int) -> str | None:
    """A plant leaves at age T, or after N periods below its scrap cost, or after N periods
    idle; the first reason that holds, in that order."""
    if age >= life:
        return "age"
    if below_cost >= periods:
        return "cost"
    if idle >= periods:
        return "idle"
    return None
