"""Production and accounts: the brief's tests (1)-(6)."""

import unittest

from equations.depreciation import depreciation, depreciation_by_use
from model.scheduler import allocate_demand, produce_and_account, scrap_plants, start_period
from helpers import history_without_labels, make_config, one_firm_industry, swapped_config
from model import Industry


class TestAccounts(unittest.TestCase):
    def test_profit_rate_at_normal_output_equals_shaikh_table(self):
        """(1) At normal output with no debt, r = (p - uc) / kappa."""
        for technique, expected in (("C", 0.16), ("D1", 24 / (18_500 / 130)),
                                    ("D2", 25 / (21_000 / 133))):
            industry = one_firm_industry(technique, DEMAND_TO_CAPACITY=1.0)
            start_period(industry)  # price stays at 100: pricing is not run
            allocate_demand(industry)
            produce_and_account(industry)
            firm = industry.firms[0]
            self.assertAlmostEqual(firm.util, 1.0)
            self.assertAlmostEqual(firm.profit_rate, expected, places=12)
        self.assertAlmostEqual(expected, 0.1583, places=4)

    def test_net_worth_identity_every_period(self):
        """(2) The change in net worth equals profit minus dividends minus write-offs."""
        industry = Industry(make_config(INITIAL_DEBT=2_000.0))
        for _ in range(30):
            industry.step()  # check_stock_flow raises otherwise
        for firm in industry.firms:
            self.assertAlmostEqual(
                firm.net_worth - firm.net_worth_start,
                firm.profit - firm.dividends - firm.write_offs + firm.equity_in,
            )

    def test_transaction_flow_matrix_sums_to_zero(self):
        """(3) Every row of the transaction-flow matrix sums to zero."""
        industry = Industry(make_config(INITIAL_DEBT=2_000.0))
        industry.run(30)
        self.assertTrue(industry.flow_history)
        for row in industry.flow_history:
            self.assertAlmostEqual(row["firms"] + row["roe"], 0.0, places=6)

    def test_depreciation_adds_up_to_purchase_cost(self):
        """(4) Depreciation charges sum to the purchase cost; book value is 0 at age T."""
        kappa, capacity, delta = 137.5, 120.0, 0.10
        book, charges = kappa * capacity, 0.0
        for _ in range(10):
            dep = depreciation(kappa, capacity, delta, book)
            book -= dep
            charges += dep
        self.assertAlmostEqual(charges, kappa * capacity)
        self.assertAlmostEqual(book, 0.0)
        self.assertEqual(depreciation(kappa, capacity, delta, book), 0.0)

    def test_firm_without_sales_loses_depreciation_plus_interest(self):
        """(5) A firm without sales loses exactly depreciation plus interest."""
        industry = one_firm_industry("D2", INITIAL_DEBT=5_000.0, PLANT_SIZE=None)
        firm = industry.firms[0]
        firm.share = 0.0
        start_period(industry)
        produce_and_account(industry)  # demand is skipped: sales stay at zero
        expected = 0.10 * 21_000.0 + 0.05 * 5_000.0
        self.assertAlmostEqual(firm.profit, -expected)

    def test_label_swap_changes_nothing(self):
        """(6) Swapping the type labels changes nothing."""
        a = Industry(make_config())
        b = Industry(swapped_config())
        a.run(30)
        b.run(30)
        self.assertEqual(history_without_labels(a), history_without_labels(b))


class TestDepreciationByUse(unittest.TestCase):
    """DEPRECIATION = "use": delta kappa x_v instead of delta kappa qbar_v."""

    kappa, capacity, delta = 137.5, 120.0, 0.10

    def test_equals_straight_line_at_normal_output(self):
        book = self.kappa * self.capacity
        self.assertAlmostEqual(
            depreciation_by_use(self.kappa, self.capacity, self.delta, book),
            depreciation(self.kappa, self.capacity, self.delta, book),
        )

    def test_idle_plant_does_not_depreciate(self):
        book = self.kappa * self.capacity
        self.assertEqual(depreciation_by_use(self.kappa, 0.0, self.delta, book), 0.0)

    def test_charges_add_up_to_purchase_cost_over_lifetime_output(self):
        """At half output the plant is fully depreciated after 2T periods, not T; overtime
        output wears it faster; the book value never goes below zero."""
        for output, periods in ((self.capacity / 2, 20), (1.2 * self.capacity, 9)):
            book, charges = self.kappa * self.capacity, 0.0
            for _ in range(periods):
                dep = depreciation_by_use(self.kappa, output, self.delta, book)
                book -= dep
                charges += dep
            self.assertAlmostEqual(charges, self.kappa * self.capacity)
            self.assertAlmostEqual(book, 0.0)

    def test_firm_without_sales_loses_only_interest(self):
        industry = one_firm_industry(
            "D2", INITIAL_DEBT=5_000.0, PLANT_SIZE=None, DEPRECIATION="use"
        )
        firm = industry.firms[0]
        firm.share = 0.0
        start_period(industry)
        produce_and_account(industry)
        self.assertAlmostEqual(firm.depreciation, 0.0)
        self.assertAlmostEqual(firm.profit, -0.05 * 5_000.0)

    def test_profit_rate_at_normal_output_unchanged(self):
        """Test (1) holds under both rules: r = (p - uc) / kappa at normal output."""
        industry = one_firm_industry("C", DEMAND_TO_CAPACITY=1.0, DEPRECIATION="use")
        start_period(industry)
        allocate_demand(industry)
        produce_and_account(industry)
        self.assertAlmostEqual(industry.firms[0].profit_rate, 0.16, places=12)

    def test_plant_life_counts_normal_output_not_age(self):
        """With PLANT_LIFE, a plant run at half output lasts twice as long under "use"."""
        retired_at = {}
        for rule in ("time", "use"):
            industry = one_firm_industry(
                "C", DEMAND_TO_CAPACITY=0.5, PLANT_SIZE=None, PLANT_LIFE=10,
                IDLE_SCRAPPING=False, SCRAP_COST="operating_cost", REPLACEMENT=False,
                DEPRECIATION=rule,
            )
            plant = industry.firms[0].plants[0]
            for t in range(30):
                start_period(industry)
                allocate_demand(industry)
                produce_and_account(industry)
                scrap_plants(industry)
                if plant not in industry.firms[0].plants:
                    retired_at[rule] = plant.age
                    break
            self.assertAlmostEqual(plant.book_value, 0.0)  # retired fully depreciated
        self.assertEqual(retired_at, {"time": 10, "use": 20})

    def test_stock_flow_and_label_swap(self):
        a = Industry(make_config(DEPRECIATION="use", INITIAL_DEBT=2_000.0))
        b = Industry(swapped_config(DEPRECIATION="use", INITIAL_DEBT=2_000.0))
        a.run(60)  # check_stock_flow raises otherwise
        b.run(60)
        self.assertEqual(history_without_labels(a), history_without_labels(b))


if __name__ == "__main__":
    unittest.main()
