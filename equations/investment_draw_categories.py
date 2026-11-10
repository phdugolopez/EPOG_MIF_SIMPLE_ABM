def draw_categories(ucs_o: float, kappa_o: float, delta: float, price: float, u_cat: float,
                    u_a: float, u_b: float, step: float, conflict_share: float) -> tuple[float, float]:
    """ucs_n = (1 - a) ucs_o, kappa_n = (1 + b) kappa_o, a = u_a x step. The unit cost falls if
    b < b_S = a ucs_o / (delta kappa_o); the rate at `price` rises if b < b_O = a ucs_o /
    (delta kappa_o + price - uc_o). With probability q the design is in the conflict zone,
    b_O <= b < b_S; otherwise 0 < b <= b_O. Without a margin there is no conflict zone."""
    a = u_a * step
    margin = max(price - (ucs_o + delta * kappa_o), 0.0)
    b_s = a * ucs_o / (delta * kappa_o)
    b_o = a * ucs_o / (delta * kappa_o + margin)
    conflict = u_cat < conflict_share and margin > 0.0
    b = b_o + u_b * (b_s - b_o) if conflict else (1.0 - u_b) * b_o
    return (1.0 - a) * ucs_o, (1.0 + b) * kappa_o
