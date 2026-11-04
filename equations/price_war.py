def price_war(util_history: list[float], war_periods: int, u_war: float) -> bool:
    """A firm cuts when its utilisation was below u_war in each of the last T periods."""
    recent = util_history[-war_periods:]
    return len(recent) == war_periods and all(u < u_war for u in recent)
