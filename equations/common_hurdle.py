"""Evaluation price and hurdle of a rule.

    p^e = (1 - lambda) p + lambda p_R
    h   = 0                                      under the unit-cost rule
    h   = max(0, max over the menu of r_j(p^e))  under the profit-rate rule

Source: v4-final-model.md, "The one rule that differs". p is the firm's own price and p_R
the price of production of the regulating technique.
"""
from equations.common_profit_rate import profit_rate_at_price


def evaluation_price(price: float, reg_price: float, lam: float) -> float:
    """The price at which a firm judges techniques: its own at lambda = 0, p_R at lambda = 1."""
    return (1.0 - lam) * price + lam * reg_price


def hurdle(rule: str, eval_price: float, menu: list, delta: float) -> float:
    """The rate a rule adds to depreciation when it compares techniques; never below 0."""
    if rule == "unit_cost":
        return 0.0
    rates = [profit_rate_at_price(eval_price, technique.ucs, technique.kappa, delta)
             for technique in menu]
    return max(0.0, max(rates))
