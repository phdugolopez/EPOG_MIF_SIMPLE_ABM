"""Demand: replicator shares on E = 1 / p, sales up to u_max times the capacity offered, one
re-allocation of unserved demand, the rest lost (v4-final-model.md, "Schedule", step 2)."""
import unittest

from equations.demand_replicator import competitiveness, replicator_shares
from helpers import add_firm, empty_industry, industry
from markets.goods_market import allocate
from model.scheduler import allocate_demand, offered_plants


class TestReplicator(unittest.TestCase):
    def shares(self, prices, previous, chi=1.0):
        return replicator_shares(previous, [competitiveness(price) for price in prices], chi)

    def test_shares_sum_to_one(self):
        shares = self.shares([100.0, 98.0, 95.0], [0.5, 0.3, 0.2])
        self.assertAlmostEqual(sum(shares), 1.0, places=12)

    def test_equal_prices_leave_shares_unchanged(self):
        for got, was in zip(self.shares([98.0] * 3, [0.5, 0.3, 0.2]), [0.5, 0.3, 0.2]):
            self.assertAlmostEqual(got, was, places=12)

    def test_the_cheaper_firm_gains(self):
        dear, cheap = self.shares([100.0, 98.0], [0.5, 0.5])
        mean = 0.5 / 98 + 0.5 / 100
        self.assertAlmostEqual(cheap, 0.5 * (1 + (1 / 98 - mean) / mean), places=12)
        self.assertGreater(cheap, 0.5)
        self.assertAlmostEqual(dear + cheap, 1.0, places=12)

    def test_without_selection_shares_do_not_move(self):
        self.assertEqual(self.shares([100.0, 90.0], [0.6, 0.4], chi=0.0), [0.6, 0.4])

    def test_a_share_cut_below_zero_is_set_to_zero(self):
        shares = self.shares([100.0, 10.0], [0.5, 0.5], chi=4.0)
        self.assertEqual(shares, [0.0, 1.0])

    def test_the_order_of_the_firms_does_not_matter(self):
        prices, previous = [100.0, 97.0, 93.0, 99.0], [0.1, 0.4, 0.3, 0.2]
        self.assertEqual(self.shares(prices, previous),
                         self.shares(prices[::-1], previous[::-1])[::-1])


class TestAllocate(unittest.TestCase):
    def test_a_firm_sells_its_share_of_demand_up_to_its_limit(self):
        sales, lost = allocate(100.0, [0.5, 0.5], [60.0, 60.0])
        self.assertEqual((sales, lost), ([50.0, 50.0], 0.0))

    def test_unserved_demand_goes_pro_rata_to_the_room_left(self):
        sales, lost = allocate(100.0, [0.6, 0.2, 0.2], [40.0, 50.0, 30.0])
        self.assertEqual(sales, [40.0, 35.0, 25.0])
        self.assertEqual(lost, 0.0)

    def test_what_no_firm_can_serve_is_lost(self):
        sales, lost = allocate(100.0, [0.6, 0.4], [40.0, 45.0])
        self.assertEqual(sales, [40.0, 45.0])
        self.assertAlmostEqual(lost, 15.0, places=12)

    def test_demand_is_re_allocated_once_only(self):
        """The demand the first firm cannot serve is shared between the two others pro rata
        to their room, 5 and 45. The second is then full; what it could not take is lost,
        although the third still has room."""
        sales, lost = allocate(100.0, [0.6, 0.3, 0.1], [20.0, 35.0, 55.0])
        self.assertAlmostEqual(sales[1], 34.0, places=12)
        self.assertAlmostEqual(sales[2], 46.0, places=12)
        self.assertAlmostEqual(lost, 0.0, places=12)
        sales, lost = allocate(100.0, [0.8, 0.1, 0.1], [20.0, 12.0, 100.0])
        self.assertAlmostEqual(sum(sales) + lost, 100.0, places=12)
        self.assertLessEqual(sales[1], 12.0)

    def test_sales_and_lost_demand_add_up_to_demand(self):
        for limits in ([40.0, 50.0, 30.0], [10.0, 10.0, 10.0], [0.0, 80.0, 5.0]):
            sales, lost = allocate(100.0, [0.6, 0.2, 0.2], limits)
            self.assertAlmostEqual(sum(sales) + lost, 100.0, places=12)
            self.assertTrue(all(sold <= limit for sold, limit in zip(sales, limits)))


class TestAllocateDemand(unittest.TestCase):
    def test_shares_notional_demand_and_sales(self):
        ind = empty_industry()
        cheap = add_firm(ind, plants=5, price=98.0, share=0.5)
        dear = add_firm(ind, plants=5, share=0.5)
        allocate_demand(ind)
        self.assertGreater(cheap.share, 0.5)
        self.assertAlmostEqual(cheap.share + dear.share, 1.0, places=12)
        self.assertAlmostEqual(cheap.notional, cheap.share * 100.0, places=12)
        self.assertAlmostEqual(cheap.sales, cheap.notional, places=12)
        self.assertAlmostEqual(ind.lost, 0.0, places=12)
        self.assertEqual(ind.excess, 0.0)

    def test_a_plant_whose_operating_cost_is_above_the_price_is_not_offered(self):
        ind = empty_industry()
        firm = add_firm(ind, plants=3, price=62.0, share=1.0)        # C: ucs 64.25
        firm.plants[0].technique = ind.public[2]                     # D2: ucs 59.21
        self.assertEqual(offered_plants(firm), firm.plants[:1])
        allocate_demand(ind)
        self.assertEqual(firm.sales, 24.0)
        self.assertAlmostEqual(ind.lost, 76.0, places=12)

    def test_rationing_does_not_move_the_market_share(self):
        ind = empty_industry()
        small, large = add_firm(ind, plants=1, share=0.5), add_firm(ind, plants=5, share=0.5)
        allocate_demand(ind)
        self.assertAlmostEqual(small.share, 0.5, places=12)
        self.assertEqual(small.sales, 24.0)
        self.assertAlmostEqual(large.sales, 76.0, places=12)

    def test_the_first_period_has_spare_capacity_and_no_lost_demand(self):
        ind = industry()
        allocate_demand(ind)
        self.assertEqual(ind.excess, 0.0)
        self.assertAlmostEqual(ind.lost, 0.0, places=9)
        self.assertAlmostEqual(sum(firm.sales for firm in ind.firms), ind.demand, places=9)

    def test_reversing_the_firms_gives_the_same_sales(self):
        straight, reverse = industry(), industry()
        for ind in (straight, reverse):
            for firm, price in zip(ind.firms, (100.0, 97.0, 95.0, 99.0, 90.0, 104.0)):
                firm.price = price
        reverse.firms.reverse()
        allocate_demand(straight)
        allocate_demand(reverse)
        self.assertEqual({firm.id: (firm.share, firm.sales) for firm in straight.firms},
                         {firm.id: (firm.share, firm.sales) for firm in reverse.firms})


class TestOvertime(unittest.TestCase):
    def one_firm(self, **overrides):
        """One firm of 4 plants, capacity 80, facing a demand of 100."""
        ind = empty_industry(**overrides)
        firm = add_firm(ind, plants=4, share=1.0)
        allocate_demand(ind)
        return ind, firm

    def test_a_firm_sells_up_to_1_2_times_what_it_offers(self):
        ind, firm = self.one_firm()
        self.assertEqual(firm.sales, 96.0)
        self.assertAlmostEqual(ind.lost, 4.0, places=12)

    def test_the_limit_follows_u_max(self):
        ind, firm = self.one_firm(u_max=1.4)
        self.assertEqual(firm.sales, 100.0)
        self.assertEqual(ind.lost, 0.0)

    def test_without_overtime_a_firm_sells_what_it_offers_as_in_version_3(self):
        ind, firm = self.one_firm(u_max=1.0)
        self.assertEqual(firm.sales, 80.0)
        self.assertAlmostEqual(ind.lost, 20.0, places=12)

    def test_the_shortage_signal_is_demand_above_normal_capacity(self):
        """With or without overtime, and whether or not the demand is served."""
        for u_max in (1.0, 1.2, 1.4):
            ind, firm = self.one_firm(u_max=u_max)
            self.assertAlmostEqual(ind.excess, 0.2, places=12)

    def test_the_signal_counts_the_plants_that_are_not_offered(self):
        ind = empty_industry()
        firm = add_firm(ind, plants=6, price=60.0, share=1.0)        # C is not offered at 60
        allocate_demand(ind)
        self.assertEqual(firm.sales, 0.0)
        self.assertEqual(ind.lost, 100.0)
        self.assertEqual(ind.excess, 0.0)


if __name__ == "__main__":
    unittest.main()
