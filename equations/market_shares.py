def _normalise(shares: list[float]) -> list[float]:
    total = sum(shares)
    return [s / total for s in shares] if total > 0.0 else shares


def replicator_shares(
    previous_shares: list[float], competitiveness: list[float], chi: float
) -> list[float]:
    """f_i,t = f_i,t-1 (1 + chi (E_i,t - Ebar_t) / Ebar_t), Ebar_t = sum_j f_j,t-1 E_j,t.

    Shares cut below zero are set to zero and the rest renormalised (K+S, n. 44).
    """
    e_bar = sum(f * e for f, e in zip(previous_shares, competitiveness))
    shares = [
        max(0.0, f * (1.0 + chi * (e - e_bar) / e_bar))
        for f, e in zip(previous_shares, competitiveness)
    ]
    return _normalise(shares)


def logit_shares(
    previous_shares: list[float], prices: list[float], eta: float
) -> list[float]:
    """Alternative: f_i,t proportional to f_i,t-1 p_i,t^(-eta); never negative."""
    return _normalise([f * p ** (-eta) for f, p in zip(previous_shares, prices)])
