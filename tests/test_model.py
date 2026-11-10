"""The whole loop. Stage 2 tests the skeleton, in which the six steps are stubs: nothing random
happens yet, so "another seed, another table" comes with stage 4."""
import unittest

from helpers import cash_total, industry
from model.model import run
from model.scheduler import period
from parameters import Parameters


class TestLoop(unittest.TestCase):
    def test_a_run_has_two_rows_a_period_and_passes_every_check(self):
        ind = run()
        self.assertEqual(ind.time, Parameters().periods)
        self.assertEqual(len(ind.rows), 2 * Parameters().periods)
        self.assertEqual([row["t"] for row in ind.rows[:4]], [0, 0, 1, 1])
        self.assertEqual([row["label"] for row in ind.rows[:2]], ["shaikh", "okishio"])

    def test_same_seed_same_table(self):
        self.assertEqual(run(seed=3).rows, run(seed=3).rows)

    def test_every_row_has_the_same_columns(self):
        rows = run().rows
        self.assertTrue(all(list(row) == list(rows[0]) for row in rows))

    def test_money_is_conserved(self):
        for overrides in ({}, {"rule_okishio": "unit_cost"}, {"rule_shaikh": "profit_rate"}):
            ind = industry(**overrides)
            for _ in range(50):
                period(ind)
                self.assertLess(abs(cash_total(ind)), 1e-6)

    def test_check_catches_money_that_appears(self):
        ind = industry()
        ind.firms[0].cash += 1.0
        with self.assertRaises(AssertionError):
            period(ind)

    def test_check_catches_shares_that_do_not_sum_to_one(self):
        ind = industry()
        ind.firms[0].share += 0.01
        with self.assertRaises(AssertionError):
            period(ind)

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
