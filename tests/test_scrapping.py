"""Scrapping: the three reasons for which a plant leaves, and the depreciation reserve it
releases or loses (A7, A13 j)."""
import unittest

from equations.scrapping_below_cost import periods_below_cost, scrap_cost
from equations.scrapping_idle_plants import periods_idle
from equations.scrapping_reserve import reserve_released
from equations.scrapping_retirement import retirement_reason
from helpers import add_firm, cash_total, empty_industry, industry
from markets.plant_market import remove_plant
from model.outputs import flows
from model.scheduler import produce_and_account, scrap_plants

COST = 137.5 * 20.0     # a plant on C: ucs 64.25, unit cost 78


class TestRules(unittest.TestCase):
    def test_scrap_cost_is_the_operating_cost_or_the_unit_cost(self):
        self.assertEqual(scrap_cost(64.25, 137.5, 0.1, "operating_cost"), 64.25)
        self.assertEqual(scrap_cost(64.25, 137.5, 0.1, "unit_cost"), 78.0)

    def test_periods_below_cost_are_consecutive(self):
        self.assertEqual(periods_below_cost(0, 60.0, 64.25), 1)
        self.assertEqual(periods_below_cost(1, 60.0, 64.25), 2)
        self.assertEqual(periods_below_cost(1, 64.25, 64.25), 0)
        self.assertEqual(periods_below_cost(1, 70.0, 64.25), 0)

    def test_periods_idle_are_consecutive(self):
        self.assertEqual(periods_idle(0, 0.0), 1)
        self.assertEqual(periods_idle(1, 0.0), 2)
        self.assertEqual(periods_idle(1, 3.5), 0)

    def test_a_plant_leaves_by_age_then_cost_then_idleness(self):
        self.assertEqual(retirement_reason(10, 10, 0, 0, 2), "age")
        self.assertEqual(retirement_reason(10, 10, 2, 2, 2), "age")
        self.assertEqual(retirement_reason(4, 10, 2, 2, 2), "cost")
        self.assertEqual(retirement_reason(4, 10, 1, 2, 2), "idle")
        self.assertIsNone(retirement_reason(9, 10, 1, 1, 2))


class TestScrapPlants(unittest.TestCase):
    def firm(self, price=100.0, plants=2, age=0, **overrides):
        ind = empty_industry(**overrides)
        return ind, add_firm(ind, plants=plants, age=age, price=price, cash=20000.0)

    def step(self, ind, firm, sales):
        firm.sales = sales
        produce_and_account(ind)
        scrap_plants(ind)

    def test_a_plant_leaves_at_the_age_t(self):
        ind, firm = self.firm(age=8)
        self.step(ind, firm, 40.0)
        self.assertEqual(len(firm.plants), 2)
        self.step(ind, firm, 40.0)
        self.assertEqual(firm.plants, [])
        self.assertEqual(flows(ind, "shaikh")["cap_retired_age"], 40.0)

    def test_a_plant_leaves_after_two_periods_with_the_price_below_its_operating_cost(self):
        ind, firm = self.firm(price=60.0)
        self.step(ind, firm, 0.0)
        self.assertEqual([plant.below_cost for plant in firm.plants], [1, 1])
        self.step(ind, firm, 0.0)
        self.assertEqual(firm.plants, [])
        self.assertEqual(flows(ind, "shaikh")["cap_retired_cost"], 40.0)

    def test_one_period_above_the_cost_resets_the_count(self):
        ind, firm = self.firm(price=60.0)
        self.step(ind, firm, 0.0)
        firm.price = 70.0
        self.step(ind, firm, 40.0)
        firm.price = 60.0
        self.step(ind, firm, 0.0)
        self.assertEqual(len(firm.plants), 2)
        self.assertEqual([plant.below_cost for plant in firm.plants], [1, 1])

    def test_a_plant_leaves_after_two_periods_without_output(self):
        ind, firm = self.firm()
        self.step(ind, firm, 20.0)
        self.assertEqual([plant.idle for plant in firm.plants], [0, 1])
        self.step(ind, firm, 20.0)
        self.assertEqual(len(firm.plants), 1)
        self.assertEqual(flows(ind, "shaikh")["cap_retired_idle"], 20.0)

    def test_one_period_with_output_resets_the_idle_count(self):
        ind, firm = self.firm()
        self.step(ind, firm, 20.0)
        self.step(ind, firm, 30.0)
        self.step(ind, firm, 20.0)
        self.assertEqual(len(firm.plants), 2)

    def test_under_unit_cost_scrapping_the_price_must_cover_the_unit_cost(self):
        """At a price of 70 a plant on C covers its operating cost (64.25), not its unit cost
        (78): it runs, and leaves only under the unit-cost switch."""
        for rule, left in (("operating_cost", 2), ("unit_cost", 0)):
            ind, firm = self.firm(price=70.0, scrap_cost=rule)
            self.step(ind, firm, 40.0)
            self.step(ind, firm, 40.0)
            self.assertEqual(len(firm.plants), left, rule)

    def test_initial_plants_retire_on_the_dates_their_staggered_ages_give(self):
        """Without investment, a plant of initial age a leaves in period T - 1 - a."""
        ind = industry()
        left = {}
        for t in range(10):
            ind.time = t
            for firm in ind.firms:
                firm.sales = firm.capacity
            produce_and_account(ind)
            before = {firm.id: len(firm.plants) for firm in ind.firms}
            scrap_plants(ind)
            for firm in ind.firms:
                left.setdefault(firm.id, []).extend([t] * (before[firm.id] - len(firm.plants)))
        self.assertEqual(left[0], [1, 3, 4, 6, 8, 9])
        self.assertEqual(left[4], [1, 2, 4, 5, 7, 8, 9])
        self.assertTrue(all(firm.plants == [] for firm in ind.firms))


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
            self.assertEqual(flows(ind, "shaikh")["cap_released"], 20.0)
            self.assertEqual(flows(ind, "shaikh")["withdrawn"], 0.0)

    def test_reserve_withdrawn_is_paid_to_the_rest_of_the_economy(self):
        ind, firm = self.leave(0.01)
        self.assertEqual(len(firm.plants), 1)
        self.assertEqual(firm.funds, 0.0)
        self.assertAlmostEqual(firm.cash, 5000.0 - COST, places=9)
        self.assertAlmostEqual(ind.roe.cash, -5000.0 + COST, places=9)
        self.assertAlmostEqual(cash_total(ind), 0.0, places=9)
        self.assertAlmostEqual(flows(ind, "shaikh")["withdrawn"], COST, places=9)
        self.assertEqual(flows(ind, "shaikh")["cap_released"], 0.0)

    def test_a_firm_short_of_cash_pays_what_it_has(self):
        ind, firm = self.leave(0.01, cash=100.0)
        self.assertEqual(firm.cash, 0.0)
        self.assertEqual(firm.funds, 0.0)
        self.assertEqual(flows(ind, "shaikh")["withdrawn"], 100.0)
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
            out = flows(ind, "shaikh")
            self.assertEqual(out["cap_retired"], 20.0)
            self.assertEqual(out["cap_retired_" + reason], 20.0)
            self.assertEqual(sum(out["cap_retired_" + r] for r in ("age", "cost", "idle")), 20.0)
            self.assertEqual(flows(ind, "okishio")["cap_retired"], 0.0)


if __name__ == "__main__":
    unittest.main()
