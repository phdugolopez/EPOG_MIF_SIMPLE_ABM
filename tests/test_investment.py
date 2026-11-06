"""Investment: the brief's tests (1)-(5)."""

import random
import unittest

from equations.hurdle import best_profit_rate, hurdle
from equations.new_technique import CATEGORIES, design_category, draw_design
from equations.plant_number import plant_number
from equations.profit_rate_at_price import profit_rate_at_price
from equations.retained_earnings_investment import retained_earnings_investment
from equations.technique_choice import choose_technique
from equations.unit_cost import unit_cost
from helpers import (
    PLANT_ALTERNATIVES, VERSION_1_PLANTS, history_without_labels, make_config,
    one_firm_industry, swapped_config,
)
from markets.plant_market import affordable_spending, buy_plant
from model import Industry
from model.entities import Technique
from model.model import build_menu
from model.scheduler import (
    allocate_demand, invest, produce_and_account, scrap_plants, set_prices, start_period,
)

CONFIG = make_config()
MENU = build_menu(CONFIG)
DELTA = CONFIG.DELTA


def pick(names, rule, price=100.0, floor=True):
    menu = [MENU[n] for n in names]
    h = hurdle(rule, price, menu, DELTA, floor)
    return choose_technique(menu, h, DELTA, tau=0.0).name


class TestInvestment(unittest.TestCase):
    def test_technique_choice_on_shaikh_menu(self):
        """(1) At p = 100: Shaikh firms build D2, Okishio firms D1; on {C, D2} Okishio keeps C."""
        self.assertEqual(pick(("C", "D1", "D2"), "unit_cost"), "D2")
        self.assertEqual(pick(("C", "D1", "D2"), "profit_rate"), "D1")
        self.assertEqual(pick(("C", "D2"), "profit_rate"), "C")
        self.assertEqual(pick(("C", "D2"), "unit_cost"), "D2")
        self.assertAlmostEqual(best_profit_rate(100.0, list(MENU.values()), DELTA), 0.16865,
                               places=5)

    def test_hurdle_argmin_equals_direct_profit_rate_maximisation(self):
        """(2) On random menus, at any price, without the floor at zero."""
        rng = random.Random(7)
        for _ in range(2000):
            menu = [Technique(str(j), rng.uniform(40, 80), rng.uniform(80, 250))
                    for j in range(rng.randint(2, 6))]
            price = rng.uniform(60, 140)
            h = hurdle("profit_rate", price, menu, DELTA, floor_at_zero=False)
            chosen = choose_technique(menu, h, DELTA, tau=0.0)
            best = max(menu, key=lambda t: profit_rate_at_price(
                price, unit_cost(t.ucs, t.kappa, DELTA), t.kappa))
            self.assertAlmostEqual(
                profit_rate_at_price(price, unit_cost(chosen.ucs, chosen.kappa, DELTA),
                                     chosen.kappa),
                profit_rate_at_price(price, unit_cost(best.ucs, best.kappa, DELTA),
                                     best.kappa),
            )
            lowest = min(menu, key=lambda t: unit_cost(t.ucs, t.kappa, DELTA))
            self.assertIs(choose_technique(menu, 0.0, DELTA, 0.0), lowest)

    def test_investment_stops_once_capacity_meets_expected_sales(self):
        """(3) Constant demand above capacity, no scrapping."""
        config = make_config(**dict(VERSION_1_PLANTS, INITIAL_FIRMS=(("C", "shaikh"),),
                                    DEMAND_TO_CAPACITY=1.1, PLANT_LIFE=1000,
                                    REPLACEMENT=False, INITIAL_CASH=50_000.0,
                                    ENTRY_SPEED=0.0))
        industry = Industry(config)
        industry.run(12)
        spending = [row["investment"] for row in industry.history]
        self.assertGreater(spending[0], 0.0)
        self.assertTrue(all(s == 0.0 for s in spending[2:]))
        self.assertAlmostEqual(industry.firms[0].capacity, 1.1 * 120.0)

    def test_debt_never_exceeds_its_cap(self):
        """(4) Borrowing for plants never takes debt above DEBT_CAP x sales revenue."""
        industry = Industry(make_config(**VERSION_1_PLANTS))
        firm = industry.firms[0]
        firm.cash, firm.debt, firm.revenue = 1_000.0, 2_000.0, 5_000.0
        spend = affordable_spending(firm, 2.0)
        self.assertAlmostEqual(spend, 1_000.0 + 8_000.0)
        buy_plant(industry, firm, MENU["D2"], spend / MENU["D2"].kappa)
        self.assertAlmostEqual(firm.debt, 2.0 * 5_000.0)

        industry = Industry(make_config(**VERSION_1_PLANTS))
        for _ in range(60):
            start_period(industry)
            set_prices(industry)
            allocate_demand(industry)
            produce_and_account(industry)
            scrap_plants(industry)
            debt_before = {f.firm_id: f.debt for f in industry.firms}
            invest(industry)
            for f in industry.firms:
                if f.debt > debt_before[f.firm_id] + 1e-9:
                    self.assertLessEqual(f.debt, 2.0 * f.revenue + 1e-6)
            industry.time += 1

    def test_same_sales_same_investment_across_types(self):
        """(5) In capacity units, while finance does not bind."""
        config = make_config(INITIAL_FIRMS=(("C", "shaikh"), ("C", "okishio")),
                             DEMAND_TO_CAPACITY=1.15, INITIAL_CASH=100_000.0,
                             ENTRY_SPEED=0.0, **VERSION_1_PLANTS)
        industry = Industry(config)
        industry.run(1)
        shaikh, okishio = industry.firms
        self.assertEqual(shaikh.pending_plants[0].technique, "D2")
        self.assertEqual(okishio.pending_plants[0].technique, "D1")
        self.assertAlmostEqual(shaikh.pending_plants[0].capacity,
                               okishio.pending_plants[0].capacity)


class TestInvestmentAlternatives(unittest.TestCase):
    """PLANT_SIZE and INVESTMENT_RULE = "retained_earnings"."""

    def test_plant_number(self):
        self.assertEqual(plant_number(133.0, 20.0), 7)
        self.assertEqual(plant_number(5.0, 20.0), 1)  # at least one plant
        self.assertEqual(plant_number(25.0, 20.0, "up"), 2)
        self.assertEqual(plant_number(40.0, 20.0, "up"), 2)
        self.assertEqual(plant_number(0.0, 20.0, "up"), 0)

    def test_retained_earnings_buy_whole_plants(self):
        self.assertEqual(retained_earnings_investment(10_000.0, 150.0, 20.0), 60.0)
        self.assertEqual(retained_earnings_investment(2_999.0, 150.0, 20.0), 0.0)
        self.assertEqual(retained_earnings_investment(-500.0, 150.0, 20.0), 0.0)
        self.assertAlmostEqual(retained_earnings_investment(3_000.0, 150.0, None), 20.0)

    def test_investment_from_retained_earnings_without_debt(self):
        """Retained earnings pay for one D2 plant of 20 (3 158), whatever the demand;
        cash beyond retained earnings and borrowing are not used."""
        industry = one_firm_industry("D2", PLANT_SIZE=20.0,
                                     INVESTMENT_RULE="retained_earnings", TECH_DRAWS=False)
        firm = industry.firms[0]
        firm.cash, firm.retained_earnings = 50_000.0, 5_000.0
        invest(industry)
        self.assertEqual([p.capacity for p in firm.pending_plants], [20.0])
        self.assertEqual(firm.pending_plants[0].technique, "D2")
        self.assertAlmostEqual(firm.retained_earnings, 5_000.0 - 20.0 * 21_000.0 / 133.0)
        self.assertEqual(firm.debt, 0.0)
        invest(industry)  # 1 842 left: not enough for another plant
        self.assertEqual(len(firm.pending_plants), 1)

    def test_every_plant_has_the_fixed_size(self):
        industry = Industry(make_config(**PLANT_ALTERNATIVES))
        industry.run(80)
        plants = [p for f in industry.firms for p in f.plants + f.pending_plants]
        plants += industry.retired
        self.assertTrue(plants)
        self.assertTrue(all(p.capacity == 20.0 for p in plants))


class TestTechnicalChange(unittest.TestCase):
    """TECH_DRAWS: a new design offered at each investment, adopted under the hurdle rule."""

    def test_design_category(self):
        self.assertEqual(design_category(0.2, 0.25), "unit_cost")
        self.assertEqual(design_category(0.7, 0.25), "both")
        self.assertEqual(design_category(0.0, 0.0), "both")

    def test_designs_are_marx_biased_and_land_in_their_category(self):
        """At prices 80-130, every design uses more capital per unit and has a lower
        operating cost, and is adopted exactly by the rules its category names."""
        rng = random.Random(7)
        menu = list(MENU.values())
        for _ in range(500):
            price = rng.uniform(80.0, 130.0)
            for rule in ("unit_cost", "profit_rate"):
                h = hurdle(rule, price, menu, DELTA, True)
                reference = choose_technique(menu, h, DELTA, 0.0)
                for category in CATEGORIES:
                    ucs, kappa = draw_design(reference.ucs, reference.kappa, DELTA, price,
                                             category, 1.0 - rng.random(), rng.random(), 0.05)
                    self.assertGreater(kappa, reference.kappa)
                    self.assertLess(ucs, reference.ucs)
                    design = Technique(name="new", ucs=ucs, kappa=kappa)
                    adopted = choose_technique([reference, design], h, DELTA, 0.0) is design
                    self.assertEqual(adopted, category in ("both", rule))

    @staticmethod
    def investing_firm(technique, rule):
        """One firm that wants 70 more units and has the cash, offered a conflict design."""
        industry = Industry(make_config(INITIAL_FIRMS=((technique, "shaikh"),),
                                        TECH_DRAWS=True, TECH_CONFLICT=1.0,
                                        INVESTMENT_RULE="accelerator", PLANT_SIZE=None))
        firm = industry.firms[0]
        firm.hurdle = hurdle(rule, firm.price, industry.menu, DELTA, True)
        firm.previous_sales, firm.cash = 200.0, 1e6
        invest(industry)
        return industry, firm

    def test_a_rejected_design_still_invests_in_the_best_known_technique(self):
        industry, firm = self.investing_firm("D1", "profit_rate")
        self.assertEqual([(p.technique, p.capacity) for p in firm.pending_plants], [("D1", 70.0)])
        self.assertEqual(len(firm.known), 3)
        self.assertEqual(industry.draw_log, [(0, firm.firm_id, "unit_cost", False)])

    def test_an_adopted_design_is_built_and_kept(self):
        industry, firm = self.investing_firm("D2", "unit_cost")
        self.assertEqual([p.technique for p in firm.pending_plants], ["T1"])
        self.assertEqual(firm.known[-1].name, "T1")
        self.assertLess(firm.known[-1].ucs + DELTA * firm.known[-1].kappa, 75.0)
        self.assertGreater(firm.known[-1].kappa, 21_000.0 / 133.0)  # more capital than D2
        self.assertEqual(industry.draw_log, [(0, firm.firm_id, "unit_cost", True)])

    def test_conflict_zone_vanishes_at_zero_margin(self):
        """At p = uc (zero profit) the two rules coincide: a conflict design is adopted by
        both."""
        c = MENU["C"]
        ucs, kappa = draw_design(c.ucs, c.kappa, DELTA, 78.0, "unit_cost", 1.0, 0.5, 0.05)
        design = Technique(name="new", ucs=ucs, kappa=kappa)
        self.assertGreater(kappa, c.kappa)
        for rule in ("unit_cost", "profit_rate"):
            h = hurdle(rule, 78.0, [c], DELTA, True)
            self.assertIs(choose_technique([c, design], h, DELTA, 0.0), design)

    def test_operating_costs_stay_positive_over_a_long_run(self):
        industry = Industry(make_config(**dict(PLANT_ALTERNATIVES, TECH_DRAWS=True,
                                               TECH_CONFLICT=0.5, PERIODS=200)))
        industry.run()
        plants = [p for f in industry.firms for p in f.plants]
        self.assertTrue(plants)
        self.assertTrue(all(p.ucs > 0.0 for p in plants))
        self.assertTrue(all(p.kappa > 21_000.0 / 133.0 for p in plants))  # all beyond D2

    def test_label_swap_with_draws(self):
        overrides = dict(PLANT_ALTERNATIVES, TECH_DRAWS=True)
        a = Industry(make_config(**overrides))
        b = Industry(swapped_config(**overrides))
        a.run(80)
        b.run(80)
        self.assertEqual(history_without_labels(a), history_without_labels(b))
        self.assertEqual(a.draw_log, b.draw_log)


if __name__ == "__main__":
    unittest.main()
