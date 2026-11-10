"""Entry and exit: r_new, the entry probability, the entrant's label, technique, price and
size, and exits (v4-final-model.md, "Schedule", step 6)."""
import unittest

from equations.entry_exit_rule import leaving
from equations.entry_inherited_rule import inherited_label
from equations.entry_new_plant_rate import new_plant_rate
from equations.entry_price import entrant_price
from equations.entry_probability import entry_probability
from equations.entry_size import entrant_plants
from helpers import add_firm, cash_total, empty_industry, tallied
from markets.entry_exit import create_entrant, remove_firm
from model.entities import Technique
from model.scheduler import (enter_and_exit, produce_and_account, set_new_plant_rate,
                             start_period)

RBAR = 0.16


class TestRules(unittest.TestCase):
    def test_entry_probability(self):
        self.assertEqual(entry_probability(0.15, RBAR, 5.0), 0.0)
        self.assertEqual(entry_probability(0.16, RBAR, 5.0), 0.0)
        self.assertAlmostEqual(entry_probability(0.176, RBAR, 5.0), 0.5, places=12)
        self.assertEqual(entry_probability(0.50, RBAR, 5.0), 1.0)
        self.assertEqual(entry_probability(None, RBAR, 5.0), 0.0)

    def test_the_gate_is_relative_to_the_general_rate(self):
        for rbar in (0.16, 0.10, 0.05):
            self.assertAlmostEqual(entry_probability(1.1 * rbar, rbar, 5.0), 0.5, places=12)

    def test_the_parent_is_drawn_by_weight(self):
        labels, shares = ["shaikh", "okishio", "shaikh"], [0.2, 0.5, 0.3]
        for u, label in ((0.0, "shaikh"), (0.19, "shaikh"), (0.21, "okishio"),
                         (0.69, "okishio"), (0.71, "shaikh"), (0.999, "shaikh")):
            self.assertEqual(inherited_label(labels, shares, 0.0, u, 0.5), label)

    def test_weights_need_not_sum_to_one(self):
        labels = ["shaikh", "okishio", "okishio", "okishio"]
        for u, label in ((0.0, "shaikh"), (0.24, "shaikh"), (0.26, "okishio"), (0.9, "okishio")):
            self.assertEqual(inherited_label(labels, [1.0] * 4, 0.0, u, 0.5), label)

    def test_mutation_flips_the_label(self):
        labels, shares = ["shaikh", "okishio"], [0.5, 0.5]
        self.assertEqual(inherited_label(labels, shares, 0.02, 0.1, 0.019), "okishio")
        self.assertEqual(inherited_label(labels, shares, 0.02, 0.1, 0.021), "shaikh")
        self.assertEqual(inherited_label(labels, shares, 1.0, 0.9, 0.5), "shaikh")
        self.assertEqual(inherited_label(labels, shares, 0.0, 0.9, 0.0), "okishio")

    def test_the_entrant_posts_one_cut_below_the_lowest_price_down_to_its_floor(self):
        self.assertAlmostEqual(entrant_price(90.0, 75.0, 0.02, "undercut"), 88.2, places=12)
        self.assertEqual(entrant_price(76.0, 75.0, 0.02, "undercut"), 75.0)
        self.assertEqual(entrant_price(70.0, 75.0, 0.02, "undercut"), 75.0)

    def test_under_the_other_level_it_posts_the_lowest_price(self):
        self.assertEqual(entrant_price(90.0, 75.0, 0.02, "lowest"), 90.0)
        self.assertEqual(entrant_price(70.0, 75.0, 0.02, "lowest"), 70.0)

    def test_entrant_size_in_whole_plants(self):
        self.assertEqual(entrant_plants([120.0, 120.0, 140.0], 0.5, 20.0), 3)
        self.assertEqual(entrant_plants([100.0, 100.0], 0.5, 20.0), 3)        # 2.5 rounds up
        self.assertEqual(entrant_plants([20.0, 0.0], 0.5, 20.0), 1)           # at least one

    def test_firms_below_the_exit_share_or_without_capacity_leave(self):
        out = leaving([0.5, 0.3, 0.195, 0.005], [100.0, 0.0, 60.0, 20.0], 0.01, 2)
        self.assertEqual(out, [False, True, False, True])

    def test_at_least_two_firms_remain(self):
        self.assertEqual(leaving([0.994, 0.004, 0.002], [100.0, 20.0, 20.0], 0.01, 2),
                         [False, False, True])
        self.assertEqual(leaving([0.6, 0.4], [0.0, 0.0], 0.01, 2), [False, False])

    def test_candidates_with_the_same_share_stay_or_leave_together(self):
        self.assertEqual(leaving([0.99, 0.005, 0.005], [100.0, 20.0, 20.0], 0.01, 2),
                         [False, False, False])
        self.assertEqual(leaving([0.5, 0.49, 0.005, 0.005], [100.0, 100.0, 20.0, 20.0],
                                 0.01, 2), [False, False, True, True])


class TestNewPlantRate(unittest.TestCase):
    def test_weighted_by_capacity(self):
        self.assertAlmostEqual(new_plant_rate([0.10, 0.20], [20.0, 60.0]), 0.175, places=12)
        self.assertAlmostEqual(new_plant_rate([0.10, 0.20], [20.0, 20.0]), 0.15, places=12)

    def test_none_without_a_plant_in_the_window(self):
        self.assertIsNone(new_plant_rate([], []))

    def test_the_order_of_the_plants_does_not_matter(self):
        rates, capacities = [0.03, 0.11, 0.07, 0.19], [20.0, 20.0, 40.0, 20.0]
        self.assertEqual(new_plant_rate(rates, capacities),
                         new_plant_rate(rates[::-1], capacities[::-1]))


class TestSignal(unittest.TestCase):
    def test_r_new_ignores_plants_older_than_the_window(self):
        ind = empty_industry()
        young, old = add_firm(ind, plants=1, age=5), add_firm(ind, plants=1, age=6)
        young.plants[0].profit = 0.08 * young.plants[0].cost
        old.plants[0].profit = 0.50 * old.plants[0].cost
        set_new_plant_rate(ind)
        self.assertAlmostEqual(ind.r_new, 0.08, places=12)

    def test_r_new_is_profit_over_purchase_cost_weighted_by_capacity(self):
        ind = empty_industry()
        firm = add_firm(ind, plants=3, age=1)
        for plant, rate in zip(firm.plants, (0.10, 0.16, 0.25)):
            plant.profit = rate * plant.cost
        set_new_plant_rate(ind)
        self.assertAlmostEqual(ind.r_new, 0.17, places=12)

    def test_a_plant_counts_for_the_first_five_periods_in_which_it_produces(self):
        """Step 3 ages the plants before it reads the window: the plant that enters the
        period at age 4 is read at 5 and counts; the one that enters at 5 does not."""
        ind = empty_industry()
        young = add_firm(ind, plants=1, age=4)
        old = add_firm(ind, plants=1, age=5, price=120.0)
        young.sales = 20.0
        old.sales = 20.0
        produce_and_account(ind)
        self.assertEqual([young.plants[0].age, old.plants[0].age], [5, 6])
        self.assertAlmostEqual(ind.r_new, (100.0 - 78.0) / 137.5, places=12)

    def test_r_new_is_none_when_every_plant_is_old(self):
        ind = empty_industry()
        add_firm(ind, plants=2, age=8)
        produce_and_account(ind)
        self.assertIsNone(ind.r_new)


def two_incumbents(**overrides):
    """A unit-cost firm of 6 plants at 90 and a profit-rate firm of 4 plants at 100."""
    ind = empty_industry(**overrides)
    first = add_firm(ind, "shaikh", plants=6, price=90.0, share=0.6, cash=1000.0)
    second = add_firm(ind, "okishio", plants=4, price=100.0, share=0.4, cash=500.0)
    ind.reg_price = 100.2614
    return ind, first, second


class TestEntrant(unittest.TestCase):
    def test_label_rule_and_size(self):
        ind, first, second = two_incumbents(mutation=0.0)
        entrant = create_entrant(ind, u_parent=0.7, u_flip=0.5)
        self.assertEqual((entrant.label, entrant.rule), ("okishio", "profit_rate"))
        self.assertEqual(len(entrant.pending_plants), 3)          # 0.5 x 100 / 20, half up
        self.assertEqual(entrant.plants, [])
        self.assertEqual((entrant.id, entrant.born, entrant.util), (2, 0, 1.0))

    def test_technique_is_chosen_by_its_own_rule_at_the_lowest_price(self):
        """At 90 the profit-rate rule prefers D1 (highest rate), the unit-cost rule D2."""
        ind, first, second = two_incumbents(mutation=0.0)
        profit_rate = create_entrant(ind, u_parent=0.7, u_flip=0.5)
        unit_cost = create_entrant(ind, u_parent=0.1, u_flip=0.5)
        self.assertEqual(profit_rate.pending_plants[0].technique.name, "D1")
        self.assertAlmostEqual(profit_rate.hurdle, (90.0 - 76.001) / 142.31, places=12)
        self.assertEqual(unit_cost.pending_plants[0].technique.name, "D2")
        self.assertEqual(unit_cost.hurdle, 0.0)
        self.assertEqual(tallied(ind, "orders_dearer", label="okishio"), 3.0)
        self.assertEqual(tallied(ind, "orders_dearer", label="shaikh"), 0.0)

    def test_it_chooses_on_the_public_menu_only(self):
        ind, first, second = two_incumbents(mutation=0.0)
        first.known.append(Technique("private", 40.0, 100.0))
        entrant = create_entrant(ind, u_parent=0.1, u_flip=0.5)
        self.assertEqual(entrant.pending_plants[0].technique.name, "D2")
        self.assertEqual(entrant.known, [])

    def test_its_plants_are_paid_by_equity(self):
        ind, first, second = two_incumbents()
        entrant = create_entrant(ind, u_parent=0.1, u_flip=0.5)
        self.assertAlmostEqual(entrant.cash, 0.0, places=9)
        self.assertAlmostEqual(entrant.funds, 0.0, places=9)
        self.assertAlmostEqual(cash_total(ind), 0.0, places=9)
        self.assertEqual(tallied(ind, "cap_entry", firm=entrant), 60.0)
        self.assertEqual(tallied(ind, "entries", label="shaikh"), 1.0)

    def test_its_share_is_its_capacity_over_next_period_s_capacity(self):
        ind, first, second = two_incumbents()
        entrant = create_entrant(ind, u_parent=0.1, u_flip=0.5)
        self.assertAlmostEqual(entrant.share, 60.0 / 260.0, places=12)
        self.assertAlmostEqual(first.share, 0.6 * 200.0 / 260.0, places=12)
        self.assertAlmostEqual(first.share + second.share + entrant.share, 1.0, places=12)

    def test_its_plants_arrive_next_period(self):
        ind, first, second = two_incumbents()
        entrant = create_entrant(ind, u_parent=0.1, u_flip=0.5)
        ind.time = 1
        start_period(ind)
        self.assertEqual(entrant.capacity, 60.0)

    def test_at_lambda_one_it_judges_at_the_price_of_production(self):
        """At 100.26, the price of production of D2, D1 earns the most: 0.1705."""
        ind, first, second = two_incumbents(mutation=0.0, lam=1.0)
        entrant = create_entrant(ind, u_parent=0.7, u_flip=0.5)
        self.assertEqual(entrant.pending_plants[0].technique.name, "D1")
        self.assertAlmostEqual(entrant.hurdle, 0.1705, places=4)

    def test_the_place_of_the_incumbents_does_not_change_the_entrant(self):
        entrants = []
        for reverse in (False, True):
            ind, first, second = two_incumbents(mutation=0.0)
            if reverse:
                ind.firms.reverse()
            entrant = create_entrant(ind, u_parent=0.7, u_flip=0.5)
            entrants.append((entrant.label, entrant.price, entrant.share,
                             len(entrant.pending_plants)))
        self.assertEqual(entrants[0], entrants[1])


class TestEntrantPrice(unittest.TestCase):
    def test_it_posts_one_cut_below_the_lowest_price_of_a_firm_with_a_plant(self):
        ind, first, second = two_incumbents(mutation=0.0)
        entrant = create_entrant(ind, u_parent=0.7, u_flip=0.5)
        self.assertAlmostEqual(entrant.price, 0.98 * 90.0, places=12)

    def test_a_firm_without_a_plant_in_operation_does_not_set_the_lowest_price(self):
        ind, first, second = two_incumbents(mutation=0.0)
        add_firm(ind, plants=0, price=60.0)
        entrant = create_entrant(ind, u_parent=0.1, u_flip=0.5)
        self.assertAlmostEqual(entrant.price, 0.98 * 90.0, places=12)

    def test_it_never_posts_below_the_unit_cost_of_its_plants(self):
        """0.98 x 75.5 is below every unit cost of the menu."""
        ind, first, second = two_incumbents(mutation=0.0)
        first.price = 75.5
        second.price = 75.5
        for u_parent, name, cost in ((0.1, "D2", 74.999), (0.7, "D2", 74.999)):
            entrant = create_entrant(ind, u_parent=u_parent, u_flip=0.5)
            self.assertEqual(entrant.pending_plants[0].technique.name, name)
            self.assertAlmostEqual(entrant.price, cost, places=9)

    def test_under_the_other_level_it_posts_the_lowest_price_as_in_version_3(self):
        ind, first, second = two_incumbents(mutation=0.0, entry_price="lowest")
        entrant = create_entrant(ind, u_parent=0.7, u_flip=0.5)
        self.assertEqual(entrant.price, 90.0)

    def test_its_technique_is_chosen_at_the_lowest_price_not_at_its_own(self):
        """At 85.3 the profit-rate rule prefers D1; at 0.98 x 85.3 = 83.6 it would prefer D2."""
        ind, first, second = two_incumbents(mutation=0.0)
        first.price = 85.3
        entrant = create_entrant(ind, u_parent=0.7, u_flip=0.5)
        self.assertEqual(entrant.pending_plants[0].technique.name, "D1")
        self.assertAlmostEqual(entrant.price, 0.98 * 85.3, places=12)

    def test_the_cut_is_the_price_cut_of_the_parameters(self):
        ind, first, second = two_incumbents(mutation=0.0, price_cut=0.05)
        entrant = create_entrant(ind, u_parent=0.7, u_flip=0.5)
        self.assertAlmostEqual(entrant.price, 0.95 * 90.0, places=12)


class TestEntrantLabel(unittest.TestCase):
    def label(self, u_parent, u_flip=0.5, **overrides):
        """Three incumbents: a unit-cost firm with 0.8 of the market and two profit-rate
        firms with 0.1 each."""
        ind = empty_industry(**overrides)
        add_firm(ind, "shaikh", plants=8, share=0.8)
        add_firm(ind, "okishio", plants=1, share=0.1)
        add_firm(ind, "okishio", plants=1, share=0.1)
        return create_entrant(ind, u_parent, u_flip).label

    def test_share_draws_the_parent_by_market_share(self):
        for u_parent, label in ((0.1, "shaikh"), (0.5, "shaikh"), (0.79, "shaikh"),
                                (0.81, "okishio"), (0.95, "okishio")):
            self.assertEqual(self.label(u_parent, mutation=0.0), label)

    def test_even_gives_each_incumbent_one_vote(self):
        for u_parent, label in ((0.1, "shaikh"), (0.32, "shaikh"), (0.34, "okishio"),
                                (0.5, "okishio"), (0.95, "okishio")):
            self.assertEqual(self.label(u_parent, mutation=0.0, entry_label="even"), label)

    def test_without_mutation_the_label_is_the_parent_s(self):
        for u_flip in (0.0, 0.5, 0.999):
            self.assertEqual(self.label(0.5, u_flip, mutation=0.0), "shaikh")
            self.assertEqual(self.label(0.5, u_flip, mutation=0.0, entry_label="even"),
                             "okishio")

    def test_with_a_mutation_of_one_the_label_is_always_the_other(self):
        for u_flip in (0.0, 0.5, 0.999):
            self.assertEqual(self.label(0.5, u_flip, mutation=1.0), "okishio")
            self.assertEqual(self.label(0.5, u_flip, mutation=1.0, entry_label="even"),
                             "shaikh")

    def test_the_default_mutation_flips_two_draws_in_a_hundred(self):
        self.assertEqual(self.label(0.5, u_flip=0.019), "okishio")
        self.assertEqual(self.label(0.5, u_flip=0.021), "shaikh")


class TestExit(unittest.TestCase):
    def test_a_leaving_firm_returns_its_cash_and_its_capacity_is_counted(self):
        ind, first, second = two_incumbents()
        remove_firm(ind, second)
        self.assertEqual(ind.firms, [first])
        self.assertEqual(second.cash, 0.0)
        self.assertAlmostEqual(cash_total(ind), 0.0, places=9)
        self.assertEqual(tallied(ind, "cap_exit", label="okishio"), 80.0)
        self.assertEqual(tallied(ind, "exits", label="okishio"), 1.0)

    def test_a_firm_that_left_is_still_in_the_tally_of_the_period(self):
        ind, first, second = two_incumbents()
        remove_firm(ind, second)
        self.assertEqual(tallied(ind, "cap_exit", firm=second), 80.0)
        self.assertNotIn(second, ind.firms)


class TestEnterAndExit(unittest.TestCase):
    def three_firms(self, r_new, **overrides):
        ind = empty_industry(**overrides)
        firms = [add_firm(ind, "shaikh", plants=6, share=0.6),
                 add_firm(ind, "okishio", plants=4, share=0.395),
                 add_firm(ind, "okishio", plants=1, share=0.005)]
        ind.r_new = r_new
        return ind, firms

    def test_a_firm_below_one_per_cent_leaves_and_the_others_shares_sum_to_one(self):
        ind, firms = self.three_firms(r_new=0.0)
        enter_and_exit(ind)
        self.assertEqual(ind.firms, firms[:2])
        self.assertAlmostEqual(firms[0].share, 0.6 / 0.995, places=12)
        self.assertAlmostEqual(sum(firm.share for firm in ind.firms), 1.0, places=12)

    def test_a_firm_without_capacity_leaves_and_one_with_plants_on_order_stays(self):
        ind, firms = self.three_firms(r_new=0.0)
        firms[1].pending_plants, firms[1].plants = firms[1].plants, []
        firms[2].share, firms[1].share = 0.105, 0.295
        firms[2].plants = []
        enter_and_exit(ind)
        self.assertEqual(ind.firms, firms[:2])

    def test_no_entry_below_the_general_rate_and_entry_far_above_it(self):
        ind, firms = self.three_firms(r_new=0.15)
        enter_and_exit(ind)
        self.assertEqual(len(ind.firms), 2)
        ind, firms = self.three_firms(r_new=0.50)
        enter_and_exit(ind)
        self.assertEqual(len(ind.firms), 3)
        self.assertEqual(ind.firms[-1].id, 3)
        self.assertAlmostEqual(sum(firm.share for firm in ind.firms), 1.0, places=12)

    def test_no_entry_while_r_new_is_undefined(self):
        ind, firms = self.three_firms(r_new=None)
        enter_and_exit(ind)
        self.assertEqual(len(ind.firms), 2)

    def test_the_entrant_is_sized_on_the_survivors(self):
        ind, firms = self.three_firms(r_new=0.50)
        enter_and_exit(ind)
        self.assertEqual(len(ind.firms[-1].pending_plants), 3)      # 0.5 x (120 + 80) / 2 / 20

    def test_the_industry_takes_three_uniforms_a_period_with_or_without_entry(self):
        for r_new in (0.0, 0.50, None):
            ind, firms = self.three_firms(r_new=r_new)
            reference = empty_industry().rng
            enter_and_exit(ind)
            reference.random(3)
            self.assertEqual(ind.rng.random(), reference.random())


if __name__ == "__main__":
    unittest.main()
