"""Investment: the brief's tests (1)-(5)."""

import random
import unittest

from equations.hurdle import best_profit_rate, hurdle
from equations.profit_rate_at_price import profit_rate_at_price
from equations.technique_choice import choose_technique
from equations.unit_cost import unit_cost
from helpers import make_config
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
        config = make_config(INITIAL_FIRMS=(("C", "shaikh"),), DEMAND_TO_CAPACITY=1.1,
                             PLANT_LIFE=1000, REPLACEMENT=False, INITIAL_CASH=50_000.0)
        industry = Industry(config)
        industry.run(12)
        spending = [row["investment"] for row in industry.history]
        self.assertGreater(spending[0], 0.0)
        self.assertTrue(all(s == 0.0 for s in spending[2:]))
        self.assertAlmostEqual(industry.firms[0].capacity, 1.1 * 120.0)

    def test_debt_never_exceeds_its_cap(self):
        """(4) Borrowing for plants never takes debt above DEBT_CAP x sales revenue."""
        industry = Industry(make_config())
        firm = industry.firms[0]
        firm.cash, firm.debt, firm.revenue = 1_000.0, 2_000.0, 5_000.0
        spend = affordable_spending(firm, 2.0)
        self.assertAlmostEqual(spend, 1_000.0 + 8_000.0)
        buy_plant(industry, firm, MENU["D2"], spend / MENU["D2"].kappa)
        self.assertAlmostEqual(firm.debt, 2.0 * 5_000.0)

        industry = Industry(make_config())
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
                             ENTRY_SPEED=0.0)
        industry = Industry(config)
        industry.run(1)
        shaikh, okishio = industry.firms
        self.assertEqual(shaikh.pending_plants[0].technique, "D2")
        self.assertEqual(okishio.pending_plants[0].technique, "D1")
        self.assertAlmostEqual(shaikh.pending_plants[0].capacity,
                               okishio.pending_plants[0].capacity)


if __name__ == "__main__":
    unittest.main()
