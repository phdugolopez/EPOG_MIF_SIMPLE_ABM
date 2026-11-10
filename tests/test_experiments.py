"""The run row and the experiments. Stage 3c tests the measures of E0 on period tables made
by hand; stage 5 adds the statistics, the harness, the cells and the gate."""
import unittest
from dataclasses import replace

from experiments.summary import E0_LINES, E0_START, crossings, e0_measures, run_row
from model.model import run
from parameters import Parameters

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


if __name__ == "__main__":
    unittest.main()
