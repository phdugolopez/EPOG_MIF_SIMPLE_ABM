"""E5 (experiments/e5_channels.py): the regression with cell effects on data made by hand,
and the spread of hurdles across firms."""
import unittest

from experiments.e5_channels import hurdle_spread, slope_with_cell_effects


class TestRegression(unittest.TestCase):
    def rows(self, noise=0.0):
        """Two cells with intercepts 1 and 5 and a common slope of -2: without the cell
        effects the slope of a pooled line would be positive."""
        out = []
        for cell, intercept, centre in (("a", 1.0, 0.2), ("b", 5.0, 0.8)):
            for step in range(-5, 6):
                x = centre + 0.02 * step
                out.append({"cell": cell, "x": str(x),
                            "y": str(intercept - 2.0 * x + noise * (-1) ** step)})
        return out

    def test_the_slope_is_within_the_cells_not_between_them(self):
        found = slope_with_cell_effects(self.rows(), "x", "y")
        self.assertAlmostEqual(found["slope"], -2.0, places=9)
        self.assertAlmostEqual(found["se"], 0.0, places=9)
        self.assertEqual((found["runs"], found["cells"]), (22, 2))

    def test_noise_gives_a_standard_error(self):
        found = slope_with_cell_effects(self.rows(noise=0.01), "x", "y")
        self.assertAlmostEqual(found["slope"], -2.0, delta=3 * found["se"])
        self.assertGreater(found["se"], 0.0)

    def test_runs_without_a_value_are_left_out(self):
        rows = self.rows() + [{"cell": "a", "x": "", "y": "1.0"},
                              {"cell": "b", "x": "0.5", "y": ""}]
        self.assertEqual(slope_with_cell_effects(rows, "x", "y")["runs"], 22)


class TestHurdleSpread(unittest.TestCase):
    def test_firms_on_the_unit_cost_rule_have_no_spread(self):
        self.assertEqual(hurdle_spread({"rule_okishio": "unit_cost", "periods": 30}, seeds=2), 0.0)

    def test_firms_with_different_prices_have_different_hurdles(self):
        self.assertGreater(hurdle_spread({"periods": 40}, seeds=2), 0.0)

    def test_at_lambda_one_every_firm_judges_at_the_same_price(self):
        """The spread left is that of the firms' own designs, far below that at lambda = 0."""
        own = hurdle_spread({"periods": 60, "tech_change": "none"}, seeds=2)
        common = hurdle_spread({"periods": 60, "tech_change": "none", "lam": 1.0}, seeds=2)
        self.assertGreater(own, 0.0)
        self.assertAlmostEqual(common, 0.0, places=12)


if __name__ == "__main__":
    unittest.main()
