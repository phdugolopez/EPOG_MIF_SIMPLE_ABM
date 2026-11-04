"""Smoke tests of the debugging plots (debug/): each script runs on a 40-period baseline
and on a run where one firm holds three plants and another exits with a plant on order,
and writes its figures. compare_runs finds no difference between a run and itself, its
label-swapped twin or its tables under the names used before the brief's; it finds the
first divergence between two different runs."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from debug import (capacity_bridge, checks, compare_runs, events_timeline, firm_panel,
                   flow_matrix, merit_order, plant_gantt, report)
from debug._common import load
from helpers import make_config, swapped_config, three_plant_industry, write_run
from model import Industry


def quiet(function, *args):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        result = function(*args)
    return result, out.getvalue()


def baseline(config, periods=40):
    industry = Industry(config)
    industry.run(periods)
    return industry


class DebugPlotsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        cls.base = root / "base"
        write_run(baseline(make_config()), cls.base, "base")
        cls.swapped = root / "swapped"
        write_run(baseline(swapped_config()), cls.swapped, "swapped")
        cls.three = root / "three"
        industry = three_plant_industry()[0]
        industry.run(12)
        write_run(industry, cls.three, "three")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def assert_written(self, paths):
        self.assertTrue(paths)
        for path in paths:
            self.assertTrue(path.exists(), path)
            self.assertGreater(path.stat().st_size, 1000, path)
            self.assertEqual(path.parent.name, "debug")

    def run_each(self, folder, merit_periods, firm_panel_options):
        d = str(folder)
        for script, extra in (
            (checks, []),
            *((firm_panel, options) for options in firm_panel_options),
            (plant_gantt, []),
            (merit_order, []),
            (merit_order, sum((["--t", str(t)] for t in merit_periods), [])),
            (merit_order, sum((["--t", str(t)] for t in merit_periods), []) + ["--firm", "0"]),
            (events_timeline, []),
            (capacity_bridge, []),
            (flow_matrix, ["--t", "0"]),
        ):
            with self.subTest(script=script.__name__, options=extra):
                paths, _ = quiet(script.main, [d, *extra])
                self.assert_written(paths)

    def test_every_script_on_the_baseline(self):
        """firm_panel --all here (every firm, entrants included); the default choice of
        firms and --firm on the smaller run below."""
        self.run_each(self.base, [2, 20], [["--all"]])

    def test_every_script_with_three_plants_and_an_exit_with_an_order(self):
        events = pd.read_csv(self.three / "events.csv")
        first = events[events["t"] == 0]
        self.assertIn("cancel", set(first["event"]))  # the case the brief asks for
        self.assertIn(3, set(pd.read_csv(self.three / "firms.csv").query("t == 0")["n_plants"]))
        self.run_each(self.three, [0, 5], [[], ["--firm", "0"]])

    def test_the_gantt_has_a_lane_for_the_cancelled_order(self):
        run = load(self.three)
        spans = plant_gantt.plant_spans(run)
        self.assertIn("cancelled", set(spans["cause"]))
        self.assertTrue({"age", "replacement"} <= set(spans["cause"]))
        lanes = plant_gantt.lanes(run)
        self.assertEqual(lanes["n_plants"].sum(), len(spans))  # every plant in one lane
        self.assertIn(["cancelled"], lanes["causes"].tolist())

    def test_checks_report_no_failure(self):
        _, out = quiet(checks.main, [str(self.base)])
        self.assertIn("All checks pass", out)

    def test_report_writes_one_pdf(self):
        """On the three-plant run, whose scripts the test above already exercised one by
        one on the baseline: the report is rendered once per suite."""
        path, out = quiet(report.main, [str(self.three)])
        self.assertEqual(path, self.three / "debug" / "report.pdf")
        self.assertGreater(path.stat().st_size, 10000)
        self.assertNotIn("skipping", out)

    def test_report_skips_pages_whose_tables_are_missing(self):
        """A folder written before the event log and the groups table (the reference
        run): the pages that need them are skipped with a note, the others drawn."""
        partial = Path(self.tmp.name) / "partial"
        partial.mkdir()
        for table in ("macro", "firms", "plants", "flows"):
            (partial / f"{table}.csv").write_bytes((self.three / f"{table}.csv").read_bytes())
        path, out = quiet(report.main, [str(partial)])
        self.assertTrue(path.exists())
        self.assertIn("skipping events_timeline", out)
        self.assertIn("skipping capacity_bridge", out)
        with self.assertRaises(SystemExit) as stop:
            quiet(events_timeline.main, [str(partial)])
        self.assertIn("no events table", str(stop.exception))

    def test_compare_finds_nothing_between_a_run_and_itself(self):
        result, out = quiet(compare_runs.main, [str(self.base), str(self.base)])
        self.assertTrue(result.identical, out)

    def test_compare_with_swapped_labels_finds_nothing(self):
        """The label-swap test on every table at once."""
        result, out = quiet(compare_runs.main,
                            [str(self.base), str(self.swapped), "--swap-labels"])
        self.assertTrue(result.identical, out)
        result, _ = quiet(compare_runs.main, [str(self.base), str(self.swapped)])
        self.assertFalse(result.identical)

    def test_compare_reads_the_names_used_before_the_brief(self):
        legacy = Path(self.tmp.name) / "legacy"
        legacy.mkdir()
        for table, names in compare_runs.LEGACY.items():
            frame = pd.read_csv(self.base / f"{table}.csv")
            back = {new: old for old, new in names.items()}
            frame.rename(columns=back).to_csv(legacy / f"{table}.csv", index=False)
        result, out = quiet(compare_runs.main, [str(self.base), str(legacy)])
        self.assertTrue(result.identical, out)

    def test_compare_reports_the_first_divergence(self):
        result, out = quiet(compare_runs.main, [str(self.base), str(self.three)])
        self.assertFalse(result.identical)
        self.assertEqual(result.first["t"], 0)
        self.assertIn("First divergence: t = 0", out)
        # The PNG goes next to the run under test (RUN_B), never into the reference.
        self.assertTrue(any(p.name.startswith("compare_base_vs_three") for p in
                            (self.three / "debug").iterdir()))
        self.assertFalse(any(p.name.startswith("compare_base_vs_three") for p in
                             (self.base / "debug").iterdir()))


if __name__ == "__main__":
    unittest.main()
