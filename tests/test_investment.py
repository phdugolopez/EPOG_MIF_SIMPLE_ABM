"""Technical change and investment (A4, A7 to A9): the three draws, the two investment rules,
the depreciation reserve, the order of a plant, the construction lag and diffusion."""
import unittest

from equations.common_profit_rate import profit_rate_at_price
from equations.common_unit_cost import unit_cost
from equations.investment_accelerator import plants_wanted
from equations.investment_draw_categories import draw_categories
from equations.investment_draw_marx import draw_marx
from equations.investment_draw_neutral import draw_neutral
from equations.investment_retained_earnings import plants_affordable
from helpers import add_firm, cash_total, empty_industry
from markets.plant_market import buy_plant
from model.entities import Technique
from model.outputs import flows
from model.scheduler import invest, produce_and_account, scrap_plants, start_period

C, D1, D2 = 137.5 * 20.0, 142.31 * 20.0, 157.89 * 20.0      # cost of a plant


class TestDraws(unittest.TestCase):
    def test_marx_cuts_operating_cost_and_raises_capital(self):
        ucs, kappa = draw_marx(60.0, 150.0, 1.0, 0.0, 0.05, 1.5, 0.8)
        self.assertAlmostEqual(ucs, 57.0, places=12)
        self.assertAlmostEqual(kappa, 161.25, places=12)

    def test_marx_without_bias_leaves_capital_unchanged(self):
        for z in (-2.0, 0.0, 2.0):
            self.assertEqual(draw_marx(60.0, 150.0, 0.5, z, 0.05, 0.0, 0.8), (58.5, 150.0))

    def test_neutral_directions(self):
        dearer = draw_neutral(60.0, 150.0, 1.0, 0.0, 0.05)
        heavier = draw_neutral(60.0, 150.0, 1.0, 0.25, 0.05)
        cheaper = draw_neutral(60.0, 150.0, 1.0, 0.5, 0.05)
        for got, expected in zip(dearer + heavier + cheaper, (63.0, 150.0, 60.0, 157.5, 57.0, 150.0)):
            self.assertAlmostEqual(got, expected, places=9)

    def test_categories_both_rules_adopt_or_only_the_unit_cost_rule(self):
        old = (64.25, 137.5)
        for u_cat, rate_rises in ((0.9, True), (0.1, False)):
            for u_b in (0.2, 0.8):
                new = draw_categories(*old, 0.1, 100.0, u_cat, 0.7, u_b, 0.05, 0.5)
                self.assertLess(unit_cost(*new, 0.1), unit_cost(*old, 0.1))
                self.assertEqual(profit_rate_at_price(100.0, *new, 0.1)
                                 > profit_rate_at_price(100.0, *old, 0.1), rate_rises)

    def test_categories_without_a_margin_have_no_conflict_zone(self):
        old = (64.25, 137.5)
        new = draw_categories(*old, 0.1, 78.0, 0.1, 0.7, 0.5, 0.05, 0.5)
        self.assertLess(unit_cost(*new, 0.1), unit_cost(*old, 0.1))
        self.assertGreater(profit_rate_at_price(78.0, *new, 0.1), profit_rate_at_price(78.0, *old, 0.1))


class TestInvestmentRules(unittest.TestCase):
    def test_retained_earnings_buy_whole_plants(self):
        self.assertEqual(plants_affordable(5500.0, 2750.0), 2)
        self.assertEqual(plants_affordable(5499.0, 2750.0), 1)
        self.assertEqual(plants_affordable(2749.0, 2750.0), 0)
        self.assertEqual(plants_affordable(-10.0, 2750.0), 0)

    def test_rounding_dust_does_not_cost_a_plant(self):
        self.assertEqual(plants_affordable(2750.0 - 1e-12, 2750.0), 1)

    def test_the_accelerator_wants_the_plants_missing_at_the_target_utilisation(self):
        self.assertEqual(plants_wanted(100.0, 0.9, 80.0, 0.0, 20.0), 2)       # 111.1 - 80 = 31.1
        self.assertEqual(plants_wanted(100.0, 0.9, 80.0, 20.0, 20.0), 1)      # plants on order count
        self.assertEqual(plants_wanted(100.0, 0.9, 120.0, 0.0, 20.0), 0)
        self.assertEqual(plants_wanted(90.0, 0.9, 60.0, 0.0, 20.0), 2)        # exactly 40 missing


class TestInvest(unittest.TestCase):
    def firm(self, label="shaikh", price=100.0, funds=6000.0, cash=10000.0, plants=4, **overrides):
        overrides.setdefault("tech_change", "none")
        ind = empty_industry(**overrides)
        firm = add_firm(ind, label, plants=plants, price=price, cash=cash)
        firm.funds, firm.active = funds, True
        ind.reg_price = 82.8935
        return ind, firm

    def test_unit_cost_firm_buys_the_lowest_unit_cost_its_funds_pay_for(self):
        ind, firm = self.firm()
        invest(ind)
        self.assertEqual([q.technique.name for q in firm.pending_plants], ["D2"])
        self.assertEqual(firm.hurdle, 0.0)
        self.assertAlmostEqual(firm.funds, 6000.0 - D2, places=9)
        self.assertAlmostEqual(firm.cash, 10000.0 - D2, places=9)
        self.assertEqual(flows(ind, "shaikh")["orders_dearer"], 0.0)

    def test_profit_rate_firm_buys_the_highest_rate_at_its_price(self):
        ind, firm = self.firm("okishio")
        invest(ind)
        self.assertEqual([q.technique.name for q in firm.pending_plants], ["D1", "D1"])
        self.assertAlmostEqual(firm.hurdle, (100.0 - 76.001) / 142.31, places=12)
        self.assertEqual(flows(ind, "okishio")["orders_dearer"], 2.0)

    def test_below_85_the_two_rules_buy_the_same_technique(self):
        ind, firm = self.firm("okishio", price=80.0)
        invest(ind)
        self.assertEqual([q.technique.name for q in firm.pending_plants], ["D2"])
        self.assertEqual(flows(ind, "okishio")["orders_dearer"], 0.0)

    def test_at_lambda_one_the_profit_rate_firm_judges_at_the_price_of_production(self):
        ind, firm = self.firm("okishio", lam=1.0)
        invest(ind)
        self.assertEqual([q.technique.name for q in firm.pending_plants], ["D2"])
        self.assertAlmostEqual(firm.hurdle, 0.05, places=9)

    def test_funds_are_spent_only_as_far_as_they_are_in_cash(self):
        ind, firm = self.firm(funds=10000.0, cash=4000.0)
        invest(ind)
        self.assertEqual(len(firm.pending_plants), 1)
        self.assertGreaterEqual(firm.cash, 0.0)

    def test_negative_funds_buy_nothing(self):
        ind, firm = self.firm(funds=-500.0)
        invest(ind)
        self.assertEqual(firm.pending_plants, [])

    def test_the_accelerator_is_capped_by_cash_not_by_funds(self):
        for cash, bought in ((20000.0, 2), (4000.0, 1), (1000.0, 0)):
            ind, firm = self.firm(funds=-500.0, cash=cash, investment="accelerator")
            firm.notional = 100.0                    # 4 plants = 80; 100 / 0.9 = 111.1
            invest(ind)
            self.assertEqual(len(firm.pending_plants), bought)

    def test_the_accelerator_orders_nothing_when_capacity_is_enough(self):
        ind, firm = self.firm(investment="accelerator")
        firm.notional = 70.0
        invest(ind)
        self.assertEqual(firm.pending_plants, [])


class TestTechnicalChange(unittest.TestCase):
    def firm(self, label="shaikh", active=True, **overrides):
        overrides.setdefault("draw_prob", 1.0)
        ind = empty_industry(**overrides)
        firm = add_firm(ind, label, plants=4, price=100.0)
        firm.active = active
        ind.reg_price = 82.8935
        return ind, firm

    def test_an_active_firm_draws_from_its_best_technique_and_keeps_what_its_rule_prefers(self):
        ind, firm = self.firm(bias=0.0)              # pure operating-cost cut: both rules keep it
        invest(ind)
        design = firm.known[0]
        self.assertEqual((flows(ind, "shaikh")["drawn"], flows(ind, "shaikh")["kept"]), (1.0, 1.0))
        self.assertEqual(design.kappa, 157.89)       # drawn from D2, the lowest unit cost
        self.assertLess(design.ucs, 59.21)
        self.assertEqual(design.name, "0.0")
        self.assertIsNone(design.first_run)
        self.assertNotIn(design, ind.public)

    def test_a_firm_that_was_not_active_does_not_draw(self):
        ind, firm = self.firm(active=False)
        invest(ind)
        self.assertEqual(flows(ind, "shaikh")["drawn"], 0.0)

    def test_without_technical_change_no_firm_draws(self):
        ind, firm = self.firm(tech_change="none")
        invest(ind)
        self.assertEqual(flows(ind, "shaikh")["drawn"], 0.0)
        self.assertEqual(firm.known, [])

    def test_a_design_that_ties_is_not_kept(self):
        ind, firm = self.firm(design_step=0.0)
        invest(ind)
        self.assertEqual((flows(ind, "shaikh")["drawn"], flows(ind, "shaikh")["kept"]), (1.0, 0.0))
        self.assertEqual(firm.known, [])

    def test_a_design_that_raises_the_unit_cost_is_not_kept(self):
        ind, firm = self.firm(bias=50.0, bias_spread=0.0)
        invest(ind)
        self.assertEqual(flows(ind, "shaikh")["kept"], 0.0)

    def test_a_conflict_design_is_kept_by_the_unit_cost_rule_only(self):
        for label, share, kept in (("shaikh", 1.0, 1.0), ("okishio", 1.0, 0.0),
                                   ("shaikh", 0.0, 1.0), ("okishio", 0.0, 1.0)):
            ind, firm = self.firm(label, tech_change="categories", conflict_share=share)
            invest(ind)
            self.assertEqual(flows(ind, label)["kept"], kept, (label, share))

    def test_the_firm_buys_the_design_it_has_just_kept(self):
        ind, firm = self.firm(bias=0.0)
        firm.cash = firm.funds = 20000.0
        ind.roe.cash = -20000.0
        invest(ind)
        self.assertTrue(all(q.technique is firm.known[0] for q in firm.pending_plants))
        self.assertGreater(len(firm.pending_plants), 0)

    def test_a_firm_takes_five_numbers_a_period_whatever_it_draws(self):
        """Q9: the stream is at the same place after three periods with or without a design."""
        after = []
        for overrides in ({"tech_change": "none"}, {"draw_prob": 1.0}, {"tech_change": "neutral"},
                          {"tech_change": "categories", "draw_prob": 0.5}):
            ind, firm = self.firm(**overrides)
            for _ in range(3):
                invest(ind)
            after.append(firm.rng.random())
        self.assertEqual(len(set(after)), 1)


class TestReserve(unittest.TestCase):
    def last_period_of_a_plant(self, rival_price):
        """A firm sells the output of its one plant, aged 9, at its unit cost: no profit. Its
        cash is the depreciation accumulated on the plant. A rival's new plant sets r_new."""
        ind = empty_industry(menu=(("C", 64.25, 137.5),), tech_change="none")
        firm = add_firm(ind, plants=1, age=9, price=78.0, cash=0.9 * C)
        rival = add_firm(ind, "okishio", plants=1, age=0, price=rival_price)
        firm.sales = rival.sales = 20.0
        produce_and_account(ind)
        scrap_plants(ind)
        invest(ind)
        return ind, firm

    def test_with_r_new_above_rbar_a_firm_with_no_profit_replaces_its_plant(self):
        ind, firm = self.last_period_of_a_plant(rival_price=100.0)       # r_new = 0.16
        self.assertAlmostEqual(firm.profit, 0.0, places=9)
        self.assertEqual(firm.plants, [])
        self.assertEqual(len(firm.pending_plants), 1)
        self.assertAlmostEqual(firm.cash, 0.0, places=6)
        self.assertAlmostEqual(firm.funds, 0.0, places=6)
        self.assertAlmostEqual(cash_total(ind), 0.0, places=6)

    def test_with_r_new_below_rbar_the_reserve_is_paid_out_and_the_plant_is_not_replaced(self):
        ind, firm = self.last_period_of_a_plant(rival_price=80.0)        # r_new = 0.0145
        self.assertEqual(firm.plants, [])
        self.assertEqual(firm.pending_plants, [])
        self.assertAlmostEqual(firm.cash, 0.0, places=6)
        self.assertAlmostEqual(firm.funds, 0.0, places=6)
        self.assertAlmostEqual(flows(ind, "shaikh")["withdrawn"], C, places=6)
        self.assertAlmostEqual(cash_total(ind), 0.0, places=6)


class TestBuyPlant(unittest.TestCase):
    def setUp(self):
        self.industry = empty_industry()
        self.firm = add_firm(self.industry, cash=10000.0)
        self.firm.funds = 4000.0
        self.d2 = self.industry.public[2]
        self.cost = self.d2.kappa * 20.0

    def test_the_firm_pays_now_and_its_funds_fall(self):
        buy_plant(self.industry, self.firm, self.d2, "ordered")
        self.assertAlmostEqual(self.firm.cash, 10000.0 - self.cost, places=9)
        self.assertAlmostEqual(self.firm.funds, 4000.0 - self.cost, places=9)
        self.assertAlmostEqual(self.industry.roe.cash, -10000.0 + self.cost, places=9)
        self.assertAlmostEqual(cash_total(self.industry), 0.0, places=9)

    def test_the_plant_is_new_and_on_order(self):
        buy_plant(self.industry, self.firm, self.d2, "ordered")
        plant = self.firm.pending_plants[0]
        self.assertIs(plant.technique, self.d2)
        self.assertEqual((plant.capacity, plant.age, plant.cost, plant.book_value),
                         (20.0, 0, self.cost, self.cost))
        self.assertEqual(self.firm.capacity, 20.0)

    def test_the_tally_separates_orders_from_entry(self):
        buy_plant(self.industry, self.firm, self.d2, "ordered")
        buy_plant(self.industry, self.firm, self.d2, "entry")
        out = flows(self.industry, "shaikh")
        self.assertEqual((out["cap_ordered"], out["cap_entry"], out["orders"]), (20.0, 20.0, 2.0))

    def test_a_plant_ordered_in_t_is_in_operation_from_t_plus_1(self):
        buy_plant(self.industry, self.firm, self.d2, "ordered")
        self.assertEqual(len(self.firm.plants), 1)
        self.industry.time = 1
        start_period(self.industry)
        self.assertEqual(len(self.firm.plants), 2)
        self.assertEqual(self.firm.pending_plants, [])
        self.assertEqual(self.firm.capacity, 40.0)


class TestDiffusion(unittest.TestCase):
    def build_a_private_design(self, **overrides):
        """Firm 0 orders a plant of its own design in period 0, among two firms."""
        ind = empty_industry(**overrides)
        owner, rival = add_firm(ind, cash=10000.0), add_firm(ind, label="okishio")
        design = Technique("design", 55.0, 170.0)
        owner.known.append(design)
        buy_plant(ind, owner, design, "ordered")
        return ind, owner, design

    def step_to(self, ind, t):
        ind.time = t
        start_period(ind)

    def test_a_design_is_public_two_periods_after_its_first_plant_produces(self):
        ind, owner, design = self.build_a_private_design()
        self.assertIsNone(design.first_run)
        self.step_to(ind, 1)
        self.assertEqual(design.first_run, 1)
        self.assertIn(design, ind.waiting)
        self.step_to(ind, 2)
        self.assertNotIn(design, ind.public)
        self.assertIn(design, owner.known)
        self.step_to(ind, 3)
        self.assertIn(design, ind.public)
        self.assertNotIn(design, ind.waiting)
        self.assertNotIn(design, owner.known)
        self.assertEqual(len(ind.public), 4)

    def test_a_design_never_becomes_public_without_a_lag(self):
        ind, owner, design = self.build_a_private_design(public_lag=None)
        for t in range(1, 12):
            self.step_to(ind, t)
        self.assertNotIn(design, ind.public)
        self.assertIn(design, owner.known)

    def test_a_design_that_is_never_built_stays_private(self):
        ind = empty_industry()
        owner = add_firm(ind)
        design = Technique("design", 55.0, 170.0)
        owner.known.append(design)
        for t in range(1, 12):
            self.step_to(ind, t)
        self.assertNotIn(design, ind.public)
        self.assertIsNone(design.first_run)

    def test_an_initial_technique_is_not_made_public_twice(self):
        ind = empty_industry()
        firm = add_firm(ind, cash=10000.0)
        buy_plant(ind, firm, ind.public[1], "ordered")
        for t in range(1, 6):
            self.step_to(ind, t)
        self.assertEqual(len(ind.public), 3)
        self.assertEqual(ind.waiting, [])


if __name__ == "__main__":
    unittest.main()
