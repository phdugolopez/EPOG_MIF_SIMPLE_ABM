"""The experiments as cells (v4-plan.md, section 9; v4-final-model.md, "Experiments").

An experiment is a dictionary of cells. A cell has its parameter overrides, the populations
it is run on and its number of seeds; it is run for each of its populations on the same
seeds. E4, Morris, E6, the reserve and the robustness checks are added in stages 8 and 9.
"""
from experiments.populations import ALL, CONTROLS, homogeneous

PRICE_RULES = ("cost_edge", "normal_price", "systematic", "universal")
THREE_RULES = ("cost_edge", "systematic", "universal")      # E3 and E4
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


def runs(experiment: dict) -> int:
    """The number of runs of an experiment."""
    return sum(len(cell["populations"]) * cell["seeds"] for cell in experiment.values())
