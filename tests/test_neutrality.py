"""Neutrality: the label is read only to look up the hurdle rule and in inheritance at entry,
and a firm's place in the list decides nothing."""
import re
import unittest
from dataclasses import replace

from model.model import build
from model.scheduler import period
from parameters import LABELS, Parameters
from test_budget import ROOT, model_files

POPULATIONS = {"mixed": {}, "all_unit_cost": {"rule_okishio": "unit_cost"},
               "all_profit_rate": {"rule_shaikh": "profit_rate"}}
OTHER = {LABELS[0]: LABELS[1], LABELS[1]: LABELS[0]}
ANOTHER_CELL = dict(pricing="systematic", investment="accelerator", tech_change="categories",
                    rbar=0.16, growth=0.01)


def swapped(params: Parameters) -> Parameters:
    """The same population with the two labels exchanged: every firm keeps its rule (Q4)."""
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
             firm.hurdle, len(firm.plants), len(firm.pending_plants), len(firm.known))
            for firm in industry.firms))
    return states, industry.rows


def mirror(rows: list[dict]) -> list[dict]:
    """The period table with the two labels exchanged, its rows in the usual order."""
    exchanged = [dict(row, label=OTHER[row["label"]]) for row in rows]
    return sorted(exchanged, key=lambda row: (row["t"], LABELS.index(row["label"])))


class TestLabelSwap(unittest.TestCase):
    def check(self, params, seed, periods):
        states, rows = trajectory(params, seed, periods)
        swapped_states, swapped_rows = trajectory(swapped(params), seed, periods)
        self.assertEqual(states, swapped_states)
        self.assertEqual(rows, mirror(swapped_rows))

    def test_swapped_labels_give_the_same_trajectories_in_the_three_populations(self):
        for name, population in POPULATIONS.items():
            with self.subTest(population=name):
                self.check(replace(Parameters(), **population), seed=4, periods=200)

    def test_swapped_labels_give_the_same_trajectories_in_another_cell(self):
        for name, population in POPULATIONS.items():
            with self.subTest(population=name):
                self.check(replace(Parameters(), **ANOTHER_CELL, **population), seed=9, periods=80)

    def test_the_swap_exchanges_the_labels_and_keeps_the_rules(self):
        firms = build(Parameters(), 0).firms
        mirrored = build(swapped(Parameters()), 0).firms
        self.assertEqual([firm.label for firm in mirrored], [OTHER[firm.label] for firm in firms])
        self.assertEqual([firm.rule for firm in mirrored], [firm.rule for firm in firms])


class TestOrderOfFirms(unittest.TestCase):
    def test_reversing_the_firms_changes_nothing_in_the_three_populations(self):
        """So a firm's draws do not depend on its place: the controls are symmetric."""
        for name, population in POPULATIONS.items():
            with self.subTest(population=name):
                params = replace(Parameters(), **population)
                self.assertEqual(trajectory(params, 6, 200), trajectory(params, 6, 200, reverse=True))

    def test_reversing_the_firms_changes_nothing_in_another_cell(self):
        params = replace(Parameters(), **ANOTHER_CELL)
        self.assertEqual(trajectory(params, 2, 80), trajectory(params, 2, 80, reverse=True))


class TestSource(unittest.TestCase):
    def test_the_label_is_read_only_at_entry_and_in_the_outputs(self):
        allowed = {"model/entities.py", "model/model.py", "model/outputs.py",
                   "markets/entry_exit.py", "equations/entry_inherited_rule.py"}
        reading = {str(path.relative_to(ROOT)) for path in model_files()
                   if re.search(r"\.label\b", path.read_text())}
        self.assertLessEqual(reading, allowed)

    def test_the_rule_is_read_only_to_look_up_the_hurdle(self):
        for path in model_files():
            for line in path.read_text().splitlines():
                if re.search(r"\.rule\b", line):
                    self.assertIn("hurdle(", line, path.name)

    def test_the_serial_number_is_read_only_to_draw_a_parent_and_to_name_a_design(self):
        reading = {str(path.relative_to(ROOT)) for path in model_files()
                   if re.search(r"\.id\b", path.read_text())}
        self.assertLessEqual(reading, {"markets/entry_exit.py", "model/scheduler.py"})


if __name__ == "__main__":
    unittest.main()
