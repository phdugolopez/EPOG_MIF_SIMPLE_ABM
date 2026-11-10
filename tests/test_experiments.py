"""The run row (experiments/summary.py), the statistics of a cell (experiments/stats.py) and
the harness (experiments/harness.py)."""
import csv
import math
import pathlib
import tempfile
import unittest

from experiments.cells import ALL, EXPERIMENTS
from experiments.harness import columns, number, run_experiment, summarise
from experiments.stats import beyond_drift, disjoint, mean_interval, wilson
from experiments.summary import average, growth, outcome, ratio, run_row, takeover, total
from model.model import run

SMALL = {"T": {"seeds": 4, "populations": ALL, "cells": {
    "short": {"periods": 25}, "short_systematic": {"periods": 25, "pricing": "systematic"}}}}


def read(folder, name="runs.csv", drop=("wall_s",)):
    """The rows of a file of the harness, without the columns that differ between two runs."""
    with open(pathlib.Path(folder) / name, newline="") as file:
        return [{key: value for key, value in row.items() if key not in drop}
                for row in csv.DictReader(file)]


class TestStats(unittest.TestCase):
    def test_wilson_interval(self):
        low, high = wilson(81, 100)
        self.assertAlmostEqual(low, 0.722, places=3)
        self.assertAlmostEqual(high, 0.875, places=3)
        self.assertEqual(wilson(0, 10)[0], 0.0)
        self.assertAlmostEqual(wilson(10, 10)[1], 1.0, places=12)
        self.assertTrue(all(math.isnan(bound) for bound in wilson(0, 0)))

    def test_beyond_drift_needs_an_interval_disjoint_from_both_controls(self):
        self.assertTrue(beyond_drift((0.77, 0.84), (0.38, 0.52), (0.44, 0.58)))
        self.assertFalse(beyond_drift((0.55, 0.70), (0.38, 0.52), (0.44, 0.58)))
        self.assertTrue(beyond_drift((0.10, 0.19), (0.38, 0.52), (0.44, 0.58)))
        self.assertFalse(beyond_drift((math.nan, math.nan), (0.38, 0.52), (0.44, 0.58)))
        self.assertTrue(disjoint((0.1, 0.2), (0.3, 0.4)))
        self.assertFalse(disjoint((0.1, 0.3), (0.3, 0.4)))

    def test_mean_and_its_interval(self):
        mean, low, high = mean_interval([1.0, 2.0, 3.0, 4.0])
        self.assertEqual(mean, 2.5)
        self.assertAlmostEqual(high - mean, 1.96 * math.sqrt(5 / 3 / 4), places=12)
        self.assertAlmostEqual(mean - low, high - mean, places=12)
        self.assertEqual(mean_interval([7.0]), (7.0, 7.0, 7.0))
        self.assertTrue(math.isnan(mean_interval([])[0]))


class TestCells(unittest.TestCase):
    def test_the_experiments_have_the_cells_of_the_proposal(self):
        counts = {name: (len(e["cells"]), len(e["populations"]), e["seeds"])
                  for name, e in EXPERIMENTS.items()}
        self.assertEqual(counts["E0"], (1, 2, 50))
        self.assertEqual(counts["E1"], (1, 3, 500))
        self.assertEqual(counts["E2"], (6, 3, 200))
        self.assertEqual(counts["E3"], (20, 3, 200))
        runs = sum(cells * populations * seeds for cells, populations, seeds in counts.values())
        self.assertEqual(runs, 100 + 1500 + 3600 + 12000)

    def test_cell_names_say_what_they_change(self):
        self.assertEqual(list(EXPERIMENTS["E2"]["cells"]),
                         ["beta_0", "beta_0.5", "beta_1.5", "beta_3", "neutral", "none"])
        self.assertEqual(EXPERIMENTS["E3"]["cells"]["lam_0.25_systematic_rbar_0.16"],
                         {"lam": 0.25, "pricing": "systematic", "rbar": 0.16})


class TestSummarise(unittest.TestCase):
    def rows(self, population, outcomes):
        return [{**dict.fromkeys(columns(), ""), "cell": "c", "population": population,
                 "seed": seed, "outcome": result, "cap_share_end": share, "error": ""}
                for seed, (result, share) in enumerate(outcomes)]

    def test_ties_are_counted_apart_and_left_out_of_the_share_won(self):
        outcomes = [("win", 0.6)] * 3 + [("loss", 0.4)] + [("tie", 0.5)] * 2
        cell, = summarise(self.rows("mixed", outcomes), columns())
        self.assertEqual((cell["won"], cell["lost"], cell["tied"]), (3, 1, 2))
        self.assertEqual(cell["share_won"], 0.75)
        self.assertEqual((cell["won_low"], cell["won_high"]), wilson(3, 4))
        self.assertAlmostEqual(cell["cap_share_end"], 3.2 / 6, places=12)

    def test_errors_and_undecided_runs_count_in_no_share(self):
        rows = self.rows("mixed", [("win", 0.6), ("undecided", ""), ("loss", 0.4)])
        rows.append({**rows[0], "seed": 3, "outcome": "", "error": "ValueError: x"})
        cell, = summarise(rows, columns())
        self.assertEqual((cell["n_seeds"], cell["n_error"], cell["n_undecided"]), (4, 1, 1))
        self.assertEqual(cell["share_won"], 0.5)

    def test_a_mixed_row_is_set_against_its_two_controls(self):
        rows = (self.rows("mixed", [("win", 0.9)] * 19 + [("loss", 0.2)])
                + self.rows("all_unit_cost", [("win", 0.6)] * 10 + [("loss", 0.4)] * 10)
                + self.rows("all_profit_rate", [("win", 0.6)] * 8 + [("loss", 0.4)] * 12))
        cells = {cell["population"]: cell for cell in summarise(rows, columns())}
        mixed = cells["mixed"]
        self.assertEqual((mixed["ctrl_uc_share_won"], mixed["ctrl_pr_share_won"]), (0.5, 0.4))
        self.assertAlmostEqual(mixed["gap"], 0.95 - 0.45, places=12)
        self.assertTrue(mixed["beyond_drift"])
        self.assertNotIn("gap", cells["all_unit_cost"])

    def test_a_cell_of_a_file_is_read_as_a_number_or_nothing(self):
        self.assertEqual([number(x) for x in ("0.5", "", None, "True", False, "win", 3)],
                         [0.5, None, None, 1.0, 0.0, None, 3.0])


class TestHarness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.base = pathlib.Path(cls.directory.name)
        run_experiment("T", jobs=1, folder=cls.base / "one", experiments=SMALL, quiet=True)
        run_experiment("T", jobs=2, folder=cls.base / "two", experiments=SMALL, quiet=True)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_one_row_a_run_in_the_order_cell_population_seed(self):
        rows = read(self.base / "one")
        self.assertEqual(len(rows), 2 * 3 * 4)
        order = [(row["cell"], row["population"], int(row["seed"])) for row in rows]
        expected = [(cell, population, seed) for cell in SMALL["T"]["cells"] for population in ALL
                    for seed in range(4)]
        self.assertEqual(order, expected)
        self.assertTrue(all(row["error"] == "" for row in rows))

    def test_the_number_of_workers_does_not_change_the_runs(self):
        self.assertEqual(read(self.base / "one"), read(self.base / "two"))
        drop = ("wall_s", "wall_s_low", "wall_s_high")
        self.assertEqual(read(self.base / "one", "cells.csv", drop),
                         read(self.base / "two", "cells.csv", drop))

    def test_a_run_of_the_harness_is_the_run_of_the_model(self):
        row = read(self.base / "one")[0]
        params_row = run_row(run(_params(periods=25), 0).rows, _params(periods=25), 0)
        self.assertEqual(row["outcome"], params_row["outcome"])
        self.assertEqual(float(row["capacity_end"]), params_row["capacity_end"])
        self.assertEqual(row["overrides"], '{"periods": 25}')

    def test_cells_csv_has_one_row_per_cell_and_population(self):
        cells = read(self.base / "one", "cells.csv")
        self.assertEqual(len(cells), 6)
        self.assertEqual({cell["n_seeds"] for cell in cells}, {"4"})
        mixed = [cell for cell in cells if cell["population"] == "mixed"]
        self.assertTrue(all(cell["ctrl_uc_share_won"] != "" for cell in mixed))

    def test_a_run_stopped_and_resumed_gives_the_same_file(self):
        """runs.csv is cut after the first complete groups and two rows of the next one."""
        folder = self.base / "resumed"
        folder.mkdir()
        lines = (self.base / "one" / "runs.csv").read_text().splitlines(keepends=True)
        (folder / "runs.csv").write_text("".join(lines[:1 + 2 * 4 + 2]))
        run_experiment("T", jobs=2, resume=True, folder=folder, experiments=SMALL, quiet=True)
        self.assertEqual(read(folder), read(self.base / "one"))

    def test_the_period_table_of_a_named_seed_is_kept(self):
        folder = self.base / "kept"
        small = {"T": {"seeds": 2, "populations": ("mixed",), "cells": {"short": {"periods": 25}}}}
        run_experiment("T", folder=folder, keep_periods=(1,), experiments=small, quiet=True)
        self.assertEqual(len(read(folder, "periods_short_mixed_1.csv")), 50)
        self.assertFalse((folder / "periods_short_mixed_0.csv").exists())

    def test_a_run_that_fails_is_reported_and_the_experiment_goes_on(self):
        folder = self.base / "failing"
        bad = {"T": {"seeds": 2, "populations": ("mixed",),
                     "cells": {"bad": {"periods": 5, "no_such_parameter": 1}, "good": {"periods": 5}}}}
        run_experiment("T", folder=folder, experiments=bad, quiet=True)
        rows = read(folder)
        self.assertTrue(all("TypeError" in row["error"] for row in rows[:2]))
        self.assertTrue(all(row["error"] == "" for row in rows[2:]))
        cells = read(folder, "cells.csv")
        self.assertEqual([cell["n_error"] for cell in cells], ["2", "0"])


def _params(**overrides):
    from dataclasses import replace
    from parameters import Parameters
    return replace(Parameters(), **overrides)


class TestOutcome(unittest.TestCase):
    def test_win_loss_tie_and_undecided(self):
        self.assertEqual([outcome(share) for share in (0.6, 0.4, 0.5, None)],
                         ["win", "loss", "tie", "undecided"])
        self.assertEqual(outcome(0.5 + 1e-12), "tie")
        self.assertEqual(outcome(0.51), "win")


class TestTakeover(unittest.TestCase):
    def test_first_period_after_which_one_label_holds_nine_tenths_to_the_end(self):
        self.assertEqual(takeover([0.5, 0.6, 0.95, 0.92, 0.99]), (2, "shaikh"))
        self.assertEqual(takeover([0.5, 0.95, 0.8, 0.95, 0.97]), (3, "shaikh"))
        self.assertEqual(takeover([0.5, 0.05, 0.02]), (1, "okishio"))

    def test_no_takeover_when_the_share_is_lost_before_the_end(self):
        self.assertEqual(takeover([0.5, 0.95, 0.7]), (None, None))
        self.assertEqual(takeover([0.5, 0.6, 0.9]), (None, None))

    def test_held_from_the_start_and_periods_without_capacity(self):
        self.assertEqual(takeover([0.95, 0.99]), (0, "shaikh"))
        self.assertEqual(takeover([None, 0.95]), (1, "shaikh"))
        self.assertEqual(takeover([0.95, None]), (None, None))


class TestHelpers(unittest.TestCase):
    def test_sums_means_and_ratios_skip_what_is_not_defined(self):
        rows = [{"x": 1.0}, {"x": None}, {"x": 3.0}]
        self.assertEqual(total(rows, "x"), 4.0)
        self.assertEqual(average(rows, "x"), 2.0)
        self.assertIsNone(average([{"x": None}], "x"))
        self.assertIsNone(ratio(1.0, 0.0))

    def test_growth_is_the_log_change_a_period_between_the_first_and_last_values(self):
        rows = [{"t": 0, "x": None}, {"t": 1, "x": 100.0}, {"t": 2, "x": 50.0}, {"t": 5, "x": 90.0}]
        self.assertAlmostEqual(growth(rows, "x"), -0.10536051565782628 / 4, places=12)
        self.assertIsNone(growth(rows[:2], "x"))


class TestRunRow(unittest.TestCase):
    def setUp(self):
        industry = run(seed=0)
        self.rows, self.row = industry.rows, run_row(industry.rows, industry.params, 0)

    def test_the_outcome_is_read_at_the_end_of_the_last_period(self):
        last = self.rows[-2:]
        share = last[0]["capacity_next"] / (last[0]["capacity_next"] + last[1]["capacity_next"])
        self.assertEqual(self.row["cap_share_end"], share)
        self.assertEqual(self.row["outcome"], outcome(share))
        self.assertEqual(self.row["capacity_end"], last[0]["capacity_next"] + last[1]["capacity_next"])

    def test_counts_and_shares_are_consistent(self):
        row = self.row
        self.assertEqual(row["entries"], row["entries_shaikh"] + row["entries_okishio"])
        self.assertEqual(row["exits"], row["exits_shaikh"] + row["exits_okishio"])
        self.assertEqual(row["firms_end"], 6 + row["entries"] - row["exits"])
        self.assertAlmostEqual(row["retired_age"] + row["retired_cost"] + row["retired_idle"], 1.0,
                               places=12)
        self.assertEqual(row["dk_accumulation"], row["dk_ordered"] + row["dk_retired"])
        for key in ("open_share", "war_freq", "leader_cheapest", "util_mean", "lost_share"):
            self.assertTrue(0.0 <= row[key] <= 1.0, key)

    def test_the_unit_cost_label_never_orders_a_dearer_technique(self):
        self.assertEqual(self.row["shaikh_dearer"], 0.0)
        self.assertEqual(self.row["hurdle_shaikh"], 0.0)
        self.assertGreater(self.row["hurdle_okishio"], 0.0)


if __name__ == "__main__":
    unittest.main()
