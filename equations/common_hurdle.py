from equations.common_profit_rate import profit_rate_at_price


def evaluation_price(price: float, reg_price: float, lam: float) -> float:
    """p^e = (1 - lambda) p + lambda p_reg, the price at which techniques are judged."""
    return (1.0 - lam) * price + lam * reg_price


def hurdle(rule: str, eval_price: float, menu: list, delta: float) -> float:
    """h = 0 under the unit-cost rule; the best rate on the menu at p^e, never below 0,
    under the profit-rate rule."""
    if rule == "unit_cost":
        return 0.0
    return max(0.0, max(profit_rate_at_price(eval_price, t.ucs, t.kappa, delta) for t in menu))
