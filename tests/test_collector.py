"""The collector: checks that report residuals, records at source, the firms, plants and
macro columns, ties, and a firm with three plants of different vintages."""

import unittest

from helpers import make_config
from model import Industry
from model.collector import StockFlowError, residuals

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

    def test_floor_and_share_checks(self):
        industry = Industry(make_config())
        industry.step()
        firm = industry.producers[0]
        firm.price = firm.p_floor - 1.0
        firm.share += 0.1
        out, _ = residuals(industry)
        self.assertEqual(out["floor_viol"], 1)
        self.assertAlmostEqual(out["share_resid_end"], 0.1)


if __name__ == "__main__":
    unittest.main()
