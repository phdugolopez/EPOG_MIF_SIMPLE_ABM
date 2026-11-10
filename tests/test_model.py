"""The whole loop. Stage 2 tests the skeleton, in which the six steps are stubs: nothing
random happens yet, so "another seed, another table" comes with stage 4, with the label swap,
the decompositions of the run row and the run of every option."""
import unittest
from dataclasses import replace

from helpers import cash_total, industry
from model.model import build, run
from model.outputs import KEYS
from model.scheduler import STEPS, check, close_period, period
from parameters import Parameters

POPULATIONS = ({}, {"rule_okishio": "unit_cost"}, {"rule_shaikh": "profit_rate"})


class TestSteps(unittest.TestCase):
    def test_a_period_is_the_seven_steps_in_the_order_of_the_schedule(self):
        names = [step.__name__ for step in STEPS]
        self.assertEqual(names, ["start_period", "set_prices", "allocate_demand",
                                 "produce_and_account", "scrap_plants", "invest",
                                 "enter_and_exit"])

    def test_every_step_takes_the_industry_alone_and_has_a_docstring(self):
        ind = industry()
        for step in STEPS + (close_period,):
            self.assertIsNone(step(ind), step.__name__)
            self.assertIn("v4-final-model.md" if step in STEPS else "period", step.__doc__)

    def test_running_the_steps_by_hand_gives_the_table_of_a_run(self):
        """What the run viewer does: STEPS in order, then close_period."""
        for overrides in POPULATIONS:
            params = replace(Parameters(), periods=30, **overrides)
            by_hand = build(params, seed=2)
            for _ in range(params.periods):
                for step in STEPS:
                    step(by_hand)
                close_period(by_hand)
            self.assertEqual(by_hand.rows, run(params, seed=2).rows)
            self.assertEqual(by_hand.time, 30)


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

    def test_a_row_has_the_flows_of_the_tally_and_the_closing_stocks(self):
        row = run(replace(Parameters(), periods=1)).rows[0]
        for column in ("t", "label", "rule", "firms", "capacity", "share", "notional", "sales",
                       *KEYS,
                       "capacity_next", "share_end", "cash", "funds", "write_offs", "hurdle"):
            self.assertIn(column, row)
        self.assertEqual((row["rule"], row["firms"], row["capacity"]), ("unit_cost", 3, 380.0))

    def test_money_is_conserved(self):
        """In the three populations, and at the three general rates of E0r."""
        cells = POPULATIONS + ({"rbar": 0.10}, {"rbar": 0.05})
        for overrides in cells:
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

    def test_check_catches_a_negative_cash(self):
        ind = industry()
        period(ind)
        ind.firms[0].cash -= 10000.0
        ind.roe.cash += 10000.0
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

    def test_check_passes_on_an_industry_that_adds_up(self):
        ind = industry()
        period(ind)
        self.assertIsNone(check(ind))

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
        self.assertAlmostEqual(ind.reg_price, 100.2614, places=9)
        self.assertIsNotNone(ind.r_new)

    def test_the_regulating_price_is_the_same_at_every_rate_on_the_scaled_menu(self):
        for rbar in (0.10, 0.05):
            ind = industry(rbar=rbar)
            period(ind)
            self.assertEqual(ind.reg.name, "D2")
            self.assertAlmostEqual(ind.reg_price, 100.2614, places=9)

    def test_the_order_of_the_firms_does_not_matter(self):
        straight, reverse = industry(), industry()
        reverse.firms.reverse()
        for _ in range(20):
            period(straight)
            period(reverse)
        self.assertEqual(straight.rows, reverse.rows)


if __name__ == "__main__":
    unittest.main()
