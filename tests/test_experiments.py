"""The run row with the measures of E0 (experiments/summary.py), the statistics of a cell
(stats.py), the cells and the populations, the harness and the gate (e0_gate.py)."""
import csv
import math
import pathlib
import tempfile
import unittest
from dataclasses import replace

from experiments.cells import EXPERIMENTS, PRICE_RULES, cells, runs
from experiments.e0_gate import gate, read_cells, report, verdicts
from experiments.harness import columns, number, run_experiment, summarise
from experiments.populations import ALL, CONTROLS, POPULATIONS, homogeneous, invasion
from experiments.stats import beyond_drift, disjoint, mean_interval, wilson
from experiments.summary import (E0_LINES, E0_START, average, crossings, e0_measures, growth,
                                 outcome, ratio, run_row, takeover, total)
from helpers import industry
from model.model import run
from parameters import Parameters

SMALL = {"T": cells({"short": {"periods": 25},
                     "short_systematic": {"periods": 25, "pricing": "systematic"}}, ALL, 4)}


def read(folder, name="runs.csv", drop=("wall_s",)):
    """The rows of a file of the harness, without the columns that differ between two runs."""
    with open(pathlib.Path(folder) / name, newline="") as file:
        return [{key: value for key, value in row.items() if key not in drop}
                for row in csv.DictReader(file)]

RBAR = 0.16


def table(periods: int = 60, **columns) -> tuple[list[dict], list[dict]]:
    """A period table made by hand, as the rows of the two labels. It passes every line of
    E0: the price crosses the price of production every third period. A column given as a
    function of t replaces the default from E0_START on."""
    u, o = [], []
    for t in range(periods):
        row = {
            "t": t, "leader_cheapest": 1, "price_over_reg": 1.05 if t % 6 < 3 else 0.95,
            "capacity": 50.0, "demand": 95.0, "r_new": 0.16, "lost": 1.0,
            "rate_high": 0.20, "rate_low": 0.10, "profit": 13.0, "capital": 100.0,
        }
        if t >= E0_START:
            row.update({name: value(t) for name, value in columns.items()})
        u.append(row)
        o.append(dict(row))
    return u, o


def measures(periods: int = 60, rbar: float = RBAR, capacity_end: float = 100.0, **columns):
    return e0_measures(*table(periods, **columns), rbar, capacity_end)


class TestCrossings(unittest.TestCase):
    def test_a_crossing_either_way_counts_once(self):
        self.assertEqual(crossings([0.9, 1.1]), 1)
        self.assertEqual(crossings([1.1, 0.9]), 1)
        self.assertEqual(crossings([0.9, 1.1, 1.2, 0.8, 0.7, 1.3]), 3)
        self.assertEqual(crossings([0.9, 0.95, 0.99]), 0)
        self.assertEqual(crossings([]), 0)

    def test_a_period_without_a_price_or_exactly_on_the_line_is_skipped(self):
        self.assertEqual(crossings([0.9, None, 1.1]), 1)
        self.assertEqual(crossings([0.9, None, 0.8]), 0)
        self.assertEqual(crossings([0.9, 1.0, 1.1]), 1)
        self.assertEqual(crossings([0.9, 1.0, 0.9]), 0)


class TestE0Measures(unittest.TestCase):
    def test_the_measures_of_the_table_made_by_hand(self):
        e0 = measures()
        self.assertEqual(e0["e0_leader"], 1.0)
        self.assertAlmostEqual(e0["e0_price"], 1.0, places=2)
        self.assertEqual(e0["e0_crossings"], 13)
        self.assertAlmostEqual(e0["e0_capacity"], 100.0 / 95.0, places=12)
        self.assertAlmostEqual(e0["e0_r_new"], 0.16, places=12)
        self.assertAlmostEqual(e0["e0_lost"], 1.0 / 95.0, places=12)
        self.assertTrue(e0["e0_alive"])
        self.assertTrue(e0["e0_pass"])
        self.assertEqual(e0["e0_lines"], 1.0)

    def test_what_is_reported_beside_the_lines(self):
        e0 = measures()
        self.assertAlmostEqual(e0["e0_rate_industry"], 0.13, places=12)
        self.assertAlmostEqual(e0["e0_rate_spread"], 0.10, places=12)
        self.assertAlmostEqual(e0["e0_capacity_min"], 100.0 / 95.0, places=12)
        self.assertAlmostEqual(e0["e0_capacity_max"], 100.0 / 95.0, places=12)
        self.assertEqual(e0["e0_price_max"], 1.05)

    def test_periods_before_20_are_not_read(self):
        u, o = table()
        for row in u[:E0_START] + o[:E0_START]:
            row.update(leader_cheapest=0, price_over_reg=3.0, capacity=5.0, r_new=0.9,
                       lost=90.0, profit=90.0)
        self.assertEqual(e0_measures(u, o, RBAR, 100.0), measures())

    def test_a_run_shorter_than_20_periods_has_no_measure_and_does_not_pass(self):
        e0 = measures(periods=15)
        self.assertIsNone(e0["e0_price"])
        self.assertIsNone(e0["e0_capacity"])
        self.assertFalse(e0["e0_pass"])

    def test_a_seed_passes_only_with_every_line(self):
        failing = {
            "leader": {"leader_cheapest": lambda t: int(t % 5 > 0)},          # 0.8 of periods
            "price": {"price_over_reg": lambda t: 1.6 if t % 6 < 3 else 0.95},   # mean 1.275
            "crossings": {"price_over_reg": lambda t: 1.05 if t < 40 else 0.95},
            "capacity": {"capacity": lambda t: 60.0},                          # 1.26 of demand
            "r_new": {"r_new": lambda t: 0.40},
            "lost": {"lost": lambda t: 12.0},                                  # 0.126 of demand
        }
        for line, columns in failing.items():
            e0 = measures(**columns)
            verdicts = {name: e0[f"e0_{name}_ok"] for name in E0_LINES if name != "alive"}
            self.assertEqual([name for name, ok in verdicts.items() if not ok], [line])
            self.assertFalse(e0["e0_pass"], line)
            self.assertAlmostEqual(e0["e0_lines"], 6 / 7, places=12)
        dead = measures(capacity_end=0.0)
        self.assertFalse(dead["e0_alive"])
        self.assertFalse(dead["e0_pass"])
        self.assertAlmostEqual(dead["e0_lines"], 6 / 7, places=12)

    def test_the_ends_of_a_band_pass(self):
        self.assertTrue(measures(capacity=lambda t: 0.6 * 95.0)["e0_capacity_ok"])
        self.assertFalse(measures(capacity=lambda t: 0.44 * 95.0)["e0_capacity_ok"])
        self.assertTrue(measures(lost=lambda t: 9.5)["e0_lost_ok"])
        self.assertFalse(measures(lost=lambda t: 9.6)["e0_lost_ok"])
        self.assertTrue(measures(leader_cheapest=lambda t: int(t % 10 > 0))["e0_leader_ok"])

    def test_the_line_on_the_rate_reads_r_new_not_the_industry_rate(self):
        """An industry rate of 0.03, far below the band, does not fail the line; a rate of
        new plants outside the band does, whatever the industry rate."""
        self.assertTrue(measures(profit=lambda t: 3.0)["e0_r_new_ok"])
        self.assertTrue(measures(profit=lambda t: 3.0)["e0_pass"])
        self.assertFalse(measures(r_new=lambda t: 0.09)["e0_r_new_ok"])
        self.assertTrue(measures(r_new=lambda t: 0.10)["e0_r_new_ok"])
        self.assertTrue(measures(r_new=lambda t: 0.32)["e0_r_new_ok"])
        self.assertFalse(measures(r_new=lambda t: 0.33)["e0_r_new_ok"])

    def test_the_band_on_the_rate_follows_the_general_rate(self):
        self.assertFalse(measures(rbar=0.05)["e0_r_new_ok"])
        self.assertTrue(measures(rbar=0.05, r_new=lambda t: 0.06)["e0_r_new_ok"])
        self.assertTrue(measures(rbar=0.10)["e0_r_new_ok"])

    def test_r_new_is_averaged_over_the_periods_in_which_it_is_defined(self):
        e0 = measures(r_new=lambda t: None if t % 2 else 0.20)
        self.assertAlmostEqual(e0["e0_r_new"], 0.20, places=12)
        self.assertFalse(measures(r_new=lambda t: None)["e0_r_new_ok"])


class TestRunRow(unittest.TestCase):
    def setUp(self):
        self.params = replace(Parameters(), periods=60)
        self.rows = run(self.params, seed=1).rows
        self.row = run_row(self.rows, self.params, seed=1)

    def test_the_run_row_has_the_columns_of_e0(self):
        for line in E0_LINES:
            self.assertIn("e0_" + line, self.row)
        for column in ("e0_pass", "e0_lines", "e0_rate_industry", "e0_rate_spread",
                       "e0_capacity_min", "e0_capacity_max", "e0_price_max"):
            self.assertIn(column, self.row)

    def test_overtime_share_is_output_above_normal_capacity_over_output(self):
        overtime = sum(row["overtime"] for row in self.rows)
        sales = sum(row["sales"] for row in self.rows)
        self.assertAlmostEqual(self.row["overtime_share"], overtime / sales, places=12)

    def test_rate_gap_is_the_rate_of_the_unit_cost_label_less_the_other(self):
        gap = self.row["rate_shaikh"] - self.row["rate_okishio"]
        self.assertAlmostEqual(self.row["rate_gap"], gap, places=12)

    def test_kept_is_designs_kept_over_designs_drawn_by_label(self):
        for label in ("shaikh", "okishio"):
            rows = [row for row in self.rows if row["label"] == label]
            drawn = sum(row["drawn"] for row in rows)
            kept = sum(row["kept"] for row in rows)
            expected = kept / drawn if drawn > 0 else None
            self.assertEqual(self.row["kept_" + label], expected)

    def test_the_columns_of_e6_are_empty_without_a_mutant(self):
        self.assertIsNone(self.row["mutant_share_end"])
        self.assertIsNone(self.row["invaded"])

    def test_the_mutant_s_share_is_read_in_e6_only(self):
        for mutant, share in (("shaikh", self.row["cap_share_end"]),
                              ("okishio", 1.0 - self.row["cap_share_end"])):
            row = run_row(self.rows, self.params, 1, mutant=mutant)
            self.assertAlmostEqual(row["mutant_share_end"], share, places=12)
            self.assertEqual(row["invaded"], share > 0.1)


class TestRunRowOfAWholeRun(unittest.TestCase):
    def setUp(self):
        ind = run(seed=0)
        self.rows = ind.rows
        self.row = run_row(ind.rows, ind.params, 0)

    def test_the_outcome_is_read_at_the_end_of_the_last_period(self):
        last = self.rows[-2:]
        capacity = last[0]["capacity_next"] + last[1]["capacity_next"]
        share = last[0]["capacity_next"] / capacity
        self.assertEqual(self.row["cap_share_end"], share)
        self.assertEqual(self.row["outcome"], outcome(share))
        self.assertEqual(self.row["capacity_end"], capacity)

    def test_counts_and_shares_are_consistent(self):
        row = self.row
        self.assertEqual(row["entries"], row["entries_shaikh"] + row["entries_okishio"])
        self.assertEqual(row["exits"], row["exits_shaikh"] + row["exits_okishio"])
        self.assertEqual(row["firms_end"], 6 + row["entries"] - row["exits"])
        by_reason = row["retired_age"] + row["retired_cost"] + row["retired_idle"]
        self.assertAlmostEqual(by_reason, 1.0, places=12)
        self.assertEqual(row["dk_accumulation"], row["dk_ordered"] + row["dk_retired"])
        for key in ("open_share", "war_freq", "leader_cheapest", "lost_share",
                    "overtime_share", "e0_lines", "kept_shaikh", "kept_okishio"):
            self.assertTrue(0.0 <= row[key] <= 1.0, key)

    def test_the_unit_cost_label_never_orders_a_dearer_technique(self):
        self.assertEqual(self.row["shaikh_dearer"], 0.0)
        self.assertEqual(self.row["hurdle_shaikh"], 0.0)
        self.assertGreater(self.row["hurdle_okishio"], 0.0)

    def test_the_measures_of_e0_are_those_of_the_period_table_from_period_20(self):
        u = [row for row in self.rows if row["label"] == "shaikh" and row["t"] >= E0_START]
        o = [row for row in self.rows if row["label"] == "okishio" and row["t"] >= E0_START]
        capacity = [(a["capacity"] + b["capacity"]) / a["demand"] for a, b in zip(u, o)]
        self.assertAlmostEqual(self.row["e0_capacity"], sum(capacity) / 180, places=12)
        self.assertEqual(self.row["e0_capacity_min"], min(capacity))
        lost = sum(row["lost"] for row in u) / sum(row["demand"] for row in u)
        self.assertAlmostEqual(self.row["e0_lost"], lost, places=12)
        leader = sum(row["leader_cheapest"] for row in u) / 180
        self.assertAlmostEqual(self.row["e0_leader"], leader, places=12)


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
        rows = [{"t": 0, "x": None}, {"t": 1, "x": 100.0}, {"t": 2, "x": 50.0},
                {"t": 5, "x": 90.0}]
        self.assertAlmostEqual(growth(rows, "x"), -0.10536051565782628 / 4, places=12)
        self.assertIsNone(growth(rows[:2], "x"))


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
    def test_the_experiments_have_the_runs_of_section_9_of_the_plan(self):
        counts = {name: runs(experiment) for name, experiment in EXPERIMENTS.items()}
        self.assertEqual(counts, {"E0": 400, "E0r": 3200, "reruns": 12500, "homogeneous": 3600,
                                  "E1": 6000, "E2": 14400, "E3": 9000, "E4": 28800,
                                  "E6": 4000, "reserve": 3200, "robustness": 25200,
                                  "fixed_menu": 1600})

    def test_e4_crosses_price_rule_investment_growth_technical_change_and_rate(self):
        e4 = EXPERIMENTS["E4"]
        self.assertEqual(len(e4), 3 * 2 * 2 * 2 * 2)
        self.assertEqual(e4["categories_universal_accelerator_g0.01_rbar0.1"]["overrides"],
                         {"tech_change": "categories", "pricing": "universal",
                          "investment": "accelerator", "growth": 0.01, "rbar": 0.10})

    def test_e6_is_one_mutant_among_nine_against_the_residents_control(self):
        e6 = EXPERIMENTS["E6"]
        self.assertEqual(list(e6), ["invader_shaikh_cost_edge", "invader_okishio_cost_edge",
                                    "invader_shaikh_universal", "invader_okishio_universal"])
        self.assertEqual(e6["invader_shaikh_cost_edge"]["populations"],
                         ("mixed", "all_profit_rate"))
        self.assertEqual(e6["invader_okishio_universal"]["populations"],
                         ("mixed", "all_unit_cost"))
        for mutant, cell in zip(("shaikh", "okishio") * 2, e6.values()):
            self.assertEqual(cell["mutant"], mutant)
            self.assertEqual(cell["overrides"]["mutation"], 0.0)

    def test_the_robustness_checks_have_the_runs_of_the_plan(self):
        checks = {"no_overtime": 4800, "operating_cost_floor": 3000, "entry_label_even": 3000,
                  "scrap_cost_unit_cost": 7800, "private_designs": 600,
                  "firms_per_pair": 6000}
        for check, expected in checks.items():
            part = {name: cell for name, cell in EXPERIMENTS["robustness"].items()
                    if name.replace("no_draws_", "").startswith(check)}
            self.assertEqual(runs(part), expected, check)

    def test_e0_is_the_two_controls_without_draws_under_the_four_price_rules(self):
        e0 = EXPERIMENTS["E0"]
        self.assertEqual(list(e0), ["no_draws_" + rule for rule in PRICE_RULES])
        for rule, cell in zip(PRICE_RULES, e0.values()):
            self.assertEqual(cell["overrides"], {"tech_change": "none", "pricing": rule})
            self.assertEqual((cell["populations"], cell["seeds"]), (CONTROLS, 50))

    def test_a_cell_without_draws_is_read_in_the_two_controls_on_50_seeds(self):
        for experiment in EXPERIMENTS.values():
            for name, cell in experiment.items():
                if name.startswith("no_draws"):
                    self.assertEqual(cell["overrides"]["tech_change"], "none", name)
                    self.assertEqual((cell["populations"], cell["seeds"]), (CONTROLS, 50))
                elif "mutant" not in cell:
                    self.assertEqual(cell["populations"], ALL, name)

    def test_cell_names_say_what_they_change(self):
        self.assertEqual(list(EXPERIMENTS["E2"])[:6],
                         ["beta_0_cost_edge", "beta_0.5_cost_edge", "beta_1.5_cost_edge",
                          "beta_3_cost_edge", "neutral_cost_edge", "none_cost_edge"])
        self.assertEqual(EXPERIMENTS["E3"]["lam_0.25_systematic"]["overrides"],
                         {"lam": 0.25, "pricing": "systematic"})
        self.assertEqual(EXPERIMENTS["E0r"]["no_draws_rbar_0.05"]["overrides"],
                         {"tech_change": "none", "rbar": 0.05})
        self.assertEqual(EXPERIMENTS["reruns"]["step_0.5_accelerator"]["overrides"],
                         {"shortage_step": 0.5, "investment": "accelerator"})
        self.assertNotIn("normal_price", {cell["overrides"]["pricing"]
                                          for cell in EXPERIMENTS["E3"].values()})

    def test_every_cell_builds_in_each_of_its_populations(self):
        for experiment in EXPERIMENTS.values():
            for name, cell in experiment.items():
                for population in cell["populations"]:
                    overrides = {**cell["overrides"], **POPULATIONS[population]}
                    self.assertGreaterEqual(len(industry(**overrides).firms), 6, name)


class TestPopulations(unittest.TestCase):
    def test_the_controls_put_both_labels_on_one_rule(self):
        self.assertEqual({firm.rule for firm in industry(**POPULATIONS["mixed"]).firms},
                         {"unit_cost", "profit_rate"})
        for control, rule in zip(CONTROLS, ("unit_cost", "profit_rate")):
            firms = industry(**POPULATIONS[control]).firms
            self.assertEqual({firm.rule for firm in firms}, {rule})
            self.assertEqual({firm.label for firm in firms}, {"shaikh", "okishio"})

    def test_the_homogeneous_start_is_six_firms_of_six_plants_on_d1(self):
        ind = industry(**homogeneous())
        self.assertEqual([firm.label for firm in ind.firms], ["shaikh", "okishio"] * 3)
        self.assertEqual([len(firm.plants) for firm in ind.firms], [6] * 6)
        names = {plant.technique.name for firm in ind.firms for plant in firm.plants}
        self.assertEqual(names, {"D1"})
        self.assertAlmostEqual(ind.demand_0, 639.2, places=1)

    def test_the_invasion_is_one_firm_of_the_mutant_label_among_nine(self):
        for mutant, resident in (("shaikh", "okishio"), ("okishio", "shaikh")):
            ind = industry(**invasion(mutant))
            labels = [firm.label for firm in ind.firms]
            self.assertEqual(labels, [resident] * 9 + [mutant])
            self.assertEqual({len(firm.plants) for firm in ind.firms}, {6})
            self.assertAlmostEqual(ind.demand_0, 1065.3, places=1)
            self.assertEqual(ind.params.mutation, 0.0)


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
        found = {cell["population"]: cell for cell in summarise(rows, columns())}
        mixed = found["mixed"]
        self.assertEqual((mixed["ctrl_uc_share_won"], mixed["ctrl_pr_share_won"]), (0.5, 0.4))
        self.assertAlmostEqual(mixed["gap"], 0.95 - 0.45, places=12)
        self.assertTrue(mixed["beyond_drift"])
        self.assertNotIn("gap", found["all_unit_cost"])

    def test_the_mean_of_a_column_of_true_and_false_is_the_share_of_seeds(self):
        rows = self.rows("all_unit_cost", [("win", 0.6)] * 4)
        for row, passed in zip(rows, ("True", "True", "True", "False")):
            row["e0_pass"] = passed
        cell, = summarise(rows, columns())
        self.assertEqual(cell["e0_pass"], 0.75)

    def test_a_cell_of_a_file_is_read_as_a_number_or_nothing(self):
        self.assertEqual([number(value) for value in ("0.5", "", None, "True", False, "win", 3)],
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
        expected = [(cell, population, seed) for cell in SMALL["T"] for population in ALL
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
        params = replace(Parameters(), periods=25)
        expected = run_row(run(params, 0).rows, params, 0)
        self.assertEqual(row["outcome"], expected["outcome"])
        self.assertEqual(float(row["capacity_end"]), expected["capacity_end"])
        self.assertEqual(row["e0_pass"], str(expected["e0_pass"]))
        self.assertEqual(row["overrides"], '{"periods": 25}')

    def test_cells_csv_has_one_row_per_cell_and_population(self):
        found = read(self.base / "one", "cells.csv")
        self.assertEqual(len(found), 6)
        self.assertEqual({cell["n_seeds"] for cell in found}, {"4"})
        mixed = [cell for cell in found if cell["population"] == "mixed"]
        self.assertTrue(all(cell["ctrl_uc_share_won"] != "" for cell in mixed))

    def test_a_run_stopped_and_resumed_gives_the_same_file(self):
        """runs.csv is cut after the first complete groups and two rows of the next one."""
        folder = self.base / "resumed"
        folder.mkdir()
        lines = (self.base / "one" / "runs.csv").read_text().splitlines(keepends=True)
        (folder / "runs.csv").write_text("".join(lines[:1 + 2 * 4 + 2]))
        run_experiment("T", jobs=2, resume=True, folder=folder, experiments=SMALL, quiet=True)
        self.assertEqual(read(folder), read(self.base / "one"))

    def test_cells_of_one_experiment_can_differ_in_populations_and_seeds(self):
        folder = self.base / "uneven"
        uneven = {"T": {**cells({"wide": {"periods": 5}}, ALL, 2),
                        **cells({"narrow": {"periods": 5}}, CONTROLS, 3)}}
        run_experiment("T", jobs=2, folder=folder, experiments=uneven, quiet=True)
        sizes = {}
        for row in read(folder):
            key = (row["cell"], row["population"])
            sizes[key] = sizes.get(key, 0) + 1
        self.assertEqual(list(sizes.values()), [2, 2, 2, 3, 3])
        run_experiment("T", resume=True, folder=folder, experiments=uneven, quiet=True)
        self.assertEqual(len(read(folder)), 12)
        run_experiment("T", seeds=1, folder=folder, experiments=uneven, quiet=True)
        self.assertEqual(len(read(folder)), 5)

    def test_the_period_table_of_a_named_seed_is_kept(self):
        folder = self.base / "kept"
        small = {"T": cells({"short": {"periods": 25}}, ("mixed",), 2)}
        run_experiment("T", folder=folder, keep_periods=(1,), experiments=small, quiet=True)
        self.assertEqual(len(read(folder, "periods_short_mixed_1.csv")), 50)
        self.assertFalse((folder / "periods_short_mixed_0.csv").exists())

    def test_a_run_that_fails_is_reported_and_the_experiment_goes_on(self):
        folder = self.base / "failing"
        bad = {"T": cells({"bad": {"periods": 5, "no_such_parameter": 1},
                           "misspelt": {"periods": 5, "pricing": "cost-edge"},
                           "good": {"periods": 5}}, ("mixed",), 2)}
        run_experiment("T", folder=folder, experiments=bad, quiet=True)
        rows = read(folder)
        self.assertTrue(all("TypeError" in row["error"] for row in rows[:2]))
        self.assertTrue(all("ValueError" in row["error"] for row in rows[2:4]))
        self.assertTrue(all(row["error"] == "" for row in rows[4:]))
        found = read(folder, "cells.csv")
        self.assertEqual([cell["n_error"] for cell in found], ["2", "2", "0"])


class TestGate(unittest.TestCase):
    def cells_file(self, shares: dict) -> pathlib.Path:
        """A cells.csv made by hand: for each cell, the share of seeds that pass E0 in the
        two controls, of 50 seeds; the line on capacity is the one that fails."""
        folder = pathlib.Path(self.directory.name)
        names = (["cell", "population", "n_seeds", "n_error", "e0_pass", "e0_alive"]
                 + [f"e0_{line}_ok" for line in E0_LINES if line != "alive"])
        with open(folder / "cells.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=names)
            writer.writeheader()
            for cell, pair in shares.items():
                for population, share in zip(CONTROLS, pair):
                    row = dict.fromkeys(names, 1.0)
                    row.update(cell=cell, population=population, n_seeds=50, n_error=0,
                               e0_pass=share, e0_capacity_ok=share)
                    writer.writerow(row)
                writer.writerow({"cell": cell, "population": "mixed", "n_seeds": 50,
                                 "n_error": 0, "e0_pass": 0.0})
        return folder

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

    def read(self, shares):
        return verdicts(read_cells(self.cells_file(shares)))

    def test_e0_holds_when_nine_seeds_of_ten_pass_in_both_populations(self):
        found = self.read({"no_draws_cost_edge": (1.0, 0.98), "no_draws_normal_price": (0.9, 0.9),
                           "no_draws_universal": (0.92, 0.86), "no_draws_systematic": (0.0, 0.0)})
        self.assertEqual([verdict["holds"] for verdict in found], [True, True, False, False])
        self.assertEqual([verdict["passed"] for verdict in found],
                         [[50, 49], [45, 45], [46, 43], [0, 0]])

    def test_the_weakest_line_is_named_with_its_two_shares(self):
        found = self.read({"no_draws_cost_edge": (1.0, 0.98), "no_draws_normal_price": (1.0, 1.0)})
        self.assertEqual((found[0]["weakest"], found[0]["weakest_shares"]),
                         ("capacity", [1.0, 0.98]))
        self.assertIsNone(found[1]["weakest"])
        text = report(found)
        self.assertIn("50 of 50 and 49 of 50", text)
        self.assertIn("weakest line: capacity (1.00 and 0.98 of seeds)", text)
        self.assertIn("every line passes in every seed", text)

    def test_the_gate_is_on_the_default_price_rule(self):
        self.assertTrue(gate(self.read({"no_draws_cost_edge": (1.0, 0.98),
                                        "no_draws_systematic": (0.0, 0.0)})))
        self.assertFalse(gate(self.read({"no_draws_cost_edge": (1.0, 0.88),
                                         "no_draws_normal_price": (1.0, 1.0)})))

    def test_a_file_without_the_default_cell_is_outside_the_gate(self):
        self.assertIsNone(gate(self.read({"defaults_cost_edge": (0.0, 0.0)})))

    def test_the_gate_reads_the_files_of_the_harness(self):
        folder = pathlib.Path(self.directory.name) / "run"
        small = {"T": cells({"no_draws_cost_edge": {"tech_change": "none", "periods": 60}},
                            CONTROLS, 3)}
        run_experiment("T", jobs=2, folder=folder, experiments=small, quiet=True)
        found, = verdicts(read_cells(folder))
        self.assertEqual(found["seeds"], [3, 3])
        rows = read(folder)
        passed = [sum(row["e0_pass"] == "True" for row in rows if row["population"] == control)
                  for control in CONTROLS]
        self.assertEqual(found["passed"], passed)


if __name__ == "__main__":
    unittest.main()
