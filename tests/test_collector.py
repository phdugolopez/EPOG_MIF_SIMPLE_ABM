"""The collector: checks that report residuals, records at source, the firms, plants and
macro columns, ties, and a firm with three plants of different vintages."""

import json
import math
import unittest
from types import SimpleNamespace

from equations.merit_order import dispatch
from equations.price_floor import price_floor
from helpers import make_config, swapped_config, three_plant_industry, without_labels
from model import Industry
from model.collector import StockFlowError, capacity_flows, firm_row, residuals, tied_ids

RESIDUALS = (
    "money_resid", "debt_resid", "nw_resid", "tfm_row_resid", "tfm_col_resid",
    "share_resid_demand", "share_resid_end", "sales_resid", "cap_resid",
)


class TestChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = Industry(make_config(PERIODS=60))
        cls.baseline.run()

    def test_residuals_are_stored_every_period_and_pass(self):
        for row in self.baseline.history:
            for name in RESIDUALS:
                self.assertLessEqual(abs(row[name]), row["check_tol"], name)
            self.assertEqual(row["check_fail"], 0)
            self.assertEqual(row["floor_viol"], 0)
            self.assertEqual(row["util_max_viol"], 0)
            self.assertGreaterEqual(row["share_min"], 0.0)
        self.assertEqual(self.baseline.n_check_fail, 0)

    def test_a_leak_stops_the_run_by_default(self):
        industry = Industry(make_config())
        industry.step()
        industry.firms[0].cash += 1.0
        with self.assertRaises(StockFlowError):
            industry.step()

    def test_a_leak_is_counted_when_checks_do_not_raise(self):
        industry = Industry(make_config(CHECKS_RAISE=False))
        industry.step()
        industry.firms[0].cash += 1.0  # money is no longer conserved from now on
        industry.run(3)
        self.assertEqual(industry.n_check_fail, 3)
        for row in industry.history[1:]:
            self.assertAlmostEqual(row["money_resid"], 1.0)
            self.assertGreaterEqual(row["check_fail"], 1)
        self.assertEqual(industry.history[0]["check_fail"], 0)

    def test_the_capacity_identity_catches_a_plant_from_nowhere(self):
        industry = Industry(make_config())
        industry.step()
        firm = industry.firms[0]
        technique = industry.techniques["C"]
        firm.plants.append(industry.new_plant(technique, 50.0, vintage=industry.time))
        out, fails = residuals(industry)
        self.assertAlmostEqual(out["cap_resid"], -50.0)
        self.assertTrue(any("cap_resid" in f for f in fails))

    def test_non_renewal_firms_report_no_desired_capacity(self):
        """A firm that invest() skips on non-renewal has exp_sales and cap_desired None,
        so its row does not look like investment that could not be financed."""
        industry = Industry(make_config())
        industry.step()
        for row in industry.firm_history:
            if row["capacity"] > 0.0:  # not an entrant of the period, which has none
                self.assertIsNotNone(row["cap_desired"])
        firm = industry.firms[0]
        firm.non_renewal = True  # as scrap_plants sets it when the last plant retires
        row = firm_row(industry, firm, set())
        self.assertIsNone(row["exp_sales"])
        self.assertIsNone(row["cap_desired"])

    def test_floor_and_share_checks(self):
        industry = Industry(make_config())
        industry.step()
        firm = industry.producers[0]
        firm.price = firm.p_floor - 1.0
        firm.share += 0.1
        out, _ = residuals(industry)
        self.assertEqual(out["floor_viol"], 1)
        self.assertAlmostEqual(out["share_resid_end"], 0.1)


class TestThreePlants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.industry, cls.a, cls.b, cls.old, cls.x = three_plant_industry()
        cls.industry.step()  # the checks, the capacity identity included, raise otherwise
        cls.rows = {r["firm_id"]: r for r in cls.industry.firm_history}
        cls.plants = {r["plant_id"]: r for r in cls.industry.plant_history}

    def test_weighted_aggregates(self):
        a, row = self.a, self.rows[0]
        plants = [p for p in a.producing_plants]
        self.assertEqual(len(plants), 3)
        caps = [p.capacity for p in plants]
        self.assertAlmostEqual(row["kappa"], sum(p.kappa * q for p, q in zip(plants, caps))
                               / sum(caps))
        self.assertAlmostEqual(row["k_cost"], sum(p.kappa * p.capacity for p in plants))
        self.assertAlmostEqual(row["r_avg"], row["profit"] / row["k_cost"])
        running = [p for p in plants if p.output > 0.0]
        self.assertAlmostEqual(row["ucs"], sum(p.ucs * p.output for p in running)
                               / sum(p.output for p in running))
        self.assertAlmostEqual(row["output"], row["sales"])
        self.assertAlmostEqual(row["gos"] - row["depreciation"] - row["interest"],
                               row["profit"])
        self.assertEqual((row["n_plants"], row["oldest_vintage"], row["newest_vintage"]),
                         (3, -9, 0))
        ucs = [p.ucs for p in running]
        self.assertAlmostEqual(row["ucs_spread"], max(ucs) / min(ucs))

    def test_floor_is_the_most_expensive_plant_needed(self):
        a, row = self.a, self.rows[0]
        ucs = [p.ucs for p in a.producing_plants]
        caps = [p.capacity for p in a.producing_plants]
        self.assertEqual(row["p_floor"], price_floor(ucs, caps, 300.0, 1.2, 0.10))
        self.assertEqual(row["p_floor"], 90.0)  # 300 needs C, D1 and part of X
        self.assertGreaterEqual(row["price"], row["p_floor"])

    def test_r_newest_is_on_the_newest_vintage(self):
        row, c = self.rows[0], self.industry.techniques["C"]
        self.assertAlmostEqual(row["r_newest"],
                               (row["price"] - (c.ucs + 0.1 * c.kappa)) / c.kappa)

    def test_merit_order_and_plant_rows(self):
        a = self.a
        normal, overtime = dispatch([p.ucs for p in a.producing_plants],
                                    [p.capacity for p in a.producing_plants],
                                    a.sales, 1.2, 0.10)
        for plant, n, o in zip(a.producing_plants, normal, overtime):
            row = self.plants[plant.plant_id]
            self.assertAlmostEqual(row["output"], n + o)
            self.assertEqual(row["running"], n + o > 0.0)
            self.assertAlmostEqual(row["uc"], plant.ucs + 0.1 * plant.kappa)
            self.assertAlmostEqual(row["r_plant"], (a.price - row["uc"]) / plant.kappa)
        self.assertEqual(self.plants[self.old.plant_id]["retire_cause"], "age")
        self.assertEqual(self.plants[self.x.plant_id]["retire_cause"], "replacement")
        self.assertAlmostEqual(self.plants[self.x.plant_id]["write_off"], 5_000.0)
        self.assertAlmostEqual(self.plants[self.old.plant_id]["write_off"], 0.0)
        self.assertTrue(self.plants[self.x.plant_id]["retired"])

    def test_capacity_flows_through_retirement_replacement_and_exit(self):
        a, b, row_a, row_b = self.a, self.b, self.rows[0], self.rows[1]
        self.assertEqual(row_a["cap_retired"], 220.0)
        self.assertEqual(row_a["cap_replace"], 100.0)
        self.assertAlmostEqual(row_a["cap_ordered"], 300.0 - 120.0)  # desired - C
        self.assertEqual(row_a["tech_new"], "D2")
        self.assertTrue(row_b["exited"])
        self.assertEqual(row_b["exit_cause"], "share")
        self.assertEqual(row_b["share_end"], 0.0)
        self.assertGreater(row_b["cap_ordered"], 0.0)
        # borrow is the period's financing, not the exit settlement: never negative here.
        self.assertGreaterEqual(row_b["borrow"], 0.0)
        self.assertEqual(row_b["borrow"], row_b["borrow_plants"])
        flows = capacity_flows(self.industry)
        self.assertEqual(flows["exit"], 130.0)
        self.assertEqual(flows["cancelled"], row_b["cap_ordered"])
        self.assertAlmostEqual(
            flows["k_start"] - flows["retired"] - flows["exit"] + flows["ordered"]
            + flows["entry"] - flows["cancelled"], flows["k_next"])
        self.assertEqual(flows["k_next"], 120.0 + row_a["cap_ordered"])
        b_plant = self.plants[b.producing_plants[0].plant_id]
        self.assertTrue(b_plant["exited_with_firm"])
        self.assertEqual(b_plant["retire_cause"], "exit")
        self.assertGreater(b_plant["write_off"], 0.0)

    def test_tech_other_and_r_best(self):
        # Firm 0 applies the unit-cost rule; the profit-rate rule at its price picks
        # the technique with the best rate, which tech_other reports.
        row = self.rows[0]
        menu = self.industry.menu
        rates = {t.name: (row["price"] - t.ucs - 0.1 * t.kappa) / t.kappa for t in menu}
        self.assertEqual(row["tech_other"], max(rates, key=rates.get))
        self.assertAlmostEqual(row["r_best"], max(rates.values()))
        self.assertEqual(row["rule"], "unit_cost")


class TestTies(unittest.TestCase):
    def test_tied_ids_keep_every_tied_firm(self):
        firms = [SimpleNamespace(firm_id=i, price=p)
                 for i, p in enumerate((100.0, 99.0, 99.0, 101.0))]
        self.assertEqual(tied_ids(firms, lambda f: f.price), [1, 2])
        self.assertEqual(tied_ids(list(reversed(firms)), lambda f: f.price), [1, 2])

    def test_leader_columns_on_the_paired_start(self):
        industry = Industry(make_config())
        industry.step()
        row = industry.history[0]
        leaders = json.loads(row["leader_ids"])
        prices = {f.firm_id: f.price for f in industry.producers}
        low = min(prices.values())
        self.assertEqual(leaders, sorted(i for i, p in prices.items() if math.isclose(p, low)))
        self.assertEqual(row["n_leaders"], len(leaders))
        self.assertEqual(row["leader_id"], leaders[0] if len(leaders) == 1 else -1)
        self.assertGreaterEqual(row["n_lowest_uc"], 2)  # the initial firms come in pairs
        self.assertEqual(row["lowest_uc_id"], -1)
        self.assertEqual(row["leader_is_lowest_cost"],
                         bool(set(leaders) & set(json.loads(row["lowest_uc_ids"]))))


def mirrored(row: dict) -> dict:
    swap = {"shaikh": "okishio", "okishio": "shaikh"}

    def name(k):
        for a, b in swap.items():
            if a in k:
                return k.replace(a, b)
        return k
    return {name(k): v for k, v in row.items()}


class TestLabelSwap(unittest.TestCase):
    def test_new_columns_are_label_free(self):
        a = Industry(make_config(PERIODS=80))
        b = Industry(swapped_config(PERIODS=80))
        a.run()
        b.run()
        self.assertEqual(without_labels(a.firm_history), without_labels(b.firm_history))
        self.assertEqual(without_labels(a.plant_history), without_labels(b.plant_history))
        self.assertEqual(a.history, [mirrored(r) for r in b.history])
        self.assertEqual(a.flow_history, b.flow_history)


if __name__ == "__main__":
    unittest.main()
