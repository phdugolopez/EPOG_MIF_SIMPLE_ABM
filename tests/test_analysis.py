"""experiments/analysis.py: the regression, the takeover reading, the seed-story figure and
the stage 4 grid (run, merge, rerun)."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

import parameters
import run
from experiments import analysis as an
from experiments import sensitivity as sens


class TestRegression(unittest.TestCase):
    def test_fixed_effects_regression_recovers_the_slopes(self):
        rng = np.random.default_rng(3)
        n_groups, per = 40, 50
        group = np.repeat(np.arange(n_groups), per)
        effect = rng.normal(0, 5, n_groups)[group]  # fixed effects, correlated with x1
        x1 = rng.normal(0, 1, len(group)) + 0.5 * effect
        x2 = rng.normal(0, 1, len(group))
        y = 2.0 * x1 - 1.0 * x2 + effect + rng.normal(0, 0.5, len(group))
        frame = pd.DataFrame({"y": y, "x1": x1, "x2": x2, "cell": group})
        table = an.ols_fe(frame, "y", ["x1", "x2"]).set_index("x")
        self.assertAlmostEqual(table.loc["x1", "coef"], 2.0, delta=0.05)
        self.assertAlmostEqual(table.loc["x2", "coef"], -1.0, delta=0.05)
        for x in ("x1", "x2"):
            self.assertLess(table.loc[x, "ci_low"], table.loc[x, "coef"])
            self.assertGreater(table.loc[x, "ci_high"], table.loc[x, "coef"])
        self.assertEqual(int(table["groups"].iloc[0]), n_groups)

    def test_a_constant_regressor_is_dropped(self):
        frame = pd.DataFrame({"y": [1.0, 2.0, 3.0, 4.0], "x": [1.0, 2.0, 3.0, 4.0],
                              "c": [1.0, 1.0, 1.0, 1.0], "cell": [0, 0, 1, 1]})
        table = an.ols_fe(frame, "y", ["x", "c"])
        self.assertEqual(list(table["x"]), ["x"])
        self.assertAlmostEqual(table["coef"].iloc[0], 1.0)


class TestTakeover(unittest.TestCase):
    def test_takeover_is_the_first_period_after_which_one_label_holds_90_percent(self):
        t = pd.Series(range(6))
        self.assertEqual(an.takeover_from_shares(t, pd.Series([0.5, 0.95, 0.6, 0.92, 0.95, 0.99])), 3)
        self.assertEqual(an.takeover_from_shares(t, pd.Series([0.5, 0.4, 0.05, 0.02, 0.0, 0.0])), 2)
        self.assertTrue(np.isnan(an.takeover_from_shares(t, pd.Series([0.5, 0.95, 0.95, 0.95, 0.95, 0.6]))))


class TestStage4(unittest.TestCase):
    def test_stage4_overrides_name_parameters_of_parameters_py(self):
        names = {k for k in vars(parameters) if k.isupper()}
        for cell, (_, overrides) in {**an.STAGE4, **an.B3}.items():
            for key in overrides:
                self.assertIn(key, names, cell)
        self.assertEqual(an.stage4_tasks(["b3-rbar-base"], 1, an.B3, "b3")[0][:2],
                         ("b3", "b3-rbar-base"))
        tasks = an.stage4_tasks(["anchor_r08", "tau_005"], 3)
        self.assertEqual(len(tasks), 2 * 3 * 3)
        self.assertEqual(tasks[0][:2], ("4", "anchor_r08"))

    def test_grid_resumes_merges_in_order_and_reruns_exactly(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            tmp = Path(tmp)
            sens_out = tmp / "sensitivity"
            sens.grid("smoke", 1, 1, sens_out)  # a runs.csv with the stage 1-3 columns
            path = tmp / "analysis" / "stage4_runs.csv"
            # A budget of 0 runs nothing; then two calls, the second resuming the first.
            self.assertEqual(an.grid4(["anchor_r08"], 2, 1, 0.0, path=path), 6)
            self.assertEqual(an.grid4(["anchor_r08"], 1, 1, 1e9, batch=2, path=path), 0)
            self.assertEqual(an.grid4(["anchor_r08"], 2, 1, 1e9, batch=2, path=path), 0)
            rows = pd.read_csv(path)
            self.assertEqual(len(rows), 6)
            self.assertFalse(rows["run_id"].duplicated().any())
            an.merge4(path, sens_out)
            runs = sens.load_runs(sens_out)
            stage4 = runs[runs["stage"] == "4"]
            self.assertEqual(
                list(stage4["run_id"]),
                [f"4_anchor_r08_{p}_s{s}" for p in an.POPULATION_ORDER for s in (1, 2)])
            cells = pd.read_csv(sens_out / "cells.csv", dtype={"stage": str})
            self.assertEqual(len(cells[cells["stage"] == "4"]), 3)
            with self.assertRaises(SystemExit):
                an.merge4(path, sens_out)
            new, diff = sens.rerun("4_anchor_r08_mixed_s2", tmp / "rerun",
                                   sens_out / "runs.csv", quiet=True)
            self.assertEqual(diff, [])


class TestStory(unittest.TestCase):
    def test_story_writes_one_figure_from_a_run_folder(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            tmp = Path(tmp)
            run.main(["--out", str(tmp / "run"), "--seed", "1", "--set", "PERIODS=40"])
            path = an.story(tmp / "run", "story_test", out=tmp / "figs", title="test")
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 10_000)


if __name__ == "__main__":
    unittest.main()
