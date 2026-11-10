"""The experiments of the proposal as cells: each cell is a dictionary of parameter overrides,
run for every population of its experiment on the same seeds (plan, section 7).
E4, E6, Morris and the robustness checks are added in stages 6 and 7."""

POPULATIONS = {
    "mixed": {},                                      # each label on its own rule
    "all_unit_cost": {"rule_okishio": "unit_cost"},   # control: both labels on the unit-cost rule
    "all_profit_rate": {"rule_shaikh": "profit_rate"},   # control: both on the profit-rate rule
}
CONTROLS = ("all_unit_cost", "all_profit_rate")
ALL = ("mixed",) + CONTROLS


def name(value) -> str:
    """A number as it appears in a cell name: 0.5 -> "0.5", 0.25 -> "0.25", 1.0 -> "1"."""
    return f"{value:g}"


EXPERIMENTS = {
    # Without technical change, does the industry show Shaikh's real-competition facts?
    "E0": {"seeds": 50, "populations": CONTROLS, "cells": {"no_draws": {"tech_change": "none"}}},
    # Which rule wins at the defaults?
    "E1": {"seeds": 500, "populations": ALL, "cells": {"defaults": {}}},
    # Does the advantage grow with the Marx bias?
    "E2": {"seeds": 200, "populations": ALL, "cells": {
        **{"beta_" + name(bias): {"bias": bias} for bias in (0.0, 0.5, 1.5, 3.0)},
        "neutral": {"tech_change": "neutral"},
        "none": {"tech_change": "none"},
    }},
    # How much of the advantage comes from the evaluation price?
    "E3": {"seeds": 200, "populations": ALL, "cells": {
        f"lam_{name(lam)}_{pricing}_rbar_{name(rbar)}": {"lam": lam, "pricing": pricing, "rbar": rbar}
        for rbar in (0.05, 0.16) for pricing in ("cost_edge", "systematic")
        for lam in (0.0, 0.25, 0.5, 0.75, 1.0)
    }},
}
