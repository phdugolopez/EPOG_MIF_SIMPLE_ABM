"""The initial industry: the scaled menu, the staggered ages, parameters, entities, the
population of model.build, the check of the options and the random streams
(v4-final-model.md, "Initial industry" and "Randomness and neutrality")."""
import unittest
from dataclasses import FrozenInstanceError, fields, replace

from equations.common_hurdle import hurdle
from equations.common_profit_rate import profit_rate_at_price
from equations.common_regulating_price import price_of_production
from equations.common_technique_choice import choose_technique
from equations.common_unit_cost import unit_cost
from equations.setup_initial_plants import initial_ages
from equations.setup_menu import scaled_menu
from helpers import cash_total, industry, menu
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
                self.assertAlmostEqual(plant.book_value, plant.cost * (1 - plant.age / 10),
                                       places=9)

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
        self.assertEqual([technique.name for technique in self.industry.public],
                         ["C", "D1", "D2"])
        self.assertEqual([technique.first_run for technique in self.industry.public], [0, 0, 0])
        self.assertTrue(all(firm.known == [] for firm in self.firms))
        self.assertEqual(self.industry.tally, [])

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


class TestInitialIndustryAtAnotherRate(unittest.TestCase):
    """The scaled menu acts in model.build: the cost of the initial plants and the initial
    cash follow rbar, and nothing else moves."""

    def test_plants_cost_and_cash_are_3_2_times_those_of_the_default_at_5_percent(self):
        base, low = industry(), industry(rbar=0.05)
        for firm, other in zip(base.firms, low.firms):
            self.assertAlmostEqual(other.cash, 3.2 * firm.cash, places=6)
            for plant, scaled_plant in zip(firm.plants, other.plants):
                self.assertAlmostEqual(scaled_plant.cost, 3.2 * plant.cost, places=9)
                self.assertEqual(scaled_plant.age, plant.age)
        self.assertAlmostEqual(low.public[0].kappa * 20.0, 8800.0, places=9)
        self.assertAlmostEqual(cash_total(low), 0.0, places=6)

    def test_population_demand_and_shares_do_not_move_with_the_rate(self):
        base = industry()
        for rbar in (0.10, 0.05):
            other = industry(rbar=rbar)
            self.assertEqual(other.demand_0, base.demand_0)
            self.assertEqual([len(firm.plants) for firm in other.firms], [6, 6, 6, 6, 7, 7])
            self.assertEqual([firm.share for firm in other.firms],
                             [firm.share for firm in base.firms])
            self.assertEqual([firm.price for firm in other.firms], [100.0] * 6)

    def test_the_menu_of_the_industry_is_the_scaled_menu(self):
        for rbar in RATES:
            public = [(technique.name, technique.ucs, technique.kappa)
                      for technique in industry(rbar=rbar).public]
            self.assertEqual(public, scaled(rbar))
        short = industry(rbar=0.10, plant_life=7)
        self.assertEqual([(technique.name, technique.ucs, technique.kappa)
                          for technique in short.public], scaled(0.10, life=7))

    def test_the_fixed_menu_keeps_the_table_and_its_plant_costs_at_any_rate(self):
        fixed = industry(rbar=0.05, menu_scaling="fixed")
        self.assertEqual([technique.kappa for technique in fixed.public], [137.5, 142.31, 157.89])
        self.assertEqual([round(firm.cash, 2) for firm in fixed.firms],
                         [6325.0, 6325.0, 6546.26, 6546.26, 8526.06, 8526.06])

    def test_a_rate_that_gives_an_operating_cost_that_is_not_positive_is_refused(self):
        for overrides in ({"rbar": 0.03}, {"rbar": 0.04, "plant_life": 7}):
            with self.assertRaises(ValueError):
                industry(**overrides)
        self.assertEqual(len(industry(rbar=0.03, menu_scaling="fixed").firms), 6)


class TestOptions(unittest.TestCase):
    def test_every_level_of_every_option_builds(self):
        for name, levels in OPTIONS.items():
            for level in levels:
                self.assertEqual(len(industry(**{name: level}).firms), 6, (name, level))

    def test_a_misspelt_level_is_refused(self):
        for name in OPTIONS:
            with self.assertRaises(ValueError, msg=name):
                industry(**{name: "cost-edge"})

    def test_the_names_of_version_3_and_of_the_notebook_are_refused(self):
        for overrides in ({"pricing": "leader_follow"}, {"pricing": "cost edge"},
                          {"reserve": "released"}, {"entry_label": "even odds"},
                          {"rule_okishio": "okishio"}, {"tech_change": None}):
            with self.assertRaises(ValueError, msg=overrides):
                industry(**overrides)

    def test_the_message_names_the_option_and_its_levels(self):
        with self.assertRaises(ValueError) as refused:
            industry(pricing="universl")
        message = str(refused.exception)
        self.assertIn("pricing", message)
        self.assertIn("universal", message)


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

    def test_the_streams_do_not_depend_on_the_parameters(self):
        """Populations and cells are compared on the same numbers."""
        base, other = industry(seed=4), industry(seed=4, rbar=0.05, pricing="universal")
        self.assertEqual([self.draws(firm) for firm in base.firms],
                         [self.draws(firm) for firm in other.firms])
        self.assertEqual(list(base.rng.random(3)), list(other.rng.random(3)))


if __name__ == "__main__":
    unittest.main()
