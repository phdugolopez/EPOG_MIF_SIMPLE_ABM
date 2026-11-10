"""Production and accounts. Stage 2 tests the payment function; stage 3c adds the merit
order with overtime, depreciation, dividends and the accounts identity."""
import unittest

from helpers import add_firm, cash_total, empty_industry
from markets.payments import pay


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


if __name__ == "__main__":
    unittest.main()
