"""Entry and exit. Stage 2 tests r_new, the signal of entry and of the reserve; stage 3b adds
the entry probability, inheritance, the entrant, its price and its label, and exits."""
import unittest

from equations.entry_new_plant_rate import new_plant_rate
from helpers import add_firm, empty_industry
from model.scheduler import set_new_plant_rate


class TestNewPlantRate(unittest.TestCase):
    def test_weighted_by_capacity(self):
        self.assertAlmostEqual(new_plant_rate([0.10, 0.20], [20.0, 60.0]), 0.175, places=12)
        self.assertAlmostEqual(new_plant_rate([0.10, 0.20], [20.0, 20.0]), 0.15, places=12)

    def test_none_without_a_plant_in_the_window(self):
        self.assertIsNone(new_plant_rate([], []))

    def test_the_order_of_the_plants_does_not_matter(self):
        rates, capacities = [0.03, 0.11, 0.07, 0.19], [20.0, 20.0, 40.0, 20.0]
        self.assertEqual(new_plant_rate(rates, capacities),
                         new_plant_rate(rates[::-1], capacities[::-1]))


class TestSignal(unittest.TestCase):
    def test_r_new_ignores_plants_older_than_the_window(self):
        ind = empty_industry()
        young, old = add_firm(ind, plants=1, age=5), add_firm(ind, plants=1, age=6)
        young.plants[0].profit = 0.08 * young.plants[0].cost
        old.plants[0].profit = 0.50 * old.plants[0].cost
        set_new_plant_rate(ind)
        self.assertAlmostEqual(ind.r_new, 0.08, places=12)

    def test_r_new_is_profit_over_purchase_cost_weighted_by_capacity(self):
        ind = empty_industry()
        firm = add_firm(ind, plants=3, age=1)
        for plant, rate in zip(firm.plants, (0.10, 0.16, 0.25)):
            plant.profit = rate * plant.cost
        set_new_plant_rate(ind)
        self.assertAlmostEqual(ind.r_new, 0.17, places=12)

    def test_r_new_is_none_when_every_plant_is_old(self):
        ind = empty_industry()
        add_firm(ind, plants=2, age=8)
        set_new_plant_rate(ind)
        self.assertIsNone(ind.r_new)


if __name__ == "__main__":
    unittest.main()
