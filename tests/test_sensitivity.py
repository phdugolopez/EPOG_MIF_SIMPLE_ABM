"""The sensitivity analysis script: run.py --set, the grid, the summary intervals and the
rerun of a row (experiments/sensitivity.py)."""

import contextlib
import io
import json
import math
import random
import tempfile
import unittest
from pathlib import Path

import pandas as pd

import run
from experiments import sensitivity as sens


class TestRunSet(unittest.TestCase):
    def test_set_overrides_parameters(self):
        with tempfile.TemporaryDirectory() as out, contextlib.redirect_stdout(io.StringIO()):
            frames = run.main(["--out", out, "--seed", "3", "--set", "CHI=2",
                               "--set", "PRICING_RULE=leader_follow",
                               "--set", 'HURDLE_RULES={"shaikh": "unit_cost", "okishio": "unit_cost"}',
                               "--set", "PERIODS=5"])
        r = frames["runs"].iloc[0]
        self.assertEqual(r["chi"], 2)
        self.assertEqual(r["pricing_rule"], "leader_follow")
        self.assertEqual(json.loads(r["hurdle_rules"]),
                         {"shaikh": "unit_cost", "okishio": "unit_cost"})
        self.assertEqual(r["seed"], 3)
        self.assertEqual(len(frames["macro"]), 5)

    def test_set_rejects_unknown_and_lower_case_names(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                run.main(["--set", "NO_SUCH_PARAMETER=1"])
            with self.assertRaises(SystemExit):
                run.main(["--set", "chi=1"])

    def test_without_set_the_configuration_is_parameters_py(self):
        self.assertEqual(vars(run.configure(42)), vars(run.configure(42, **{})))

    def test_rerun_args_rebuild_the_configuration(self):
        row = {"overrides": json.dumps({"CHI": 2.0, "PRICING_RULE": "leader_follow"}),
               "population": "all_profit_rate", "stage": "1", "cell": "x", "seed": 4}
        args = sens.rerun_args(row)
        sets = [args[i + 1] for i, a in enumerate(args) if a == "--set"]
        from experiments.neutral_control import parse_overrides
        parsed = parse_overrides(sets)
        self.assertEqual(parsed["CHI"], 2.0)
        self.assertEqual(parsed["PRICING_RULE"], "leader_follow")
        self.assertEqual(parsed["HURDLE_RULES"],
                         {"shaikh": "profit_rate", "okishio": "profit_rate"})


class TestIntervals(unittest.TestCase):
    def test_share_won_wilson_and_undecided(self):
        rows = pd.DataFrame({
            "error": [None] * 5,
            "undecided": [False, False, False, False, True],
            "shaikh_wins": [True, True, True, False, False],
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
        })
        out = sens.summarise_cell(rows, ["x"])
        self.assertEqual(out["n_undecided"], 1)
        self.assertEqual(out["won"], 3)
        self.assertAlmostEqual(out["share_won"], 0.75)
        self.assertLess(out["won_low"], 0.75)
        self.assertGreater(out["won_high"], 0.75)
        self.assertAlmostEqual(out["x_mean"], 3.0)
        self.assertAlmostEqual(out["x_lo"], 1.1)
        self.assertAlmostEqual(out["x_hi"], 4.9)
        half = 1.96 * pd.Series([1.0, 2, 3, 4, 5]).std() / math.sqrt(5)
        self.assertAlmostEqual(out["x_ci_lo"], 3.0 - half)
        self.assertAlmostEqual(out["x_ci_hi"], 3.0 + half)

    def test_disjoint(self):
        self.assertTrue(sens._disjoint(0.7, 0.9, 0.3, 0.6))
        self.assertFalse(sens._disjoint(0.5, 0.9, 0.3, 0.6))

    def test_takeover(self):
        s = pd.Series([0.5, 0.95, 0.5, 0.92, 0.97, 0.99], index=range(6))
        self.assertEqual(sens.takeover(s), (3.0, "shaikh"))
        s = pd.Series([0.5, 0.05, 0.02], index=range(3))
        self.assertEqual(sens.takeover(s), (1.0, "okishio"))
        t, label = sens.takeover(pd.Series([0.5, 0.95, 0.5], index=range(3)))
        self.assertTrue(math.isnan(t))
        self.assertIsNone(label)


class TestSmokeGrid(unittest.TestCase):
    """A two-cell, two-seed grid run on two workers: rows in order, the summary, and three
    random rows rerun through run.py --set reproduce their observables exactly."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        with contextlib.redirect_stdout(io.StringIO()):
            sens.grid("smoke", 2, 2, cls.out)
            cls.cells = sens.summarise(cls.out)
        cls.runs = sens.load_runs(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_rows_in_cell_population_seed_order(self):
        expected = [f"smoke_{c}_{p}_s{s}" for c in ("base", "lf")
                    for p in ("mixed", "all_unit_cost", "all_profit_rate") for s in (1, 2)]
        self.assertEqual(list(self.runs["run_id"]), expected)
        self.assertTrue(self.runs["error"].isna().all())
        self.assertTrue((self.runs["n_check_fail"] == 0).all())
        self.assertTrue((self.out / "runs.parquet").exists())
        self.assertIn("cell lf", (self.out / "progress.log").read_text())

    def test_parameter_columns_as_the_runs_table(self):
        with tempfile.TemporaryDirectory() as out, contextlib.redirect_stdout(io.StringIO()):
            frames = run.main(["--out", out, "--seed", "1"])
        for column in frames["runs"].columns:
            self.assertIn(column, self.runs.columns)
        row = self.runs.iloc[0]
        self.assertEqual(row["param_hash"], frames["runs"].iloc[0]["param_hash"])
        self.assertEqual(json.loads(self.runs.iloc[8]["overrides"]),
                         {"PRICING_RULE": "leader_follow"})

    def test_resume_skips_finished_cells_and_refuses_to_duplicate(self):
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit):
                sens.grid("smoke", 2, 1, self.out)
            sens.grid("smoke", 2, 1, self.out, resume=True)
        self.assertEqual(len(sens.load_runs(self.out)), 12)

    def test_summary_rows_and_controls(self):
        self.assertEqual(len(self.cells), 6)
        mixed = self.cells[self.cells["population"] == "mixed"]
        self.assertEqual(len(mixed), 2)
        self.assertTrue(mixed["gap"].notna().all())
        self.assertTrue(((self.cells["won_low"] <= self.cells["share_won"])
                         & (self.cells["share_won"] <= self.cells["won_high"])).all())

    def test_rerun_reproduces_three_random_rows(self):
        rng = random.Random(7)
        for run_id in rng.sample(list(self.runs["run_id"]), 3):
            with tempfile.TemporaryDirectory() as out:
                new, diff = sens.rerun(run_id, Path(out), self.out / "runs.csv", quiet=True)
            self.assertEqual(diff, [], run_id)
            row = self.runs[self.runs["run_id"] == run_id].iloc[0]
            self.assertEqual(new["param_hash"], row["param_hash"])


if __name__ == "__main__":
    unittest.main()
