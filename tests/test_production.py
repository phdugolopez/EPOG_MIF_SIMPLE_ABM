"""Production: merit order, overtime and the price-covers-cost condition."""

import unittest

from equations.merit_order import dispatch
from equations.offered_capacity import offered_capacity
from equations.operating_cost import operating_cost


class TestProduction(unittest.TestCase):
    def test_cheapest_plant_runs_first(self):
        normal, overtime = dispatch([64.25, 59.21], [120.0, 133.0], 150.0, 1.2, 0.1)
        self.assertAlmostEqual(normal[1], 133.0)
        self.assertAlmostEqual(normal[0], 17.0)
        self.assertEqual(overtime, [0.0, 0.0])

    def test_overtime_only_when_needed_and_at_a_premium(self):
        normal, overtime = dispatch([64.25, 59.21], [120.0, 133.0], 260.0, 1.2, 0.1)
        self.assertEqual(normal, [120.0, 133.0])
        self.assertAlmostEqual(sum(overtime), 7.0)
        cost = operating_cost([64.25, 59.21], normal, overtime, 0.1)
        self.assertGreater(cost, 64.25 * 120 + 59.21 * 133 + 59.21 * 7)

    def test_ties_share_output_pro_rata(self):
        normal, _ = dispatch([60.0, 60.0], [100.0, 50.0], 90.0, 1.2, 0.1)
        self.assertAlmostEqual(normal[0], 60.0)
        self.assertAlmostEqual(normal[1], 30.0)

    def test_output_capped_at_u_max(self):
        normal, overtime = dispatch([60.0], [100.0], 500.0, 1.2, 0.1)
        self.assertAlmostEqual(normal[0] + overtime[0], 120.0)

    def test_plants_not_covering_cost_are_not_offered(self):
        self.assertAlmostEqual(
            offered_capacity([64.25, 59.21], [120.0, 133.0], 62.0, 1.2, 0.1), 133.0
        )
        self.assertAlmostEqual(
            offered_capacity([64.25, 59.21], [120.0, 133.0], 100.0, 1.2, 0.1), 1.2 * 253.0
        )


if __name__ == "__main__":
    unittest.main()
