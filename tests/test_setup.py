"""Initial population (addendum A2, A3, A13 k), parameters, entities and random streams."""
import unittest
from dataclasses import FrozenInstanceError, replace

from equations.setup_initial_plants import initial_ages
from helpers import cash_total, industry, menu
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


class TestInitialIndustry(unittest.TestCase):
    def setUp(self):
        self.industry = industry()
        self.firms = self.industry.firms

    def test_six_firms_one_per_technique_and_label(self):
        self.assertEqual([firm.id for firm in self.firms], list(range(6)))
        self.assertEqual([firm.label for firm in self.firms], ["shaikh", "okishio"] * 3)
        self.assertEqual([firm.rule for firm in self.firms], ["unit_cost", "profit_rate"] * 3)
        names = [firm.plants[0].technique.name for firm in self.firms]
        self.assertEqual(names, ["C", "C", "D1", "D1", "D2", "D2"])

    def test_plants_capacity_and_demand(self):
        self.assertEqual([len(firm.plants) for firm in self.firms], [6, 6, 6, 6, 7, 7])
        self.assertEqual(sum(firm.capacity for firm in self.firms), 760.0)
        self.assertAlmostEqual(self.industry.demand_0, 674.67, places=2)
        self.assertEqual(self.industry.demand, self.industry.demand_0)

    def test_staggered_ages_and_book_values(self):
        self.assertEqual([plant.age for plant in self.firms[0].plants], [0, 1, 3, 5, 6, 8])
        self.assertEqual([plant.age for plant in self.firms[4].plants], [0, 1, 2, 4, 5, 7, 8])
        for firm in self.firms:
            for plant in firm.plants:
                self.assertEqual(plant.cost, plant.technique.kappa * 20.0)
                self.assertAlmostEqual(plant.book_value, plant.cost * (1 - plant.age / 10), places=9)

    def test_prices_shares_and_utilisation(self):
        for firm in self.firms:
            self.assertEqual(firm.price, 100.0)
            self.assertAlmostEqual(firm.share, firm.capacity / 760.0, places=12)
            self.assertAlmostEqual(firm.sales, firm.share * self.industry.demand_0, places=9)
            self.assertAlmostEqual(firm.util, 340 / 383, places=12)
        self.assertAlmostEqual(sum(firm.share for firm in self.firms), 1.0, places=12)

    def test_cash_is_the_depreciation_accumulated_on_the_plants(self):
        cash = [round(firm.cash, 2) for firm in self.firms]
        self.assertEqual(cash, [6325.0, 6325.0, 6546.26, 6546.26, 8526.06, 8526.06])
        self.assertEqual([firm.funds for firm in self.firms], [0.0] * 6)
        self.assertAlmostEqual(self.industry.roe.cash, -42794.64, places=2)
        self.assertAlmostEqual(cash_total(self.industry), 0.0, places=9)

    def test_public_menu_and_no_private_design(self):
        self.assertEqual([t.name for t in self.industry.public], ["C", "D1", "D2"])
        self.assertEqual([t.first_run for t in self.industry.public], [0, 0, 0])
        self.assertTrue(all(firm.known == [] for firm in self.firms))

    def test_controls_change_the_rule_and_keep_the_labels(self):
        control = industry(rule_okishio="unit_cost")
        self.assertEqual([firm.label for firm in control.firms], ["shaikh", "okishio"] * 3)
        self.assertEqual({firm.rule for firm in control.firms}, {"unit_cost"})
        control = industry(rule_shaikh="profit_rate")
        self.assertEqual({firm.rule for firm in control.firms}, {"profit_rate"})

    def test_two_firms_per_pair_double_firms_and_demand(self):
        double = industry(firms_per_pair=2)
        self.assertEqual(len(double.firms), 12)
        self.assertEqual(sum(firm.capacity for firm in double.firms), 1520.0)
        self.assertAlmostEqual(double.demand_0, 2 * self.industry.demand_0, places=9)
        self.assertAlmostEqual(cash_total(double), 0.0, places=9)

    def test_plant_size_keeps_normal_outputs_and_utilisation(self):
        small = industry(plant_size=10.0)
        self.assertEqual([len(firm.plants) for firm in small.firms], [12, 12, 12, 12, 14, 14])
        self.assertAlmostEqual(small.demand_0, self.industry.demand_0, places=9)

    def test_plant_life_moves_ages_and_cash(self):
        short = industry(plant_life=7)
        for firm in short.firms:
            self.assertLess(max(plant.age for plant in firm.plants), 7)
            expected = sum(plant.cost * plant.age / 7 for plant in firm.plants)
            self.assertAlmostEqual(firm.cash, expected, places=6)


class TestStreams(unittest.TestCase):
    def draws(self, firm):
        return list(firm.rng.random(4))

    def test_same_seed_same_numbers_another_seed_other_numbers(self):
        same = [self.draws(firm) for firm in industry(seed=1).firms]
        self.assertEqual(same, [self.draws(firm) for firm in industry(seed=1).firms])
        self.assertNotEqual(same, [self.draws(firm) for firm in industry(seed=2).firms])

    def test_every_firm_and_the_industry_have_their_own_stream(self):
        ind = industry()
        streams = [tuple(self.draws(firm)) for firm in ind.firms] + [tuple(ind.rng.random(4))]
        self.assertEqual(len(set(streams)), 7)

    def test_a_stream_is_keyed_by_the_serial_number_not_the_place(self):
        """Firm 3 draws the same numbers among 6 firms and among 12, and wherever it stands."""
        six, twelve = industry(seed=5), industry(seed=5, firms_per_pair=2)
        twelve.firms.reverse()
        third = next(firm for firm in twelve.firms if firm.id == 3)
        self.assertEqual(self.draws(six.firms[3]), self.draws(third))


if __name__ == "__main__":
    unittest.main()
