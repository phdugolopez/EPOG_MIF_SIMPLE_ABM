"""The industry at t = 0 (addendum A1 to A3, A13 k) and one run."""
from math import fsum

import numpy as np

from equations.setup_initial_plants import initial_ages
from model.entities import Industry, Plant, Technique, new_firm
from model.outputs import reset_tally
from model.scheduler import period
from parameters import Parameters


def build(params: Parameters, seed: int) -> Industry:
    """Initial population (A2, A3): plants of staggered ages, cash equal to the depreciation
    accumulated on them, shares by capacity, demand at demand_ratio x capacity."""
    p = params
    stream = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(0,)))
    industry = Industry(p, seed, stream, demand_0=0.0)
    industry.public = [Technique(name, ucs, kappa, first_run=0) for name, ucs, kappa in p.menu]
    menu = {technique.name: technique for technique in industry.public}
    for name, label, output in p.start * p.firms_per_pair:
        firm = new_firm(industry, label, p.initial_price, share=0.0)
        cost = menu[name].kappa * p.plant_size
        for age in initial_ages(output, p.plant_size, p.plant_life):
            book_value = cost * (1.0 - age / p.plant_life)
            firm.plants.append(Plant(menu[name], p.plant_size, cost, book_value, age))
        firm.cash = fsum(plant.cost - plant.book_value for plant in firm.plants)
    capacity = fsum(firm.capacity for firm in industry.firms)
    industry.demand_0 = industry.demand = p.demand_ratio * capacity
    for firm in industry.firms:
        firm.share = firm.capacity / capacity
        firm.sales = firm.share * industry.demand_0
        firm.util = firm.sales / firm.capacity
    industry.roe.cash = -fsum(firm.cash for firm in industry.firms)
    reset_tally(industry)
    return industry


def run(params: Parameters = Parameters(), seed: int = 0) -> Industry:
    """One run of params.periods periods; the period table is industry.rows."""
    industry = build(params, seed)
    for _ in range(params.periods):
        period(industry)
    return industry
