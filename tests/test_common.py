"""Definitions several steps share: unit cost, rate at a price, hurdle, technique choice and
regulating price, on Shaikh's menu (addendum A1) with delta = 0.10."""
import unittest

from equations.common_hurdle import evaluation_price, hurdle
from equations.common_profit_rate import profit_rate_at_price
from equations.common_regulating_price import price_of_production, regulating_technique
from equations.common_technique_choice import choose_technique, frontier, technique_cost
from equations.common_unit_cost import unit_cost
from helpers import menu
from model.entities import Technique

DELTA = 0.1


class TestMenu(unittest.TestCase):
    def setUp(self):
        self.menu = menu()
        self.c, self.d1, self.d2 = self.menu

    def test_d2_has_the_lowest_unit_cost(self):
        costs = [unit_cost(t.ucs, t.kappa, DELTA) for t in self.menu]
        for cost, expected in zip(costs, (78.0, 76.001, 74.999)):
            self.assertAlmostEqual(cost, expected, places=9)
        self.assertEqual(min(costs), costs[2])

    def test_d1_has_the_highest_rate_at_100(self):
        rates = [profit_rate_at_price(100.0, t.ucs, t.kappa, DELTA) for t in self.menu]
        for rate, expected in zip(rates, (0.16, 0.168639, 0.158344)):
            self.assertAlmostEqual(rate, expected, places=5)
        self.assertEqual(max(rates), rates[1])

    def test_rate_is_zero_at_the_unit_cost(self):
        for t in self.menu:
            price = unit_cost(t.ucs, t.kappa, DELTA)
            self.assertEqual(profit_rate_at_price(price, t.ucs, t.kappa, DELTA), 0.0)


class TestHurdle(unittest.TestCase):
    def setUp(self):
        self.menu = menu()
        self.c, self.d1, self.d2 = self.menu

    def test_unit_cost_rule_has_no_hurdle_at_any_price(self):
        for price in (50.0, 100.0, 200.0):
            self.assertEqual(hurdle("unit_cost", price, self.menu, DELTA), 0.0)

    def test_profit_rate_rule_takes_the_best_rate_on_the_menu(self):
        for price, best in ((100.0, self.d1), (80.0, self.d2), (150.0, self.c)):
            expected = profit_rate_at_price(price, best.ucs, best.kappa, DELTA)
            self.assertEqual(hurdle("profit_rate", price, self.menu, DELTA), expected)
            for t in self.menu:
                self.assertLessEqual(profit_rate_at_price(price, t.ucs, t.kappa, DELTA), expected)

    def test_hurdle_is_zero_below_every_unit_cost(self):
        self.assertEqual(hurdle("profit_rate", 70.0, self.menu, DELTA), 0.0)

    def test_hurdle_does_not_depend_on_the_order_of_the_menu(self):
        self.assertEqual(hurdle("profit_rate", 100.0, self.menu, DELTA),
                         hurdle("profit_rate", 100.0, self.menu[::-1], DELTA))


class TestEvaluationPrice(unittest.TestCase):
    def setUp(self):
        self.menu = menu()
        self.c, self.d1, self.d2 = self.menu

    def test_between_own_price_and_the_regulating_price(self):
        self.assertEqual(evaluation_price(100.0, 80.0, 0.0), 100.0)
        self.assertEqual(evaluation_price(100.0, 80.0, 0.5), 90.0)
        self.assertEqual(evaluation_price(100.0, 80.0, 1.0), 80.0)

    def test_regulating_technique_and_its_price_of_production(self):
        reg = regulating_technique(self.menu, DELTA)
        self.assertIs(reg, self.d2)
        for rbar, expected in ((0.05, 82.8935), (0.16, 100.2614)):
            price = price_of_production(reg.ucs, reg.kappa, DELTA, rbar)
            self.assertAlmostEqual(price, expected, places=9)

    def test_hurdle_at_the_price_of_production(self):
        """lambda = 1: the hurdle is rbar when the regulating technique has the best rate at its
        own price of production (rbar = 0.05), and above rbar when another has (rbar = 0.16)."""
        reg = regulating_technique(self.menu, DELTA)
        low = evaluation_price(100.0, price_of_production(reg.ucs, reg.kappa, DELTA, 0.05), 1.0)
        self.assertAlmostEqual(hurdle("profit_rate", low, self.menu, DELTA), 0.05, places=12)
        self.assertIs(choose_technique(self.menu, 0.05, DELTA), self.d2)
        high = evaluation_price(100.0, price_of_production(reg.ucs, reg.kappa, DELTA, 0.16), 1.0)
        h = hurdle("profit_rate", high, self.menu, DELTA)
        self.assertAlmostEqual(h, 0.1705, places=4)
        self.assertEqual(h, profit_rate_at_price(high, self.d1.ucs, self.d1.kappa, DELTA))
        self.assertIs(choose_technique(self.menu, h, DELTA), self.d1)

    def test_hurdle_at_the_price_of_production_is_never_below_rbar(self):
        reg = regulating_technique(self.menu, DELTA)
        for rbar in (0.01, 0.05, 0.10, 0.16, 0.30):
            price = price_of_production(reg.ucs, reg.kappa, DELTA, rbar)
            self.assertGreaterEqual(hurdle("profit_rate", price, self.menu, DELTA), rbar - 1e-12)


class TestTechniqueChoice(unittest.TestCase):
    def setUp(self):
        self.menu = menu()
        self.c, self.d1, self.d2 = self.menu

    def test_cost_at_no_hurdle_is_the_unit_cost(self):
        for t in self.menu:
            cost = technique_cost(t.ucs, t.kappa, 0.0, DELTA)
            self.assertEqual(cost, unit_cost(t.ucs, t.kappa, DELTA))

    def test_unit_cost_rule_chooses_the_lowest_unit_cost(self):
        self.assertIs(choose_technique(self.menu, 0.0, DELTA), self.d2)

    def test_profit_rate_rule_chooses_the_highest_rate(self):
        """D1 and D2 have the same rate at a price of 85.15: D2 below it, D1 above."""
        for price, best in ((85.0, self.d2), (85.3, self.d1), (100.0, self.d1), (150.0, self.c)):
            h = hurdle("profit_rate", price, self.menu, DELTA)
            self.assertIs(choose_technique(self.menu, h, DELTA), best)

    def test_choice_does_not_depend_on_the_order_of_the_menu(self):
        for h in (0.0, 0.05, 0.17, 0.5):
            reverse = choose_technique(self.menu[::-1], h, DELTA)
            self.assertIs(choose_technique(self.menu, h, DELTA), reverse)

    def test_exact_ties_go_to_the_lower_kappa(self):
        light, heavy = Technique("light", 60.0, 40.0), Technique("heavy", 50.0, 80.0)
        costs = [technique_cost(t.ucs, t.kappa, 0.0, 0.25) for t in (light, heavy)]
        self.assertEqual(costs[0], costs[1])
        self.assertIs(choose_technique([light, heavy], 0.0, 0.25), light)
        self.assertIs(choose_technique([heavy, light], 0.0, 0.25), light)
        self.assertIs(regulating_technique([heavy, light], 0.25), light)


class TestFrontier(unittest.TestCase):
    def setUp(self):
        self.menu = menu() + [
            Technique("dearer and heavier than D1", 62.0, 150.0),      # unit cost 77.0
            Technique("cheaper and heavier than D2", 55.0, 170.0),     # unit cost 72.0
            Technique("as cheap as C and heavier", 64.0, 140.0),       # unit cost 78.0
        ]

    def test_a_technique_beaten_on_unit_cost_and_capital_is_dropped(self):
        kept = [t.name for t in frontier(self.menu, DELTA)]
        self.assertEqual(kept, ["C", "D1", "D2", "cheaper and heavier than D2"])

    def test_the_three_techniques_of_the_menu_are_on_the_frontier(self):
        self.assertEqual(len(frontier(menu(), DELTA)), 3)

    def test_identical_techniques_do_not_beat_each_other(self):
        twins = [Technique("a", 60.0, 150.0), Technique("b", 60.0, 150.0)]
        self.assertEqual(frontier(twins, DELTA), twins)

    def test_dropping_beaten_techniques_changes_no_choice_and_no_hurdle(self):
        pruned = frontier(self.menu, DELTA)
        for price in (60.0, 74.0, 80.0, 85.0, 100.0, 150.0, 400.0):
            h = hurdle("profit_rate", price, self.menu, DELTA)
            self.assertEqual(h, hurdle("profit_rate", price, pruned, DELTA))
            for rate in (0.0, h, 0.05, 0.5):
                self.assertIs(choose_technique(self.menu, rate, DELTA),
                              choose_technique(pruned, rate, DELTA))


if __name__ == "__main__":
    unittest.main()
