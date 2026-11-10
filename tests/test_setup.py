"""The initial industry: the scaled menu, the staggered ages, parameters and entities
(v4-final-model.md, "Initial industry")."""
import unittest
from dataclasses import FrozenInstanceError, fields, replace

from equations.common_hurdle import hurdle
from equations.common_profit_rate import profit_rate_at_price
from equations.common_regulating_price import price_of_production
from equations.common_technique_choice import choose_technique
from equations.common_unit_cost import unit_cost
from equations.setup_initial_plants import initial_ages
from equations.setup_menu import scaled_menu
from helpers import menu
from model.entities import Firm, Plant, Technique
from parameters import LABELS, OPTIONS, SHAIKH_MENU, SHAIKH_RATE, START, Parameters

RATES = (0.16, 0.10, 0.05)
PRICES = (60.0, 75.0, 80.0, 85.0, 85.3, 90.0, 100.0, 120.0, 135.0, 136.0, 150.0, 300.0)


def scaled(rbar: float, life: int = 10, scaling: str = "scaled") -> list[tuple]:
    return scaled_menu(SHAIKH_MENU, SHAIKH_RATE, rbar, 1.0 / life, scaling)


class TestScaledMenu(unittest.TestCase):
    def test_at_the_rate_of_the_table_it_is_the_table_at_any_plant_life(self):
        for life in (10, 7, 19):
            self.assertEqual(scaled(0.16, life), list(SHAIKH_MENU))

    def test_the_table_of_the_proposal_at_the_two_other_rates(self):
        expected = {
            0.10: [("C", 56.00, 220.00), ("D1", 53.23, 227.70), ("D2", 49.74, 252.62)],
            0.05: [("C", 34.00, 440.00), ("D1", 30.46, 455.39), ("D2", 24.47, 505.25)],
        }
        for rbar, table in expected.items():
            rounded = [(name, round(ucs, 2), round(kappa, 2)) for name, ucs, kappa in scaled(rbar)]
            self.assertEqual(rounded, table)

    def test_a_plant_costs_the_table_s_price_times_the_ratio_of_the_rates(self):
        for rbar, cost in ((0.16, 2750.0), (0.10, 4400.0), (0.05, 8800.0)):
            _, _, kappa = scaled(rbar)[0]
            self.assertAlmostEqual(kappa * Parameters().plant_size, cost, places=9)

    def test_unit_costs_and_prices_of_production_are_those_of_the_table_at_every_rate(self):
        for life in (10, 7):
            delta = 1.0 / life
            for rbar in (0.10, 0.05, 0.25):
                for (_, ucs, kappa), (_, ucs_s, kappa_s) in zip(scaled(rbar, life), SHAIKH_MENU):
                    self.assertAlmostEqual(unit_cost(ucs, kappa, delta),
                                           unit_cost(ucs_s, kappa_s, delta), places=9)
                    self.assertAlmostEqual(price_of_production(ucs, kappa, delta, rbar),
                                           price_of_production(ucs_s, kappa_s, delta, 0.16),
                                           places=9)

    def test_at_100_the_techniques_earn_the_same_multiples_of_the_general_rate(self):
        for rbar in RATES:
            rates = [profit_rate_at_price(100.0, ucs, kappa, 0.1) for _, ucs, kappa in scaled(rbar)]
            multiples = [round(rate / rbar, 3) for rate in rates]
            self.assertEqual(multiples, [1.0, 1.054, 0.990])

    def test_at_a_given_price_each_rule_chooses_the_same_technique_at_every_rate(self):
        names = {}
        for rbar in RATES:
            techniques = [Technique(*row) for row in scaled(rbar)]
            for rule in ("unit_cost", "profit_rate"):
                for price in PRICES:
                    h = hurdle(rule, price, techniques, 0.1)
                    names[rbar, rule, price] = choose_technique(techniques, h, 0.1).name
        for rule in ("unit_cost", "profit_rate"):
            for price in PRICES:
                chosen = {names[rbar, rule, price] for rbar in RATES}
                self.assertEqual(len(chosen), 1, (rule, price, chosen))
        self.assertEqual({names[0.05, "unit_cost", price] for price in PRICES}, {"D2"})
        self.assertEqual(names[0.05, "profit_rate", 85.0], "D2")
        self.assertEqual(names[0.05, "profit_rate", 85.3], "D1")
        self.assertEqual(names[0.05, "profit_rate", 136.0], "C")

    def test_the_hurdle_at_a_given_price_is_proportional_to_the_general_rate(self):
        base = hurdle("profit_rate", 100.0, menu(), 0.1)
        for rbar in (0.10, 0.05):
            techniques = [Technique(*row) for row in scaled(rbar)]
            h = hurdle("profit_rate", 100.0, techniques, 0.1)
            self.assertAlmostEqual(h / rbar, base / 0.16, places=9)

    def test_a_menu_with_an_operating_cost_that_is_not_positive_is_refused(self):
        """The limit is 0.034 at T = 10 and 0.044 at T = 7."""
        for rbar, life in ((0.03, 10), (0.04, 7), (0.033, 10)):
            with self.assertRaises(ValueError):
                scaled(rbar, life)
        for rbar, life in ((0.04, 10), (0.035, 10), (0.05, 7)):
            self.assertTrue(all(ucs > 0.0 for _, ucs, _ in scaled(rbar, life)))

    def test_the_fixed_menu_is_the_table_at_any_rate(self):
        for rbar in (0.16, 0.10, 0.05, 0.03):
            self.assertEqual(scaled(rbar, scaling="fixed"), list(SHAIKH_MENU))


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
            Parameters().rbar = 0.05

    def test_the_defaults_of_version_4(self):
        p = Parameters()
        self.assertEqual((p.rbar, p.shortage_step, p.u_max), (0.16, 0.25, 1.2))
        self.assertEqual((p.pricing, p.entry_price, p.reserve), ("cost_edge", "undercut",
                                                                 "conditional"))
        names = {field.name for field in fields(Parameters)}
        self.assertFalse({"u_target", "menu"} & names)

    def test_every_option_is_a_parameter_and_its_default_is_one_of_its_levels(self):
        p = Parameters()
        for name, levels in OPTIONS.items():
            self.assertIn(getattr(p, name), levels, name)

    def test_start_has_one_firm_per_technique_and_label(self):
        pairs = {(name, label) for name, label, _ in START}
        self.assertEqual(pairs, {(name, label) for name, _, _ in SHAIKH_MENU for label in LABELS})
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
