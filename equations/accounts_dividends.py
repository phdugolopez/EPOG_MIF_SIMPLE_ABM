"""Dividends of a firm in a period: d x max(0, profit).

Source: v4-final-model.md, "Schedule", step 3. Profit is after depreciation; what is not
paid out joins the investible funds, and a loss lowers them.
"""


def dividends(profit: float, payout: float) -> float:
    """The share d of a positive profit; nothing on a loss."""
    return payout * max(0.0, profit)
