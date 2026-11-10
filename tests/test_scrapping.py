"""Scrapping. Stage 2 tests the depreciation reserve of a plant that leaves (A7, A13 j); stage 3c
adds the three reasons for which a plant leaves."""
import unittest

from equations.scrapping_reserve import reserve_released
from helpers import add_firm, cash_total, empty_industry
from markets.plant_market import remove_plant

COST = 137.5 * 20.0     # a plant on C


class TestReserveRule(unittest.TestCase):
    def test_released_when_new_plants_earn_the_general_rate(self):
        self.assertTrue(reserve_released(0.08, 0.05))
        self.assertTrue(reserve_released(0.05, 0.05))
        self.assertFalse(reserve_released(0.0499, 0.05))
        self.assertFalse(reserve_released(-0.02, 0.05))

    def test_released_when_no_plant_is_in_the_window(self):
        self.assertTrue(reserve_released(None, 0.05))


class TestRemovePlant(unittest.TestCase):
    def leave(self, r_new, age=10, cash=5000.0, reason="age"):
        ind = empty_industry()
        firm = add_firm(ind, plants=2, age=age, cash=cash)
        ind.r_new = r_new
        remove_plant(ind, firm, firm.plants[0], reason)
        return ind, firm

    def test_reserve_released_joins_the_funds_and_moves_no_cash(self):
        for r_new in (0.05, 0.20, None):
            ind, firm = self.leave(r_new)
            self.assertEqual(len(firm.plants), 1)
            self.assertAlmostEqual(firm.funds, COST, places=9)
            self.assertEqual(firm.cash, 5000.0)
            self.assertEqual(ind.tally["shaikh"]["cap_released"], 20.0)
            self.assertEqual(ind.tally["shaikh"]["withdrawn"], 0.0)

    def test_reserve_withdrawn_is_paid_to_the_rest_of_the_economy(self):
        ind, firm = self.leave(0.01)
        self.assertEqual(len(firm.plants), 1)
        self.assertEqual(firm.funds, 0.0)
        self.assertAlmostEqual(firm.cash, 5000.0 - COST, places=9)
        self.assertAlmostEqual(ind.roe.cash, -5000.0 + COST, places=9)
        self.assertAlmostEqual(cash_total(ind), 0.0, places=9)
        self.assertAlmostEqual(ind.tally["shaikh"]["withdrawn"], COST, places=9)
        self.assertEqual(ind.tally["shaikh"]["cap_released"], 0.0)

    def test_a_firm_short_of_cash_pays_what_it_has(self):
        ind, firm = self.leave(0.01, cash=100.0)
        self.assertEqual(firm.cash, 0.0)
        self.assertEqual(firm.funds, 0.0)
        self.assertEqual(ind.tally["shaikh"]["withdrawn"], 100.0)
        self.assertAlmostEqual(cash_total(ind), 0.0, places=9)

    def test_a_plant_scrapped_early_releases_its_depreciation_and_writes_off_the_rest(self):
        for r_new, funds, cash in ((0.08, 0.3 * COST, 5000.0), (0.01, 0.0, 5000.0 - 0.3 * COST)):
            ind, firm = self.leave(r_new, age=3, reason="idle")
            self.assertAlmostEqual(firm.funds, funds, places=9)
            self.assertAlmostEqual(firm.cash, cash, places=9)
            self.assertAlmostEqual(firm.write_offs, 0.7 * COST, places=9)

    def test_the_tally_counts_the_capacity_that_leaves_by_reason(self):
        for reason in ("age", "cost", "idle"):
            ind, firm = self.leave(0.08, reason=reason)
            flows = ind.tally["shaikh"]
            self.assertEqual(flows["cap_retired"], 20.0)
            self.assertEqual(flows["cap_retired_" + reason], 20.0)
            self.assertEqual(sum(flows["cap_retired_" + r] for r in ("age", "cost", "idle")), 20.0)
            self.assertEqual(ind.tally["okishio"]["cap_retired"], 0.0)


if __name__ == "__main__":
    unittest.main()
