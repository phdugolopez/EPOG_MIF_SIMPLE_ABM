"""The price of a firm under one of the three cutting rules.

    after a shortage:   the next higher rival price, or previous x (1 + step x excess)
                        with no rival above; never below the floor
    without a rival:    max(previous, floor)
    otherwise:          target = (1 - c) P if the firm is entitled to cut, P if not
                        price  = max(min(previous, target), floor)

Source: v4-final-model.md, "Schedule", step 1; v4-choices.md, decision 15 and the row Q2 kept
from v3. P is the lowest price of the firm's rivals and excess the excess-demand share of
last period. The three rules (cost edge, normal price, systematic) differ only in who is
entitled, which equations/pricing_entitlement.py says. A price rises only after a shortage
or to reach the floor.
"""
from math import isclose


def cutting_price(previous: float, rival_prices: list[float], entitled: bool, excess: float,
                  floor: float, cut: float, shortage_step: float) -> tuple[float, bool]:
    """The price the firm posts, and whether it cut."""
    if excess > 0.0:
        # The rival prices that are above the firm's own, and not equal to it by rounding.
        higher = [price for price in rival_prices
                  if price > previous and not isclose(price, previous)]
        target = previous * (1.0 + shortage_step * excess)
        if higher:
            target = min(higher)
        return max(target, floor), False

    if not rival_prices:
        return max(previous, floor), False

    lowest = min(rival_prices)
    target = lowest
    if entitled:
        target = (1.0 - cut) * lowest
    price = max(min(previous, target), floor)

    # The firm cut if it is entitled and its price is below both its own and the lowest.
    reference = min(previous, lowest)
    fell = price < reference and not isclose(price, reference)
    return price, entitled and fell
