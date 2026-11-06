import math


def target_return_price(uc: float, kappa: float, rbar: float) -> float:
    """p^N_i = uc_i + rbar kappa_i: the firm's own price of production at normal output."""
    return uc + rbar * kappa


def markup_price(uc: float, markup: float) -> float:
    """Alternative anchor: (1 + mu) uc_i. It favours the lowest unit cost by construction."""
    return (1.0 + markup) * uc


def leader_anchor(anchors: list[float], previous_prices: list[float]) -> float:
    """Alternative anchor, the same for every firm: the target-return price of last period's
    price leader, p^N = uc_L + rbar kappa_L, where L posted the lowest price.

    Followers aim at the leader's price rather than their own price of production (Shaikh
    2016, ch. 7: followers match the price leader), so capital intensity no longer orders
    peacetime prices. Tied leaders are averaged, so the anchor never depends on firm order.
    `anchors` are the firms' own target-return prices, in the order of `previous_prices`.
    """
    lowest = min(previous_prices)
    tied = [a for a, p in zip(anchors, previous_prices) if math.isclose(p, lowest)]
    return sum(tied) / len(tied)
