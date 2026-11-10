"""Technical change and investment. Stage 2 tests the order of a plant, the construction lag
(A4) and the diffusion of a design (A9); stage 3d adds the draws and the two investment rules."""
import unittest

from helpers import add_firm, cash_total, empty_industry
from markets.plant_market import buy_plant
from model.entities import Technique
from model.outputs import flows
from model.scheduler import start_period


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
