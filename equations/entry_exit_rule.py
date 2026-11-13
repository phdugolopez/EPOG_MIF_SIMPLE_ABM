"""Who leaves the industry: a share below exit_share, no capacity, or bankruptcy.

Source: v4-final-model.md, "Schedule", step 6; v4-choices.md, the row A13 e kept from v3.
Capacity counts the plants in operation and on order. If fewer than min_firms would remain,
the candidates with the largest shares stay; those with the same share stay or leave
together, so that no tie is broken by a firm's place.
"""


def leaving(shares: list[float], capacities: list[float], exit_share: float,
            min_firms: int, broke: list[bool] | None = None) -> list[bool]:
    """For each firm, in the order given, whether it leaves. broke flags the bankrupt
    firms; none is bankrupt when it is not given."""
    if broke is None:
        broke = [False] * len(shares)
    out = [share < exit_share or capacity <= 0.0 or is_broke
           for share, capacity, is_broke in zip(shares, capacities, broke)]
    staying = out.count(False)
    # The shares of the candidates, largest first: each level stays or leaves as one.
    levels = sorted({share for share, leaves in zip(shares, out) if leaves}, reverse=True)
    for level in levels:
        if staying >= min_firms:
            break
        for i, share in enumerate(shares):
            if out[i] and share == level:
                out[i] = False
                staying += 1
    return out
