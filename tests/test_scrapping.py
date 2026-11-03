"""Scrapping: the brief's tests (1)-(5)."""

import unittest

from equations.replacement import replacement_pays
from equations.retirement import periods_below_cost, retirement_reason
from helpers import make_config, one_firm_industry
from model import Industry
from model.scheduler import (
    allocate_demand, produce_and_account, scrap_plants, set_prices, start_period,
)


def run_to_scrapping(industry):
    start_period(industry)
    set_prices(industry)
    allocate_demand(industry)
    produce_and_account(industry)
    capacity_before = sum(f.capacity for f in industry.firms)
    scrap_plants(industry)
    return capacity_before


class TestScrapping(unittest.TestCase):
    def test_plant_reaching_age_t_leaves(self):
        """(1)"""
        industry = one_firm_industry("C")
        for t in range(10):
            run_to_scrapping(industry)
            industry.time += 1
            if t < 9:
                self.assertEqual(len(industry.firms[0].plants), 1)
        self.assertEqual(industry.firms[0].plants, [])
        self.assertEqual(industry.retired[0].age, 10)
        self.assertAlmostEqual(industry.firms[0].write_offs, 0.0)  # fully depreciated

    def test_plant_below_cost_for_n_periods_leaves(self):
        """(2)"""
        count = 0
        for t in range(4):
            self.assertIsNone(retirement_reason(t, 10, count, 4))
            count = periods_below_cost(count, price=60.0, ucs=64.25)
        self.assertEqual(retirement_reason(4, 10, count, 4), "obsolescence")
        self.assertEqual(periods_below_cost(count, price=70.0, ucs=64.25), 0)

        industry = one_firm_industry("C", REPLACEMENT=False)
        firm = industry.firms[0]
        for t in range(4):
            start_period(industry)
            firm.price = 60.0  # below ucs = 64.25, set by hand
            allocate_demand(industry)
            produce_and_account(industry)
            scrap_plants(industry)
            industry.time += 1
        self.assertEqual(firm.plants, [])
        self.assertGreater(firm.write_offs, 0.0)  # early retirement leaves book value

    def test_replacement_inequality(self):
        """(3) ucs 80 against a new technique with ucs 60 and kappa 150, delta 10 %."""
        self.assertTrue(replacement_pays(80.0, 60.0, 150.0, 0.10, hurdle=0.0))  # 75 < 80
        self.assertFalse(replacement_pays(80.0, 60.0, 150.0, 0.10, hurdle=0.16))  # 99 > 80

    def test_no_working_plant_replaced_on_the_test_industry(self):
        """(4) C's operating cost (64.25) is below D2's unit cost (75)."""
        industry = Industry(make_config())
        industry.run(60)
        self.assertEqual(sum(row["replacements"] for row in industry.history), 0)

    def test_capacity_after_scrapping(self):
        """(5) Capacity after scrapping = capacity before minus retired plants."""
        industry = Industry(make_config())
        for _ in range(12):
            before = run_to_scrapping(industry)
            after = sum(f.capacity for f in industry.firms)
            self.assertAlmostEqual(after, before - sum(p.capacity for p in industry.retired))
            industry.time += 1


if __name__ == "__main__":
    unittest.main()
