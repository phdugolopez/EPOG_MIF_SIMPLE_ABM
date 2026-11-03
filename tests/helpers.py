"""Shared helpers for the tests: modified copies of parameters.py and small industries."""

from types import SimpleNamespace

import parameters
from model import Industry


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
