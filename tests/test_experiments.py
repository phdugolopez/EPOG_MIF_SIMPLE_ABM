"""The experiment scripts: the neutral control runs, writes its tables and reads the
labels as labels only."""

import contextlib
import io
import math
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from experiments import neutral_control as nc


class TestNeutralControl(unittest.TestCase):
    def test_wilson_interval(self):
        low, high = nc.wilson(10, 20)
        self.assertLess(low, 0.5)
        self.assertGreater(high, 0.5)
        self.assertAlmostEqual(low, 0.299, places=3)
        self.assertAlmostEqual(high, 0.701, places=3)
        self.assertTrue(all(math.isnan(v) for v in nc.wilson(0, 0)))

    def test_overrides(self):
        self.assertEqual(nc.parse_overrides(["CHI=2", "PRICING_RULE=leader_follow"]),
                         {"CHI": 2, "PRICING_RULE": "leader_follow"})
        with self.assertRaises(SystemExit):
            nc.parse_overrides(["chi=2"])

    def test_runs_three_populations_and_writes_the_tables(self):
        with tempfile.TemporaryDirectory() as out:
            with contextlib.redirect_stdout(io.StringIO()):
                summary = nc.main(["--seeds", "2", "--periods", "20", "--out", out])
            self.assertEqual(list(summary["population"]),
                             ["mixed", "all_unit_cost", "all_profit_rate"])
            self.assertTrue((summary["seeds"] == 2).all())
            self.assertTrue(((summary["won_low"] <= summary["share_won"])
                             & (summary["share_won"] <= summary["won_high"])).all())
            rows = pd.read_csv(Path(out) / "neutral_control_seeds.csv")
            self.assertEqual(len(rows), 6)
            self.assertTrue(pd.read_csv(Path(out) / "neutral_control.csv").equals(
                pd.read_csv(Path(out) / "neutral_control.csv")))

    def test_same_rule_under_both_labels_is_a_label_only_difference(self):
        """With both labels on one rule, the run equals the mixed run of a population
        whose HURDLE_RULES map both labels to that rule: the control is by construction
        neutral, and only the random draws consumed in firm order can separate the twins."""
        a = nc.run_seed(3, 30, {"shaikh": "unit_cost", "okishio": "unit_cost"})
        b = nc.run_seed(3, 30, None, HURDLE_RULES={"shaikh": "unit_cost", "okishio": "unit_cost"})
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
