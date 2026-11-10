"""Entry and exit (A10): r_new, the signal of entry and of the reserve, the entry probability,
inheritance, the entrant and exits."""
import unittest

from equations.entry_exit_rule import leaving
from equations.entry_inherited_rule import inherited_label
from equations.entry_new_plant_rate import new_plant_rate
from equations.entry_probability import entry_probability
from equations.entry_size import entrant_plants
from helpers import add_firm, cash_total, empty_industry
from markets.entry_exit import create_entrant, remove_firm
from model.entities import Technique
from model.outputs import flows
from model.scheduler import enter_and_exit, produce_and_account, start_period


class TestRules(unittest.TestCase):
    def test_entry_probability(self):
        self.assertEqual(entry_probability(0.04, 0.05, 5.0), 0.0)
        self.assertEqual(entry_probability(0.05, 0.05, 5.0), 0.0)
        self.assertAlmostEqual(entry_probability(0.055, 0.05, 5.0), 0.5, places=12)
        self.assertEqual(entry_probability(0.20, 0.05, 5.0), 1.0)
        self.assertEqual(entry_probability(None, 0.05, 5.0), 0.0)

    def test_the_parent_is_drawn_by_share(self):
        labels, shares = ["shaikh", "okishio", "shaikh"], [0.2, 0.5, 0.3]
        for u, label in ((0.0, "shaikh"), (0.19, "shaikh"), (0.21, "okishio"), (0.69, "okishio"),
                         (0.71, "shaikh"), (0.999, "shaikh")):
            self.assertEqual(inherited_label(labels, shares, 0.0, u, 0.5), label)

    def test_mutation_flips_the_label(self):
        labels, shares = ["shaikh", "okishio"], [0.5, 0.5]
        self.assertEqual(inherited_label(labels, shares, 0.02, 0.1, 0.019), "okishio")
        self.assertEqual(inherited_label(labels, shares, 0.02, 0.1, 0.021), "shaikh")
        self.assertEqual(inherited_label(labels, shares, 1.0, 0.9, 0.5), "shaikh")
        self.assertEqual(inherited_label(labels, shares, 0.0, 0.9, 0.0), "okishio")

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
        self.assertEqual(leaving([0.5, 0.49, 0.005, 0.005], [100.0, 100.0, 20.0, 20.0], 0.01, 2),
                         [False, False, True, True])


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
        """A plant counts in r_new for the first entry_window periods in which it produces."""
        ind = empty_industry()
        young, old = add_firm(ind, plants=1, age=4), add_firm(ind, plants=1, age=5, price=120.0)
        young.sales = old.sales = 20.0
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
    ind.reg_price = 82.8935
    return ind, first, second


class TestEntrant(unittest.TestCase):
    def test_label_rule_price_and_size(self):
        ind, first, second = two_incumbents(mutation=0.0)
        entrant = create_entrant(ind, u_parent=0.7, u_flip=0.5)
        self.assertEqual((entrant.label, entrant.rule), ("okishio", "profit_rate"))
        self.assertEqual(entrant.price, 90.0)
        self.assertEqual(len(entrant.pending_plants), 3)          # 0.5 x 100 / 20, rounded half up
        self.assertEqual(entrant.plants, [])
        self.assertEqual((entrant.id, entrant.born, entrant.util), (2, 0, 1.0))

    def test_technique_is_chosen_by_its_own_rule_at_its_entry_price(self):
        """At 90 the profit-rate rule prefers D1 (highest rate), the unit-cost rule D2."""
        ind, first, second = two_incumbents(mutation=0.0)
        profit_rate = create_entrant(ind, u_parent=0.7, u_flip=0.5)
        unit_cost = create_entrant(ind, u_parent=0.1, u_flip=0.5)
        self.assertEqual(profit_rate.pending_plants[0].technique.name, "D1")
        self.assertAlmostEqual(profit_rate.hurdle, (90.0 - 76.001) / 142.31, places=12)
        self.assertEqual(unit_cost.pending_plants[0].technique.name, "D2")
        self.assertEqual(unit_cost.hurdle, 0.0)
        self.assertEqual(flows(ind, "okishio")["orders_dearer"], 3.0)
        self.assertEqual(flows(ind, "shaikh")["orders_dearer"], 0.0)

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
        self.assertEqual(flows(ind, "shaikh")["cap_entry"], 60.0)
        self.assertEqual(flows(ind, "shaikh")["entries"], 1.0)

    def test_its_share_is_its_capacity_over_next_periods_capacity(self):
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
        ind, first, second = two_incumbents(mutation=0.0, lam=1.0)
        entrant = create_entrant(ind, u_parent=0.7, u_flip=0.5)
        self.assertEqual(entrant.pending_plants[0].technique.name, "D2")
        self.assertAlmostEqual(entrant.hurdle, 0.05, places=9)


class TestExit(unittest.TestCase):
    def test_a_leaving_firm_returns_its_cash_and_its_capacity_is_counted(self):
        ind, first, second = two_incumbents()
        remove_firm(ind, second)
        self.assertEqual(ind.firms, [first])
        self.assertEqual(second.cash, 0.0)
        self.assertAlmostEqual(cash_total(ind), 0.0, places=9)
        self.assertEqual(flows(ind, "okishio")["cap_exit"], 80.0)
        self.assertEqual(flows(ind, "okishio")["exits"], 1.0)


class TestEnterAndExit(unittest.TestCase):
    def three_firms(self, r_new, **overrides):
        ind = empty_industry(**overrides)
        firms = [add_firm(ind, "shaikh", plants=6, share=0.6), add_firm(ind, "okishio", plants=4, share=0.395),
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
        ind, firms = self.three_firms(r_new=0.04)
        enter_and_exit(ind)
        self.assertEqual(len(ind.firms), 2)
        ind, firms = self.three_firms(r_new=0.20)
        enter_and_exit(ind)
        self.assertEqual(len(ind.firms), 3)
        self.assertEqual(ind.firms[-1].id, 3)
        self.assertAlmostEqual(sum(firm.share for firm in ind.firms), 1.0, places=12)

    def test_the_entrant_is_sized_on_the_survivors(self):
        ind, firms = self.three_firms(r_new=0.20)
        enter_and_exit(ind)
        self.assertEqual(len(ind.firms[-1].pending_plants), 3)      # 0.5 x (120 + 80) / 2 / 20 = 2.5

    def test_the_industry_takes_three_uniforms_a_period_with_or_without_entry(self):
        for r_new in (0.0, 0.20, None):
            ind, firms = self.three_firms(r_new=r_new)
            reference = empty_industry().rng
            enter_and_exit(ind)
            reference.random(3)
            self.assertEqual(ind.rng.random(), reference.random())


if __name__ == "__main__":
    unittest.main()
