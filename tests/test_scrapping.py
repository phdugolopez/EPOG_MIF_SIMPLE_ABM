"""Scrapping. Stage 2 tests the depreciation reserve of a plant that leaves, under the three
levels of the option `reserve`; stage 3c adds the three reasons for which a plant leaves."""
import unittest

from equations.scrapping_reserve import reserve_released
from helpers import add_firm, cash_total, empty_industry, tallied
from markets.plant_market import remove_plant

COST = 137.5 * 20.0     # a plant of C at the default rate
RBAR = 0.16


class TestReserveRule(unittest.TestCase):
    def test_conditional_released_when_new_plants_earn_the_general_rate(self):
        self.assertTrue(reserve_released("conditional", 0.20, RBAR))
        self.assertTrue(reserve_released("conditional", 0.16, RBAR))
        self.assertFalse(reserve_released("conditional", 0.1599, RBAR))
        self.assertFalse(reserve_released("conditional", -0.02, RBAR))

    def test_conditional_released_when_no_plant_is_in_the_window(self):
        self.assertTrue(reserve_released("conditional", None, RBAR))

    def test_always_and_never_do_not_read_the_rate_of_new_plants(self):
        for r_new in (None, -0.02, 0.1599, 0.16, 0.50):
            self.assertTrue(reserve_released("always", r_new, RBAR))
            self.assertFalse(reserve_released("never", r_new, RBAR))


class TestRemovePlant(unittest.TestCase):
    def leave(self, r_new, age=10, cash=5000.0, reason="age", reserve="conditional"):
        ind = empty_industry(reserve=reserve)
        firm = add_firm(ind, plants=2, age=age, cash=cash)
        ind.r_new = r_new
        remove_plant(ind, firm, firm.plants[0], reason)
        return ind, firm

    def test_reserve_released_joins_the_funds_and_moves_no_cash(self):
        for r_new in (0.16, 0.30, None):
            ind, firm = self.leave(r_new)
            self.assertEqual(len(firm.plants), 1)
            self.assertAlmostEqual(firm.funds, COST, places=9)
            self.assertEqual(firm.cash, 5000.0)
            self.assertEqual(tallied(ind, "cap_released", label="shaikh"), 20.0)
            self.assertEqual(tallied(ind, "withdrawn", label="shaikh"), 0.0)

    def test_reserve_withdrawn_is_paid_to_the_rest_of_the_economy(self):
        ind, firm = self.leave(0.10)
        self.assertEqual(len(firm.plants), 1)
        self.assertEqual(firm.funds, 0.0)
        self.assertAlmostEqual(firm.cash, 5000.0 - COST, places=9)
        self.assertAlmostEqual(ind.roe.cash, -5000.0 + COST, places=9)
        self.assertAlmostEqual(cash_total(ind), 0.0, places=9)
        self.assertAlmostEqual(tallied(ind, "withdrawn", label="shaikh"), COST, places=9)
        self.assertEqual(tallied(ind, "cap_released", label="shaikh"), 0.0)

    def test_a_firm_short_of_cash_pays_what_it_has(self):
        ind, firm = self.leave(0.10, cash=100.0)
        self.assertEqual(firm.cash, 0.0)
        self.assertEqual(firm.funds, 0.0)
        self.assertEqual(tallied(ind, "withdrawn", label="shaikh"), 100.0)
        self.assertAlmostEqual(cash_total(ind), 0.0, places=9)

    def test_a_plant_scrapped_early_releases_its_depreciation_and_writes_off_the_rest(self):
        for r_new, funds, cash in ((0.20, 0.3 * COST, 5000.0), (0.10, 0.0, 5000.0 - 0.3 * COST)):
            ind, firm = self.leave(r_new, age=3, reason="idle")
            self.assertAlmostEqual(firm.funds, funds, places=9)
            self.assertAlmostEqual(firm.cash, cash, places=9)
            self.assertAlmostEqual(firm.write_offs, 0.7 * COST, places=9)

    def test_always_adds_the_reserve_to_the_funds_whatever_the_rate_of_new_plants(self):
        for r_new in (None, -0.05, 0.10, 0.16, 0.30):
            ind, firm = self.leave(r_new, reserve="always")
            self.assertAlmostEqual(firm.funds, COST, places=9)
            self.assertEqual(firm.cash, 5000.0)
            self.assertEqual(tallied(ind, "withdrawn"), 0.0)
            self.assertEqual(tallied(ind, "cap_released"), 20.0)

    def test_never_pays_the_reserve_out_whatever_the_rate_of_new_plants(self):
        for r_new in (None, -0.05, 0.10, 0.16, 0.30):
            ind, firm = self.leave(r_new, reserve="never")
            self.assertEqual(firm.funds, 0.0)
            self.assertAlmostEqual(firm.cash, 5000.0 - COST, places=9)
            self.assertAlmostEqual(tallied(ind, "withdrawn"), COST, places=9)
            self.assertEqual(tallied(ind, "cap_released"), 0.0)
            self.assertAlmostEqual(cash_total(ind), 0.0, places=9)

    def test_never_pays_as_far_as_cash_allows(self):
        ind, firm = self.leave(0.30, cash=100.0, reserve="never")
        self.assertEqual(firm.cash, 0.0)
        self.assertEqual(tallied(ind, "withdrawn"), 100.0)

    def test_the_tally_counts_the_capacity_that_leaves_by_reason(self):
        for reason in ("age", "cost", "idle"):
            ind, firm = self.leave(0.20, reason=reason)
            self.assertEqual(tallied(ind, "cap_retired", label="shaikh"), 20.0)
            self.assertEqual(tallied(ind, "cap_retired_" + reason, label="shaikh"), 20.0)
            by_reason = sum(tallied(ind, "cap_retired_" + other)
                            for other in ("age", "cost", "idle"))
            self.assertEqual(by_reason, 20.0)
            self.assertEqual(tallied(ind, "cap_retired", label="okishio"), 0.0)

    def test_the_tally_is_kept_by_firm(self):
        ind = empty_industry()
        first, second = add_firm(ind, plants=2, age=10), add_firm(ind, plants=2, age=10)
        remove_plant(ind, first, first.plants[0], "age")
        remove_plant(ind, second, second.plants[0], "idle")
        remove_plant(ind, second, second.plants[0], "idle")
        self.assertEqual(tallied(ind, "cap_retired", firm=first), 20.0)
        self.assertEqual(tallied(ind, "cap_retired", firm=second), 40.0)
        self.assertEqual(tallied(ind, "cap_retired", label="shaikh"), 60.0)
        self.assertEqual({flow.firm_id for flow in ind.tally}, {first.id, second.id})


if __name__ == "__main__":
    unittest.main()
