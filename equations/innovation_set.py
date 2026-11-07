"""Technical change from an innovation set (TECH_CHANGE = "innovation_set").

A design n is drawn relative to a reference technique o as two proportional changes of its
unit operating cost and its capital per unit of output, with nothing read from the firm
but o. The two rules then filter the same draw with the hurdle inequality
    ucs_n + (delta + h) kappa_n < ucs_o + (delta + h) kappa_o
(equations/technique_choice.py), h = 0 for the unit-cost rule and h the profit rate at
the firm's price for the profit-rate rule. The zones (both adopt, only the unit-cost
rule, only the profit-rate rule, neither) are outcomes of the draw and of the price: the
conflict zone closes as the margin p - uc_o closes (docs/design/review-v2.md, section 4).
"""

import math

from equations.unit_cost import unit_cost

ZONES = ("both", "unit_cost", "profit_rate", "none")


def draw_marx(
    ucs_o: float, kappa_o: float, u: float, z: float, step: float, bias: float, spread: float,
) -> tuple[float, float]:
    """A Marx-biased design (TECH_SET = "marx"): lower operating cost, more capital per unit,
        ucs_n = (1 - a) ucs_o,   kappa_n = (1 + b) kappa_o,
        a = u step,              b = k a,   k = bias exp(spread z),
    u in (0, 1], z standard normal. k is the capital per unit given up per unit of
    operating cost saved, log-normal around the median `bias` (TECH_BIAS, the treatment)
    with spread `spread` (TECH_BIAS_SPREAD)."""
    a = u * step
    k = bias * math.exp(spread * z)
    return (1.0 - a) * ucs_o, (1.0 + k * a) * kappa_o


def draw_neutral(
    ucs_o: float, kappa_o: float, u: float, v: float, step: float,
) -> tuple[float, float]:
    """A design of the neutral set (TECH_SET = "neutral"): direction uniform on the circle
    in the plane (delta ucs / ucs, delta kappa / kappa), size s = u step,
        ucs_n = (1 + s cos theta) ucs_o,   kappa_n = (1 + s sin theta) kappa_o,
    theta = 2 pi v, u in (0, 1], v in [0, 1). Capital-saving and dearer designs appear;
    most of the circle is rejected by both rules."""
    s = u * step
    theta = 2.0 * math.pi * v
    return (1.0 + s * math.cos(theta)) * ucs_o, (1.0 + s * math.sin(theta)) * kappa_o


def adoption_zone(
    ucs_o: float, kappa_o: float, ucs_n: float, kappa_n: float, delta: float, price: float,
    floor_at_zero: bool = True,
) -> str:
    """Which rules adopt design n against reference o at `price`: "both", "unit_cost"
    (the conflict zone: only the unit-cost rule), "profit_rate" (only the profit-rate
    rule: dearer, capital-saving designs) or "none".

    The unit-cost rule adopts if uc_n < uc_o. The profit-rate rule adopts if the rate at
    `price` rises, (price - uc_n) / kappa_n > (price - uc_o) / kappa_o, which is the hurdle
    inequality with h = (price - uc_o) / kappa_o; with floor_at_zero, h is floored at 0,
    so below the reference's unit cost the two rules coincide (equations/hurdle.py)."""
    uc_o = unit_cost(ucs_o, kappa_o, delta)
    uc_n = unit_cost(ucs_n, kappa_n, delta)
    h = (price - uc_o) / kappa_o
    if floor_at_zero:
        h = max(0.0, h)
    unit_cost_adopts = uc_n < uc_o
    profit_rate_adopts = uc_n + h * kappa_n < uc_o + h * kappa_o
    if unit_cost_adopts and profit_rate_adopts:
        return "both"
    if unit_cost_adopts:
        return "unit_cost"
    if profit_rate_adopts:
        return "profit_rate"
    return "none"


def frontier_technique(techniques, delta: float):
    """The industry's best practice (TECH_REFERENCE = "frontier"): the technique with the
    lowest unit cost among `techniques`; exact ties go to the lower kappa, then the name,
    never to firm order."""
    return min(techniques, key=lambda t: (unit_cost(t.ucs, t.kappa, delta), t.kappa, t.name))
