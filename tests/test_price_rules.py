"""The price rules run beside the experiments (experiments/price_rules.py): version 2's
leader-follow rule with the unit-cost floor, and the cells it is run on."""
import importlib.util
import pathlib
import tempfile
import unittest
from dataclasses import replace
from unittest import mock

from experiments.cells import EXPERIMENTS
from experiments.harness import run_experiment
from experiments.price_rules import (MONOPOLY_CAP, RISE, RULES, U_MAX, allocate_with_overtime,
                                     dispatch_with_overtime, experiments, install_leader_follow,
                                     install_leader_follow_overtime, install_leader_follow_ucs,
                                     install_leader_follow_ucs_overtime, leader_follow_price,
                                     operating_cost_floor, set_prices_leader_follow,
                                     set_prices_leader_follow_ucs, unit_cost_floor)
from experiments.summary import run_row
from helpers import add_firm, empty_industry
from model import scheduler
from model.model import run
from parameters import Parameters
from test_experiments import read
from test_neutrality import POPULATIONS, mirror, swapped, trajectory

V2_RULE = pathlib.Path(__file__).resolve().parents[2] / "ABM-sources/equations/leader_follow_price.py"


def patched(step=set_prices_leader_follow, overtime=False):
    """The scheduler with the step in place of step 1 and, if asked, overtime in steps 2 and 3."""
    changes = {"set_prices": step}
    if overtime:
        changes.update(allocate=allocate_with_overtime, dispatch=dispatch_with_overtime)
    return mock.patch.multiple(scheduler, **changes)


class TestLeaderFollowPrice(unittest.TestCase):
    def test_every_firm_undercuts_the_leader_whatever_its_own_price(self):
        for previous in (90.0, 100.0, 120.0):
            self.assertEqual(leader_follow_price(previous, 100.0, 75.0, 0.0, False, 0.02), (98.0, True))

    def test_the_floor_stops_the_cut(self):
        self.assertEqual(leader_follow_price(76.0, 76.0, 75.0, 0.0, False, 0.02), (75.0, False))
        self.assertEqual(leader_follow_price(80.0, 70.0, 75.0, 0.0, False, 0.02), (75.0, False))

    def test_after_excess_demand_every_firm_posts_the_leader_plus_the_rise(self):
        for previous in (100.0, 110.0):       # a firm above that level lowers its price
            price, cut = leader_follow_price(previous, 100.0, 75.0, 0.1, False, 0.02)
            self.assertAlmostEqual(price, 100.0 * (1.0 + RISE), places=12)
            self.assertFalse(cut)

    def test_a_firm_alone_raises_its_price_up_to_the_cap(self):
        price, cut = leader_follow_price(100.0, 100.0, 75.0, 0.0, True, 0.02)
        self.assertAlmostEqual(price, 103.0, places=12)
        self.assertFalse(cut)
        self.assertEqual(leader_follow_price(224.0, 224.0, 75.0, 0.0, True, 0.02),
                         (MONOPOLY_CAP * 75.0, False))

    @unittest.skipUnless(V2_RULE.exists(), "the version 2 checkout is not beside this one")
    def test_it_is_the_function_of_version_2(self):
        spec = importlib.util.spec_from_file_location("v2_leader_follow_price", V2_RULE)
        v2 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v2)
        for previous in (70.0, 76.0, 100.0, 240.0):
            for leader in (70.0, 76.5, 100.0):
                for excess in (0.0, 0.2):
                    for alone in (False, True):
                        self.assertEqual(
                            leader_follow_price(previous, leader, 75.0, excess, alone, 0.02),
                            v2.leader_follow_price(previous, leader, 75.0, excess, alone, 0.02, RISE,
                                                   MONOPOLY_CAP, "leader"))


class TestStep(unittest.TestCase):
    def setUp(self):
        self.industry = empty_industry()
        menu = self.industry.public                   # unit costs 78.0, 76.0 and 75.0
        self.firms = [add_firm(self.industry, technique=menu[0], price=100.0),
                      add_firm(self.industry, technique=menu[2], price=90.0),
                      add_firm(self.industry, technique=menu[1], price=78.0)]

    def test_firms_post_from_the_prices_at_the_start_of_the_step(self):
        set_prices_leader_follow(self.industry)
        cut_price = 0.98 * 78.0                       # 76.44: below the floor of the firm on C only
        expected = [(78.0, False), (cut_price, True), (cut_price, True)]
        for firm, (price, cut) in zip(self.firms, expected):
            self.assertAlmostEqual(firm.price, price, places=9)
            self.assertEqual(firm.cut, cut)

    def test_the_order_of_firms_does_not_matter(self):
        set_prices_leader_follow(self.industry)
        prices = [firm.price for firm in self.firms]
        for firm, price in zip(self.firms, (100.0, 90.0, 78.0)):
            firm.price = price
        self.industry.firms.reverse()
        set_prices_leader_follow(self.industry)
        self.assertEqual([firm.price for firm in self.firms], prices)

    def test_a_firm_without_a_plant_keeps_its_price_and_does_not_lead(self):
        idle = self.firms[2]
        idle.plants.clear()
        set_prices_leader_follow(self.industry)
        self.assertEqual((idle.price, idle.cut), (78.0, False))
        self.assertAlmostEqual(self.firms[0].price, 0.98 * 90.0, places=9)

    def test_after_excess_demand_prices_meet_above_the_leader(self):
        self.industry.excess = 0.05
        set_prices_leader_follow(self.industry)
        for firm in self.firms:
            self.assertAlmostEqual(firm.price, 78.0 * (1.0 + RISE), places=9)
            self.assertFalse(firm.cut)

    def test_the_one_firm_with_a_plant_raises_its_price(self):
        for firm in self.firms[1:]:
            firm.plants.clear()
        set_prices_leader_follow(self.industry)
        self.assertAlmostEqual(self.firms[0].price, 103.0, places=9)


class TestFloors(unittest.TestCase):
    def setUp(self):
        self.industry = empty_industry()
        menu = self.industry.public                   # operating costs 64.25, 61.77 and 59.21
        self.firm = add_firm(self.industry, technique=menu[2], plants=2, price=90.0)
        self.firm.plants += add_firm(self.industry, technique=menu[0]).plants
        self.industry.firms.pop()                     # one firm: two plants on D2, one on C

    def test_the_unit_cost_floor_is_that_of_the_best_plant(self):
        self.assertAlmostEqual(unit_cost_floor(self.firm, 0.1), 59.21 + 15.789, places=9)

    def test_the_operating_cost_floor_is_that_of_the_dearest_plant_that_ran(self):
        for plant, output in zip(self.firm.plants, (20.0, 5.0, 0.0)):
            plant.output = output
        self.assertEqual(operating_cost_floor(self.firm, 0.1), 59.21)
        self.firm.plants[2].output = 1.0
        self.assertEqual(operating_cost_floor(self.firm, 0.1), 64.25)

    def test_without_output_it_is_the_operating_cost_of_the_cheapest_plant(self):
        self.assertEqual(operating_cost_floor(self.firm, 0.1), 59.21)

    def test_the_step_stops_at_the_operating_cost(self):
        rival = add_firm(self.industry, technique=self.industry.public[1], price=60.0)
        set_prices_leader_follow_ucs(self.industry)
        self.assertEqual((self.firm.price, self.firm.cut), (59.21, False))    # 0.98 x 60 = 58.8
        self.assertEqual((rival.price, rival.cut), (61.77, False))

    def test_each_rule_installs_its_step(self):
        for install, step in ((install_leader_follow, set_prices_leader_follow),
                              (install_leader_follow_ucs, set_prices_leader_follow_ucs)):
            with mock.patch.object(scheduler, "set_prices"):
                install()
                self.assertIs(scheduler.set_prices, step)
        self.assertEqual(set(RULES), {"systematic", "leader_follow", "leader_follow_ucs",
                                      "leader_follow_overtime", "leader_follow_ucs_overtime"})


class TestOvertime(unittest.TestCase):
    def test_plants_run_to_normal_capacity_in_merit_order_before_any_overtime(self):
        ucs, ages, capacity = [64.25, 59.21, 59.21], [1, 4, 2], [20.0, 20.0, 20.0]
        self.assertEqual(dispatch_with_overtime(ucs, ages, capacity, 30.0), [0.0, 10.0, 20.0])
        self.assertEqual(dispatch_with_overtime(ucs, ages, capacity, 60.0), [20.0, 20.0, 20.0])
        outputs = dispatch_with_overtime(ucs, ages, capacity, 66.0)       # 6 of overtime
        self.assertEqual([round(x, 9) for x in outputs], [20.0, 22.0, 24.0])

    def test_output_stops_at_the_overtime_limit(self):
        outputs = dispatch_with_overtime([60.0, 61.0], [0, 0], [20.0, 20.0], 100.0)
        self.assertEqual([round(x, 9) for x in outputs], [U_MAX * 20.0, U_MAX * 20.0])

    def test_a_firm_sells_up_to_the_overtime_limit(self):
        sales, lost = allocate_with_overtime(100.0, [0.5, 0.5], [40.0, 40.0])
        self.assertEqual([round(x, 9) for x in sales], [48.0, 48.0])
        self.assertAlmostEqual(lost, 4.0, places=9)
        self.assertEqual(allocate_with_overtime(80.0, [0.5, 0.5], [40.0, 40.0]), ([40.0, 40.0], 0.0))

    def test_the_overtime_rules_install_the_three_steps(self):
        for install, step in ((install_leader_follow_overtime, set_prices_leader_follow),
                              (install_leader_follow_ucs_overtime, set_prices_leader_follow_ucs)):
            with mock.patch.multiple(scheduler, set_prices=None, allocate=None, dispatch=None):
                install()
                self.assertIs(scheduler.set_prices, step)
                self.assertIs(scheduler.allocate, allocate_with_overtime)
                self.assertIs(scheduler.dispatch, dispatch_with_overtime)

    def test_overtime_raises_utilisation_and_lowers_the_demand_lost(self):
        params = replace(Parameters(), tech_change="none", rule_okishio="unit_cost")
        with patched():
            without = run_row(run(params, 1).rows, params, 1)
        with patched(overtime=True):
            industry = run(params, 1)
        row = run_row(industry.rows, params, 1)
        self.assertLess(row["lost_share"], without["lost_share"])
        self.assertTrue(any(a["sales"] + b["sales"] > a["capacity"] + b["capacity"]
                            for a, b in zip(industry.rows[0::2], industry.rows[1::2])))

    def test_swapped_labels_give_the_same_trajectories_with_overtime(self):
        for step in (set_prices_leader_follow, set_prices_leader_follow_ucs):
            for name, population in POPULATIONS.items():
                with self.subTest(step=step.__name__, population=name), patched(step, overtime=True):
                    params = replace(Parameters(), **population)
                    states, rows = trajectory(params, 4, 200)
                    swapped_states, swapped_rows = trajectory(swapped(params), 4, 200)
                    self.assertEqual(states, swapped_states)
                    self.assertEqual(rows, mirror(swapped_rows))
                    self.assertEqual(trajectory(params, 7, 120), trajectory(params, 7, 120, reverse=True))


class TestNeutrality(unittest.TestCase):
    def test_swapped_labels_give_the_same_trajectories_under_the_rule(self):
        for name, population in POPULATIONS.items():
            with self.subTest(population=name), patched():
                params = replace(Parameters(), **population)
                states, rows = trajectory(params, 4, 200)
                swapped_states, swapped_rows = trajectory(swapped(params), 4, 200)
                self.assertEqual(states, swapped_states)
                self.assertEqual(rows, mirror(swapped_rows))

    def test_swapped_labels_give_the_same_trajectories_with_the_operating_cost_floor(self):
        for name, population in POPULATIONS.items():
            with self.subTest(population=name), patched(set_prices_leader_follow_ucs):
                params = replace(Parameters(), **population)
                states, rows = trajectory(params, 4, 200)
                swapped_states, swapped_rows = trajectory(swapped(params), 4, 200)
                self.assertEqual(states, swapped_states)
                self.assertEqual(rows, mirror(swapped_rows))
                self.assertEqual(trajectory(params, 7, 120), trajectory(params, 7, 120, reverse=True))

    def test_the_order_of_firms_changes_nothing_under_the_rule(self):
        with patched():
            self.assertEqual(trajectory(Parameters(), 7, 120), trajectory(Parameters(), 7, 120, reverse=True))

    def test_without_technical_change_no_price_is_below_the_lowest_unit_cost(self):
        with patched():
            industry = run(replace(Parameters(), periods=120, tech_change="none"), 3)
        self.assertTrue(all(row["low_price"] >= 74.99 for row in industry.rows))
        self.assertLess(min(row["low_price"] for row in industry.rows), 80.0)    # from 100


class TestCells(unittest.TestCase):
    def test_the_cells_are_those_of_the_experiments_without_their_pricing(self):
        cells = experiments("leader_follow")
        self.assertEqual(set(cells), {name + "_leader_follow" for name in EXPERIMENTS})
        for name in ("E0", "E1", "E2"):
            self.assertEqual(cells[name + "_leader_follow"], EXPERIMENTS[name])
        e3 = cells["E3_leader_follow"]["cells"]
        self.assertEqual(len(e3), 10)
        self.assertEqual(e3["lam_0.25_leader_follow_rbar_0.16"], {"lam": 0.25, "rbar": 0.16})

    def test_the_systematic_cells_set_the_regime(self):
        cells = experiments("systematic")
        self.assertEqual(cells["E1_systematic"]["cells"], {"defaults": {"pricing": "systematic"}})
        self.assertEqual(cells["E3_systematic"]["cells"]["lam_1_systematic_rbar_0.05"],
                         {"lam": 1.0, "pricing": "systematic", "rbar": 0.05})
        self.assertIsNone(RULES["systematic"])


class TestWorkers(unittest.TestCase):
    def test_every_worker_runs_the_rule(self):
        small = {"T": {"seeds": 3, "populations": ("mixed",), "cells": {"short": {"periods": 40}}}}
        params = replace(Parameters(), periods=40)
        with patched():
            expected = [run_row(run(params, seed).rows, params, seed) for seed in range(3)]
        default = [run_row(run(params, seed).rows, params, seed) for seed in range(3)]
        with tempfile.TemporaryDirectory() as folder:
            run_experiment("T", jobs=2, folder=folder, experiments=small, quiet=True,
                           initializer=install_leader_follow)
            rows = read(pathlib.Path(folder))
        for row, under_rule, under_default in zip(rows, expected, default):
            self.assertEqual(float(row["capacity_end"]), under_rule["capacity_end"])
            self.assertEqual(float(row["price_over_reg"]), under_rule["price_over_reg"])
            self.assertNotEqual(under_rule["price_over_reg"], under_default["price_over_reg"])


if __name__ == "__main__":
    unittest.main()
