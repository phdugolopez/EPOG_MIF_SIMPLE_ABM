def leaving(shares: list[float], capacities: list[float], exit_share: float,
            min_firms: int) -> list[bool]:
    """Firms below the exit share or without capacity leave. If fewer than min_firms would
    remain, the candidates with the largest share stay, those with the same share together."""
    out = [share < exit_share or capacity <= 0.0 for share, capacity in zip(shares, capacities)]
    staying = out.count(False)
    for level in sorted({share for share, flag in zip(shares, out) if flag}, reverse=True):
        if staying >= min_firms:
            break
        for i, share in enumerate(shares):
            if out[i] and share == level:
                out[i] = False
                staying += 1
    return out
