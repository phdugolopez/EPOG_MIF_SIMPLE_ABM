from equations.unit_cost import unit_cost


def regulating_price(ucs: list[float], kappas: list[float], delta: float, rbar: float) -> float | None:
    """p* = uc* + rbar kappa*: the price of production of the regulating capital, the
    technique in operation with the lowest unit cost uc = ucs + delta kappa (Shaikh 2016,
    pp. 265-266: the lowest reproducible cost regulates, and its price of production is the
    centre of gravity of the market price). Exact ties in uc go to the lower kappa (the
    lower price of production), never to an order of plants or firms. None if no plant.

    Used by HURDLE_PRICE = "regulating": the profit-rate rule evaluates techniques at the
    price the market gravitates to rather than at the firm's posted price (Okishio's theorem
    compares techniques at prices of production; Shaikh 2016, p. 320).
    """
    if not ucs:
        return None
    uc, kappa = min((unit_cost(s, k, delta), k) for s, k in zip(ucs, kappas))
    return uc + rbar * kappa
