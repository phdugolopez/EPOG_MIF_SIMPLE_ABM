"""E0 to E3 under another price rule, to set beside the runs of stage 5 (plan, section 9).

    python -m experiments.price_rules leader_follow [E0 E1 ...] [--seeds N] [--jobs N]
                                                    [--resume] [--keep-periods 0,1]

An analysis variant, registered in docs/design/v3-choices.md: no file of the model changes and
no rule below is the default of version 3. Each runs the cells of cells.py on their seeds:

  systematic         version 3's own regime, pricing = "systematic" in every cell
  leader_follow      version 2's leader-follow rule with the floor at the unit cost of the
                     firm's best plant, put in place of step 1 in every worker
  leader_follow_ucs  the same rule with version 2's operating-cost floor: the operating cost
                     ucs of the dearest plant the firm ran last period
  leader_follow_overtime, leader_follow_ucs_overtime
                     the two rules above with overtime: output up to 1.2 times normal
                     capacity at the same operating cost (no premium)

E3 keeps its ten cost-edge cells (lambda x rbar), renamed after the rule. The files are those of
the harness, in outputs/<rule>/<experiment>/.
"""
import argparse
import os
import pathlib

from equations.common_unit_cost import unit_cost
from equations.pricing_floor import price_floor
from experiments.cells import EXPERIMENTS
from experiments.harness import run_experiment
from markets.goods_market import allocate
from model import scheduler
from parameters import EPS

RISE = 0.03          # version 2's LEADER_RISE: the rise after excess demand, and of a firm alone
MONOPOLY_CAP = 3.0   # version 2's MONOPOLY_CAP: a firm alone stops at this multiple of its floor
U_MAX = 1.2          # overtime: output up to this multiple of normal capacity, without a premium


def leader_follow_price(previous: float, leader: float, floor: float, excess: float, alone: bool,
                        cut: float, rise: float = RISE, cap: float = MONOPOLY_CAP) -> tuple[float, bool]:
    """Version 2's rule (its equations/leader_follow_price.py, SHORTAGE_RULE = "leader"), with
    `leader` the lowest price posted last period. A firm alone raises its price by `rise`, up to
    cap x floor. After excess demand every firm posts (1 + rise) x leader, so a firm above that
    lowers its price. Otherwise every firm posts (1 - cut) x leader, or its floor if that is
    higher. Returns the price and whether the firm cut."""
    if alone:
        return min(previous * (1.0 + rise), cap * floor), False
    if excess > 0.0:
        return (1.0 + rise) * leader, False
    target = (1.0 - cut) * leader
    return (target, True) if target >= floor else (floor, False)


def unit_cost_floor(firm, delta: float) -> float:
    """Version 3's floor: the unit cost ucs + delta kappa of the firm's best plant."""
    return price_floor([unit_cost(q.technique.ucs, q.technique.kappa, delta) for q in firm.plants])


def operating_cost_floor(firm, delta: float) -> float:
    """Version 2's LEADER_FOLLOW_FLOOR = "operating_cost" (the floor of version 1): the
    operating cost ucs of the dearest plant the firm ran last period, or of its cheapest plant
    if none ran. Depreciation is sunk, so it is left out."""
    ran = [q.technique.ucs for q in firm.plants if q.output > EPS]
    return max(ran) if ran else min(q.technique.ucs for q in firm.plants)


def set_prices_leader_follow(industry, floor=unit_cost_floor) -> None:
    """Step 1 under the leader-follow rule, with version 3's conventions: every firm is computed
    from the state at the start of the step, and the firms that count are those with a plant in
    operation. A firm without a plant keeps its price."""
    p = industry.params
    active = [firm for firm in industry.firms if firm.plants]
    leader = min((firm.price for firm in active), default=0.0)
    posted = [leader_follow_price(firm.price, leader, floor(firm, p.delta), industry.excess,
                                  len(active) == 1, p.price_cut) for firm in active]
    for firm in industry.firms:
        firm.cut = False
    for firm, (price, cut) in zip(active, posted):
        firm.price, firm.cut = price, cut


def set_prices_leader_follow_ucs(industry) -> None:
    """The same step with the floor at the operating cost."""
    set_prices_leader_follow(industry, operating_cost_floor)


def allocate_with_overtime(demand: float, shares: list[float], offered: list[float]):
    """Step 2 with overtime: a firm sells up to U_MAX times the capacity it offers."""
    return allocate(demand, shares, [U_MAX * capacity for capacity in offered])


def dispatch_with_overtime(ucs: list[float], ages: list[int], capacity: list[float],
                           quantity: float) -> list[float]:
    """Step 3 with overtime: plants run to normal capacity cheapest first, then youngest; what
    is left runs as overtime in the same order, up to U_MAX times capacity, at the same cost."""
    outputs = [0.0] * len(ucs)
    order = sorted(range(len(ucs)), key=lambda i: (ucs[i], ages[i]))
    for room in (1.0, U_MAX - 1.0):
        for i in order:
            extra = min(room * capacity[i], quantity)
            outputs[i] += extra
            quantity -= extra
    return outputs


def install_leader_follow() -> None:
    """Run once in each worker: the period loop then calls the rule above at step 1."""
    scheduler.set_prices = set_prices_leader_follow


def install_leader_follow_ucs() -> None:
    scheduler.set_prices = set_prices_leader_follow_ucs


def install_overtime() -> None:
    """Steps 2 and 3 with overtime. The shortage signal stays demand above normal capacity."""
    scheduler.allocate, scheduler.dispatch = allocate_with_overtime, dispatch_with_overtime


def install_leader_follow_overtime() -> None:
    install_leader_follow()
    install_overtime()


def install_leader_follow_ucs_overtime() -> None:
    install_leader_follow_ucs()
    install_overtime()


RULES = {"systematic": None, "leader_follow": install_leader_follow,
         "leader_follow_ucs": install_leader_follow_ucs,
         "leader_follow_overtime": install_leader_follow_overtime,
         "leader_follow_ucs_overtime": install_leader_follow_ucs_overtime}


def experiments(rule: str) -> dict:
    """The experiments of cells.py under the rule, named <experiment>_<rule>. A cell that sets
    systematic cutting is left out; the others lose their `pricing` and take the rule's name."""
    regime = {"pricing": "systematic"} if rule == "systematic" else {}
    return {
        f"{name}_{rule}": {**experiment, "cells": {
            cell.replace("cost_edge", rule): {
                **{key: value for key, value in overrides.items() if key != "pricing"}, **regime}
            for cell, overrides in experiment["cells"].items()
            if overrides.get("pricing") != "systematic"}}
        for name, experiment in EXPERIMENTS.items()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("rule", choices=sorted(RULES))
    parser.add_argument("experiments", nargs="*", default=sorted(EXPERIMENTS), metavar="experiment")
    parser.add_argument("--seeds", type=int, help="seeds per cell (default: the experiment's)")
    parser.add_argument("--jobs", type=int, default=os.cpu_count(), help="worker processes")
    parser.add_argument("--resume", action="store_true", help="keep the groups already complete")
    parser.add_argument("--keep-periods", default="", help="seeds whose period table is kept")
    arguments = parser.parse_args()
    kept = tuple(int(seed) for seed in arguments.keep_periods.split(",") if seed)
    for name in arguments.experiments:
        print(run_experiment(
            f"{name}_{arguments.rule}", arguments.seeds, arguments.jobs, arguments.resume, kept,
            folder=pathlib.Path("outputs") / arguments.rule / name,
            experiments=experiments(arguments.rule), initializer=RULES[arguments.rule]))
