"""Production and accounts: the brief's tests (1)-(6)."""

import unittest

from equations.depreciation import depreciation
from model.scheduler import allocate_demand, produce_and_account, start_period
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


if __name__ == "__main__":
    unittest.main()
