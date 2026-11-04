def plant_profit(
    price: float,
    ucs: float,
    output: float,
    overtime_output: float,
    overtime_premium: float,
    depreciation: float,
) -> float:
    """Profit of one plant, before interest: (p - ucs) x_v - premium ucs x_v^over - dep_v."""
    return (
        (price - ucs) * output
        - overtime_premium * ucs * overtime_output
        - depreciation
    )
