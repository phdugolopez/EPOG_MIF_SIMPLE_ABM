CATEGORIES = ("both", "unit_cost")


def design_category(u: float, conflict_share: float) -> str:
    """Which rules a new design satisfies (u uniform on [0, 1)): "unit_cost" only, the
    conflict zone, with probability conflict_share; otherwise "both"."""
    return "unit_cost" if u < conflict_share else "both"


def draw_design(
    ucs_o: float, kappa_o: float, delta: float, price: float, category: str,
    u_a: float, u_b: float, step: float,
) -> tuple[float, float]:
    """A Marx-biased design relative to the reference technique o (the one the firm would
    otherwise build), judged at the firm's price p: operating cost falls by a share a
    (labour-saving), capital per unit rises by a share b (capital-using),
        ucs_n = (1 - a) ucs_o,    kappa_n = (1 + b) kappa_o,    a = u_a x step.
    The unit cost falls if b < b_S = a ucs_o / (delta kappa_o) (the unit-cost rule adopts);
    the profit rate at p rises if b < b_O = a ucs_o / (delta kappa_o + p - uc_o) (the
    profit-rate rule adopts). "both": 0 < b < b_O. "unit_cost": b_O <= b < b_S, the conflict
    zone, which shrinks to nothing as the margin p - uc_o falls to zero (taken as zero when
    negative: the profit-rate rule then behaves like the unit-cost rule). With no margin there
    is no conflict zone, and a conflict draw becomes a design both rules adopt.
    u_a in (0, 1], u_b in [0, 1).
    """
    a = u_a * step
    margin = max(price - (ucs_o + delta * kappa_o), 0.0)
    b_s = a * ucs_o / (delta * kappa_o)
    b_o = a * ucs_o / (delta * kappa_o + margin)
    if category == "unit_cost" and margin > 0.0:
        b = b_o + u_b * (b_s - b_o)
    else:
        b = (1.0 - u_b) * b_o
    return (1.0 - a) * ucs_o, (1.0 + b) * kappa_o
