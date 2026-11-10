"""The figure scripts draw, where matplotlib is installed. Figure 3 is drawn on a run of E2
and E3 with 2 seeds of 30 periods: the test is on the script, not on the numbers."""
import importlib.util
from dataclasses import fields, replace
import pathlib
import tempfile
import unittest
from unittest import mock

from experiments.cells import EXPERIMENTS
from experiments.harness import run_experiment, write_csv
from parameters import Parameters

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

    def test_figures_4_and_5_on_e4(self):
        from figures import fig4_heatmaps, fig5_decomposition
        small = {"E4": short(EXPERIMENTS["E4"])}
        run_experiment("E4", seeds=3, jobs=4, folder=self.base / "E4", experiments=small,
                       quiet=True)
        self.assert_drawn(fig4_heatmaps.main(self.base))
        self.assert_drawn(fig5_decomposition.main(self.base))
        self.assertEqual(fig5_decomposition.label("marx_universal_accelerator_g0.01_rbar0.16"),
                         "universal, accelerator, g = 1 %")

    def test_figure_6_the_morris_screening(self):
        from experiments.morris import NAMES, OUTCOMES
        from figures import fig6_morris
        rows = [{"outcome": outcome, "parameter": parameter, "mu_star": 0.1 * place,
                 "mu_star_low": 0.1 * place - 0.02, "mu_star_high": 0.1 * place + 0.02,
                 "mu": 0.0, "sigma": 0.05 * place}
                for outcome in OUTCOMES for place, parameter in enumerate(NAMES)]
        (self.base / "morris").mkdir()
        write_csv(self.base / "morris" / "morris.csv", rows, list(rows[0]))
        self.assert_drawn(fig6_morris.main(self.base))
        self.assertEqual(set(fig6_morris.WORDS), set(NAMES))

    def test_the_rules_of_figure_3_have_a_colour_each(self):
        from figures import style
        self.assertEqual(set(style.RULE_COLOUR), set(style.PRICING))
        self.assertEqual(len(set(style.RULE_COLOUR.values())), 4)


class TestTable3(unittest.TestCase):
    """The table needs no matplotlib: it is checked on the list of its rows."""

    def test_every_check_names_a_cell_of_its_experiment_and_the_cell_it_varies(self):
        from figures.tab3_robustness import checks
        rows = checks()
        self.assertEqual(len(rows), 1 + 3 + 3 + 2 + 2 + 3 + 12 + 2 * 5)
        for label, experiment, cell, base_experiment, base_cell in rows:
            self.assertIn(cell, EXPERIMENTS[experiment], label)
            self.assertIn(base_cell, EXPERIMENTS[base_experiment], label)
            changed = replace(Parameters(), **EXPERIMENTS[experiment][cell]["overrides"])
            base = replace(Parameters(), **EXPERIMENTS[base_experiment][base_cell]["overrides"])
            differing = [field.name for field in fields(Parameters)
                         if getattr(changed, field.name) != getattr(base, field.name)]
            self.assertEqual(len(differing), 1, (cell, base_cell, differing))

    def test_the_table_is_written_from_the_files_of_the_harness(self):
        from figures import tab3_robustness
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            names = {name for row in tab3_robustness.checks() for name in (row[1], row[3])}
            for name in sorted(names):
                run_experiment(name, seeds=2, jobs=4, folder=base / name, quiet=True,
                               experiments={name: short(EXPERIMENTS[name])})
            path = tab3_robustness.main(base, base / "figures")
            lines = path.read_text().splitlines()
            self.assertEqual(len(lines), 2 + len(tab3_robustness.checks()))
            self.assertIn("No overtime", lines[2])


if __name__ == "__main__":
    unittest.main()
