"""Technical change from an innovation set (TECH_CHANGE = "innovation_set"): the draws,
the zones as outcomes, the two rules choosing differently on one design, public diffusion,
draws per period, and the label swap."""

import random
import unittest

from equations.hurdle import hurdle
from equations.innovation_set import (ZONES, adoption_zone, draw_marx, draw_neutral,
                                      frontier_technique)
from equations.profit_rate_at_price import profit_rate_at_price
from equations.technique_choice import choose_technique
from equations.unit_cost import unit_cost
from helpers import history_without_labels, make_config, swapped_config
from model import Industry
from model.entities import Technique

DELTA = 0.10
C = Technique("C", 64.25, 137.5)  # uc 78
SET = {"TECH_CHANGE": "innovation_set"}


def marx_draws(n, bias, seed=1, step=0.05, spread=0.8):
    rng = random.Random(seed)
    return [draw_marx(C.ucs, C.kappa, 1.0 - rng.random(), rng.gauss(0.0, 1.0), step, bias,
                      spread) for _ in range(n)]


class TestDraws(unittest.TestCase):
    def test_marx_designs_save_labour_and_use_capital(self):
        for ucs, kappa in marx_draws(2_000, 1.5):
            self.assertLess(ucs, C.ucs)
            self.assertGreaterEqual(ucs, (1.0 - 0.05) * C.ucs)
            self.assertGreater(kappa, C.kappa)

    def test_neutral_designs_cover_the_four_quadrants(self):
        rng = random.Random(2)
        quadrants = set()
        for _ in range(2_000):
            ucs, kappa = draw_neutral(C.ucs, C.kappa, 1.0 - rng.random(), rng.random(), 0.05)
            self.assertLessEqual(abs(ucs / C.ucs - 1.0), 0.05 + 1e-12)
            self.assertLessEqual(abs(kappa / C.kappa - 1.0), 0.05 + 1e-12)
            quadrants.add((ucs < C.ucs, kappa < C.kappa))
        self.assertEqual(len(quadrants), 4)

    def test_frontier_is_the_lowest_unit_cost_never_firm_order(self):
        a = Technique("A", 60.0, 150.0)  # uc 75
        b = Technique("B", 62.0, 130.0)  # uc 75, less capital
        self.assertIs(frontier_technique([a, b], DELTA), b)
        self.assertIs(frontier_technique([b, a], DELTA), b)
        self.assertIs(frontier_technique([a, C], DELTA), a)


class TestZones(unittest.TestCase):
    def test_zone_matches_the_direct_comparison_on_random_draws(self):
        """The critique's test 3: the zone from (k_O, k_S) agrees with comparing unit
        costs and profit rates at p directly, and with the hurdle inequality itself."""
        rng = random.Random(3)
        seen = set()
        for _ in range(10_000):
            price = rng.uniform(60.0, 130.0)
            if rng.random() < 0.5:
                ucs, kappa = draw_marx(C.ucs, C.kappa, 1.0 - rng.random(),
                                       rng.gauss(0.0, 1.0), 0.05, 2.0, 1.0)
            else:
                ucs, kappa = draw_neutral(C.ucs, C.kappa, 1.0 - rng.random(), rng.random(),
                                          0.05)
            zone = adoption_zone(C.ucs, C.kappa, ucs, kappa, DELTA, price)
            seen.add(zone)
            uc_o, uc_n = unit_cost(C.ucs, C.kappa, DELTA), unit_cost(ucs, kappa, DELTA)
            by_unit_cost = uc_n < uc_o
            h = max(0.0, profit_rate_at_price(price, uc_o, C.kappa))
            by_profit_rate = profit_rate_at_price(price, uc_n, kappa) > h if price > uc_o \
                else by_unit_cost
            self.assertEqual(zone, {(True, True): "both", (True, False): "unit_cost",
                                    (False, True): "profit_rate", (False, False): "none"}
                             [(by_unit_cost, by_profit_rate)])
            # The hurdle inequality with h = r_o(p) says the same.
            design = Technique("n", ucs, kappa)
            self.assertEqual(choose_technique([C, design], h, DELTA, 0.0) is design,
                             by_profit_rate)
        self.assertEqual(seen, set(ZONES))

    def test_at_zero_margin_the_rules_agree_on_every_draw(self):
        for ucs, kappa in marx_draws(1_000, 3.0):
            zone = adoption_zone(C.ucs, C.kappa, ucs, kappa, DELTA, 78.0)
            self.assertIn(zone, ("both", "none"))

    def test_conflict_share_rises_with_the_bias_and_closes_in_a_war(self):
        def shares(bias, price):
            draws = marx_draws(5_000, bias)
            zones = [adoption_zone(C.ucs, C.kappa, u, k, DELTA, price) for u, k in draws]
            return {z: zones.count(z) / len(zones) for z in ZONES}
        low, mid, high = shares(0.53, 100.0), shares(1.5, 100.0), shares(3.0, 100.0)
        self.assertLess(low["unit_cost"], 0.10)
        self.assertGreater(mid["unit_cost"], 0.25)
        self.assertGreater(high["unit_cost"], mid["unit_cost"])
        self.assertLess(low["none"], mid["none"])
        self.assertLess(mid["none"], high["none"])
        # Both-reject does not depend on the price; the conflict zone closes as p falls.
        war = shares(1.5, 80.0)
        self.assertAlmostEqual(war["none"], mid["none"])
        self.assertLess(war["unit_cost"], mid["unit_cost"])
        self.assertEqual(shares(1.5, 78.0)["unit_cost"], 0.0)
        for s in (low, mid, high, war):
            self.assertEqual(s["profit_rate"], 0.0)  # no capital-saving design in the set

    def test_one_design_two_choices(self):
        """A design in the conflict zone at p = 100: a Shaikh firm (h = 0) adopts it, an
        Okishio firm at that price refuses it, and both adopt it at p = 78."""
        ucs, kappa = (1.0 - 0.05) * C.ucs, (1.0 + 3.0 * 0.05) * C.kappa  # k = 3
        design = Technique("n", ucs, kappa)
        self.assertEqual(adoption_zone(C.ucs, C.kappa, ucs, kappa, DELTA, 100.0), "unit_cost")
        shaikh = hurdle("unit_cost", 100.0, [C], DELTA, True)
        okishio = hurdle("profit_rate", 100.0, [C], DELTA, True)
        self.assertIs(choose_technique([C, design], shaikh, DELTA, 0.0), design)
        self.assertIs(choose_technique([C, design], okishio, DELTA, 0.0), C)
        okishio_war = hurdle("profit_rate", 78.0, [C], DELTA, True)
        self.assertIs(choose_technique([C, design], okishio_war, DELTA, 0.0), design)


class TestInTheModel(unittest.TestCase):
    def events(self, industry, name):
        return [e for e in industry.events if e["event"] == name]

    def test_public_diffusion_after_the_lag(self):
        """A design built at t is known to every firm once its first plant has produced
        for IMITATION_LAG periods, and to no other firm before (private until then)."""
        industry = Industry(make_config(PERIODS=40, IMITATION_LAG=2, **SET))
        industry.run()
        publics = self.events(industry, "public")
        self.assertTrue(publics)
        first_production = {}
        for r in industry.plant_history:  # a row per plant in operation and period
            first_production.setdefault(r["tech"], r["t"])
        for e in publics:
            self.assertEqual(e["t"], first_production[e["tech"]] + 2)
        known_now = {t.name for f in industry.firms for t in f.known}
        self.assertTrue(industry.public <= known_now)
        for firm in industry.firms:
            self.assertTrue(industry.public <= {t.name for t in firm.known})

    def test_private_diffusion_keeps_designs_with_their_adopter(self):
        industry = Industry(make_config(PERIODS=40, TECH_DIFFUSION="private", **SET))
        industry.run()
        self.assertEqual(self.events(industry, "public"), [])
        adopters = {}
        for e in self.events(industry, "adopt"):
            adopters.setdefault(e["tech"], set()).add(e["firm_id"])
        for firm in industry.firms:
            if firm.born == 0:  # entrants may know every technique in use
                for t in firm.known:
                    if t.name in adopters:
                        self.assertIn(firm.firm_id, adopters[t.name])

    def test_draws_per_period_adopt_now_and_build_later(self):
        industry = Industry(make_config(PERIODS=60, TECH_DRAW_RATE=1.0, **SET))
        industry.run()
        offered = self.events(industry, "design")
        # One offer per period to every firm that still has plants after scrapping, at
        # rate 1, whether it invests or not.
        for row in industry.history:
            t = row["t"]
            with_plants = sum(
                r["t"] == t and r["born"] < t + (t == 0) and r["capacity"] > r["cap_retired"]
                for r in industry.firm_history
            )
            self.assertEqual(sum(e["t"] == t for e in offered), with_plants)
        adopted = {(e["t"], e["tech"]) for e in self.events(industry, "adopt")}
        built = {e["tech"]: e["t"] for e in self.events(industry, "order")}
        self.assertTrue(adopted)
        self.assertTrue(any(tech in built and built[tech] > t for t, tech in adopted))

    def test_draws_at_investment_only(self):
        industry = Industry(make_config(PERIODS=40, TECH_DRAW_TIMING="investment", **SET))
        industry.run()
        orders = {(e["t"], e["firm_id"]) for e in self.events(industry, "order")
                  if e["cause"] == "expansion"}
        for e in self.events(industry, "design"):
            self.assertIn((e["t"], e["firm_id"]), orders | {
                (e2["t"], e2["firm_id"]) for e2 in industry.events if e2["event"] == "design"
            })
        self.assertTrue(self.events(industry, "design"))

    def test_zones_are_recorded_and_the_groups_count_them(self):
        industry = Industry(make_config(PERIODS=40, **SET))
        industry.run()
        zones = {e["cause"] for e in self.events(industry, "design")}
        self.assertTrue(zones <= set(ZONES))
        self.assertIn("both", zones)
        offered = sum(r["n_designs_offered"] for r in industry.group_history)
        self.assertEqual(offered, len(self.events(industry, "design")))
        adopted = sum(r["n_designs_adopted"] for r in industry.group_history)
        self.assertEqual(adopted, len(self.events(industry, "adopt")))
        for r in industry.group_history:
            if r["capacity"] > 0.0:
                self.assertGreater(r["ucs_mean"], 0.0)
                self.assertGreater(r["kappa_mean"], 0.0)

    def test_the_categories_rule_is_unchanged(self):
        """The default draws the same designs as before the switch."""
        industry = Industry(make_config(PERIODS=30))
        industry.run()
        self.assertEqual(industry.parameters.TECH_CHANGE, "categories")
        self.assertTrue({z for _, _, z, _ in industry.draw_log} <= {"both", "unit_cost"})
        self.assertTrue(all(a for _, _, z, a in industry.draw_log if z == "both"))

    def test_label_swap_changes_nothing(self):
        for overrides in ({}, {"TECH_SET": "neutral"}, {"TECH_REFERENCE": "frontier"},
                          {"TECH_DRAW_TIMING": "investment"}, {"TECH_DIFFUSION": "private"}):
            with self.subTest(**overrides):
                a = Industry(make_config(PERIODS=80, **SET, **overrides))
                b = Industry(swapped_config(PERIODS=80, **SET, **overrides))
                a.run()
                b.run()
                self.assertEqual(history_without_labels(a), history_without_labels(b))
                self.assertEqual(a.draw_log, b.draw_log)


if __name__ == "__main__":
    unittest.main()
