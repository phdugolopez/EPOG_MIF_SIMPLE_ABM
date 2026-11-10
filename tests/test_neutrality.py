"""Neutrality: the label is read only to look up the rule and in inheritance at entry, and a
firm's place in the list decides nothing (v4-final-model.md, "Randomness and neutrality").

The label swap exchanges the two labels and leaves every firm on its rule (register, Q4):
the trajectories must be identical. Both tests run under every price rule and investment
rule, in the three populations.
"""
import re
import unittest
from dataclasses import replace

from model.model import build
from model.scheduler import period
from parameters import LABELS, OPTIONS, Parameters
from test_budget import ROOT, model_files

POPULATIONS = {"mixed": {}, "all_unit_cost": {"rule_okishio": "unit_cost"},
               "all_profit_rate": {"rule_shaikh": "profit_rate"}}
OTHER = {LABELS[0]: LABELS[1], LABELS[1]: LABELS[0]}
RULES = [{"pricing": pricing, "investment": investment}
         for pricing in OPTIONS["pricing"] for investment in OPTIONS["investment"]]
ONCE_EACH = ({"reserve": "always"}, {"reserve": "never"}, {"price_floor": "operating_cost"},
             {"entry_label": "even"}, {"entry_price": "lowest"}, {"rbar": 0.05},
             {"tech_change": "categories", "growth": 0.01}, {"tech_change": "neutral"},
             {"u_max": 1.0}, {"pricing": "universal", "price_floor": "operating_cost"})


def swapped(params: Parameters) -> Parameters:
    """The same population with the two labels exchanged: every firm keeps its rule."""
    start = tuple((name, OTHER[label], output) for name, label, output in params.start)
    return replace(params, start=start, rule_shaikh=params.rule_okishio,
                   rule_okishio=params.rule_shaikh)


def trajectory(params: Parameters, seed: int, periods: int, reverse: bool = False):
    """The state of every firm after each period, by serial number, and the period table."""
    industry = build(params, seed)
    if reverse:
        industry.firms.reverse()
    states = []
    for _ in range(periods):
        period(industry)
        states.append(sorted(
            (firm.id, firm.rule, firm.price, firm.share, firm.sales, firm.cash, firm.funds,
             firm.hurdle, firm.util, len(firm.plants), len(firm.pending_plants),
             len(firm.known))
            for firm in industry.firms))
    return states, industry.rows


def mirror(rows: list[dict]) -> list[dict]:
    """The period table with the two labels exchanged, its rows in the usual order."""
    exchanged = [dict(row, label=OTHER[row["label"]]) for row in rows]
    return sorted(exchanged, key=lambda row: (row["t"], LABELS.index(row["label"])))


class Neutrality(unittest.TestCase):
    def check_swap(self, params, seed, periods):
        states, rows = trajectory(params, seed, periods)
        swapped_states, swapped_rows = trajectory(swapped(params), seed, periods)
        self.assertEqual(states, swapped_states)
        self.assertEqual(rows, mirror(swapped_rows))

    def check_order(self, params, seed, periods):
        states, rows = trajectory(params, seed, periods)
        reversed_states, reversed_rows = trajectory(params, seed, periods, reverse=True)
        self.assertEqual(states, reversed_states)
        self.assertEqual(rows, reversed_rows)


class TestLabelSwap(Neutrality):
    def test_under_every_price_rule_and_investment_rule_in_the_three_populations(self):
        for rules in RULES:
            for name, population in POPULATIONS.items():
                with self.subTest(population=name, **rules):
                    self.check_swap(replace(Parameters(), **rules, **population), 4, 60)

    def test_over_a_whole_run_at_the_defaults(self):
        for name, population in POPULATIONS.items():
            with self.subTest(population=name):
                self.check_swap(replace(Parameters(), **population), seed=4, periods=200)

    def test_once_under_each_other_option(self):
        for overrides in ONCE_EACH:
            with self.subTest(**overrides):
                self.check_swap(replace(Parameters(), **overrides), seed=9, periods=60)

    def test_the_swap_exchanges_the_labels_and_keeps_the_rules(self):
        firms = build(Parameters(), 0).firms
        mirrored = build(swapped(Parameters()), 0).firms
        self.assertEqual([firm.label for firm in mirrored],
                         [OTHER[firm.label] for firm in firms])
        self.assertEqual([firm.rule for firm in mirrored], [firm.rule for firm in firms])

    def test_the_runs_compared_are_not_trivial(self):
        """Firms enter and leave, designs are kept and both labels order plants."""
        _, rows = trajectory(Parameters(), 4, 60)
        for column in ("entries", "exits", "kept", "cap_ordered", "cap_retired"):
            self.assertGreater(sum(row[column] for row in rows), 0.0, column)


class TestOrderOfFirms(Neutrality):
    def test_under_every_price_rule_and_investment_rule_in_the_three_populations(self):
        """So a firm's draws do not depend on its place: the controls are symmetric."""
        for rules in RULES:
            for name, population in POPULATIONS.items():
                with self.subTest(population=name, **rules):
                    self.check_order(replace(Parameters(), **rules, **population), 6, 60)

    def test_over_a_whole_run_at_the_defaults(self):
        for name, population in POPULATIONS.items():
            with self.subTest(population=name):
                self.check_order(replace(Parameters(), **population), seed=6, periods=200)

    def test_once_under_each_other_option(self):
        for overrides in ONCE_EACH:
            with self.subTest(**overrides):
                self.check_order(replace(Parameters(), **overrides), seed=2, periods=60)


class TestSource(unittest.TestCase):
    def reading(self, pattern: str) -> set[str]:
        """The model files in which a pattern is found."""
        return {str(path.relative_to(ROOT)) for path in model_files()
                if re.search(pattern, path.read_text())}

    def test_the_label_is_read_only_at_entry_and_in_the_outputs(self):
        """entities.py looks the rule up from the label when a firm is created."""
        allowed = {"model/entities.py", "model/outputs.py", "markets/entry_exit.py",
                   "equations/entry_inherited_rule.py"}
        self.assertLessEqual(self.reading(r"\.label\b"), allowed)
        self.assertLessEqual(self.reading(r"\bLABELS\b"),
                             allowed | {"parameters.py", "model/scheduler.py"})

    def test_the_rule_is_read_only_to_look_up_the_hurdle(self):
        for path in model_files():
            for line in path.read_text().splitlines():
                if re.search(r"\.rule\b", line):
                    self.assertIn("hurdle(", line, path.name)

    def test_the_serial_number_is_read_only_where_the_plan_allows_it(self):
        """To order the incumbents for the draw of a parent (entry_exit.py), to name a
        design (scheduler.py) and to keep the tally by firm (outputs.py). The stream is
        keyed by industry.next_id in entities.py."""
        allowed = {"markets/entry_exit.py", "model/scheduler.py", "model/outputs.py"}
        self.assertLessEqual(self.reading(r"\.id\b"), allowed)

    def test_the_scheduler_reads_the_labels_only_to_count_the_rows_of_a_period(self):
        text = (ROOT / "model" / "scheduler.py").read_text()
        uses = [line.strip() for line in text.splitlines()
                if "LABELS" in line and "import" not in line]
        self.assertEqual(len(uses), 1)
        self.assertIn("industry.rows[-len(LABELS):]", uses[0])


if __name__ == "__main__":
    unittest.main()
