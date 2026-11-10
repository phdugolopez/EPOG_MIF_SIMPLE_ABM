"""Initial population (addendum A2, A3), parameters and entities. Stage 2 adds the tests of the
population that model.build() creates."""
import unittest
from dataclasses import FrozenInstanceError, replace

from equations.setup_initial_plants import initial_ages
from helpers import menu
from model.entities import Firm, Plant
from parameters import LABELS, MENU, START, Parameters


class TestInitialAges(unittest.TestCase):
    def test_staggered_ages_of_the_initial_firms(self):
        self.assertEqual(initial_ages(120.0, 20.0, 10), [0, 1, 3, 5, 6, 8])
        self.assertEqual(initial_ages(140.0, 20.0, 10), [0, 1, 2, 4, 5, 7, 8])

    def test_number_of_plants_is_rounded_half_up_and_at_least_one(self):
        self.assertEqual(len(initial_ages(130.0, 20.0, 10)), 7)
        self.assertEqual(len(initial_ages(129.0, 20.0, 10)), 6)
        self.assertEqual(initial_ages(5.0, 20.0, 10), [0])

    def test_ages_stay_below_the_plant_life(self):
        for life in (7, 10, 19):
            for size in (10.0, 20.0, 40.0):
                ages = initial_ages(140.0, size, life)
                self.assertEqual(ages, sorted(ages))
                self.assertLess(max(ages), life)


class TestParameters(unittest.TestCase):
    def test_delta_is_derived_from_the_plant_life(self):
        self.assertEqual(Parameters().delta, 0.1)
        self.assertEqual(replace(Parameters(), plant_life=20).delta, 0.05)

    def test_parameters_cannot_be_changed_in_place(self):
        with self.assertRaises(FrozenInstanceError):
            Parameters().rbar = 0.16

    def test_start_has_one_firm_per_technique_and_label(self):
        pairs = {(name, label) for name, label, _ in START}
        self.assertEqual(pairs, {(name, label) for name, _, _ in MENU for label in LABELS})
        self.assertEqual(len(START), 6)

    def test_initial_capacity_and_demand(self):
        p = Parameters()
        plants = sum(len(initial_ages(output, p.plant_size, p.plant_life))
                     for _, _, output in p.start)
        self.assertEqual(plants * p.plant_size, 760.0)
        self.assertAlmostEqual(p.demand_ratio * plants * p.plant_size, 674.67, places=2)


class TestEntities(unittest.TestCase):
    def firm(self) -> Firm:
        technique = menu()[0]
        cost = technique.kappa * 20.0
        plants = [Plant(technique, 20.0, cost, cost) for _ in range(3)]
        return Firm(id=0, label="shaikh", rule="unit_cost", rng=None, born=0, price=100.0,
                    share=0.5, plants=plants)

    def test_capacity_is_the_sum_over_plants_in_operation(self):
        firm = self.firm()
        self.assertEqual(firm.capacity, 60.0)
        firm.pending_plants.append(firm.plants.pop())
        self.assertEqual(firm.capacity, 40.0)

    def test_objects_are_compared_by_identity(self):
        self.assertNotEqual(self.firm(), self.firm())
        self.assertIsNot(self.firm().plants, self.firm().plants)


if __name__ == "__main__":
    unittest.main()
