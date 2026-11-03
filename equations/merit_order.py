import math


def plant_segments(
    ucs: list[float], capacity: list[float], u_max: float, overtime_premium: float
) -> list[tuple[float, int, float, bool]]:
    """Each plant offers normal output at ucs_v and overtime up to u_max at a premium.

    Returns (unit cost, plant index, size, is_overtime), cheapest first.
    """
    segments = []
    for v, (cost, cap) in enumerate(zip(ucs, capacity)):
        segments.append((cost, v, cap, False))
        segments.append(((1.0 + overtime_premium) * cost, v, (u_max - 1.0) * cap, True))
    return sorted(segments, key=lambda s: s[0])


def dispatch(
    ucs: list[float],
    capacity: list[float],
    quantity: float,
    u_max: float,
    overtime_premium: float,
) -> tuple[list[float], list[float]]:
    """Run plants in merit order, lowest operating cost first, to produce `quantity`.

    Segments with the same cost share the quantity in proportion to their size, so a tie
    never depends on the order of plants. Returns normal and overtime output per plant.
    """
    normal = [0.0] * len(ucs)
    overtime = [0.0] * len(ucs)
    remaining = quantity
    segments = plant_segments(ucs, capacity, u_max, overtime_premium)
    i = 0
    while i < len(segments) and remaining > 0.0:
        j = i
        while j < len(segments) and math.isclose(segments[j][0], segments[i][0]):
            j += 1
        group = segments[i:j]
        size = sum(s[2] for s in group)
        take = min(remaining, size)
        for _, v, seg_size, is_overtime in group:
            q = take * seg_size / size if size > 0.0 else 0.0
            if is_overtime:
                overtime[v] += q
            else:
                normal[v] += q
        remaining -= take
        i = j
    return normal, overtime
