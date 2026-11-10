"""The industry at t = 0 and one run (v4-final-model.md, "Initial industry")."""
from math import fsum

import numpy as np

from equations.setup_initial_plants import initial_ages
from equations.setup_menu import scaled_menu
from markets.payments import pay
from model.entities import Industry, Plant, Technique, new_firm
from model.scheduler import period
from parameters import OPTIONS, SHAIKH_MENU, SHAIKH_RATE, Parameters


def build(params: Parameters, seed: int) -> Industry:
    """The industry before period 0.

    Shaikh's three techniques, scaled to the general rate, each given to one firm of each
    label. Plants have staggered ages, a firm's cash is the depreciation accumulated on its
    plants, every share is the capacity share and demand is demand_ratio times capacity.
    """
    check_options(params)

    # The industry's own stream; each firm gets its own when it is created.
    key = np.random.SeedSequence(seed, spawn_key=(0,))
    industry = Industry(params, seed, np.random.default_rng(key), demand_0=0.0)

    # The public menu follows the general rate, and with it the cost of every plant.
    industry.public = initial_menu(params)

    # One firm for each pair (technique, label), firms_per_pair times.
    for name, label, output in params.start * params.firms_per_pair:
        add_initial_firm(industry, name, label, output)

    # Demand is a given share of the initial capacity.
    capacity = fsum(firm.capacity for firm in industry.firms)
    industry.demand_0 = params.demand_ratio * capacity
    industry.demand = industry.demand_0

    # Every share is the capacity share, so every firm starts at the same utilisation.
    for firm in industry.firms:
        firm.share = firm.capacity / capacity
        firm.sales = firm.share * industry.demand_0
        firm.util = firm.sales / firm.capacity
    return industry


def check_options(params: Parameters) -> None:
    """Refuse a level that the table of options does not list, so that a misspelt cell fails
    at once instead of running the default."""
    for name, levels in OPTIONS.items():
        level = getattr(params, name)
        if level not in levels:
            raise ValueError(f"{name} = {level!r}: the levels are {', '.join(levels)}")


def initial_menu(params: Parameters) -> list[Technique]:
    """The public menu at t = 0: Shaikh's table scaled to rbar, or the table itself under
    menu_scaling = "fixed". Its techniques count as run from the start."""
    rows = scaled_menu(SHAIKH_MENU, SHAIKH_RATE, params.rbar, params.delta, params.menu_scaling)
    return [Technique(name, ucs, kappa, first_run=0) for name, ucs, kappa in rows]


def add_initial_firm(industry: Industry, name: str, label: str, output: float) -> None:
    """A firm of the initial population: plants of one technique, of staggered ages."""
    p = industry.params
    # The technique of the public menu that carries this name.
    technique = next(technique for technique in industry.public if technique.name == name)
    firm = new_firm(industry, label, p.initial_price, share=0.0)

    # Its plants, each already depreciated for its age.
    cost = technique.kappa * p.plant_size
    for age in initial_ages(output, p.plant_size, p.plant_life):
        book_value = cost * (1.0 - age / p.plant_life)
        firm.plants.append(Plant(technique, p.plant_size, cost, book_value, age))

    # Its cash is the depreciation accumulated on them: it backs the reserves they release.
    accumulated = fsum(plant.cost - plant.book_value for plant in firm.plants)
    pay(industry.roe, firm, accumulated)


def run(params: Parameters = Parameters(), seed: int = 0) -> Industry:
    """One run of params.periods periods; the period table is industry.rows."""
    industry = build(params, seed)
    for _ in range(params.periods):
        period(industry)
    return industry
