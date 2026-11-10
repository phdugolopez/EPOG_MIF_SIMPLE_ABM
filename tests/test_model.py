"""The whole loop: reproducibility, the checks of every period, and the two decompositions of
the run row."""
import unittest
from dataclasses import replace
from unittest import mock

from experiments.summary import run_row
from helpers import cash_total, industry
from model.model import run
from model.scheduler import check, period
from parameters import Parameters

CELLS = ({}, {"rule_okishio": "unit_cost"}, {"rule_shaikh": "profit_rate"},
         {"pricing": "systematic", "investment": "accelerator", "rbar": 0.16, "growth": 0.01},
         {"tech_change": "categories"}, {"tech_change": "neutral"}, {"tech_change": "none"},
         {"scrap_cost": "unit_cost"}, {"public_lag": None}, {"lam": 1.0}, {"firms_per_pair": 2})


class TestLoop(unittest.TestCase):
    def test_a_run_has_two_rows_a_period_and_passes_every_check(self):
        ind = run()
        self.assertEqual(ind.time, Parameters().periods)
        self.assertEqual(len(ind.rows), 2 * Parameters().periods)
        self.assertEqual([row["t"] for row in ind.rows[:4]], [0, 0, 1, 1])
        self.assertEqual([row["label"] for row in ind.rows[:2]], ["shaikh", "okishio"])

    def test_same_seed_same_table_another_seed_another_table(self):
        self.assertEqual(run(seed=3).rows, run(seed=3).rows)
        self.assertNotEqual(run(seed=3).rows, run(seed=4).rows)

    def test_a_run_at_the_defaults_ends_with_capacity(self):
        for seed in range(3):
            industry = run(seed=seed)
            row = run_row(industry.rows, industry.params, seed)
            self.assertGreater(row["capacity_end"], 0.0)
            self.assertIn(row["outcome"], ("win", "loss", "tie"))

    def test_every_switch_runs_and_passes_the_checks_of_every_period(self):
        for overrides in CELLS:
            with self.subTest(overrides=overrides):
                params = replace(Parameters(), periods=120, **overrides)
                self.assertEqual(len(run(params, seed=1).rows), 240)

    def test_the_terms_of_the_two_decompositions_sum_to_the_change_in_the_share(self):
        """Capacity share: ordered, retired, entry, exit. Sales share: price, entry and exit,
        rationing. Both residuals are zero up to rounding."""
        for overrides in CELLS[:5]:
            for seed in (0, 1):
                params = replace(Parameters(), **overrides)
                row = run_row(run(params, seed).rows, params, seed)
                self.assertLess(abs(row["dk_resid"]), 1e-9, (overrides, seed))
                self.assertLess(abs(row["ds_resid"]), 1e-9, (overrides, seed))

    def test_dropping_beaten_techniques_from_the_public_menu_changes_no_run(self):
        """The pruning of start_period is for speed only: without it the table is the same."""
        for overrides in CELLS[:6]:
            params = replace(Parameters(), periods=150, **overrides)
            pruned = run(params, seed=5).rows
            with mock.patch("model.scheduler.frontier", lambda menu, delta: menu):
                self.assertEqual(run(params, seed=5).rows, pruned, overrides)

    def test_every_row_has_the_same_columns(self):
        rows = run().rows
        self.assertTrue(all(list(row) == list(rows[0]) for row in rows))

    def test_money_is_conserved(self):
        for overrides in ({}, {"rule_okishio": "unit_cost"}, {"rule_shaikh": "profit_rate"}):
            ind = industry(**overrides)
            for _ in range(50):
                period(ind)
                self.assertLess(abs(cash_total(ind)), 1e-6 + 1e-9 * abs(ind.roe.cash))

    def test_check_catches_money_that_appears(self):
        ind = industry()
        period(ind)
        ind.firms[0].cash += 1.0
        with self.assertRaises(AssertionError):
            check(ind)

    def test_check_catches_shares_that_do_not_sum_to_one(self):
        ind = industry()
        period(ind)
        ind.firms[0].share += 0.01
        with self.assertRaises(AssertionError):
            check(ind)

    def test_check_catches_capacity_that_appears(self):
        ind = industry()
        period(ind)
        ind.firms[0].plants.append(ind.firms[0].plants[0])
        with self.assertRaises(AssertionError):
            check(ind)

    def test_demand_grows_at_the_rate_g(self):
        ind = industry(growth=0.01)
        for _ in range(10):
            period(ind)
        self.assertAlmostEqual(ind.demand, ind.demand_0 * 1.01 ** 9, places=9)

    def test_regulating_price_and_r_new_are_set_in_the_period(self):
        ind = industry()
        self.assertIsNone(ind.reg)
        period(ind)
        self.assertEqual(ind.reg.name, "D2")
        self.assertAlmostEqual(ind.reg_price, 82.8935, places=9)
        self.assertIsNotNone(ind.r_new)

    def test_the_order_of_the_firms_does_not_matter(self):
        straight, reverse = industry(), industry()
        reverse.firms.reverse()
        for _ in range(20):
            period(straight)
            period(reverse)
        self.assertEqual(straight.rows, reverse.rows)


if __name__ == "__main__":
    unittest.main()
