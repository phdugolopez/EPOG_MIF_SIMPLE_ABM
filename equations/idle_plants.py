def idle_plants(
    ucs: list[float], vintage: list[int], capacity: list[float], output: float
) -> list[bool]:
    """Plants the firm did not need: those it could have left off and still produced its
    output at normal capacity. Highest operating cost first, then oldest, so the plants a
    firm would keep are its cheapest and newest. Identical plants are interchangeable."""
    spare = sum(capacity) - output
    order = sorted(range(len(ucs)), key=lambda v: (-ucs[v], vintage[v]))
    idle = [False] * len(ucs)
    for v in order:
        if capacity[v] <= spare + 1e-9:
            idle[v] = True
            spare -= capacity[v]
        else:
            break
    return idle
