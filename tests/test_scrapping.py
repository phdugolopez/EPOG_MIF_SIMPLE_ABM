"""Scrapping: the three reasons for which a plant leaves, and the depreciation reserve it
releases or loses under the three levels of the option `reserve`."""
import unittest

from equations.scrapping_below_cost import periods_below_cost, scrap_cost
from equations.scrapping_idle_plants import periods_idle
from equations.scrapping_reserve import reserve_released
from equations.scrapping_retirement import retirement_reason
from helpers import add_firm, cash_total, empty_industry, industry, tallied
from markets.plant_market import remove_plant
from model.scheduler import produce_and_account, scrap_plants

COST = 137.5 * 20.0     # a plant of C at the default rate
RBAR = 0.16


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
        self.assertEqual(tallied(ind, "cap_retired_age", label="shaikh"), 40.0)

    def test_a_plant_leaves_after_two_periods_with_the_price_below_its_operating_cost(self):
        ind, firm = self.firm(price=60.0)
        self.step(ind, firm, 0.0)
        self.assertEqual([plant.below_cost for plant in firm.plants], [1, 1])
        self.step(ind, firm, 0.0)
        self.assertEqual(firm.plants, [])
        self.assertEqual(tallied(ind, "cap_retired_cost", label="shaikh"), 40.0)

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
        self.assertEqual(tallied(ind, "cap_retired_idle", label="shaikh"), 20.0)

    def test_one_period_with_output_resets_the_idle_count(self):
        ind, firm = self.firm()
        self.step(ind, firm, 20.0)
        self.step(ind, firm, 30.0)
        self.step(ind, firm, 20.0)
        self.assertEqual(len(firm.plants), 2)

    def test_overtime_on_one_plant_leaves_the_other_idle(self):
        """Overtime starts only when every offered plant is full, so a plant is idle only if
        the firm sells no more than the normal capacity of the others."""
        ind, firm = self.firm()
        self.step(ind, firm, 20.0)
        self.step(ind, firm, 21.0)
        self.assertEqual([plant.output for plant in firm.plants], [20.0, 1.0])
        self.assertEqual([plant.idle for plant in firm.plants], [0, 0])

    def test_under_unit_cost_scrapping_the_price_must_cover_the_unit_cost(self):
        """At a price of 70 a plant of C covers its operating cost (64.25), not its unit cost
        (78): it runs, and leaves only under the unit-cost option."""
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

    def test_the_reserve_of_a_plant_that_leaves_follows_the_option(self):
        """A plant of age T leaves with a reserve equal to its cost, 2,750. The firm sold
        nothing, so its funds are the loss of 275, its last depreciation. No plant is left in
        the window of r_new: only `never` pays the reserve out."""
        cells = (("conditional", 2475.0, 20000.0), ("always", 2475.0, 20000.0),
                 ("never", -275.0, 17250.0))
        for reserve, funds, cash in cells:
            ind, firm = self.firm(plants=1, age=9, reserve=reserve)
            self.step(ind, firm, 0.0)
            self.assertEqual(firm.plants, [])
            self.assertIsNone(ind.r_new)
            self.assertAlmostEqual(firm.funds, funds, places=9, msg=reserve)
            self.assertAlmostEqual(firm.cash, cash, places=9, msg=reserve)


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
