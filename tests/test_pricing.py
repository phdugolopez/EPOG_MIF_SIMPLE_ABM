"""Pricing: the three cutting rules and who is entitled under each, universal undercutting,
the two floors, and step 1 (v4-final-model.md, "Schedule", step 1)."""
import unittest

from equations.pricing_cutting import cutting_price
from equations.pricing_entitlement import (entitled_cost_edge, entitled_normal_price,
                                           entitled_systematic)
from equations.pricing_floor import operating_cost_floor, unit_cost_floor
from equations.pricing_universal import universal_price
from helpers import add_firm, empty_industry, industry
from markets.plant_market import buy_plant
from model.scheduler import (STEPS, close_period, read_quote, set_prices, start_period)
from parameters import OPTIONS

CUTTING_RULES = ("cost_edge", "normal_price", "systematic")


def price(previous=100.0, rival_prices=(100.0,), entitled=True, excess=0.0, floor=75.0,
          cut=0.02, shortage_step=0.25):
    return cutting_price(previous, list(rival_prices), entitled, excess, floor, cut,
                         shortage_step)


def universal(previous=100.0, lowest=100.0, floor=75.0, excess=0.0, alone=False):
    return universal_price(previous, lowest, floor, excess, alone, cut=0.02, rise=0.03, cap=3.0)


class TestShortage(unittest.TestCase):
    def test_a_firm_moves_up_to_the_next_higher_rival_price(self):
        self.assertEqual(price(previous=90.0, rival_prices=(95.0, 92.0, 88.0), excess=0.1),
                         (92.0, False))

    def test_with_no_rival_above_it_rises_by_a_quarter_of_the_excess_share(self):
        posted, cut = price(previous=100.0, rival_prices=(95.0, 100.0), excess=0.1)
        self.assertAlmostEqual(posted, 102.5, places=9)
        self.assertFalse(cut)

    def test_the_rise_follows_the_shortage_step(self):
        posted, cut = price(rival_prices=(95.0,), excess=0.1, shortage_step=0.5)
        self.assertAlmostEqual(posted, 105.0, places=9)
        self.assertFalse(cut)

    def test_no_firm_cuts_after_a_shortage_even_if_entitled(self):
        posted, cut = price(excess=0.01, entitled=True)
        self.assertAlmostEqual(posted, 100.25, places=9)
        self.assertFalse(cut)

    def test_after_a_shortage_a_price_is_never_below_the_floor(self):
        self.assertEqual(price(previous=70.0, rival_prices=(72.0,), excess=0.1, floor=75.0),
                         (75.0, False))

    def test_a_firm_without_a_rival_rises_by_the_same_step_without_a_cap(self):
        for previous in (100.0, 1000.0):
            posted, cut = price(previous=previous, rival_prices=(), excess=0.4)
            self.assertAlmostEqual(posted, 1.1 * previous, places=9)
            self.assertFalse(cut)


class TestCutting(unittest.TestCase):
    def test_an_entitled_firm_undercuts_the_lowest_rival_price(self):
        self.assertEqual(price(rival_prices=(100.0, 104.0)), (98.0, True))

    def test_a_firm_that_is_not_entitled_follows_the_lowest_price_its_own_included(self):
        self.assertEqual(price(previous=100.0, rival_prices=(96.0, 99.0), entitled=False),
                         (96.0, False))
        self.assertEqual(price(previous=94.0, rival_prices=(96.0, 99.0), entitled=False),
                         (94.0, False))

    def test_a_cut_stops_at_the_floor(self):
        self.assertEqual(price(previous=76.0, rival_prices=(76.0,), floor=75.0), (75.0, True))

    def test_a_firm_at_its_floor_does_not_follow_below_it(self):
        self.assertEqual(price(previous=78.0, rival_prices=(74.0,), entitled=False, floor=78.0),
                         (78.0, False))

    def test_without_a_shortage_a_price_does_not_rise(self):
        """A firm already below the cut price stays where it is, and that is not a cut."""
        self.assertEqual(price(previous=90.0, rival_prices=(100.0,)), (90.0, False))
        self.assertEqual(price(previous=90.0, rival_prices=(100.0,), entitled=False),
                         (90.0, False))

    def test_a_firm_that_falls_to_a_floor_above_the_lowest_rival_does_not_cut(self):
        self.assertEqual(price(previous=100.0, rival_prices=(96.0, 99.0), floor=97.0),
                         (97.0, False))

    def test_the_floor_wins_over_the_previous_price(self):
        """Q2: when the floor has moved above last period's price, the firm posts its floor."""
        self.assertEqual(price(previous=75.5, rival_prices=(75.5,), entitled=False, floor=76.0),
                         (76.0, False))

    def test_a_firm_without_a_rival_keeps_its_price_or_takes_its_floor(self):
        self.assertEqual(price(rival_prices=()), (100.0, False))
        self.assertEqual(price(previous=70.0, rival_prices=(), floor=75.0), (75.0, False))


class TestEntitlement(unittest.TestCase):
    def test_cost_edge_needs_spare_capacity_and_a_strictly_lower_unit_cost(self):
        self.assertTrue(entitled_cost_edge(True, 75.0, [78.0]))
        self.assertFalse(entitled_cost_edge(False, 75.0, [78.0]))
        self.assertFalse(entitled_cost_edge(True, 78.0, [78.0]))
        self.assertFalse(entitled_cost_edge(True, 78.0, [75.0]))

    def test_the_edge_is_over_one_rival_that_posts_the_lowest_price(self):
        self.assertTrue(entitled_cost_edge(True, 76.0, [75.0, 78.0]))
        self.assertFalse(entitled_cost_edge(True, 76.0, [75.0, 76.0]))

    def test_normal_price_above_its_price_of_production_spare_capacity_is_enough(self):
        """A firm with a unit cost of 75 and a price of production of 83, without an edge."""
        self.assertTrue(entitled_normal_price(True, 75.0, [75.0], 90.0, 83.0))
        self.assertTrue(entitled_normal_price(True, 75.0, [70.0], 83.5, 83.0))
        self.assertFalse(entitled_normal_price(False, 75.0, [75.0], 90.0, 83.0))

    def test_normal_price_at_or_below_its_price_of_production_it_needs_the_cost_edge(self):
        self.assertFalse(entitled_normal_price(True, 75.0, [75.0], 83.0, 83.0))
        self.assertFalse(entitled_normal_price(True, 75.0, [75.0], 80.0, 83.0))
        self.assertTrue(entitled_normal_price(True, 75.0, [78.0], 80.0, 83.0))
        self.assertFalse(entitled_normal_price(False, 75.0, [78.0], 80.0, 83.0))

    def test_normal_price_a_cut_can_end_below_the_price_of_production(self):
        """Decision 16: a cut is a full (1 - c) P."""
        entitled = entitled_normal_price(True, 75.0, [75.0], 84.0, 83.0)
        posted, cut = price(rival_prices=(84.0,), entitled=entitled)
        self.assertAlmostEqual(posted, 82.32, places=9)
        self.assertTrue(cut)

    def test_systematic_needs_spare_capacity_alone(self):
        self.assertTrue(entitled_systematic(True))
        self.assertFalse(entitled_systematic(False))


class TestUniversal(unittest.TestCase):
    def test_every_firm_undercuts_the_lowest_price_whatever_its_own_price(self):
        for previous in (90.0, 100.0, 120.0):
            self.assertEqual(universal(previous=previous), (98.0, True))

    def test_the_floor_stops_a_cut(self):
        self.assertEqual(universal(previous=76.0, lowest=76.0), (75.0, False))
        self.assertEqual(universal(previous=80.0, lowest=70.0), (75.0, False))

    def test_after_a_shortage_every_firm_posts_the_lowest_price_plus_the_rise(self):
        for previous in (100.0, 110.0):       # a firm above that level lowers its price
            posted, cut = universal(previous=previous, excess=0.1)
            self.assertAlmostEqual(posted, 103.0, places=12)
            self.assertFalse(cut)

    def test_after_a_shortage_a_price_can_be_below_the_floor(self):
        """Decision 17: the floor applies to a cut only."""
        posted, cut = universal(previous=80.0, lowest=70.0, floor=75.0, excess=0.1)
        self.assertAlmostEqual(posted, 72.1, places=12)
        self.assertFalse(cut)

    def test_a_firm_alone_raises_its_price_up_to_three_times_its_floor(self):
        posted, cut = universal(alone=True)
        self.assertAlmostEqual(posted, 103.0, places=12)
        self.assertFalse(cut)
        self.assertEqual(universal(previous=224.0, lowest=224.0, alone=True), (225.0, False))
        self.assertEqual(universal(previous=300.0, lowest=300.0, alone=True), (225.0, False))

    def test_a_firm_alone_rises_with_or_without_a_shortage(self):
        self.assertEqual(universal(alone=True, excess=0.2), universal(alone=True))


class TestFloors(unittest.TestCase):
    def setUp(self):
        self.industry = empty_industry()
        menu = self.industry.public               # operating costs 64.25, 61.77 and 59.21
        self.firm = add_firm(self.industry, technique=menu[2], plants=2, price=90.0)
        other = add_firm(self.industry, technique=menu[0])
        self.firm.plants += other.plants
        self.industry.firms.remove(other)         # one firm: two plants of D2, one of C

    def quote(self, **overrides):
        return read_quote(self.firm, empty_industry(**overrides).params)

    def test_the_two_floors_as_equations(self):
        self.assertEqual(unit_cost_floor([78.0, 75.0, 76.0]), 75.0)
        self.assertEqual(operating_cost_floor([59.21, 64.25], [59.21, 59.21, 64.25]), 64.25)
        self.assertEqual(operating_cost_floor([], [59.21, 59.21, 64.25]), 59.21)

    def test_the_unit_cost_floor_is_the_unit_cost_of_the_best_plant(self):
        quote = self.quote()
        self.assertAlmostEqual(quote.floor, 59.21 + 15.789, places=9)
        self.assertEqual(quote.floor, quote.cost)

    def test_the_price_of_production_is_that_of_the_best_plant(self):
        self.assertAlmostEqual(self.quote().normal_price, 74.999 + 0.16 * 157.89, places=9)
        self.assertAlmostEqual(self.quote(rbar=0.05).normal_price, 74.999 + 0.05 * 157.89,
                               places=9)

    def test_the_operating_cost_floor_is_that_of_the_dearest_plant_that_ran(self):
        for plant, output in zip(self.firm.plants, (20.0, 5.0, 0.0)):
            plant.output = output
        self.assertEqual(self.quote(price_floor="operating_cost").floor, 59.21)
        self.firm.plants[2].output = 1.0
        self.assertEqual(self.quote(price_floor="operating_cost").floor, 64.25)

    def test_without_output_it_is_the_operating_cost_of_the_cheapest_plant(self):
        self.assertEqual(self.quote(price_floor="operating_cost").floor, 59.21)

    def test_under_the_operating_cost_floor_the_cost_edge_is_still_read_on_unit_cost(self):
        quote = self.quote(price_floor="operating_cost")
        self.assertAlmostEqual(quote.cost, 74.999, places=9)
        self.assertLess(quote.floor, quote.cost)

    def test_spare_capacity_is_a_last_utilisation_below_one(self):
        self.firm.util = 0.99
        self.assertTrue(self.quote().spare)
        for util in (1.0, 1.15):
            self.firm.util = util
            self.assertFalse(self.quote().spare)

    def test_a_cutting_step_stops_at_the_operating_cost(self):
        ind = empty_industry(pricing="systematic", price_floor="operating_cost")
        low = add_firm(ind, technique=ind.public[2], price=60.0)
        rival = add_firm(ind, technique=ind.public[1], price=60.0)
        for firm in ind.firms:
            firm.util = 0.5
        set_prices(ind)
        self.assertEqual((low.price, low.cut), (59.21, True))       # 0.98 x 60 = 58.8
        self.assertEqual((rival.price, rival.cut), (61.77, False))


class TestSetPrices(unittest.TestCase):
    def test_the_first_period_under_cost_edge_cutting(self):
        """Every firm has spare capacity (0.888). The firms on D1 and D2 have a cost edge
        over a firm posting 100 and cut to 98; those on C have none and follow."""
        ind = industry()
        set_prices(ind)
        self.assertEqual([firm.price for firm in ind.firms],
                         [100.0, 100.0, 98.0, 98.0, 98.0, 98.0])
        self.assertEqual([firm.cut for firm in ind.firms], [False, False, True, True, True, True])

    def test_the_first_period_under_normal_price_cutting(self):
        """100 is above the price of production of D1 (98.8), so its firms cut on spare
        capacity; it is not above that of C (100.0) or D2 (100.3): C has no edge and follows,
        D2 has one and cuts."""
        ind = industry(pricing="normal_price")
        set_prices(ind)
        self.assertEqual([firm.price for firm in ind.firms],
                         [100.0, 100.0, 98.0, 98.0, 98.0, 98.0])

    def test_normal_price_cutting_lets_a_firm_without_an_edge_cut_above_its_normal_price(self):
        """Three firms on D2, price of production 100.26. At 110 all cut, with no cost edge;
        under cost-edge cutting none does."""
        for pricing, expected in (("normal_price", 107.8), ("cost_edge", 110.0)):
            ind = empty_industry(pricing=pricing)
            firms = [add_firm(ind, technique=ind.public[2], price=110.0) for _ in range(3)]
            for firm in firms:
                firm.util = 0.8
            set_prices(ind)
            for firm in firms:
                self.assertAlmostEqual(firm.price, expected, places=9)

    def test_under_systematic_cutting_every_firm_with_spare_capacity_cuts(self):
        ind = industry(pricing="systematic")
        set_prices(ind)
        self.assertEqual({firm.price for firm in ind.firms}, {98.0})
        full = industry(pricing="systematic")
        full.firms[0].util = 1.0
        set_prices(full)
        self.assertEqual((full.firms[0].price, full.firms[0].cut), (100.0, False))

    def test_under_universal_undercutting_every_firm_cuts_whatever_its_utilisation_and_cost(self):
        ind = industry(pricing="universal")
        for firm in ind.firms:
            firm.util = 1.2
        set_prices(ind)
        self.assertEqual({firm.price for firm in ind.firms}, {98.0})
        self.assertTrue(all(firm.cut for firm in ind.firms))

    def test_universal_firms_post_from_the_prices_at_the_start_of_the_step(self):
        ind = empty_industry(pricing="universal")
        menu = ind.public                         # unit costs 78.0, 76.0 and 75.0
        firms = [add_firm(ind, technique=menu[0], price=100.0),
                 add_firm(ind, technique=menu[2], price=90.0),
                 add_firm(ind, technique=menu[1], price=78.0)]
        set_prices(ind)
        cut_price = 0.98 * 78.0                   # 76.44: below the floor of the firm on C only
        expected = [(78.0, False), (cut_price, True), (cut_price, True)]
        for firm, (posted, cut) in zip(firms, expected):
            self.assertAlmostEqual(firm.price, posted, places=9)
            self.assertEqual(firm.cut, cut)

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
        for pricing in OPTIONS["pricing"]:
            straight, reverse = industry(pricing=pricing), industry(pricing=pricing)
            reverse.firms.reverse()
            for _ in range(3):
                set_prices(straight)
                set_prices(reverse)
            self.assertEqual({firm.id: firm.price for firm in straight.firms},
                             {firm.id: firm.price for firm in reverse.firms}, pricing)

    def test_after_a_shortage_prices_rise(self):
        for pricing, expected in (("cost_edge", 102.5), ("normal_price", 102.5),
                                  ("systematic", 102.5), ("universal", 103.0)):
            ind = industry(pricing=pricing)
            ind.excess = 0.1
            set_prices(ind)
            for firm in ind.firms:
                self.assertAlmostEqual(firm.price, expected, places=9, msg=pricing)
            self.assertFalse(any(firm.cut for firm in ind.firms))

    def test_the_one_firm_with_a_plant_keeps_its_price_or_raises_it(self):
        for pricing, expected in (("cost_edge", 100.0), ("normal_price", 100.0),
                                  ("systematic", 100.0), ("universal", 103.0)):
            ind = empty_industry(pricing=pricing)
            alone = add_firm(ind, price=100.0)
            add_firm(ind, plants=0, price=60.0)
            set_prices(ind)
            self.assertAlmostEqual(alone.price, expected, places=9, msg=pricing)
            self.assertFalse(alone.cut)


class TestFirmsWithoutAPlant(unittest.TestCase):
    """Decision 14: a firm without a plant in operation keeps its price under each of the
    four rules and is no one's rival."""

    def build(self, pricing, excess=0.0):
        ind = empty_industry(pricing=pricing)
        leader = add_firm(ind, technique=ind.public[2], price=90.0)
        dear = add_firm(ind, price=100.0)
        empty = add_firm(ind, plants=0, price=80.0)
        for firm in ind.firms:
            firm.util = 0.5
        ind.excess = excess
        set_prices(ind)
        return leader, dear, empty

    def test_it_keeps_its_price_and_does_not_cut(self):
        for pricing in OPTIONS["pricing"]:
            for excess in (0.0, 0.2):
                leader, dear, empty = self.build(pricing, excess)
                self.assertEqual((empty.price, empty.cut), (80.0, False), (pricing, excess))

    def test_it_is_no_one_s_rival(self):
        """Its price of 80 is below every other and is read by no firm."""
        leader, dear, empty = self.build("cost_edge")
        self.assertEqual((leader.price, leader.cut), (90.0, False))
        self.assertEqual((dear.price, dear.cut), (90.0, False))
        leader, dear, empty = self.build("universal")
        self.assertAlmostEqual(leader.price, 88.2, places=9)
        self.assertAlmostEqual(dear.price, 88.2, places=9)

    def test_an_entrant_of_the_last_period_is_a_rival(self):
        """Its plants are delivered at the start of the period, so its price counts."""
        for pricing, expected in (("cost_edge", 80.0), ("universal", 78.4)):
            ind = empty_industry(pricing=pricing)
            incumbent = add_firm(ind, price=100.0)
            entrant = add_firm(ind, plants=0, price=80.0, cash=5000.0)
            buy_plant(ind, entrant, ind.public[2], "entry")
            ind.time = 1
            start_period(ind)
            set_prices(ind)
            self.assertAlmostEqual(incumbent.price, expected, places=9, msg=pricing)
            self.assertEqual(entrant.util, 1.0)
            self.assertFalse(entrant.cut and pricing == "cost_edge")


class TestFullRun(unittest.TestCase):
    def test_no_price_is_below_the_floor_under_the_cutting_rules(self):
        for pricing in CUTTING_RULES:
            for price_floor in OPTIONS["price_floor"]:
                ind = industry(seed=2, pricing=pricing, price_floor=price_floor)
                for _ in range(80):
                    for step in STEPS:
                        step(ind)
                        if step is set_prices:
                            for firm in ind.firms:
                                if firm.plants:
                                    floor = read_quote(firm, ind.params).floor
                                    self.assertGreaterEqual(firm.price, floor - 1e-9,
                                                            (pricing, price_floor))
                    close_period(ind)

    def test_without_draws_systematic_cutting_goes_down_to_the_lowest_unit_cost(self):
        ind = industry(pricing="systematic", tech_change="none")
        for _ in range(40):
            set_prices(ind)
        self.assertAlmostEqual(ind.firms[4].price, 74.999, places=9)
        for firm in ind.firms:
            self.assertGreaterEqual(firm.price, read_quote(firm, ind.params).floor)


if __name__ == "__main__":
    unittest.main()
