"""Scrapping: the brief's tests (1)-(5)."""

import unittest

from equations.idle_plants import idle_plants
from equations.replacement import replacement_pays
from equations.retirement import periods_below_cost, retirement_reason, scrap_cost
from helpers import (
    PLANT_ALTERNATIVES, VERSION_1_PLANTS, history_without_labels, make_config,
    one_firm_industry, swapped_config,
)
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
        industry = one_firm_industry("C", **VERSION_1_PLANTS)
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

        industry = one_firm_industry("C", REPLACEMENT=False, **VERSION_1_PLANTS)
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


class TestScrappingAlternatives(unittest.TestCase):
    """PLANT_LIFE = None, SCRAP_COST = "unit_cost", IDLE_SCRAPPING = True."""

    def test_no_maximum_age(self):
        self.assertIsNone(retirement_reason(50, None, 0, 2))
        self.assertEqual(retirement_reason(10, 10, 0, 2), "age")

    def test_scrap_below_unit_cost_for_two_periods(self):
        # C: ucs 64.25, kappa 137.5, unit cost 78. A price of 70 covers ucs but not uc.
        self.assertAlmostEqual(scrap_cost(64.25, 137.5, 0.1, "unit_cost"), 78.0)
        self.assertAlmostEqual(scrap_cost(64.25, 137.5, 0.1, "operating_cost"), 64.25)
        count = 0
        for _ in range(2):
            self.assertIsNone(retirement_reason(1, None, count, 2))
            count = periods_below_cost(count, 70.0, scrap_cost(64.25, 137.5, 0.1, "unit_cost"))
        self.assertEqual(retirement_reason(1, None, count, 2), "obsolescence")
        self.assertEqual(periods_below_cost(0, 70.0, 64.25), 0)  # covered at ucs

    def test_idle_plants_highest_cost_then_oldest(self):
        ucs, vintage, cap = [60.0, 60.0, 64.0], [0, 3, 1], [20.0, 20.0, 20.0]
        self.assertEqual(idle_plants(ucs, vintage, cap, 25.0), [False, False, True])
        self.assertEqual(idle_plants(ucs, vintage, cap, 15.0), [True, False, True])
        self.assertEqual(idle_plants(ucs, vintage, cap, 60.0), [False, False, False])
        self.assertEqual(idle_plants(ucs, vintage, cap, 70.0), [False, False, False])

    def test_idle_plants_leave_after_idle_periods(self):
        """One C firm split into six plants of 20 sells 60: three plants idle for two
        periods leave, three stay."""
        industry = one_firm_industry("C", PLANT_SIZE=20.0, IDLE_SCRAPPING=True,
                                     IDLE_PERIODS=2, DEMAND_TO_CAPACITY=0.5,
                                     REPLACEMENT=False)
        firm = industry.firms[0]
        self.assertEqual(len(firm.plants), 6)
        run_to_scrapping(industry)
        industry.time += 1
        self.assertEqual(len(firm.plants), 6)
        run_to_scrapping(industry)
        self.assertEqual(len(firm.plants), 3)
        self.assertTrue(all(p.periods_idle == 0 for p in firm.plants))

    def test_label_swap_with_the_alternatives(self):
        a = Industry(make_config(**PLANT_ALTERNATIVES))
        b = Industry(swapped_config(**PLANT_ALTERNATIVES))
        a.run(80)
        b.run(80)
        self.assertEqual(history_without_labels(a), history_without_labels(b))


if __name__ == "__main__":
    unittest.main()
