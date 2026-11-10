"""The run row (experiments/summary.py). Stage 5 adds the Wilson interval, the beyond-drift
test and the harness."""
import unittest

from experiments.summary import average, growth, outcome, ratio, run_row, takeover, total
from model.model import run


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
