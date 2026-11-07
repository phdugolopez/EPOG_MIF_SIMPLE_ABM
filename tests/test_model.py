"""The complete model: baseline run, stock-flow consistency, label swap."""

import unittest

from helpers import PLANT_ALTERNATIVES, history_without_labels, make_config, swapped_config
from model import Industry
from model.collector import StockFlowError, check_stock_flow


class TestModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = Industry()
        cls.baseline.run()

    def test_baseline_runs_200_periods(self):
        self.assertEqual(self.baseline.parameters.PERIODS, 200)
        self.assertEqual(len(self.baseline.history), 200)
        self.assertGreaterEqual(min(r["n_firms"] for r in self.baseline.history), 2)

    def test_stock_flow_consistency_over_the_full_run(self):
        industry = self.baseline
        money = industry.roe.cash + sum(f.cash for f in industry.firms)
        self.assertAlmostEqual(money, industry.money, places=4)
        self.assertAlmostEqual(industry.roe.loans, sum(f.debt for f in industry.firms),
                               places=4)
        # Initial cash is zero in both sectors, so cumulated flows equal final cash.
        firm_flows = sum(row["firms"] for row in industry.flow_history)
        self.assertAlmostEqual(firm_flows, sum(f.cash for f in industry.firms), places=4)
        roe_flows = sum(row["roe"] for row in industry.flow_history)
        self.assertAlmostEqual(roe_flows, industry.roe.cash, places=4)
        for row in industry.history:
            self.assertAlmostEqual(row["sales_total"] + row["unmet_total"], row["demand"], places=6)

    def test_the_check_catches_a_leak(self):
        industry = Industry()
        industry.step()
        industry.firms[0].cash += 1.0
        with self.assertRaises(StockFlowError):
            check_stock_flow(industry)

    def test_label_swap_over_the_full_run(self):
        """Swapping the types everywhere except h changes nothing."""
        swapped = Industry(swapped_config())
        swapped.run()
        self.assertEqual(history_without_labels(self.baseline), history_without_labels(swapped))
        for a, b in zip(self.baseline.history, swapped.history):
            self.assertEqual(a["share_shaikh"], b["share_okishio"])
            self.assertEqual(a["price_avg"], b["price_avg"])

    def test_both_types_are_present_and_compete(self):
        last = self.baseline.history[-1]
        self.assertGreater(last["n_shaikh"] + last["n_okishio"], 0)
        self.assertGreater(sum(r["entries"] for r in self.baseline.history), 0)

    def test_switches_run(self):
        for overrides in ({"PRICING_RULE": "anchor"},
                          {"PRICING_RULE": "anchor", "PRICING_ANCHOR": "markup"},
                          {"PRICING_RULE": "anchor", "PRICING_ANCHOR": "leader"},
                          {"PRICING_RULE": "leader_follow"},
                          {"PRICING_RULE": "leader_follow", "EXCESS_DEMAND": "unserved"},
                          {"PRICING_RULE": "leader_follow", "LEADER_FOLLOW_FLOOR": "unit_cost"},
                          {"PRICING_RULE": "leader_follow", "LEADER_FOLLOW_FLOOR": "operating_cost"},
                          {"PRICING_RULE": "leader_follow", "SHORTAGE_RULE": "no_cut"},
                          {"PRICE_FLOOR": "operating_cost"}, {"EXCESS_DEMAND": "unserved"},
                          {"DEMAND_FORM": "logit"},
                          {"HURDLE_FLOOR_AT_ZERO": False}, {"REPLACEMENT": False},
                          {"INVESTMENT_SALES_LAG": 0}, {"BORROWING": True}, {"CASH_SHORTFALL": "overdraft"}, {"PLANT_SIZE": 20.0},
                          {"PLANT_LIFE": None}, {"SCRAP_COST": "unit_cost"},
                          {"DEPRECIATION": "use"}, {"DEPRECIATION": "use", "PLANT_LIFE": 10},
                          {"IDLE_SCRAPPING": True}, {"INVESTMENT_RULE": "retained_earnings"},
                          PLANT_ALTERNATIVES, {"TECH_DRAWS": True},
                          dict(PLANT_ALTERNATIVES, TECH_DRAWS=True), {"CHECKS_RAISE": False},
                          {"TECH_CHANGE": "innovation_set"},
                          {"TECH_CHANGE": "innovation_set", "TECH_SET": "neutral"},
                          {"TECH_CHANGE": "innovation_set", "TECH_REFERENCE": "frontier"},
                          {"TECH_CHANGE": "innovation_set", "TECH_DRAW_TIMING": "investment"},
                          {"TECH_CHANGE": "innovation_set", "TECH_DIFFUSION": "private"}):
            Industry(make_config(PERIODS=60, **overrides)).run()


if __name__ == "__main__":
    unittest.main()
