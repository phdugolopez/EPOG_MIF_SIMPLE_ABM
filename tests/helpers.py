"""Small builders shared by the tests. A mechanism test builds a small industry by hand with
empty_industry and add_firm and calls one step function, so no step's test needs another step."""
from dataclasses import replace
from math import fsum

import numpy as np

from model.entities import Firm, Industry, Plant, Technique, new_firm
from model.model import build
from model.outputs import reset_tally
from parameters import MENU, Parameters


def menu() -> list[Technique]:
    """Shaikh's three techniques, in the order C, D1, D2 (addendum A1)."""
    return [Technique(name, ucs, kappa) for name, ucs, kappa in MENU]


def industry(seed: int = 0, **overrides) -> Industry:
    """The initial industry of model.build, with some parameters overridden."""
    return build(replace(Parameters(), **overrides), seed)


def empty_industry(seed: int = 0, **overrides) -> Industry:
    """An industry with the public menu (C, D1, D2), a demand of 100, an empty tally and no
    firm."""
    p = replace(Parameters(), **overrides)
    stream = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(0,)))
    ind = Industry(p, seed, stream, demand_0=100.0, demand=100.0)
    ind.public = [Technique(name, ucs, kappa, first_run=0) for name, ucs, kappa in p.menu]
    reset_tally(ind)
    return ind


def add_firm(ind: Industry, label: str = "shaikh", technique: Technique | None = None,
             plants: int = 1, age: int = 0, price: float = 100.0, share: float = 0.0,
             cash: float = 0.0) -> Firm:
    """A firm with `plants` plants in operation, of one technique (C by default) and one age.
    Its cash comes from the rest of the economy, so all cash still sums to zero."""
    p = ind.params
    firm = new_firm(ind, label, price, share)
    technique = technique or ind.public[0]
    cost = technique.kappa * p.plant_size
    for _ in range(plants):
        book_value = cost * (1.0 - age / p.plant_life)
        firm.plants.append(Plant(technique, p.plant_size, cost, book_value, age))
    firm.cash = cash
    ind.roe.cash -= cash
    return firm


def cash_total(ind: Industry) -> float:
    """All cash, the rest of the economy included: zero when money is conserved."""
    return ind.roe.cash + fsum(firm.cash for firm in ind.firms)
