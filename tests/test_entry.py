"""Entry and exit. Stage 2 tests r_new, the signal of entry and of the reserve (A7, A10);
stage 3b adds the entry probability, inheritance, the entrant and exits."""
import unittest

from equations.entry_new_plant_rate import new_plant_rate
from helpers import add_firm, empty_industry
from model.scheduler import produce_and_account


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
        """A plant counts in r_new for the first entry_window periods in which it produces."""
        ind = empty_industry()
        young, old = add_firm(ind, plants=1, age=4), add_firm(ind, plants=1, age=5, price=120.0)
        young.sales = old.sales = 20.0
        produce_and_account(ind)
        self.assertEqual([young.plants[0].age, old.plants[0].age], [5, 6])
        self.assertAlmostEqual(ind.r_new, (100.0 - 78.0) / 137.5, places=12)

    def test_r_new_is_none_when_every_plant_is_old(self):
        ind = empty_industry()
        add_firm(ind, plants=2, age=8)
        produce_and_account(ind)
        self.assertIsNone(ind.r_new)


if __name__ == "__main__":
    unittest.main()
