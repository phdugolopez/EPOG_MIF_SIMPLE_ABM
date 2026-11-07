"""The groups table and the exact decompositions of the collector brief (sections 4.2
and 4.3): each sums to the change it decomposes, and both are label-free."""

import unittest

import pandas as pd

from analysis.indicators import CAPACITY_FLOWS, capacity_share_terms, cumulate, sales_share_terms
from helpers import BANKRUPTCIES, make_config, swapped_config, three_plant_industry
from model import Industry

TOL = 1e-12
SWAP = {"shaikh": "okishio", "okishio": "shaikh"}

# groups column -> macro column it must add up to over the groups.
TOTALS = {
    "n_firms": "n_active", "capacity": "capacity_total", "sales": "sales_total",
    "cap_retired": "capacity_retired", "n_entry": "entries", "n_exit": "exits",
    "n_exit_bankruptcy": "exits_bankruptcy", "n_exit_share": "exits_share",
    "n_exit_non_renewal": "exits_non_renewal", "profit": "profit", "gos": "gos_total",
    "invest_spend": "invest_total", "cash": "cash", "debt": "debt",
    "net_worth": "net_worth",
}


def run(config=None, periods=None, industry=None):
    industry = industry or Industry(config or make_config())
    industry.run(periods)
    return industry


class GroupsAndDecompositions:
    """Mixed into one test case per configuration; setUpClass sets cls.industry."""

    @classmethod
    def setUpClass(cls):
        cls.groups = pd.DataFrame(cls.industry.group_history)
        cls.macro = pd.DataFrame(cls.industry.history).set_index("t")

    def test_one_row_per_period_and_label(self):
        labels = sorted(self.industry.parameters.HURDLE_RULES)
        self.assertEqual(len(self.groups), len(self.macro) * len(labels))
        for t, rows in self.groups.groupby("t"):
            self.assertEqual(list(rows["group"]), labels)

    def test_groups_add_up_to_the_industry(self):
        sums = self.groups.groupby("t").sum(numeric_only=True)
        for column, macro_column in TOTALS.items():
            for t in self.macro.index:
                a, b = sums.at[t, column], self.macro.at[t, macro_column]
                self.assertAlmostEqual(a, b, delta=1e-9 * max(1.0, abs(b)),
                                       msg=(t, column))
        for name in self.industry.techniques:
            for t in self.macro.index:
                self.assertAlmostEqual(sums.at[t, f"capacity_{name}"],
                                       self.macro.at[t, f"capacity_{name}"])
        for t in self.macro.index:
            self.assertAlmostEqual(sums.at[t, "share_demand"], 1.0, delta=TOL)
            self.assertAlmostEqual(sums.at[t, "share_end"], 1.0, delta=TOL)

    def test_capacity_identity_by_group(self):
        g = self.groups
        self.assertLessEqual(g["cap_resid"].abs().max(), 1e-9 * self.macro["demand"].max())
        self.assertTrue((g["cap_replace"] <= g["cap_ordered"] + 1e-9).all())
        # capacity_next is next period's capacity.
        nxt = g.assign(t=g["t"] - 1).set_index(["t", "group"])["capacity"]
        here = g.set_index(["t", "group"])["capacity_next"].reindex(nxt.index).dropna()
        for key, value in here.items():
            self.assertAlmostEqual(value, nxt[key], delta=1e-9 * max(1.0, value))

    def test_capacity_share_terms_sum_to_the_change(self):
        terms = capacity_share_terms(self.groups)
        self.assertLessEqual(terms["resid"].abs().max(), TOL)
        # The actual change, from the capacity of consecutive rows.
        share = terms.set_index(["t", "group"])["share_k"]
        for (t, group), d in terms.set_index(["t", "group"])["d_share_k"].items():
            if (t + 1, group) in share.index:
                self.assertAlmostEqual(d, share[(t + 1, group)] - share[(t, group)],
                                       delta=TOL)
        # Each term sums to zero over the groups (shares sum to one).
        for flow in CAPACITY_FLOWS:
            self.assertLessEqual(terms.groupby("t")[f"term_{flow}"].sum().abs().max(), TOL)

    def test_sales_share_terms_sum_to_the_change(self):
        terms = sales_share_terms(self.groups)
        later = terms[terms["t"] > terms["t"].min()]
        self.assertFalse(later[["d_sales_share", "term_price"]].isna().any().any())
        self.assertLessEqual(later["resid"].abs().max(), TOL)
        # No entry and no exit in t - 1: the entry-and-exit term is exactly zero.
        quiet = self.macro[(self.macro["entries"] == 0) & (self.macro["exits"] == 0)].index
        for _, row in later[later["t"].isin(quiet + 1)].iterrows():
            self.assertEqual(row["term_entry_exit"], 0.0)

    def test_cumulated_terms(self):
        terms = capacity_share_terms(self.groups)
        total = cumulate(terms).sum(axis=1)
        k = terms.set_index(["t", "group"])
        first, last = terms["t"].min(), terms["t"].max()
        for group, value in total.items():
            change = k.at[(last, group), "share_k_next"] - k.at[(first, group), "share_k"]
            self.assertAlmostEqual(value, change, delta=1e-9)


class TestBaseline(GroupsAndDecompositions, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.industry = run()
        super().setUpClass()

    def test_the_baseline_moves_through_every_channel(self):
        g = self.groups
        # No replacement in the baseline (macro replacements = 0); see TestThreePlants.
        for column in ("cap_ordered", "cap_retired", "cap_entry", "n_exit"):
            self.assertGreater(g[column].sum(), 0.0, column)


class TestBankruptcies(GroupsAndDecompositions, unittest.TestCase):
    """Exits with orders cancelled, defaults and bankruptcies."""

    @classmethod
    def setUpClass(cls):
        cls.industry = run(make_config(**BANKRUPTCIES))
        super().setUpClass()

    def test_the_run_cancels_orders(self):
        self.assertGreater(self.groups["cap_cancelled"].sum(), 0.0)
        self.assertGreater(self.groups["cap_exit"].sum(), 0.0)


class TestMutations(GroupsAndDecompositions, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.industry = run(make_config(MIN_SHARE=0.08, MUTATION=0.5))
        super().setUpClass()


class TestThreePlants(GroupsAndDecompositions, unittest.TestCase):
    """Retirement by age, a replacement and an exit with a plant on order at t = 0."""

    @classmethod
    def setUpClass(cls):
        cls.industry = run(industry=three_plant_industry()[0], periods=30)
        super().setUpClass()

    def test_first_period_flows(self):
        first = self.groups[self.groups["t"] == 0].set_index("group")
        self.assertEqual(first.at["shaikh", "cap_retired"], 220.0)
        self.assertEqual(first.at["shaikh", "cap_replace"], 100.0)
        self.assertEqual(first.at["okishio", "cap_exit"], 130.0)
        self.assertGreater(first.at["okishio", "cap_cancelled"], 0.0)
        self.assertEqual(first.at["okishio", "n_exit_share"], 1)
        self.assertEqual(first.at["okishio", "capacity_next"], 0.0)


class TestSeveralRuns(unittest.TestCase):
    def test_concatenated_runs_are_decomposed_run_by_run(self):
        """Two seeds in one table (run_id first, as run.py writes it): the same terms as
        each run on its own, and each run's terms still sum to its change."""
        parts = {}
        for seed in (42, 43):
            rows = pd.DataFrame(run(make_config(SEED=seed, PERIODS=60)).group_history)
            rows.insert(0, "run_id", f"s{seed}")
            parts[f"s{seed}"] = rows
        both = pd.concat(parts.values(), ignore_index=True)
        for terms in (capacity_share_terms, sales_share_terms):
            pooled = terms(both)
            self.assertLessEqual(pooled["resid"].abs().max(), TOL)
            for run_id, rows in parts.items():
                alone = terms(rows).reset_index(drop=True)
                mine = pooled[pooled["run_id"] == run_id].reset_index(drop=True)
                pd.testing.assert_frame_equal(mine, alone, check_exact=True)
        totals = cumulate(capacity_share_terms(both))
        self.assertEqual(list(totals.index.names), ["run_id", "group"])
        self.assertEqual(len(totals), 4)


class TestLabelSwap(unittest.TestCase):
    def test_groups_and_terms_are_mirrored(self):
        config = BANKRUPTCIES
        a = run(make_config(**config))
        b = run(swapped_config(**config))
        rows_a = pd.DataFrame(a.group_history)
        rows_b = pd.DataFrame(b.group_history)
        rows_b["group"] = rows_b["group"].map(SWAP)
        for frame_a, frame_b in ((rows_a, rows_b),
                                 (capacity_share_terms(rows_a),
                                  capacity_share_terms(rows_b)),
                                 (sales_share_terms(rows_a), sales_share_terms(rows_b))):
            frame_a = frame_a.sort_values(["t", "group"]).reset_index(drop=True)
            frame_b = frame_b.sort_values(["t", "group"]).reset_index(drop=True)
            pd.testing.assert_frame_equal(frame_a, frame_b, check_exact=True)


if __name__ == "__main__":
    unittest.main()
