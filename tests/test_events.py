"""The event log: consistency with the tables, the inherited rule's random draws, war
and cutting episodes, and the label swap."""

import random
import unittest
from collections import Counter

from equations.inherited_rule import FLIP, inherit, inherited_type
from helpers import make_config, swapped_config, three_plant_industry, without_labels
from model import Industry
from model.collector import EVENT_COLUMNS, events_table

EXIT_COLUMNS = {"bankruptcy": "exits_bankruptcy", "share": "exits_share",
                "non-renewal": "exits_non_renewal"}


def run(config=None, periods=None):
    industry = Industry(config or make_config())
    industry.run(periods)
    return industry


class Consistency:
    """Mixed into one test case per configuration; setUpClass sets cls.industry."""

    @classmethod
    def setUpClass(cls):
        cls.events = events_table(cls.industry)

    def of(self, event, cause=None):
        return [e for e in self.events
                if e["event"] == event and (cause is None or e["cause"] == cause)]

    def test_columns(self):
        for e in self.events:
            self.assertEqual(tuple(e), EVENT_COLUMNS)

    def test_orders_are_the_plants_created(self):
        industry = self.industry
        initial = {r["plant_id"] for r in industry.plant_history if r["initial"]}
        ordered = [e["plant_id"] for e in self.of("order")]
        self.assertEqual(sorted(ordered),
                         [i for i in range(industry.next_plant_id) if i not in initial])
        for e in self.of("order"):
            self.assertEqual(e["step"], {"replacement": 4, "expansion": 5, "entry": 6}[e["cause"]])

    def test_retire_events_are_the_plants_retired(self):
        plants = self.industry.plant_history
        retired = {(r["t"], r["plant_id"]) for r in plants if r["retired"]}
        logged = {(e["t"], e["plant_id"]) for e in self.of("retire") if e["cause"] != "exit"}
        self.assertEqual(logged, retired)
        # Plants in operation when their firm leaves (not those it retired at step 4).
        with_firm = {(r["t"], r["plant_id"]) for r in plants
                     if r["exited_with_firm"] and not r["retired"]}
        self.assertEqual({(e["t"], e["plant_id"]) for e in self.of("retire", "exit")},
                         with_firm)
        for r in plants:
            self.assertEqual(r["retire_cause"] != "", r["retired"] or r["exited_with_firm"])

    def test_every_plant_has_an_order_or_is_initial(self):
        ordered = {e["plant_id"] for e in self.of("order")}
        for r in self.industry.plant_history:
            self.assertTrue(r["initial"] or r["plant_id"] in ordered, r["plant_id"])

    def test_entries_and_exits_match_the_macro_table(self):
        for row in self.industry.history:
            t = row["t"]
            self.assertEqual(sum(e["t"] == t for e in self.of("entry")), row["entries"])
            exits = [e for e in self.of("exit") if e["t"] == t]
            self.assertEqual(len(exits), row["exits"])
            causes = Counter(e["cause"] for e in exits)
            for cause, column in EXIT_COLUMNS.items():
                self.assertEqual(causes[cause], row[column], (t, cause))

    def test_cancels_and_defaults(self):
        firms = self.industry.firm_history
        cancelled = sum(r["cap_ordered"] for r in firms if r["exited"])
        self.assertAlmostEqual(sum(e["capacity"] for e in self.of("cancel")), cancelled)
        self.assertAlmostEqual(sum(e["value"] for e in self.of("default")),
                               self.industry.roe.loan_losses)

    def test_war_episodes(self):
        wars = sum(r["war_on"] for r in self.industry.history)
        starts, ends = self.of("war_start"), self.of("war_end")
        self.assertEqual(len(starts), len(ends))
        self.assertEqual(sum(e["t"] - s["t"] + 1 for s, e in zip(starts, ends)), wars)
        cuts = sum(r["cutting"] for r in self.industry.firm_history)
        spans = Counter()
        for e in self.of("cut_start"):
            spans[e["firm_id"]] -= e["t"]
        for e in self.of("cut_end"):
            spans[e["firm_id"]] += e["t"] + 1
        self.assertEqual(sum(spans.values()), cuts)


class TestBaseline(Consistency, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.industry = run()
        super().setUpClass()

    def test_the_baseline_has_entries_exits_and_wars(self):
        self.assertTrue(self.of("entry") and self.of("exit") and self.of("war_start"))


class TestBankruptcies(Consistency, unittest.TestCase):
    """Deep price cuts with initial debt: bankruptcies, defaults and cancelled orders."""

    @classmethod
    def setUpClass(cls):
        cls.industry = run(make_config(PRICE_CUT=0.06, MIN_SHARE=0.05, INITIAL_DEBT=5_000.0))
        super().setUpClass()

    def test_the_run_has_defaults_and_cancels(self):
        self.assertTrue(self.of("default") and self.of("cancel") and self.of("exit", "bankruptcy"))


class TestMutations(Consistency, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.industry = run(make_config(MIN_SHARE=0.08, MUTATION=0.5))
        super().setUpClass()

    def test_entry_records_parent_and_mutation(self):
        entries = self.of("entry")
        self.assertTrue(entries)
        groups = {(r["t"], r["firm_id"]): r["group"] for r in self.industry.firm_history}
        for e in entries:
            parent = groups[(e["t"], e["other_id"])]  # the parent produced that period
            expected = FLIP[parent] if e["cause"] == "mutated" else parent
            self.assertEqual(e["group"], expected)
        self.assertEqual({e["cause"] for e in entries}, {"inherited", "mutated"})


class TestThreePlantEvents(Consistency, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.industry = three_plant_industry()[0]
        cls.industry.run(30)
        super().setUpClass()

    def test_replacement_and_age_retirements_are_logged(self):
        first = [e for e in self.events if e["t"] == 0]
        self.assertEqual({(e["cause"], e["tech"]) for e in first if e["event"] == "retire"
                          and e["firm_id"] == 0}, {("age", "D1"), ("replacement", "X")})
        self.assertIn(("replacement", "D2"), {(e["cause"], e["tech"]) for e in first
                                              if e["event"] == "order"})
        self.assertTrue(any(e["event"] == "cancel" for e in first))
        self.assertTrue(any(e["event"] == "exit" and e["cause"] == "share" for e in first))


class TestInheritance(unittest.TestCase):
    def test_inherit_draws_like_the_old_rule(self):
        """inherit uses the random stream exactly as the former inherited_type did."""
        def old(types, shares, mutation, rng):
            parent = rng.choices(types, weights=shares, k=1)[0]
            return FLIP[parent] if rng.random() < mutation else parent

        types = ["shaikh", "okishio", "okishio", "shaikh", "okishio"]
        shares = [0.1, 0.3, 0.05, 0.4, 0.15]
        a, b = random.Random(7), random.Random(7)
        for _ in range(2_000):
            firm_type, parent, mutated = inherit(types, shares, 0.3, a)
            self.assertEqual(firm_type, old(types, shares, 0.3, b))
            self.assertEqual(firm_type, FLIP[types[parent]] if mutated else types[parent])
        self.assertEqual(a.getstate(), b.getstate())
        self.assertEqual(inherited_type(types, shares, 0.3, random.Random(3)),
                         old(types, shares, 0.3, random.Random(3)))


class TestLabelSwap(unittest.TestCase):
    def test_events_are_identical_up_to_labels(self):
        config = dict(PRICE_CUT=0.06, MIN_SHARE=0.05, INITIAL_DEBT=5_000.0)
        a = run(make_config(**config))
        b = run(swapped_config(**config))
        self.assertEqual(without_labels(events_table(a)), without_labels(events_table(b)))
        swap = {"shaikh": "okishio", "okishio": "shaikh", "": ""}
        self.assertEqual([e["group"] for e in events_table(a)],
                         [swap[e["group"]] for e in events_table(b)])


if __name__ == "__main__":
    unittest.main()
