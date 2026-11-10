"""The figure scripts draw, where matplotlib is installed. Figure 3 is drawn on a run of E2
and E3 with 2 seeds of 30 periods: the test is on the script, not on the numbers."""
import importlib.util
import pathlib
import tempfile
import unittest
from unittest import mock

from experiments.cells import EXPERIMENTS
from experiments.harness import run_experiment

HAS_MATPLOTLIB = importlib.util.find_spec("matplotlib") is not None


def short(experiment: dict) -> dict:
    """The cells of an experiment, each cut to 30 periods."""
    return {name: {**cell, "overrides": {**cell["overrides"], "periods": 30}}
            for name, cell in experiment.items()}


@unittest.skipUnless(HAS_MATPLOTLIB, "matplotlib is not installed with this interpreter")
class TestFigures(unittest.TestCase):
    def setUp(self):
        from figures import style
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.base = pathlib.Path(self.directory.name)
        patch = mock.patch.object(style, "FOLDER", self.base / "figures")
        patch.start()
        self.addCleanup(patch.stop)

    def assert_drawn(self, path):
        self.assertEqual(path.parent, self.base / "figures")
        for suffix in (".pdf", ".png"):
            self.assertGreater(path.with_suffix(suffix).stat().st_size, 5000)

    def test_figure_1_the_conflict_zone(self):
        from figures import fig1_conflict_zone
        self.assert_drawn(fig1_conflict_zone.main())
        self.assertAlmostEqual(fig1_conflict_zone.crossing("D1", "D2"), 85.15, places=2)

    def test_figure_2_a_typical_run(self):
        from figures import fig2_typical_run
        self.assert_drawn(fig2_typical_run.main(seed=1))

    def test_figure_3_the_bias_and_lambda(self):
        from figures import fig3_bias_lambda
        small = {name: short(EXPERIMENTS[name]) for name in ("E2", "E3")}
        for name in small:
            run_experiment(name, seeds=2, jobs=4, folder=self.base / name, experiments=small,
                           quiet=True)
        self.assert_drawn(fig3_bias_lambda.main(self.base))

    def test_the_rules_of_figure_3_have_a_colour_each(self):
        from figures import style
        self.assertEqual(set(style.RULE_COLOUR), set(style.PRICING))
        self.assertEqual(len(set(style.RULE_COLOUR.values())), 4)


if __name__ == "__main__":
    unittest.main()
