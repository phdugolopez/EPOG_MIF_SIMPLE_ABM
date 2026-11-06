"""Shared helpers for the tests: modified copies of parameters.py and small industries."""

from types import SimpleNamespace

import parameters
from model import Industry


# Fixed plants, no lifespan, scrapping below unit cost or when idle, investment from
# retained earnings: the version 2 defaults (stated here so tests do not depend on them).
PLANT_ALTERNATIVES = dict(
    PLANT_SIZE=20.0, PLANT_LIFE=None, SCRAP_COST="unit_cost", OBSOLESCENCE_PERIODS=2,
    IDLE_SCRAPPING=True, IDLE_PERIODS=2, INVESTMENT_RULE="retained_earnings",
)
# The version 1 plants, scrapping, investment and fixed menu, for the tests written for them.
VERSION_1_PLANTS = dict(
    PLANT_SIZE=None, PLANT_LIFE=10, SCRAP_COST="operating_cost", OBSOLESCENCE_PERIODS=4,
    IDLE_SCRAPPING=False, INVESTMENT_RULE="accelerator", TECH_DRAWS=False, BORROWING=True,
)


def make_config(**overrides) -> SimpleNamespace:
    values = {k: v for k, v in vars(parameters).items() if k.isupper()}
    values.update(overrides)
    return SimpleNamespace(**values)


def swapped_config(**overrides) -> SimpleNamespace:
    """Swap the type labels everywhere and swap the hurdle mapping with them."""
    base = make_config(**overrides)
    swap = {"shaikh": "okishio", "okishio": "shaikh"}
    base.INITIAL_FIRMS = tuple((tech, swap[t]) for tech, t in base.INITIAL_FIRMS)
    base.HURDLE_RULES = {swap[t]: rule for t, rule in base.HURDLE_RULES.items()}
    return base


def one_firm_industry(technique: str = "C", **overrides) -> Industry:
    config = make_config(INITIAL_FIRMS=((technique, "shaikh"),), **overrides)
    return Industry(config)


def history_without_labels(industry) -> list[dict]:
    return [
        {k: v for k, v in row.items() if k not in ("type", "firm_type")}
        for row in industry.firm_history
    ]
