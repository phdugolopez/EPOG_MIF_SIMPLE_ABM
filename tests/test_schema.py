"""The schema and the tables run.py writes: same columns in both directions, run_id
first, the runs table, the output folder and formats, and the generated documentation."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

import run
from analysis import schema_doc
from helpers import make_config, swapped_config
from model import Industry
from model.schema import SCHEMA, TABLES, columns

try:
    import pyarrow  # noqa: F401
    HAS_PYARROW = True
except ImportError:
    HAS_PYARROW = False


def frames_for(config, periods=None):
    industry = Industry(config)
    industry.run(periods)
    meta = run.runs_row(industry, "test_run", "test", "S50_O50", "BASE", 0.0)
    return run.tables(industry, meta)


class TestSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = make_config(PRICE_CUT=0.06, MIN_SHARE=0.05, INITIAL_DEBT=5_000.0)
        cls.frames = frames_for(cls.config)

    def test_every_table_matches_the_schema_both_ways(self):
        self.assertEqual(tuple(self.frames), TABLES)
        for table, frame in self.frames.items():
            expected = columns(table, self.config)
            self.assertEqual(len(expected), len(set(expected)), table)
            self.assertEqual(sorted(set(frame.columns) - set(expected)), [], table)
            self.assertEqual(sorted(set(expected) - set(frame.columns)), [], table)

    def test_swapped_labels_and_other_runs_match_too(self):
        for config in (swapped_config(PERIODS=40), make_config(PERIODS=40, CHECKS_RAISE=False)):
            for table, frame in frames_for(config).items():
                self.assertEqual(set(frame.columns), set(columns(table, config)), table)

    def test_run_id_is_the_first_column(self):
        for table, frame in self.frames.items():
            self.assertEqual(frame.columns[0], "run_id", table)
            self.assertEqual(set(frame["run_id"]), {"test_run"}, table)

    def test_every_column_is_described(self):
        for table, entries in SCHEMA.items():
            for c in entries:
                self.assertTrue(c.meaning and c.unit and c.mechanism, (table, c.name))
                self.assertIn(c.phase, ("v1", "later"))
                self.assertIn(c.step, (None, 0, 1, 2, 3, 4, 5, 6, 7))

    def test_generated_documentation_is_up_to_date(self):
        self.assertEqual(schema_doc.TARGET.read_text(), schema_doc.render(),
                         "run: python -m analysis.schema_doc")


class TestRuns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.row = frames_for(make_config(PERIODS=30))["runs"].iloc[0]

    def test_metadata(self):
        row = self.row
        self.assertEqual(row["seed"], 42)
        self.assertEqual(row["horizon"], 30)
        self.assertEqual(row["periods"], 30)
        self.assertEqual(row["n_check_fail"], 0)
        self.assertEqual(row["anchor"], "target_return")
        self.assertEqual(json.loads(row["menu"]), ["C", "D1", "D2"])
        self.assertEqual(json.loads(row["hurdle_rules"]),
                         {"shaikh": "unit_cost", "okishio": "profit_rate"})
        self.assertEqual(json.loads(row["shaikh_plants"])["C"], [120.0, 16_500.0, 78.0])
        version = row["code_version"]
        self.assertTrue(version == "unknown" or len(version.split("-")[0]) == 40, version)

    def test_param_hash(self):
        a, b = make_config(), make_config()
        self.assertEqual(run.param_hash(a), run.param_hash(b))
        self.assertNotEqual(run.param_hash(a), run.param_hash(make_config(SEED=43)))
        self.assertNotEqual(run.param_hash(a), run.param_hash(make_config(RBAR=0.17)))

    def test_run_id(self):
        self.assertEqual(run.make_run_id("selection", "BASE", "S50_O50", 7),
                         "selection_BASE_S50_O50_s7")


class TestMain(unittest.TestCase):
    def call(self, *argv):
        with contextlib.redirect_stdout(io.StringIO()):
            return run.main(list(argv))

    def test_csv_output_folder_and_seed(self):
        with tempfile.TemporaryDirectory() as out:
            frames = self.call("--out", out, "--seed", "7", "--experiment", "selection")
            for table in TABLES:
                read = pd.read_csv(Path(out) / f"{table}.csv")
                self.assertEqual(list(read.columns), list(frames[table].columns), table)
            runs = pd.read_csv(Path(out) / "runs.csv")
            self.assertEqual(runs.at[0, "seed"], 7)
            self.assertEqual(runs.at[0, "run_id"], "selection_baseline_baseline_s7")

    def test_the_default_seed_is_the_baseline(self):
        with tempfile.TemporaryDirectory() as out:
            frames = self.call("--out", out)
        baseline = Industry()
        baseline.run()
        macro = frames["macro"].drop(columns="run_id")
        pd.testing.assert_frame_equal(macro, pd.DataFrame(baseline.history))

    @unittest.skipUnless(HAS_PYARROW, "pyarrow not installed")
    def test_parquet(self):
        with tempfile.TemporaryDirectory() as out:
            frames = self.call("--out", out, "--format", "parquet")
            for table in TABLES:
                read = pd.read_parquet(Path(out) / f"{table}.parquet")
                self.assertEqual(list(read.columns), list(frames[table].columns), table)
                self.assertEqual(len(read), len(frames[table]), table)


if __name__ == "__main__":
    unittest.main()
