"""Production and accounts: the payment function, the merit order with overtime,
depreciation, dividends, money conservation and the identity between cash, funds and
accumulated depreciation."""
import unittest
from dataclasses import replace
from math import fsum
from unittest import mock

from equations.accounts_depreciation import depreciation
from equations.accounts_dividends import dividends
from equations.accounts_merit_order import dispatch
from helpers import add_firm, cash_total, empty_industry, industry, tallied
from markets.payments import pay
from model.model import run
from model.scheduler import period, produce_and_account
from parameters import OPTIONS, Parameters

COST = 137.5 * 20.0     # a plant of C: operating cost 64.25, unit cost 78
SIZES = [20.0, 20.0, 20.0]


class TestPay(unittest.TestCase):
    def setUp(self):
        self.industry = empty_industry()
        self.firm = add_firm(self.industry, cash=500.0)

    def test_cash_moves_from_the_payer_to_the_payee(self):
        pay(self.firm, self.industry.roe, 120.0)
        self.assertEqual(self.firm.cash, 380.0)
        self.assertEqual(self.industry.roe.cash, -380.0)
        self.assertEqual(cash_total(self.industry), 0.0)

    def test_a_negative_payment_is_refused(self):
        with self.assertRaises(AssertionError):
            pay(self.firm, self.industry.roe, -1.0)


class TestRules(unittest.TestCase):
    def test_plants_run_cheapest_first_then_youngest(self):
        outputs = dispatch([60.0, 50.0, 60.0], [3, 5, 1], SIZES, 30.0, 1.2)
        self.assertEqual(outputs, [0.0, 20.0, 10.0])

    def test_output_is_the_quantity_and_no_plant_exceeds_its_limit(self):
        for quantity in (0.0, 7.5, 20.0, 45.0, 60.0, 66.0, 72.0):
            outputs = dispatch([60.0, 50.0, 55.0], [0, 0, 0], SIZES, quantity, 1.2)
            self.assertAlmostEqual(sum(outputs), quantity, places=12)
            self.assertLessEqual(max(outputs), 24.0)

    def test_every_plant_runs_to_normal_capacity_before_any_overtime(self):
        """The dearest plant is full before the cheapest works overtime."""
        self.assertEqual(dispatch([60.0, 50.0, 55.0], [0, 0, 0], SIZES, 55.0, 1.2),
                         [15.0, 20.0, 20.0])
        self.assertEqual(dispatch([60.0, 50.0, 55.0], [0, 0, 0], SIZES, 60.0, 1.2),
                         [20.0, 20.0, 20.0])

    def test_overtime_runs_in_the_same_order(self):
        self.assertEqual(dispatch([60.0, 50.0, 55.0], [0, 0, 0], SIZES, 63.0, 1.2),
                         [20.0, 23.0, 20.0])
        self.assertEqual(dispatch([60.0, 50.0, 55.0], [0, 0, 0], SIZES, 66.0, 1.2),
                         [20.0, 24.0, 22.0])
        self.assertEqual(dispatch([60.0, 60.0], [4, 1], [20.0, 20.0], 43.0, 1.2), [20.0, 23.0])

    def test_output_stops_at_u_max_times_capacity(self):
        outputs = dispatch([60.0, 50.0, 55.0], [0, 0, 0], SIZES, 100.0, 1.2)
        self.assertEqual(outputs, [24.0, 24.0, 24.0])
        self.assertEqual(dispatch([60.0], [0], [20.0], 100.0, 1.4), [28.0])

    def test_without_overtime_output_stops_at_normal_capacity(self):
        self.assertEqual(dispatch([60.0, 50.0, 55.0], [0, 0, 0], SIZES, 100.0, 1.0), SIZES)
        self.assertEqual(dispatch([60.0, 50.0, 55.0], [0, 0, 0], SIZES, 30.0, 1.0),
                         [0.0, 20.0, 10.0])

    def test_depreciation_is_straight_line_and_stops_at_the_book_value(self):
        self.assertEqual(depreciation(COST, COST, 0.1), 275.0)
        self.assertEqual(depreciation(COST, 100.0, 0.1), 100.0)
        self.assertEqual(depreciation(COST, 0.0, 0.1), 0.0)

    def test_dividends_are_a_share_of_positive_profit(self):
        self.assertEqual(dividends(140.0, 0.5), 70.0)
        self.assertEqual(dividends(0.0, 0.5), 0.0)
        self.assertEqual(dividends(-50.0, 0.5), 0.0)


class TestProduceAndAccount(unittest.TestCase):
    def produce(self, price, sales, plants=2, age=0, **overrides):
        ind = empty_industry(**overrides)
        firm = add_firm(ind, plants=plants, age=age, price=price)
        firm.sales = sales
        produce_and_account(ind)
        return ind, firm

    def test_profit_is_revenue_less_operating_cost_less_depreciation(self):
        ind, firm = self.produce(price=85.0, sales=30.0)
        self.assertEqual([plant.output for plant in firm.plants], [20.0, 10.0])
        self.assertAlmostEqual(firm.plants[0].profit, 140.0, places=9)
        self.assertAlmostEqual(firm.plants[1].profit, -67.5, places=9)
        self.assertAlmostEqual(firm.profit, 72.5, places=9)

    def test_half_of_a_positive_profit_is_paid_out_and_half_joins_the_funds(self):
        ind, firm = self.produce(price=85.0, sales=30.0)
        self.assertAlmostEqual(tallied(ind, "dividends", firm=firm), 36.25, places=9)
        self.assertAlmostEqual(firm.funds, 36.25, places=9)
        self.assertAlmostEqual(firm.cash, (85.0 - 64.25) * 30.0 - 36.25, places=9)
        self.assertAlmostEqual(cash_total(ind), 0.0, places=9)

    def test_a_loss_pays_no_dividend_and_lowers_the_funds(self):
        ind, firm = self.produce(price=70.0, sales=40.0)
        self.assertAlmostEqual(firm.profit, (70.0 - 78.0) * 40.0, places=9)
        self.assertEqual(tallied(ind, "dividends", firm=firm), 0.0)
        self.assertAlmostEqual(firm.funds, -320.0, places=9)
        self.assertAlmostEqual(firm.cash, (70.0 - 64.25) * 40.0, places=9)

    def test_every_plant_ages_and_depreciates_with_or_without_output(self):
        ind, firm = self.produce(price=85.0, sales=20.0)
        self.assertEqual([plant.output for plant in firm.plants], [20.0, 0.0])
        self.assertEqual([plant.age for plant in firm.plants], [1, 1])
        for plant in firm.plants:
            self.assertAlmostEqual(plant.book_value, COST - 275.0, places=9)
        self.assertAlmostEqual(firm.plants[1].profit, -275.0, places=9)

    def test_book_value_is_zero_after_the_plant_life(self):
        ind = empty_industry()
        firm = add_firm(ind, plants=1, price=85.0)
        for _ in range(10):
            firm.sales = 20.0
            produce_and_account(ind)
        self.assertAlmostEqual(firm.plants[0].book_value, 0.0, places=9)
        self.assertEqual(firm.plants[0].age, 10)

    def test_utilisation_is_sales_over_capacity(self):
        ind, firm = self.produce(price=85.0, sales=30.0)
        self.assertEqual(firm.util, 0.75)
        self.assertTrue(firm.active)

    def test_with_overtime_utilisation_passes_one(self):
        ind, firm = self.produce(price=85.0, sales=46.0)
        self.assertEqual([plant.output for plant in firm.plants], [24.0, 22.0])
        self.assertEqual(firm.util, 1.15)
        self.assertAlmostEqual(firm.profit, (85.0 - 64.25) * 46.0 - 550.0, places=9)
        self.assertAlmostEqual(ind.rows[0]["overtime"], 6.0, places=9)
        self.assertEqual(ind.rows[1]["overtime"], 0.0)

    def test_overtime_has_the_same_operating_cost_and_no_more_depreciation(self):
        normal, firm_normal = self.produce(price=85.0, sales=20.0, plants=1)
        over, firm_over = self.produce(price=85.0, sales=24.0, plants=1)
        self.assertAlmostEqual(firm_over.profit - firm_normal.profit, (85.0 - 64.25) * 4.0,
                               places=9)
        self.assertEqual(firm_over.plants[0].book_value, firm_normal.plants[0].book_value)

    def test_a_plant_that_was_not_offered_does_not_run(self):
        """Decision 18: at a price of 62 the plant of C (64.25) is not offered at step 2, so
        it has no output at step 3 and the plant of D2 (59.21) works overtime instead."""
        ind = empty_industry()
        firm = add_firm(ind, plants=1, price=62.0, technique=ind.public[2])
        dear = add_firm(ind, plants=1, price=62.0)
        firm.plants.append(dear.plants.pop())
        ind.firms.remove(dear)
        firm.sales = 24.0
        produce_and_account(ind)
        self.assertEqual([plant.output for plant in firm.plants], [24.0, 0.0])
        self.assertEqual([plant.age for plant in firm.plants], [1, 1])
        self.assertAlmostEqual(firm.plants[1].profit, -275.0, places=9)
        self.assertEqual(firm.util, 0.6)

    def test_a_firm_without_a_plant_keeps_its_utilisation_and_is_not_active(self):
        ind, firm = self.produce(price=85.0, sales=0.0, plants=0)
        self.assertEqual(firm.util, 1.0)
        self.assertFalse(firm.active)
        self.assertEqual(firm.profit, 0.0)


def dispatch_without_overtime(ucs, ages, capacity, quantity, u_max):
    """Version 3's merit order: one round, each plant up to its normal capacity."""
    outputs = [0.0] * len(ucs)
    for i in sorted(range(len(ucs)), key=lambda i: (ucs[i], ages[i])):
        outputs[i] = min(capacity[i], quantity)
        quantity -= outputs[i]
    return outputs


class TestNoOvertime(unittest.TestCase):
    def test_u_max_of_one_gives_the_run_without_overtime_row_for_row(self):
        for overrides in ({}, {"rule_okishio": "unit_cost"}, {"pricing": "universal"}):
            params = replace(Parameters(), periods=80, u_max=1.0, **overrides)
            rows = run(params, seed=3).rows
            with mock.patch("model.scheduler.dispatch", dispatch_without_overtime):
                self.assertEqual(run(params, seed=3).rows, rows, overrides)
            self.assertEqual({row["overtime"] for row in rows}, {0.0})

    def test_no_firm_works_above_its_limit_in_a_run(self):
        for u_max in (1.0, 1.2, 1.4):
            ind = industry(seed=2, u_max=u_max)
            for _ in range(60):
                period(ind)
                for firm in ind.firms:
                    for plant in firm.plants:
                        self.assertLessEqual(plant.output, u_max * plant.capacity + 1e-9)


POPULATIONS = ({}, {"rule_okishio": "unit_cost"}, {"rule_shaikh": "profit_rate"})
CELLS = ([dict(population, pricing=pricing, investment=investment)
          for population in POPULATIONS
          for pricing in OPTIONS["pricing"]
          for investment in OPTIONS["investment"]]
         + [dict(population, rbar=rbar) for population in POPULATIONS for rbar in (0.10, 0.05)])


class TestMoney(unittest.TestCase):
    def test_money_is_conserved_and_no_cash_is_negative(self):
        """50 periods in the three populations, under the four price rules and both
        investment rules, and at the two other general rates."""
        for overrides in CELLS:
            ind = industry(seed=1, **overrides)
            for _ in range(50):
                period(ind)
                self.assertLess(abs(cash_total(ind)), 1e-6 + 1e-9 * abs(ind.roe.cash), overrides)
                self.assertTrue(all(firm.cash > -1e-6 for firm in ind.firms), overrides)

    def test_cash_less_funds_is_the_depreciation_accumulated_on_the_plants(self):
        """Never below it, and equal to it for a firm whose funds were never negative: only
        such a firm can lack the cash for a withdrawal. So funds never exceed cash."""
        for overrides in CELLS:
            ind = industry(seed=2, **overrides)
            negative = set()
            for _ in range(50):
                period(ind)
                for firm in ind.firms:
                    reserve = fsum(plant.cost - plant.book_value for plant in firm.plants)
                    gap = firm.cash - firm.funds - reserve
                    self.assertGreater(gap, -1e-6, overrides)
                    self.assertLess(firm.funds, firm.cash + 1e-6, overrides)
                    if firm.funds < 0.0:
                        negative.add(firm.id)
                    if firm.id not in negative:
                        self.assertLess(gap, 1e-6, overrides)


if __name__ == "__main__":
    unittest.main()
