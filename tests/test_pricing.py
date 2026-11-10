"""Pricing (A5): one rule, two regimes (cost-edge cutting, systematic cutting), a shortage step
and a common floor, the unit cost of the firm's best plant in operation."""
import unittest

from equations.pricing_floor import price_floor
from equations.pricing_rule import posted_price
from helpers import add_firm, empty_industry, industry
from model.scheduler import set_prices


def price(previous=100.0, rival_prices=(100.0,), rival_costs=(78.0,), own_cost=75.0, spare=True,
          excess=0.0, cost_edge=True, cut=0.02, shortage_step=0.5):
    return posted_price(previous, list(rival_prices), list(rival_costs), own_cost, spare, excess,
                        cost_edge, cut, shortage_step)


class TestFloor(unittest.TestCase):
    def test_floor_is_the_unit_cost_of_the_best_plant(self):
        self.assertEqual(price_floor([78.0, 75.0, 76.0]), 75.0)
        self.assertEqual(price_floor([]), 0.0)


class TestShortage(unittest.TestCase):
    def test_a_firm_moves_up_to_the_next_higher_rival_price(self):
        self.assertEqual(price(previous=90.0, rival_prices=(95.0, 92.0, 88.0), rival_costs=(78.0,) * 3,
                               excess=0.1), (92.0, False))

    def test_with_no_rival_above_it_rises_by_half_the_excess_share(self):
        self.assertEqual(price(previous=100.0, rival_prices=(95.0, 100.0), rival_costs=(78.0,) * 2,
                               excess=0.1), (105.0, False))

    def test_no_firm_cuts_after_a_shortage(self):
        posted, cut = price(previous=100.0, rival_prices=(100.0,), excess=0.01, spare=True)
        self.assertAlmostEqual(posted, 100.5, places=9)
        self.assertFalse(cut)


class TestCostEdgeCutting(unittest.TestCase):
    def test_a_firm_with_spare_capacity_and_a_cost_edge_undercuts(self):
        self.assertEqual(price(own_cost=75.0, rival_costs=(78.0,)), (98.0, True))

    def test_equal_costs_give_no_edge(self):
        self.assertEqual(price(own_cost=78.0, rival_costs=(78.0,)), (100.0, False))

    def test_the_edge_is_over_a_rival_posting_the_lowest_rival_price(self):
        """The rival at 100 has the lower cost; the dearer rival posts more than the lowest."""
        result = price(own_cost=76.0, rival_prices=(100.0, 104.0), rival_costs=(75.0, 78.0))
        self.assertEqual(result, (100.0, False))

    def test_without_spare_capacity_it_follows(self):
        self.assertEqual(price(own_cost=75.0, spare=False), (100.0, False))

    def test_it_follows_the_lowest_price_posted_its_own_included(self):
        self.assertEqual(price(previous=100.0, rival_prices=(96.0, 99.0), rival_costs=(70.0, 70.0),
                               own_cost=78.0), (96.0, False))
        self.assertEqual(price(previous=94.0, rival_prices=(96.0, 99.0), rival_costs=(70.0, 70.0),
                               own_cost=78.0), (94.0, False))


class TestSystematicCutting(unittest.TestCase):
    def test_spare_capacity_is_enough_to_cut(self):
        self.assertEqual(price(own_cost=78.0, rival_costs=(75.0,), cost_edge=False), (98.0, True))

    def test_without_spare_capacity_it_follows(self):
        self.assertEqual(price(own_cost=78.0, cost_edge=False, spare=False), (100.0, False))


class TestFloorAndRises(unittest.TestCase):
    def test_a_cut_stops_at_the_floor(self):
        self.assertEqual(price(previous=76.0, rival_prices=(76.0,), own_cost=75.0), (75.0, True))

    def test_a_firm_at_its_floor_does_not_follow_below_it(self):
        self.assertEqual(price(previous=78.0, rival_prices=(74.0,), rival_costs=(70.0,),
                               own_cost=78.0), (78.0, False))

    def test_without_a_shortage_a_price_does_not_rise(self):
        """A firm already below the cut price stays where it is, and that is not a cut."""
        self.assertEqual(price(previous=90.0, rival_prices=(100.0,), own_cost=75.0), (90.0, False))
        self.assertEqual(price(previous=90.0, rival_prices=(100.0,), own_cost=78.0), (90.0, False))

    def test_a_firm_that_falls_to_a_floor_above_the_lowest_rival_does_not_cut(self):
        result = price(previous=100.0, rival_prices=(96.0, 99.0), rival_costs=(98.0, 98.0),
                       own_cost=97.0)
        self.assertEqual(result, (97.0, False))

    def test_the_floor_wins_over_the_previous_price(self):
        """Q2: when the floor has moved above last period's price, the firm posts its floor."""
        self.assertEqual(price(previous=75.5, rival_prices=(75.5,), rival_costs=(75.0,),
                               own_cost=76.0), (76.0, False))

    def test_a_firm_alone_keeps_its_price(self):
        self.assertEqual(price(rival_prices=(), rival_costs=()), (100.0, False))


class TestSetPrices(unittest.TestCase):
    def test_the_first_period(self):
        """Every firm has spare capacity (0.888). The firms on D1 and D2 have a cost edge over a
        firm posting 100 and cut to 98; those on C have none and follow."""
        ind = industry()
        set_prices(ind)
        self.assertEqual([firm.price for firm in ind.firms], [100.0, 100.0, 98.0, 98.0, 98.0, 98.0])
        self.assertEqual([firm.cut for firm in ind.firms], [False, False, True, True, True, True])

    def test_under_systematic_cutting_every_firm_cuts(self):
        ind = industry(pricing="systematic")
        set_prices(ind)
        self.assertEqual({firm.price for firm in ind.firms}, {98.0})

    def test_moves_are_simultaneous(self):
        """In the second period every firm reads the prices of the first, not this period's.
        The firms on C follow to 98. Those on D1 have no edge over the firms posting 98 (the
        other one on D1, and D2) and stay. Those on D2 have one over D1 and cut again."""
        ind = industry()
        set_prices(ind)
        set_prices(ind)
        prices = [round(firm.price, 4) for firm in ind.firms]
        self.assertEqual(prices, [98.0, 98.0, 98.0, 98.0, 96.04, 96.04])
        self.assertEqual([firm.cut for firm in ind.firms], [False] * 4 + [True] * 2)

    def test_reversing_the_firms_gives_the_same_prices(self):
        straight, reverse = industry(), industry()
        reverse.firms.reverse()
        for _ in range(3):
            set_prices(straight)
            set_prices(reverse)
        self.assertEqual({f.id: f.price for f in straight.firms}, {f.id: f.price for f in reverse.firms})

    def test_no_price_is_below_the_unit_cost_of_the_best_plant(self):
        ind = industry(pricing="systematic")
        for _ in range(40):
            set_prices(ind)
        for firm in ind.firms:
            self.assertGreaterEqual(firm.price, min(q.technique.ucs + 0.1 * q.technique.kappa
                                                    for q in firm.plants))
        self.assertAlmostEqual(ind.firms[4].price, 74.999, places=9)

    def test_a_firm_without_a_plant_is_no_rival_and_does_not_cut(self):
        ind = empty_industry()
        leader = add_firm(ind, technique=ind.public[2], price=90.0)
        dear = add_firm(ind, price=100.0)
        empty = add_firm(ind, plants=0, price=80.0)
        for firm in ind.firms:
            firm.util = 0.5
        set_prices(ind)
        self.assertEqual((leader.price, leader.cut), (90.0, False))
        self.assertEqual((dear.price, dear.cut), (90.0, False))
        self.assertEqual((empty.price, empty.cut), (80.0, False))

    def test_after_a_shortage_prices_rise(self):
        ind = industry()
        ind.excess = 0.1
        set_prices(ind)
        self.assertEqual({firm.price for firm in ind.firms}, {105.0})
        self.assertFalse(any(firm.cut for firm in ind.firms))


if __name__ == "__main__":
    unittest.main()
