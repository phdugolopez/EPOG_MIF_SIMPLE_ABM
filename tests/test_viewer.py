"""The run viewer (experiments/show_run.py): its tables on a short run, the settings given
as name=value, and its figure where matplotlib is installed."""
import csv
import importlib.util
import pathlib
import tempfile
import unittest
from dataclasses import replace
from math import fsum, log

from experiments.show_run import (FIRM_COLUMNS, PRICE_COLUMNS, convert, price_spread,
                                  read_settings, run_name, show_run, trace)
from model.model import run
from model.outputs import KEYS
from parameters import LABELS, Parameters

HAS_MATPLOTLIB = importlib.util.find_spec("matplotlib") is not None


def read(path) -> list[dict]:
    with open(path, newline="") as file:
        return list(csv.DictReader(file))


class TestTrace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params = replace(Parameters(), periods=60)
        cls.industry, cls.firm_rows = trace(cls.params, seed=0)

    def test_the_period_table_is_that_of_a_run_of_the_model(self):
        self.assertEqual(self.industry.rows, run(self.params, seed=0).rows)
        for overrides in ({"pricing": "universal", "investment": "accelerator"},
                          {"rule_okishio": "unit_cost", "tech_change": "none"}):
            params = replace(Parameters(), periods=30, **overrides)
            self.assertEqual(trace(params, 4)[0].rows, run(params, 4).rows)

    def test_the_run_has_entries_and_exits(self):
        self.assertGreater(sum(row["entered"] for row in self.firm_rows), 0)
        self.assertGreater(sum(row["left"] for row in self.firm_rows), 0)

    def test_one_row_per_firm_and_period(self):
        keys = [(row["t"], row["firm"]) for row in self.firm_rows]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(keys, sorted(keys))
        self.assertEqual({t for t, _ in keys}, set(range(60)))
        for row in self.firm_rows:
            self.assertEqual(list(row), list(FIRM_COLUMNS))

    def test_the_firms_of_a_period_are_those_of_the_period_table_and_the_entrant(self):
        for t in range(60):
            rows = [row for row in self.firm_rows if row["t"] == t]
            at_step_3 = sum(row["firms"] for row in self.industry.rows if row["t"] == t)
            self.assertEqual(len(rows) - sum(row["entered"] for row in rows), at_step_3)

    def test_a_firm_that_left_has_a_row_in_its_last_period_and_none_after(self):
        for row in self.firm_rows:
            if row["left"]:
                later = [other for other in self.firm_rows
                         if other["firm"] == row["firm"] and other["t"] > row["t"]]
                self.assertEqual(later, [])
                self.assertEqual(row["exits"], 1.0)
                self.assertIsNone(row["share_end"])
                self.assertIsNotNone(row["hurdle"])

    def test_an_entrant_has_a_row_in_its_first_period_with_its_plants_on_order(self):
        entrants = [row for row in self.firm_rows if row["entered"]]
        for row in entrants:
            self.assertEqual((row["born"], row["plants"], row["capacity"]), (row["t"], 0, 0.0))
            self.assertGreater(row["on_order"], 0.0)
            self.assertEqual(row["cap_entry"], row["on_order"])
            self.assertEqual(row["entries"], 1.0)
            self.assertGreater(row["share_end"], 0.0)
            self.assertIsNone(row["unit_cost"])

    def test_the_flows_of_the_firms_sum_to_those_of_their_label(self):
        for row in self.industry.rows:
            firms = [firm for firm in self.firm_rows
                     if firm["t"] == row["t"] and firm["label"] == row["label"]]
            for key in KEYS:
                self.assertAlmostEqual(fsum(firm[key] for firm in firms), row[key], places=9,
                                       msg=(row["t"], row["label"], key))

    def test_the_stocks_of_the_firms_sum_to_those_of_their_label(self):
        for row in self.industry.rows:
            firms = [firm for firm in self.firm_rows if firm["t"] == row["t"]
                     and firm["label"] == row["label"] and not firm["entered"]]
            for key in ("capacity", "sales", "profit", "share"):
                self.assertAlmostEqual(fsum(firm[key] for firm in firms), row[key], places=9)
            staying = [firm["share_end"] for firm in self.firm_rows if firm["t"] == row["t"]
                       and firm["label"] == row["label"] and not firm["left"]]
            self.assertAlmostEqual(fsum(staying), row["share_end"], places=9)

    def test_the_floor_is_the_unit_cost_of_the_best_plant_at_the_defaults(self):
        for row in self.firm_rows:
            if row["plants"] > 0:
                self.assertEqual(row["floor"], row["unit_cost"])
            else:
                self.assertIsNone(row["floor"])


class TestPriceSpread(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params = replace(Parameters(), periods=60)
        cls.industry, cls.firm_rows = trace(cls.params, seed=0)
        cls.rows = price_spread(cls.industry.rows, cls.firm_rows)

    def test_one_row_a_period_with_its_columns(self):
        self.assertEqual([row["t"] for row in self.rows], list(range(60)))
        for row in self.rows:
            self.assertEqual(list(row), list(PRICE_COLUMNS))

    def test_the_lowest_price_and_the_industry_price_are_those_of_the_period_table(self):
        for row, period in zip(self.rows, self.industry.rows[::2]):
            self.assertEqual(row["low"], period["low_price"])
            self.assertEqual(row["price_over_reg"], period["price_over_reg"])
            self.assertEqual(row["war"], period["war"])

    def test_the_dispersion_is_consistent(self):
        for row in self.rows:
            if row["priced"] == 0:
                continue
            self.assertLessEqual(row["low"], row["mean"] + 1e-12)
            self.assertLessEqual(row["mean"], row["high"] + 1e-12)
            self.assertGreaterEqual(row["sd"], 0.0)
            self.assertAlmostEqual(row["cv"], row["sd"] / row["mean"], places=12)
            if row["priced"] == 1:
                self.assertEqual(row["spread"], 0.0)

    def test_the_change_is_the_log_change_of_the_industry_price(self):
        self.assertIsNone(self.rows[0]["change"])
        for before, now in zip(self.rows, self.rows[1:]):
            if before["price"] and now["price"]:
                self.assertAlmostEqual(now["change"], log(now["price"] / before["price"]))


class TestSettings(unittest.TestCase):
    def test_a_value_is_converted_by_the_type_of_its_field(self):
        self.assertEqual(convert("rbar", "0.05"), 0.05)
        self.assertEqual(convert("periods", "30"), 30)
        self.assertEqual(convert("pricing", "universal"), "universal")
        self.assertEqual(convert("public_lag", "3"), 3)
        self.assertIsNone(convert("public_lag", "none"))
        self.assertIsInstance(convert("plant_life", "7"), int)
        self.assertIsInstance(convert("plant_size", "40"), float)

    def test_a_wrong_name_or_a_value_of_the_wrong_type_is_refused(self):
        for name, text in (("u_target", "0.9"), ("price_rule", "universal"), ("periods", "3.5"),
                           ("rbar", "low"), ("start", "D1")):
            with self.assertRaises(ValueError, msg=name):
                convert(name, text)

    def test_the_settings_give_the_overrides_and_the_population(self):
        overrides, population = read_settings(["pricing=universal", "rbar=0.05",
                                               "population=all_unit_cost"])
        self.assertEqual(overrides, {"pricing": "universal", "rbar": 0.05})
        self.assertEqual(population, "all_unit_cost")
        self.assertEqual(read_settings([]), ({}, "mixed"))
        for pairs in (["population=all"], ["pricing"], ["no_such=1"]):
            with self.assertRaises(ValueError):
                read_settings(pairs)

    def test_a_misspelt_level_is_refused_by_the_model(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                show_run(["pricing=leader_follow"], figure=False, folder=pathlib.Path(folder))

    def test_the_folder_is_named_after_the_settings_and_the_seed(self):
        self.assertEqual(run_name([], 0), "defaults_seed_0")
        self.assertEqual(run_name(["rbar=0.05", "pricing=universal"], 7),
                         "pricing=universal_rbar=0.05_seed_7")


class TestFiles(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.base = pathlib.Path(self.directory.name)

    def test_the_tables_of_a_run_of_30_periods(self):
        folder = show_run(["periods=30", "population=all_profit_rate"], seed=2, figure=False,
                          folder=self.base)
        self.assertEqual(folder.name, "periods=30_population=all_profit_rate_seed_2")
        params = replace(Parameters(), periods=30, rule_shaikh="profit_rate")
        expected = run(params, seed=2).rows
        periods = read(folder / "periods.csv")
        self.assertEqual(len(periods), 60)
        self.assertEqual(list(periods[0]), list(expected[0]))
        for written, row in zip(periods, expected):
            for column in ("t", "label", "rule", "capacity", "sales", "price", "r_new"):
                self.assertEqual(written[column], "" if row[column] is None
                                 else str(row[column]))
        firms = read(folder / "firms.csv")
        self.assertEqual(list(firms[0]), list(FIRM_COLUMNS))
        self.assertEqual({row["label"] for row in firms}, set(LABELS))
        self.assertEqual({row["rule"] for row in firms}, {"profit_rate"})
        self.assertEqual(len(read(folder / "run.csv")), 1)
        prices = read(folder / "prices.csv")
        self.assertEqual(list(prices[0]), list(PRICE_COLUMNS))
        self.assertEqual(len(prices), 30)
        text = (folder / "run.txt").read_text()
        for phrase in ("Outcome for the unit-cost label", "E0, on periods 20 to 29",
                       "every line:", "through the price",
                       "Variability of prices, periods 20 to 29"):
            self.assertIn(phrase, text)
        self.assertFalse((folder / "run.pdf").exists())

    def test_the_folder_can_be_named(self):
        folder = show_run(["periods=5"], name="short", figure=False, folder=self.base)
        self.assertEqual(folder, self.base / "short")

    @unittest.skipUnless(HAS_MATPLOTLIB, "matplotlib is not installed with this interpreter")
    def test_the_figure_is_drawn(self):
        for by_firm in (False, True):
            folder = show_run(["periods=40"], seed=1, by_firm=by_firm, folder=self.base)
            self.assertGreater((folder / "run.pdf").stat().st_size, 10000)
            self.assertGreater((folder / "run.png").stat().st_size, 10000)

    @unittest.skipIf(HAS_MATPLOTLIB, "matplotlib is installed with this interpreter")
    def test_without_matplotlib_the_tables_are_written_and_the_figure_is_not(self):
        folder = show_run(["periods=5"], folder=self.base)
        self.assertTrue((folder / "firms.csv").exists())
        self.assertFalse((folder / "run.pdf").exists())


if __name__ == "__main__":
    unittest.main()
