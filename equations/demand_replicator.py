"""Market shares: the replicator on competitiveness E = 1 / p.

    f_i = f_i,-1 [1 + chi (E_i - Ebar) / Ebar],   Ebar = sum over j of f_j,-1 E_j

Source: v4-final-model.md, "Schedule", step 2, and the first formula below the schedule. A
share that would fall below zero is set to zero and the others are renormalised.
"""
from math import fsum


def competitiveness(price: float) -> float:
    """E = 1 / p: the lower the price, the more competitive the firm."""
    return 1.0 / price


def replicator_shares(previous_shares: list[float], competitiveness: list[float],
                      chi: float) -> list[float]:
    """The market shares of the period, in the order of the firms given."""
    mean = fsum(share * level for share, level in zip(previous_shares, competitiveness))
    shares = [max(0.0, share * (1.0 + chi * (level - mean) / mean))
              for share, level in zip(previous_shares, competitiveness)]
    total = fsum(shares)
    return [share / total for share in shares]
