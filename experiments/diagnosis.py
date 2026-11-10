"""Diagnosis of the overcapacity and of the cycle found after stages 3 and 4 (plan, section 9).

A throwaway script, like the v2 pilot: each variant changes one parameter, or patches one rule
from here, and no file of the model is changed. It is not an experiment of the report.

    python -m experiments.diagnosis [seeds]

Four cells a variant, on the same seeds: E0 for each rule (no technical change, one rule), the
mixed population at the defaults and its unit-cost control. Per cell, means over seeds of
measures taken from period 20 on, once the initial plants are gone.
"""
import statistics
import sys
from contextlib import ExitStack
from dataclasses import replace
from math import fsum
from unittest import mock

from experiments.summary import run_row
from markets.goods_market import allocate
from model.model import run
from model.outputs import count
from model.scheduler import allocate_demand as ALLOCATE_DEMAND
from parameters import Parameters

CELLS = {
    "E0 unit-cost": dict(tech_change="none", rule_okishio="unit_cost"),
    "E0 profit-rate": dict(tech_change="none", rule_shaikh="profit_rate"),
    "mixed": {},
    "control unit-cost": dict(rule_okishio="unit_cost"),
}
START = 20      # measures skip the first periods, in which the initial plants retire
U_MAX = 1.2     # overtime variant: output up to 1.2 x normal capacity, without a premium


def keep_withdrawn_reserve(industry, firm, plant, reason):
    """remove_plant with the withdrawn reserve left in the firm's cash, as in the pilot."""
    firm.plants.remove(plant)
    if industry.r_new is None or industry.r_new >= industry.params.rbar:
        firm.funds += plant.cost - plant.book_value
        count(industry, firm, "cap_released", plant.capacity)
    firm.write_offs += plant.book_value
    count(industry, firm, "cap_retired", plant.capacity)
    count(industry, firm, "cap_retired_" + reason, plant.capacity)


def allocate_with_overtime(demand, shares, offered):
    return allocate(demand, shares, [U_MAX * capacity for capacity in offered])


def dispatch_with_overtime(ucs, ages, capacity, quantity):
    """Normal capacity cheapest first, then youngest; then overtime in the same order."""
    outputs = [0.0] * len(ucs)
    order = sorted(range(len(ucs)), key=lambda i: (ucs[i], ages[i]))
    for room in (1.0, U_MAX - 1.0):
        for i in order:
            extra = min(room * capacity[i], quantity)
            outputs[i] += extra
            quantity -= extra
    return outputs


def demand_with_overtime_signal(industry):
    """allocate_demand, with a shortage only when demand exceeds capacity with overtime."""
    ALLOCATE_DEMAND(industry)
    capacity = fsum(firm.capacity for firm in industry.firms)
    industry.excess = max(0.0, industry.demand - U_MAX * capacity) / industry.demand


RELEASED = "markets.plant_market.reserve_released"
OVERTIME = {"model.scheduler.allocate": allocate_with_overtime,
            "model.scheduler.dispatch": dispatch_with_overtime}
VARIANTS = {
    "default": ({}, {}),
    "shortage_step 0.1": (dict(shortage_step=0.1), {}),
    "price_cut 0.05": (dict(price_cut=0.05), {}),
    "systematic cutting": (dict(pricing="systematic"), {}),
    "entry_speed 1": (dict(entry_speed=1.0), {}),
    "entry_speed 0.2": (dict(entry_speed=0.2), {}),
    "entry_size 0.25": (dict(entry_size=0.25), {}),
    "accelerator": (dict(investment="accelerator"), {}),
    "idle scrapping after 4": (dict(scrap_periods=4), {}),
    "reserve always released": ({}, {RELEASED: lambda r_new, rbar: True}),
    "reserve never released": ({}, {RELEASED: lambda r_new, rbar: False}),
    "withdrawn reserve in cash": ({}, {"model.scheduler.remove_plant": keep_withdrawn_reserve}),
    "overtime to 1.2": ({}, OVERTIME),
    "overtime, shortage_step 0.25": (dict(shortage_step=0.25), OVERTIME),
    "overtime, entry_speed 1": (dict(entry_speed=1.0), OVERTIME),
    "overtime, step 0.25, speed 1": (dict(shortage_step=0.25, entry_speed=1.0), OVERTIME),
    "overtime, shortage above 1.2 K": (
        {}, {**OVERTIME, "model.scheduler.allocate_demand": demand_with_overtime_signal}),
    "overtime, reserve always released": ({}, {**OVERTIME, RELEASED: lambda r_new, rbar: True}),
    "systematic, reserve always released": (
        dict(pricing="systematic"), {RELEASED: lambda r_new, rbar: True}),
}


def measures(rows: list[dict], params: Parameters, seed: int) -> dict:
    """The run row, plus what describes a cycle from period START on."""
    row = run_row(rows, params, seed)
    u, o = rows[2 * START::2], rows[2 * START + 1::2]
    ratio = [(a["capacity"] + b["capacity"]) / a["demand"] for a, b in zip(u, o)]
    price = [a["price_over_reg"] for a in u if a["price_over_reg"] is not None]
    short = [a["lost"] > 1e-9 for a in u]
    row.update(
        kd_mean=statistics.mean(ratio), kd_min=min(ratio), kd_max=max(ratio),
        in_band=0.9 <= row["capacity_over_demand"] <= 1.2,
        price_mean=statistics.mean(price), price_max=max(price),
        shortage=fsum(short) / len(short),
        episodes=sum(now and not before for before, now in zip(short, short[1:])),
        won=row["outcome"] == "win", lost_run=row["outcome"] == "loss")
    return row


def cell(overrides: dict, seeds: int) -> dict:
    """Means over seeds of the measures of one cell."""
    params = replace(Parameters(), **overrides)
    runs = [measures(run(params, seed).rows, params, seed) for seed in range(seeds)]
    keys = ("kd_mean", "kd_min", "kd_max", "in_band", "price_mean", "price_max", "shortage",
            "episodes", "util_mean", "rate_industry", "firms_end", "entries", "war_freq",
            "retired_idle", "cap_share_end", "won", "lost_run")
    return {key: statistics.mean(r[key] for r in runs if r[key] is not None) for key in keys}


def main(seeds: int, names: list[str]) -> None:
    head = ("K/D", "min", "max", "band", "p/pp", "max", "short", "epis", "util", "rate",
            "firms", "entry", "war", "idle", "shareU", "won", "lost")
    for name in names or VARIANTS:
        overrides, patches = VARIANTS[name]
        print(f"\n{name}\n{'':20s}" + "".join(f"{h:>7s}" for h in head))
        with ExitStack() as stack:
            for target, replacement in patches.items():
                stack.enter_context(mock.patch(target, replacement))
            for label, base in CELLS.items():
                if base.get("tech_change") == "none" and overrides.get("tech_change"):
                    continue
                result = cell({**base, **overrides}, seeds)
                print(f"  {label:18s}" + "".join(f"{value:7.2f}" for value in result.values()))


if __name__ == "__main__":
    arguments = sys.argv[1:]
    count_seeds = int(arguments.pop(0)) if arguments and arguments[0].isdigit() else 20
    main(count_seeds, arguments)
