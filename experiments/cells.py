"""The experiments as cells (v4-plan.md, section 9; v4-final-model.md, "Experiments").

An experiment is a dictionary of cells. A cell has its parameter overrides, the populations
it is run on and its number of seeds; it is run for each of its populations on the same
seeds. The points of the Morris screening are cells too, built in experiments/morris.py.
"""
from experiments.populations import ALL, CONTROLS, homogeneous, invasion
from parameters import LABELS

PRICE_RULES = ("cost_edge", "normal_price", "systematic", "universal")
THREE_RULES = ("cost_edge", "systematic", "universal")      # E3 and E4
TWO_RULES = ("cost_edge", "universal")                      # E6 and some robustness checks
INVESTMENT_RULES = ("retained", "accelerator")
E4_RATES = (0.16, 0.10)                                     # register, decision 29
NO_DRAWS = {"tech_change": "none"}
E0_SEEDS = 50


def name(value) -> str:
    """A number as it appears in a cell name: 0.5 -> "0.5", 0.25 -> "0.25", 1.0 -> "1"."""
    return f"{value:g}"


def cells(named: dict, populations: tuple, seeds: int) -> dict:
    """Cells that share their populations and their number of seeds."""
    return {cell: {"overrides": overrides, "populations": populations, "seeds": seeds}
            for cell, overrides in named.items()}


def with_and_without_draws(named: dict, seeds: int = 500) -> dict:
    """Each setting twice: at the defaults in the three populations, and without draws in
    the two controls, where E0 is read."""
    with_draws = cells(named, ALL, seeds)
    without = cells({"no_draws_" + cell: {**NO_DRAWS, **overrides}
                     for cell, overrides in named.items()}, CONTROLS, E0_SEEDS)
    return {**with_draws, **without}


# The six cells of E2: the bias, then the two controls of technical change.
E2_CELLS = {
    **{"beta_" + name(bias): {"bias": bias} for bias in (0.0, 0.5, 1.5, 3.0)},
    "neutral": {"tech_change": "neutral"},
    "none": {"tech_change": "none"},
}

EXPERIMENTS = {
    # The gate: without technical change, does the industry behave as under real competition?
    "E0": cells({f"no_draws_{rule}": {**NO_DRAWS, "pricing": rule} for rule in PRICE_RULES},
                CONTROLS, E0_SEEDS),
    # Does another general rate give a working industry, on the scaled menu?
    "E0r": with_and_without_draws({f"rbar_{name(rbar)}": {"rbar": rbar}
                                   for rbar in (0.10, 0.05)}),
    # What the proposal marks "100 seeds", at the default rule.
    "reruns": {
        **cells({"accelerator": {"investment": "accelerator"},
                 "step_0.5_accelerator": {"shortage_step": 0.5, "investment": "accelerator"},
                 "growth_0.01": {"growth": 0.01}}, ALL, 500),
        **with_and_without_draws({"step_0.5": {"shortage_step": 0.5},
                                  "entry_lowest": {"entry_price": "lowest"},
                                  "no_overtime": {"u_max": 1.0},
                                  "reserve_always": {"reserve": "always"},
                                  "reserve_never": {"reserve": "never"}}),
    },
    # The bias or the initial menu? The cells of E2 from six firms on D1.
    "homogeneous": cells({cell: {**overrides, **homogeneous()}
                          for cell, overrides in E2_CELLS.items()}, ALL, 200),
    # Which rule wins, by price rule?
    "E1": cells({f"defaults_{rule}": {"pricing": rule} for rule in PRICE_RULES}, ALL, 500),
    # Does the advantage need the Marx bias, and grow with it?
    "E2": cells({f"{cell}_{rule}": {**overrides, "pricing": rule}
                 for rule in PRICE_RULES for cell, overrides in E2_CELLS.items()}, ALL, 200),
    # How much comes from the evaluation price?
    "E3": cells({f"lam_{name(lam)}_{rule}": {"lam": lam, "pricing": rule}
                 for rule in THREE_RULES for lam in (0.0, 0.25, 0.5, 0.75, 1.0)}, ALL, 200),
}


def e4_cells(tech_change: str, rbar: float, growth: tuple = (0.0, 0.01),
             rules: tuple = THREE_RULES) -> dict:
    """The cells of E4 for one rule of technical change and one general rate: price rule x
    investment rule x demand growth."""
    return {f"{tech_change}_{rule}_{investment}_g{name(g)}_rbar{name(rbar)}":
            {"tech_change": tech_change, "pricing": rule, "investment": investment,
             "growth": g, "rbar": rbar}
            for rule in rules for investment in INVESTMENT_RULES for g in growth}


def invasion_cell(mutant: str, rule: str) -> dict:
    """One cell of E6: one firm of the mutant label among nine of the other, against the
    control in which the mutant follows the residents' rule."""
    control = "all_profit_rate" if mutant == LABELS[0] else "all_unit_cost"
    return {"overrides": {**invasion(mutant), "pricing": rule},
            "populations": ("mixed", control), "seeds": 500, "mutant": mutant}


def with_setting(named: dict, **setting) -> dict:
    """The same cells with one setting added to each, named after it."""
    tag = "_".join(f"{key}_{value}" for key, value in setting.items())
    return {f"{tag}_{cell}": {**overrides, **setting} for cell, overrides in named.items()}


MARX_CELLS = e4_cells("marx", 0.16)
GROWTH_CELLS = e4_cells("marx", 0.16, growth=(0.01,), rules=TWO_RULES)

EXPERIMENTS.update({
    # Where does each rule win? Price rule x investment rule x growth, under the Marx-biased
    # set and under the categories rule, at the two general rates that meet E0.
    "E4": cells({cell: overrides for rbar in E4_RATES for tech_change in ("marx", "categories")
                 for cell, overrides in e4_cells(tech_change, rbar).items()}, ALL, 200),
    # Can one firm of a rule invade the other?
    "E6": {f"invader_{mutant}_{rule}": invasion_cell(mutant, rule)
           for rule in TWO_RULES for mutant in LABELS},
    # The sensitivity over the reserve, under universal undercutting (the default is in
    # the reruns).
    "reserve": with_and_without_draws({f"reserve_{level}_universal":
                                       {"reserve": level, "pricing": "universal"}
                                       for level in ("always", "never")}),
    "robustness": {
        # No overtime under the three other price rules.
        **with_and_without_draws({f"no_overtime_{rule}": {"u_max": 1.0, "pricing": rule}
                                  for rule in PRICE_RULES[1:]}),
        # The operating-cost floor, and the entrant's parent drawn evenly.
        **cells({f"operating_cost_floor_{rule}": {"price_floor": "operating_cost",
                                                  "pricing": rule} for rule in TWO_RULES},
                ALL, 500),
        **cells({f"entry_label_even_{rule}": {"entry_label": "even", "pricing": rule}
                 for rule in TWO_RULES}, ALL, 500),
        # Scrapping on unit cost: E1 and the Marx cells of E4.
        **cells({"scrap_cost_unit_cost_defaults": {"scrap_cost": "unit_cost"},
                 **with_setting(MARX_CELLS, scrap_cost="unit_cost")}, ALL, 200),
        # Designs that never become public.
        **cells({"private_designs": {"public_lag": None}}, ALL, 200),
        # 12 and 30 firms: E1 and the four cells of E4 with growth.
        **cells({cell: overrides for firms in (2, 5)
                 for cell, overrides in {
                     f"firms_per_pair_{firms}_defaults": {"firms_per_pair": firms},
                     **with_setting(GROWTH_CELLS, firms_per_pair=firms)}.items()}, ALL, 200),
    },
    # E0 and E1 on the fixed menu, at the second level of the general rate.
    "fixed_menu": with_and_without_draws({"fixed_menu_rbar_0.1":
                                          {"rbar": 0.10, "menu_scaling": "fixed"}}),
})


def runs(experiment: dict) -> int:
    """The number of runs of an experiment."""
    return sum(len(cell["populations"]) * cell["seeds"] for cell in experiment.values())
