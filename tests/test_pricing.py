"""Pricing: the real-competition rule (default) and the version 1 anchor rule."""

import random
import unittest

from equations.anchor_price import leader_anchor
from equations.leader_follow_price import leader_follow_price, markup_floor
from equations.posted_price import posted_price
from equations.real_competition_price import real_competition_price
from helpers import history_without_labels, make_config, swapped_config
from model import Industry
from model.scheduler import allocate_demand, produce_and_account, set_prices, start_period

TEST_INDUSTRY = (("C", "shaikh"), ("D1", "shaikh"), ("D2", "shaikh"))
ANCHOR = {"PRICING_RULE": "anchor", "RBAR": 0.16}  # version 1: the brief's rbar
UC = [78.0, 76.0, 75.0]  # unit costs of C, D1, D2


def run_without_capacity_change(industry, periods, demand_path=None):
    """Pricing, demand and production only: scrapping, investment and entry are stubbed."""
    prices = []
    for t in range(periods):
        if demand_path:
            industry.initial_demand = demand_path(t)
        start_period(industry)
        set_prices(industry)
        allocate_demand(industry)
        produce_and_account(industry)
        prices.append([f.price for f in industry.firms])
        industry.time += 1
    return prices


class TestRealCompetitionPrice(unittest.TestCase):
    """PRICING_RULE = "real_competition": follow, undercut with a cost edge, raise on shortage."""

    @staticmethod
    def price(previous=100.0, rivals=(100.0, 100.0), rival_costs=(78.0, 76.0), own_cost=75.0,
              floor=75.0, spare=True, unserved=0.0):
        return real_competition_price(previous, list(rivals), list(rival_costs), own_cost,
                                      floor, spare, unserved, 0.02, 0.5)

    def test_cost_edge_and_spare_capacity_undercut(self):
        self.assertEqual(self.price(), (98.0, True))

    def test_no_cut_without_spare_capacity(self):
        self.assertEqual(self.price(spare=False), (100.0, False))

    def test_no_cut_without_a_cost_edge(self):
        # Rivals at the lowest price are as efficient (an identical twin) or more.
        self.assertEqual(self.price(rival_costs=(75.0, 75.0)), (100.0, False))
        self.assertEqual(self.price(own_cost=78.0, floor=78.0), (100.0, False))
        # An edge over a rival that is not at the lowest price does not count.
        self.assertEqual(self.price(rivals=(100.0, 101.0), rival_costs=(75.0, 78.0)),
                         (100.0, False))
        # The cut price must still cover the firm's own unit cost.
        self.assertEqual(self.price(rivals=(76.0, 76.0), floor=75.0), (76.0, False))

    def test_a_cut_never_raises_the_price(self):
        self.assertEqual(self.price(previous=97.0), (97.0, True))

    def test_the_leader_does_not_undercut_itself(self):
        # Alone at the lowest price, the leader compares itself with its rivals only.
        self.assertEqual(self.price(previous=98.0, rivals=(100.0, 100.0)), (98.0, True))
        self.assertEqual(self.price(previous=98.0, rivals=(100.0, 100.0), spare=False),
                         (98.0, False))

    def test_follow_the_lowest_price_but_not_below_the_floor(self):
        self.assertEqual(self.price(previous=100.0, rivals=(98.0, 99.0), own_cost=80.0,
                                    floor=80.0), (98.0, False))
        self.assertEqual(self.price(previous=100.0, rivals=(70.0, 99.0), own_cost=80.0,
                                    floor=80.0), (80.0, False))

    def test_shortage_moves_up_to_the_next_price(self):
        self.assertEqual(self.price(previous=98.0, rivals=(100.0, 102.0), unserved=0.1),
                         (100.0, False))
        # The firm with no rival above it raises by shortage_response x unserved share.
        p, cut = self.price(previous=102.0, rivals=(100.0, 102.0), unserved=0.1)
        self.assertAlmostEqual(p, 102.0 * 1.05)
        self.assertFalse(cut)

    def test_never_below_the_floor(self):
        rng = random.Random(5)
        for _ in range(2000):
            rivals = [rng.uniform(60, 120) for _ in range(3)]
            costs = [rng.uniform(60, 90) for _ in range(3)]
            own = rng.uniform(60, 90)
            previous = rng.uniform(own, 120)
            p, cut = real_competition_price(previous, rivals, costs, own, own,
                                            rng.random() < 0.5, 0.0, 0.02, 0.5)
            self.assertGreaterEqual(p, own - 1e-9)
            self.assertLessEqual(p, previous + 1e-9)  # no rise without a shortage

    def test_identical_firms_with_spare_capacity_never_start_a_war(self):
        """No cost difference, no war: two C firms at demand 89 % of capacity keep 100."""
        industry = Industry(make_config(INITIAL_FIRMS=(("C", "shaikh"), ("C", "okishio"))))
        for row in run_without_capacity_change(industry, 40):
            for p in row:
                self.assertAlmostEqual(p, 100.0)

    def test_war_from_a_cost_difference_and_shortage_raises_prices(self):
        """Test industry, capacity fixed, demand 340 against capacity 383, then 420 (above
        normal capacity). D2 cuts first, the others follow down to their own unit cost and
        stop there; D2 ends as the lowest-priced, lowest-cost leader. Excess demand then
        raises every price."""
        industry = Industry(make_config(INITIAL_FIRMS=TEST_INDUSTRY, PLANT_SIZE=None))
        prices = run_without_capacity_change(
            industry, 45, demand_path=lambda t: 340.0 if t < 30 else 420.0
        )
        self.assertLess(prices[0][2], 100.0)  # D2 cuts first
        self.assertAlmostEqual(prices[0][0], 100.0)  # C has no edge
        for row in prices[:30]:
            for p, uc in zip(row, UC):
                self.assertGreaterEqual(p, uc - 1e-9)
        settled = prices[29]
        self.assertAlmostEqual(settled[0], 78.0)
        self.assertAlmostEqual(settled[1], 76.0)
        self.assertLess(settled[2], 76.0)
        for p, q in zip(prices[-1], settled):
            self.assertGreater(p, q + 5.0)

    def test_operating_cost_floor_ends_the_war_on_one_price(self):
        """With PRICE_FLOOR = "operating_cost" the followers match the leader all the way."""
        industry = Industry(make_config(INITIAL_FIRMS=TEST_INDUSTRY,
                                        PRICE_FLOOR="operating_cost"))
        settled = run_without_capacity_change(industry, 30)[-1]
        self.assertAlmostEqual(max(settled), min(settled))
        self.assertGreaterEqual(min(settled), UC[2])

    def test_label_swap_with_switches(self):
        for overrides in ({}, {"PRICE_FLOOR": "operating_cost"},
                          {"EXCESS_DEMAND": "normal_capacity"}):
            a = Industry(make_config(**overrides))
            b = Industry(swapped_config(**overrides))
            a.run(60)
            b.run(60)
            self.assertEqual(history_without_labels(a), history_without_labels(b))


class TestLeaderFollowPrice(unittest.TestCase):
    """PRICING_RULE = "leader_follow": the group notebook's rule."""

    LEADER_FOLLOW = {"PRICING_RULE": "leader_follow"}

    @staticmethod
    def price(previous=100.0, leader=100.0, floor=90.0, excess=0.0, only=False):
        return leader_follow_price(previous, leader, floor, excess, only, 0.02, 0.03, 3.0)

    def test_markup_floor_on_average_unit_cost(self):
        self.assertAlmostEqual(markup_floor([78.0, 75.0], [20.0, 60.0], 0.2), 1.2 * 75.75)

    def test_undercut_the_leader_without_shortage(self):
        self.assertEqual(self.price(), (98.0, True))

    def test_never_below_the_floor(self):
        self.assertEqual(self.price(leader=91.0), (90.0, False))

    def test_shortage_posts_above_the_leader(self):
        price, cut = self.price(previous=110.0, leader=100.0, excess=0.1)
        self.assertAlmostEqual(price, 103.0)
        self.assertFalse(cut)

    def test_lone_firm_raises_up_to_the_cap(self):
        self.assertAlmostEqual(self.price(previous=100.0, only=True)[0], 103.0)
        self.assertAlmostEqual(self.price(previous=269.0, only=True)[0], 270.0)

    def test_prices_fall_to_the_floors_without_shortage(self):
        """Capacity fixed and demand below it: every firm cuts each period until its floor
        binds, 1.2 x uc; the lowest-cost firm ends as the leader."""
        industry = Industry(make_config(INITIAL_FIRMS=TEST_INDUSTRY, **self.LEADER_FOLLOW))
        prices = run_without_capacity_change(industry, 30)
        for path in zip(*prices):
            self.assertTrue(all(b <= a + 1e-9 for a, b in zip(path, path[1:])))
        for settled, uc in zip(prices[-1], UC):
            self.assertAlmostEqual(settled, 1.2 * uc)

    def test_identical_firms_post_identical_prices(self):
        industry = Industry(make_config(**self.LEADER_FOLLOW))
        for row in run_without_capacity_change(industry, 30):
            for a, b in zip(row[0::2], row[1::2]):  # the pairs of the initial population
                self.assertEqual(a, b)

    def test_shortage_never_lowers_a_price_with_no_cut(self):
        """SHORTAGE_RULE = "no_cut": max{previous, (1 + z) L}; "leader" posts (1 + z) L."""
        high = leader_follow_price(110.0, 100.0, 90.0, 0.1, False, 0.02, 0.03, 3.0, "no_cut")
        self.assertEqual(high, (110.0, False))
        low = leader_follow_price(95.0, 100.0, 90.0, 0.1, False, 0.02, 0.03, 3.0, "no_cut")
        self.assertAlmostEqual(low[0], 103.0)
        self.assertAlmostEqual(self.price(previous=110.0, excess=0.1)[0], 103.0)

    def test_floor_switch_sets_where_the_cuts_stop(self):
        """LEADER_FOLLOW_FLOOR: cuts stop at 1.2 uc (markup), at uc, or at ucs (the marginal
        plant's operating cost; one technique per firm here, so its ucs)."""
        ucs = [78.0 - 13.75, 76.0 - 18_500.0 / 130.0 * 0.1, 75.0 - 21_000.0 / 133.0 * 0.1]
        for floor, expected in (("markup", [1.2 * c for c in UC]), ("unit_cost", UC),
                                ("operating_cost", ucs)):
            with self.subTest(floor=floor):
                industry = Industry(make_config(
                    INITIAL_FIRMS=TEST_INDUSTRY, LEADER_FOLLOW_FLOOR=floor,
                    **self.LEADER_FOLLOW,
                ))
                prices = run_without_capacity_change(industry, 40)
                for settled, value in zip(prices[-1], expected):
                    self.assertAlmostEqual(settled, value)

    def test_label_swap_changes_nothing(self):
        for overrides in ({}, {"LEADER_FOLLOW_FLOOR": "unit_cost"},
                          {"LEADER_FOLLOW_FLOOR": "operating_cost"}, {"SHORTAGE_RULE": "no_cut"}):
            with self.subTest(**overrides):
                a = Industry(make_config(**self.LEADER_FOLLOW, **overrides))
                b = Industry(swapped_config(**self.LEADER_FOLLOW, **overrides))
                a.run(100)
                b.run(100)
                self.assertEqual(history_without_labels(a), history_without_labels(b))


class TestAnchorPricing(unittest.TestCase):
    """PRICING_RULE = "anchor" (version 1): the brief's tests (1)-(4)."""

    def test_no_price_below_the_floor(self):
        """(1)"""
        rng = random.Random(3)
        for _ in range(500):
            floor = rng.uniform(50, 70)
            p = posted_price(
                rng.uniform(40, 120), rng.uniform(80, 110), rng.uniform(40, 120), floor,
                rng.random() < 0.5, 0.25, 0.025, 0.02,
            )
            self.assertGreaterEqual(p, floor)

    def test_identical_firms_at_normal_capacity_keep_their_anchor(self):
        """(2)"""
        config = make_config(INITIAL_FIRMS=(("C", "shaikh"), ("C", "okishio")),
                             DEMAND_TO_CAPACITY=1.0, **ANCHOR)
        industry = Industry(config)
        for row in run_without_capacity_change(industry, 40):
            for p in row:
                self.assertAlmostEqual(p, 100.0)  # C's target-return price

    def test_war_starts_deepens_ends_and_prices_recover(self):
        """(3) Test industry, demand 340 against capacity 383, capacity fixed. The war
        ends when demand returns to normal capacity (standing in for the capacity
        adjustment that scrapping and investment provide in the full model)."""
        industry = Industry(make_config(INITIAL_FIRMS=TEST_INDUSTRY, **ANCHOR))
        prices = run_without_capacity_change(
            industry, 50, demand_path=lambda t: 340.0 if t < 15 else 383.0
        )
        mean = [sum(row) / len(row) for row in prices]
        self.assertLess(mean[2], mean[1])  # starts after WAR_PERIODS low periods
        self.assertLess(mean[14], mean[8])  # deepens
        trough = min(mean)
        self.assertLess(trough, 80.0)
        floors = [64.25, 76 - 0.1 * 18_500 / 130, 75 - 0.1 * 21_000 / 133]  # ucs
        for row in prices:
            for p, floor in zip(row, floors):
                self.assertGreaterEqual(p, floor - 1e-9)
        self.assertGreater(mean[-1], trough + 15.0)  # recovers
        self.assertGreater(mean[-1], 95.0)

    def test_label_swap_changes_nothing(self):
        """(4)"""
        a, b = Industry(make_config(**ANCHOR)), Industry(swapped_config(**ANCHOR))
        a.run(40)
        b.run(40)
        self.assertEqual(history_without_labels(a), history_without_labels(b))

    # --- Alternative anchor: PRICING_ANCHOR = "leader" ----------------------------------

    def test_leader_anchor_averages_tied_leaders(self):
        self.assertAlmostEqual(leader_anchor([100.0, 98.0, 96.0], [97.0, 97.0, 99.0]), 99.0)
        self.assertAlmostEqual(leader_anchor([100.0, 98.0], [97.0, 98.0]), 100.0)

    def test_leader_anchor_gives_one_price(self):
        """Different techniques at normal capacity: under their own anchors the
        capital-intensive D2 stays dearer than C; under the leader's anchor they end on
        one price."""
        firms = (("C", "shaikh"), ("D2", "okishio"))
        own = run_without_capacity_change(
            Industry(make_config(INITIAL_FIRMS=firms, DEMAND_TO_CAPACITY=1.0, **ANCHOR)), 60
        )[-1]
        common = run_without_capacity_change(
            Industry(make_config(INITIAL_FIRMS=firms, DEMAND_TO_CAPACITY=1.0,
                                 PRICING_ANCHOR="leader", **ANCHOR)), 60
        )[-1]
        self.assertGreater(own[1] - own[0], 0.2)
        self.assertAlmostEqual(common[0], common[1])

    def test_label_swap_with_the_leader_anchor(self):
        overrides = {"PRICING_ANCHOR": "leader", **ANCHOR}
        a = Industry(make_config(**overrides))
        b = Industry(swapped_config(**overrides))
        a.run(60)
        b.run(60)
        self.assertEqual(history_without_labels(a), history_without_labels(b))


if __name__ == "__main__":
    unittest.main()
