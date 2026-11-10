"""The Morris screening (experiments/morris.py): the design of the trajectories, the
elementary effects and the screening, on functions whose effects are known."""
import pathlib
import tempfile
import unittest

import numpy as np

from experiments.morris import (LEVELS, NAMES, OUTCOMES, PARAMETERS, elementary_effects,
                                experiment, main, overrides, screen, trajectories)
from helpers import industry


class TestDesign(unittest.TestCase):
    def setUp(self):
        self.points = trajectories(10, len(PARAMETERS), LEVELS, np.random.default_rng(0))

    def test_ten_trajectories_of_thirteen_points_on_a_grid_of_four_levels(self):
        self.assertEqual(self.points.shape, (10, 13, 12))
        grid = {0.0, 1 / 3, 2 / 3, 1.0}
        for value in self.points.ravel():
            self.assertTrue(any(abs(value - level) < 1e-12 for level in grid), value)

    def test_one_parameter_moves_at_each_step_and_each_moves_once(self):
        for trajectory in self.points:
            moved = []
            for before, after in zip(trajectory, trajectory[1:]):
                change = np.abs(after - before)
                self.assertEqual(int((change > 1e-12).sum()), 1)
                self.assertAlmostEqual(float(change.max()), 2 / 3, places=12)
                moved.append(int(change.argmax()))
            self.assertEqual(sorted(moved), list(range(12)))

    def test_the_sample_is_the_same_at_each_call(self):
        again = trajectories(10, len(PARAMETERS), LEVELS, np.random.default_rng(0))
        self.assertTrue((self.points == again).all())

    def test_a_point_gives_the_parameters_of_the_plan(self):
        low, high = overrides(np.zeros(12)), overrides(np.ones(12))
        self.assertEqual((low["bias"], high["bias"]), (0.5, 3.0))
        self.assertEqual((low["chi"], high["chi"]), (0.25, 4.0))
        self.assertEqual((low["plant_life"], high["plant_life"]), (7, 19))
        self.assertEqual((low["plant_size"], high["plant_size"]), (10.0, 40.0))
        self.assertEqual((low["u_max"], high["u_max"]), (1.0, 1.4))
        self.assertEqual((low["shortage_step"], high["shortage_step"]), (0.1, 0.5))
        self.assertNotIn("log2_chi", low)
        lives = {overrides(np.full(12, level))["plant_life"] for level in (0, 1 / 3, 2 / 3, 1)}
        self.assertEqual(lives, {7, 11, 15, 19})

    def test_every_point_builds_an_industry(self):
        cells = experiment(self.points, 100)
        self.assertEqual(len(cells), 130)
        for cell in list(cells.values())[::7]:
            self.assertEqual(len(industry(**cell["overrides"]).firms), 6)


class TestEffects(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(1)
        self.points = trajectories(10, 12, LEVELS, self.rng)

    def test_a_linear_outcome_gives_its_coefficients_and_no_spread(self):
        slopes = np.arange(12) - 4.0
        effects = elementary_effects(self.points, self.points @ slopes)
        self.assertTrue(np.allclose(effects, slopes))
        rows = screen(effects, self.rng)
        self.assertEqual([row["parameter"] for row in rows], list(NAMES))
        for row, slope in zip(rows, slopes):
            self.assertAlmostEqual(row["mu_star"], abs(slope), places=9)
            self.assertAlmostEqual(row["mu"], slope, places=9)
            self.assertAlmostEqual(row["sigma"], 0.0, places=9)
            self.assertAlmostEqual(row["mu_star_low"], row["mu_star_high"], places=9)

    def test_an_interaction_shows_in_sigma(self):
        outcome = self.points[:, :, 0] * self.points[:, :, 1] + 3.0 * self.points[:, :, 2]
        rows = {row["parameter"]: row for row in screen(
            elementary_effects(self.points, outcome), self.rng)}
        self.assertGreater(rows[NAMES[0]]["sigma"], 0.1)
        self.assertAlmostEqual(rows[NAMES[2]]["sigma"], 0.0, places=9)
        self.assertAlmostEqual(rows[NAMES[3]]["mu_star"], 0.0, places=9)

    def test_a_short_screening_writes_its_files(self):
        with tempfile.TemporaryDirectory() as folder:
            cut = {"periods": 25}
            import experiments.morris as module
            original = module.overrides
            module.overrides = lambda point: {**original(point), **cut}
            try:
                path = main(seeds=2, jobs=4, count=2, folder=pathlib.Path(folder), quiet=True)
            finally:
                module.overrides = original
            import csv
            with open(path, newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), len(OUTCOMES) * len(NAMES))
            self.assertEqual({row["outcome"] for row in rows}, set(OUTCOMES))
            self.assertTrue((pathlib.Path(folder) / "sample.csv").exists())


if __name__ == "__main__":
    unittest.main()
