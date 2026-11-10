"""Production and accounts: the payment function, the merit order, depreciation, dividends,
money conservation and the identity between cash, funds and accumulated depreciation."""
import unittest
from math import fsum

from equations.accounts_depreciation import depreciation
from equations.accounts_dividends import dividends
from equations.accounts_merit_order import dispatch
from helpers import add_firm, cash_total, empty_industry, industry
from markets.payments import pay
from model.outputs import flows
from model.scheduler import period, produce_and_account

COST = 137.5 * 20.0     # a plant on C: ucs 64.25, unit cost 78


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
        outputs = dispatch([60.0, 50.0, 60.0], [3, 5, 1], [20.0, 20.0, 20.0], 30.0)
        self.assertEqual(outputs, [0.0, 20.0, 10.0])

    def test_output_is_the_quantity_and_no_plant_exceeds_its_capacity(self):
        for quantity in (0.0, 7.5, 20.0, 45.0, 60.0):
            outputs = dispatch([60.0, 50.0, 55.0], [0, 0, 0], [20.0, 20.0, 20.0], quantity)
            self.assertAlmostEqual(sum(outputs), quantity, places=12)
            self.assertLessEqual(max(outputs), 20.0)

    def test_depreciation_is_straight_line_and_stops_at_the_book_value(self):
        self.assertEqual(depreciation(COST, COST, 0.1), 275.0)
        self.assertEqual(depreciation(COST, 100.0, 0.1), 100.0)
        self.assertEqual(depreciation(COST, 0.0, 0.1), 0.0)

    def test_dividends_are_a_share_of_positive_profit(self):
        self.assertEqual(dividends(140.0, 0.5), 70.0)
        self.assertEqual(dividends(0.0, 0.5), 0.0)
        self.assertEqual(dividends(-50.0, 0.5), 0.0)


class TestProduceAndAccount(unittest.TestCase):
    def produce(self, price, sales, plants=2, age=0):
        ind = empty_industry()
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
        self.assertAlmostEqual(flows(ind, "shaikh")["dividends"], 36.25, places=9)
        self.assertAlmostEqual(firm.funds, 36.25, places=9)
        self.assertAlmostEqual(firm.cash, (85.0 - 64.25) * 30.0 - 36.25, places=9)
        self.assertAlmostEqual(cash_total(ind), 0.0, places=9)

    def test_a_loss_pays_no_dividend_and_lowers_the_funds(self):
        ind, firm = self.produce(price=70.0, sales=40.0)
        self.assertAlmostEqual(firm.profit, (70.0 - 78.0) * 40.0, places=9)
        self.assertEqual(flows(ind, "shaikh")["dividends"], 0.0)
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

    def test_a_firm_without_a_plant_keeps_its_utilisation_and_is_not_active(self):
        ind, firm = self.produce(price=85.0, sales=0.0, plants=0)
        self.assertEqual(firm.util, 1.0)
        self.assertFalse(firm.active)
        self.assertEqual(firm.profit, 0.0)


CELLS = [dict(population, investment=investment, rbar=rbar)
         for population in ({}, {"rule_okishio": "unit_cost"}, {"rule_shaikh": "profit_rate"})
         for investment in ("retained", "accelerator") for rbar in (0.05, 0.16)]


class TestMoney(unittest.TestCase):
    def test_money_is_conserved_and_no_cash_is_negative(self):
        """50 periods in the three populations, under both investment rules and both rates."""
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
