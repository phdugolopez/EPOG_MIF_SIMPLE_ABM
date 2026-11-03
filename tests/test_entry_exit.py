"""Entry and exit: the brief's tests (1)-(6)."""

import random
import unittest

from equations.entry_probability import entry_probability
from equations.inherited_rule import inherited_type
from helpers import history_without_labels, make_config, swapped_config
from markets.entry_exit import create_entrant, remove_firm
from model import Industry
from model.collector import check_stock_flow
from model.scheduler import (
    admit_entrant, allocate_demand, exit_firms, invest, produce_and_account,
    scrap_plants, set_prices, start_period,
)


def run_to_entry(industry):
    start_period(industry)
    set_prices(industry)
    allocate_demand(industry)
    produce_and_account(industry)
    scrap_plants(industry)
    invest(industry)


class TestEntryExit(unittest.TestCase):
    def test_no_entry_when_r_new_at_or_below_rbar(self):
        """(1)"""
        for r_new in (None, -0.1, 0.0, 0.10, 0.159, 0.16):
            self.assertEqual(entry_probability(r_new, 0.16, 5.0), 0.0)
        self.assertAlmostEqual(entry_probability(0.17, 0.16, 5.0), 0.3125)
        industry = Industry(make_config())
        industry.run(200)
        for row in industry.history:
            if row["r_new"] is None or row["r_new"] <= 0.16:
                self.assertEqual(row["entries"], 0)

    def test_negative_net_worth_exit_shares_out_customers(self):
        """(2)"""
        industry = Industry(make_config())
        doomed = industry.firms[0]
        run_to_entry(industry)
        doomed.debt += 1e6  # by hand, with the matching loan in the rest of the economy
        industry.roe.loans += 1e6
        doomed.net_worth_start -= 1e6
        exit_firms(industry)
        self.assertNotIn(doomed, industry.firms)
        self.assertEqual(industry.exits[0][1], "bankruptcy")
        self.assertAlmostEqual(sum(f.share for f in industry.firms), 1.0)
        self.assertGreater(industry.roe.loan_losses, 0.0)
        self.assertAlmostEqual(industry.roe.loans, sum(f.debt for f in industry.firms))

    def test_floor_of_two_firms(self):
        industry = Industry(make_config())
        run_to_entry(industry)
        for f in industry.firms:
            f.share = 0.0  # every firm below f_min
        industry.firms[0].share = 1.0e-3
        exit_firms(industry)
        self.assertEqual(len(industry.firms), 2)

    def test_inherited_rules_match_market_shares(self):
        """(3) Up to the mutation rate."""
        rng = random.Random(11)
        draws = [inherited_type(["shaikh", "okishio"], [0.7, 0.3], 0.02, rng)
                 for _ in range(40_000)]
        expected = 0.7 * 0.98 + 0.3 * 0.02
        self.assertAlmostEqual(draws.count("shaikh") / len(draws), expected, delta=0.01)

    def test_entrants_pick_their_plant_with_their_own_rule(self):
        """(4) At p = 100, on the same trigger, Okishio entrants build D1, Shaikh entrants D2."""
        for rule, expected in (("profit_rate", "D1"), ("unit_cost", "D2")):
            config = make_config(HURDLE_RULES={"shaikh": rule, "okishio": rule},
                                 ENTRANT_UNDERCUT=0.0)
            industry = Industry(config)
            run_to_entry(industry)
            industry.leader_price = 100.0
            admit_entrant(industry)
            self.assertEqual(industry.entries[0].pending_plants[0].technique, expected)

    def test_capacity_and_money_identities_at_entry_and_exit(self):
        """(5)"""
        industry = Industry(make_config(INITIAL_DEBT=3_000.0))
        run_to_entry(industry)
        capacity = lambda: sum(  # noqa: E731
            f.capacity + sum(p.capacity for p in f.pending_plants) for f in industry.firms
        )
        before = capacity()
        leaver = industry.firms[0]
        leaver_capacity = leaver.capacity + sum(p.capacity for p in leaver.pending_plants)
        remove_firm(industry, leaver, "bankruptcy")
        technique = industry.techniques["D1"]
        create_entrant(industry, "okishio", 99.0, technique, 60.0)
        self.assertAlmostEqual(capacity(), before + 60.0 - leaver_capacity)
        self.assertAlmostEqual(sum(f.share for f in industry.firms), 1.0)
        check_stock_flow(industry)  # money conserved, loans = debt, NW identities

    def test_label_swap_changes_nothing(self):
        """(6) Over a full run with entry, mutation and exit."""
        a, b = Industry(make_config()), Industry(swapped_config())
        a.run(200)
        b.run(200)
        self.assertGreater(sum(r["entries"] for r in a.history), 0)
        self.assertEqual(history_without_labels(a), history_without_labels(b))


if __name__ == "__main__":
    unittest.main()
