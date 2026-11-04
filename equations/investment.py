def investment(desired_capacity: float, capacity: float) -> float:
    """I_i,t = max{0, qbar^d_i,t - qbar_i,t}, in units of capacity, the same for both types.

    capacity counts plants in operation after scrapping plus plants already on order.
    """
    return max(0.0, desired_capacity - capacity)
