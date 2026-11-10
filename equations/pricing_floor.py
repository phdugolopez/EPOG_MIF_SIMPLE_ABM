def price_floor(unit_costs: list[float]) -> float:
    """The unit cost of the firm's lowest-unit-cost plant in operation; 0 without a plant."""
    return min(unit_costs, default=0.0)
