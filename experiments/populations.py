"""The populations an experiment runs its cells on, as parameter overrides (v4-plan.md,
section 9).

A cell is run for every population of its experiment on the same seeds. In a control both
labels follow one rule, so a label that wins there wins by drift. The other functions give
the overrides of an initial population that is not the default one.
"""
from parameters import LABELS

POPULATIONS = {
    "mixed": {},                                         # each label on its own rule
    "all_unit_cost": {"rule_okishio": "unit_cost"},      # control: both on the unit-cost rule
    "all_profit_rate": {"rule_shaikh": "profit_rate"},   # control: both on the profit-rate rule
}
CONTROLS = ("all_unit_cost", "all_profit_rate")
ALL = ("mixed",) + CONTROLS


def homogeneous(technique: str = "D1", output: float = 120.0, pairs: int = 3) -> dict:
    """The homogeneous start: six firms of 6 plants on D1, three of each label, so that no
    firm starts with a technique the rules disagree on. D_0 = 639.2 (register, Q7)."""
    start = tuple((technique, label, output) for _ in range(pairs) for label in LABELS)
    return {"start": start}


def invasion(mutant: str, residents: int = 9, technique: str = "D1",
             output: float = 120.0) -> dict:
    """E6: ten firms of 6 plants on D1, nine of the resident label and one of the mutant
    label, without mutation at entry. D_0 = 1,065.3 (register, A13 d)."""
    resident = LABELS[1] if mutant == LABELS[0] else LABELS[0]
    start = ((technique, resident, output),) * residents + ((technique, mutant, output),)
    return {"start": start, "mutation": 0.0}


def firms_per_pair(firms: int) -> dict:
    """The default population with several firms for each pair (technique, label)."""
    return {"firms_per_pair": firms}
