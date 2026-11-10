"""Small builders shared by the tests.

A mechanism test builds a small industry by hand with empty_industry and add_firm and calls
one step function, so no step's test depends on another step.
"""
from dataclasses import replace
from math import fsum

import numpy as np

from markets.payments import pay
from model.entities import Firm, Industry, Plant, Technique, new_firm
from model.model import build, initial_menu
from parameters import SHAIKH_MENU, Parameters


def menu() -> list[Technique]:
    """Shaikh's three techniques, in the order C, D1, D2: the menu at rbar = 0.16."""
    return [Technique(name, ucs, kappa) for name, ucs, kappa in SHAIKH_MENU]


def industry(seed: int = 0, **overrides) -> Industry:
    """The initial industry of model.build, with some parameters overridden."""
    return build(replace(Parameters(), **overrides), seed)


def empty_industry(seed: int = 0, **overrides) -> Industry:
    """An industry with the public menu (C, D1, D2 at the general rate of the parameters), a
    demand of 100, an empty tally and no firm."""
    p = replace(Parameters(), **overrides)
    stream = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(0,)))
    ind = Industry(p, seed, stream, demand_0=100.0, demand=100.0)
    ind.public = initial_menu(p)
    return ind


def add_firm(ind: Industry, label: str = "shaikh", technique: Technique | None = None,
             plants: int = 1, age: int = 0, price: float = 100.0, share: float = 0.0,
             cash: float = 0.0) -> Firm:
    """A firm with `plants` plants in operation, of one technique (C by default) and one age.
    Its cash is paid by the rest of the economy, so all cash still sums to zero."""
    p = ind.params
    firm = new_firm(ind, label, price, share)
    technique = technique or ind.public[0]
    cost = technique.kappa * p.plant_size
    for _ in range(plants):
        book_value = cost * (1.0 - age / p.plant_life)
        firm.plants.append(Plant(technique, p.plant_size, cost, book_value, age))
    pay(ind.roe, firm, cash)
    return firm


def cash_total(ind: Industry) -> float:
    """All cash, the rest of the economy included: zero when money is conserved."""
    return ind.roe.cash + fsum(firm.cash for firm in ind.firms)


def tallied(ind: Industry, key: str, label: str | None = None, firm: Firm | None = None) -> float:
    """The total of one flow in the tally of the period: of the whole industry, of a label or
    of a firm."""
    return fsum(flow.amount for flow in ind.tally
                if flow.key == key
                and (label is None or flow.label == label)
                and (firm is None or flow.firm_id == firm.id))
