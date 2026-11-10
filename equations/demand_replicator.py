from math import fsum


def competitiveness(price: float) -> float:
    """E = 1 / p."""
    return 1.0 / price


def replicator_shares(previous_shares: list[float], competitiveness: list[float],
                      chi: float) -> list[float]:
    """f_i = f_i,-1 (1 + chi (E_i - Ebar) / Ebar), with Ebar = sum_j f_j,-1 E_j; shares cut
    below zero are set to zero and the rest renormalised."""
    mean = fsum(f * e for f, e in zip(previous_shares, competitiveness))
    shares = [max(0.0, f * (1.0 + chi * (e - mean) / mean))
              for f, e in zip(previous_shares, competitiveness)]
    total = fsum(shares)
    return [share / total for share in shares]
