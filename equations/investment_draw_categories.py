"""A design of the categories rule, drawn from a technique o.

    ucs_n = (1 - a) ucs_o,   kappa_n = (1 + b) kappa_o,   a = u A
    the unit cost falls            if b < b_S = a ucs_o / (delta kappa_o)
    the rate at p^e rises          if b < b_O = a ucs_o / (delta kappa_o + p^e - uc_o)
    with probability q:  b_O <= b < b_S   (only the unit-cost rule adopts)
    otherwise:           0 < b <= b_O     (both rules adopt)

Source: v4-final-model.md, "Technical change", the option `tech_change = "categories"`;
v4-choices.md, the row Q13 kept from v3: the two categories are defined at the evaluation
price. Without a margin, p^e at or below uc_o, the two limits are equal and no design is in
conflict.
"""


def draw_categories(ucs_o: float, kappa_o: float, delta: float, eval_price: float,
                    u_kind: float, u_step: float, u_size: float, step: float,
                    conflict_share: float) -> tuple[float, float]:
    """The design as (ucs, kappa)."""
    saving = u_step * step
    margin = max(eval_price - (ucs_o + delta * kappa_o), 0.0)
    limit_unit_cost = saving * ucs_o / (delta * kappa_o)
    limit_rate = saving * ucs_o / (delta * kappa_o + margin)
    if u_kind < conflict_share and margin > 0.0:
        deepening = limit_rate + u_size * (limit_unit_cost - limit_rate)
    else:
        deepening = (1.0 - u_size) * limit_rate
    return (1.0 - saving) * ucs_o, (1.0 + deepening) * kappa_o
