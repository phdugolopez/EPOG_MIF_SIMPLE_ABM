"""Demand: the brief's tests (1)-(5), plus the logit alternative."""

import random
import unittest

from equations.competitiveness import competitiveness
from equations.market_shares import logit_shares, replicator_shares
from markets.goods_market import allocate
from helpers import history_without_labels, make_config, swapped_config
from model import Industry


def replicate(shares, prices, chi=1.0):
    return replicator_shares(shares, [competitiveness(p) for p in prices], chi)


class TestDemand(unittest.TestCase):
    def test_shares_non_negative_and_sum_to_one(self):
        """(1) Even with strong selection and wide price gaps."""
        rng = random.Random(1)
        for _ in range(200):
            n = rng.randint(2, 8)
            shares = [rng.random() for _ in range(n)]
            shares = [s / sum(shares) for s in shares]
            prices = [rng.uniform(50, 150) for _ in range(n)]
            for new in (replicate(shares, prices, chi=20.0),
                        logit_shares(shares, prices, eta=20.0)):
                self.assertTrue(all(s >= 0.0 for s in new))
                self.assertAlmostEqual(sum(new), 1.0)

    def test_equal_prices_leave_shares_unchanged(self):
        """(2)"""
        shares = [0.5, 0.3, 0.2]
        for new in (replicate(shares, [97.0] * 3), logit_shares(shares, [97.0] * 3, 1.0)):
            for a, b in zip(new, shares):
                self.assertAlmostEqual(a, b)

    def test_two_percent_cheaper_gains_at_the_rate_chi_predicts(self):
        """(3) A small firm 2 % cheaper than average grows its share by about 2 % a period."""
        shares = [0.01, 0.99]
        new = replicate(shares, [98.0, 100.0], chi=1.0)
        growth = new[0] / shares[0] - 1.0
        self.assertAlmostEqual(growth, 0.02, delta=0.001)
        new = replicate(shares, [98.0, 100.0], chi=0.5)
        self.assertAlmostEqual(new[0] / shares[0] - 1.0, 0.01, delta=0.0005)

    def test_overflow_goes_to_others_and_no_unit_is_sold_twice(self):
        """(4)"""
        sales, unmet, unserved = allocate(
            demand=100.0, shares=[0.6, 0.2, 0.2], prices=[95.0, 100.0, 99.0],
            offered=[40.0, 30.0, 25.0],
        )
        self.assertAlmostEqual(unmet[0], 20.0)
        self.assertEqual(sales[0], 40.0)
        self.assertAlmostEqual(sales[2], 25.0)  # cheapest with spare capacity fills first
        self.assertAlmostEqual(sales[1], 30.0)
        self.assertAlmostEqual(sum(sales) + unserved, 100.0)
        self.assertAlmostEqual(unserved, 5.0)
        for s, o in zip(sales, [40.0, 30.0, 25.0]):
            self.assertLessEqual(s, o + 1e-12)

    def test_overflow_ties_are_shared_pro_rata(self):
        """Tied prices share the overflow by spare capacity, never by firm order."""
        sales, _, _ = allocate(100.0, [0.8, 0.1, 0.1], [90.0, 95.0, 95.0], [50.0, 40.0, 40.0])
        self.assertAlmostEqual(sales[1], sales[2])

    def test_label_swap_changes_nothing(self):
        """(5)"""
        a, b = Industry(make_config()), Industry(swapped_config())
        a.run(25)
        b.run(25)
        self.assertEqual(history_without_labels(a), history_without_labels(b))


if __name__ == "__main__":
    unittest.main()
