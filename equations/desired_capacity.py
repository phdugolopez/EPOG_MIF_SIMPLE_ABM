def desired_capacity(expected_sales: float, expected_growth: float) -> float:
    """qbar^d_i,t = (1 + g) x_i,t-1: capacity for expected sales at normal utilisation."""
    return (1.0 + expected_growth) * expected_sales
