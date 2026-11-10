"""Why a plant leaves: its age, its cost, or its idleness.

    "age"   at age T
    "cost"  after scrap_periods consecutive periods with the price below its cost
    "idle"  after scrap_periods consecutive periods without output

Source: v4-final-model.md, "Schedule", step 4. The first reason that holds, in that order,
is the one recorded. A working plant is never replaced.
"""


def retirement_reason(age: int, life: int, below_cost: int, idle: int,
                      periods: int) -> str | None:
    """The reason for which the plant leaves this period; None if it stays."""
    if age >= life:
        return "age"
    if below_cost >= periods:
        return "cost"
    if idle >= periods:
        return "idle"
    return None
