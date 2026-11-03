"""Pricing: the brief's tests (1)-(4)."""

import random
import unittest

from equations.posted_price import posted_price
from helpers import history_without_labels, make_config, swapped_config
from model import Industry
from model.scheduler import allocate_demand, produce_and_account, set_prices, start_period

TEST_INDUSTRY = (("C", "shaikh"), ("D1", "shaikh"), ("D2", "shaikh"))


def run_without_capacity_change(industry, periods, demand_path=None):
    """Pricing, demand and production only: scrapping, investment and entry are stubbed."""
    prices = []
    for t in range(periods):
        if demand_path:
            industry.initial_demand = demand_path(t)
        start_period(industry)
        set_prices(industry)
        allocate_demand(industry)
        produce_and_account(industry)
        prices.append([f.price for f in industry.firms])
        industry.time += 1
    return prices


class TestPricing(unittest.TestCase):
    def test_no_price_below_the_floor(self):
        """(1)"""
        rng = random.Random(3)
        for _ in range(500):
            floor = rng.uniform(50, 70)
            p = posted_price(
                rng.uniform(40, 120), rng.uniform(80, 110), rng.uniform(40, 120), floor,
                rng.random() < 0.5, 0.25, 0.025, 0.02,
            )
            self.assertGreaterEqual(p, floor)

    def test_identical_firms_at_normal_capacity_keep_their_anchor(self):
        """(2)"""
        config = make_config(INITIAL_FIRMS=(("C", "shaikh"), ("C", "okishio")),
                             DEMAND_TO_CAPACITY=1.0)
        industry = Industry(config)
        for row in run_without_capacity_change(industry, 40):
            for p in row:
                self.assertAlmostEqual(p, 100.0)  # C's target-return price

    def test_war_starts_deepens_ends_and_prices_recover(self):
        """(3) Test industry, demand 340 against capacity 383, capacity fixed. The war
        ends when demand returns to normal capacity (standing in for the capacity
        adjustment that scrapping and investment provide in the full model)."""
        industry = Industry(make_config(INITIAL_FIRMS=TEST_INDUSTRY))
        prices = run_without_capacity_change(
            industry, 50, demand_path=lambda t: 340.0 if t < 15 else 383.0
        )
        mean = [sum(row) / len(row) for row in prices]
        self.assertLess(mean[2], mean[1])  # starts after WAR_PERIODS low periods
        self.assertLess(mean[14], mean[8])  # deepens
        trough = min(mean)
        self.assertLess(trough, 80.0)
        floors = [64.25, 76 - 0.1 * 18_500 / 130, 75 - 0.1 * 21_000 / 133]  # ucs
        for row in prices:
            for p, floor in zip(row, floors):
                self.assertGreaterEqual(p, floor - 1e-9)
        self.assertGreater(mean[-1], trough + 15.0)  # recovers
        self.assertGreater(mean[-1], 95.0)

    def test_label_swap_changes_nothing(self):
        """(4)"""
        a, b = Industry(make_config()), Industry(swapped_config())
        a.run(40)
        b.run(40)
        self.assertEqual(history_without_labels(a), history_without_labels(b))


if __name__ == "__main__":
    unittest.main()
