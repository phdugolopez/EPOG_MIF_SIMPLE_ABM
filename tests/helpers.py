"""Shared helpers for the tests: modified copies of parameters.py and small industries."""

from pathlib import Path
from types import SimpleNamespace

import run
from model import Industry
from model.entities import Technique


# Fixed plants, no lifespan, scrapping below unit cost or when idle, investment from
# retained earnings: the version 2 defaults (stated here so tests do not depend on them).
PLANT_ALTERNATIVES = dict(
    PLANT_SIZE=20.0, PLANT_LIFE=None, SCRAP_COST="unit_cost", OBSOLESCENCE_PERIODS=2,
    IDLE_SCRAPPING=True, IDLE_PERIODS=2, INVESTMENT_RULE="retained_earnings",
)
# The version 1 plants, scrapping, investment and fixed menu, for the tests written for them.
VERSION_1_PLANTS = dict(
    PLANT_SIZE=None, PLANT_LIFE=10, SCRAP_COST="operating_cost", OBSOLESCENCE_PERIODS=4,
    IDLE_SCRAPPING=False, INVESTMENT_RULE="accelerator", TECH_DRAWS=False, BORROWING=True,
)
# Deep price cuts with initial debt on the version 1 plants and pricing: a run with
# bankruptcies, defaults, unpaid bills and cancelled orders, for the collector's event and
# decomposition tests (under the version 2 defaults no firm ever borrows).
BANKRUPTCIES = dict(VERSION_1_PLANTS, PRICING_RULE="anchor", PRICE_CUT=0.06, MIN_SHARE=0.05,
                    INITIAL_DEBT=5_000.0)


def make_config(**overrides) -> SimpleNamespace:
    """parameters.py with overrides, as run.py builds it."""
    return run.configure(**overrides)


def swapped_config(**overrides) -> SimpleNamespace:
    """Swap the type labels everywhere and swap the hurdle mapping with them."""
    base = make_config(**overrides)
    swap = {"shaikh": "okishio", "okishio": "shaikh"}
    base.INITIAL_FIRMS = tuple((tech, swap[t]) for tech, t in base.INITIAL_FIRMS)
    base.HURDLE_RULES = {swap[t]: rule for t, rule in base.HURDLE_RULES.items()}
    return base


def one_firm_industry(technique: str = "C", **overrides) -> Industry:
    config = make_config(INITIAL_FIRMS=((technique, "shaikh"),), **overrides)
    return Industry(config)


LABEL_COLUMNS = ("type", "firm_type", "group")


def without_labels(rows) -> list[dict]:
    """Rows with the label columns dropped (rule stays: it is the same under a swap)."""
    return [{k: v for k, v in row.items() if k not in LABEL_COLUMNS} for row in rows]


def history_without_labels(industry) -> list[dict]:
    return without_labels(industry.firm_history)


def three_plant_industry():
    """Firm 0 (Shaikh) runs three plants of different vintages and techniques: C (new),
    D1 (age 9, retires by age this period) and X (ucs 90, replaced by D2). Firm 1
    (Okishio) has a tiny share, orders a large plant and exits on its share at step 6.
    Version 1 plants, investment and pricing: the case needs an age limit, borrowing for
    the replacement, the accelerator and the anchor rule's floor."""
    config = make_config(
        INITIAL_FIRMS=(("C", "shaikh"), ("D1", "okishio")), MIN_FIRMS=1,
        DEMAND_TO_CAPACITY=1.6, ENTRY_SPEED=0.0, PRICING_RULE="anchor",
        **VERSION_1_PLANTS,
    )
    industry = Industry(config)
    a, b = industry.firms
    d1 = industry.techniques["D1"]
    old = industry.new_plant(d1, 120.0, vintage=-9, initial=True)
    old.age, old.book_value = 9, 0.1 * d1.kappa * 120.0
    x = industry.new_plant(Technique("X", 90.0, 100.0), 100.0, vintage=-4, initial=True)
    x.age, x.book_value = 4, 0.6 * 100.0 * 100.0
    a.plants += [old, x]
    a.share, b.share = 0.999, 0.001
    a.sales, b.sales = 300.0, 500.0  # become previous_sales at the start of period 0
    b.cash = 1e6
    industry.money = industry.roe.cash + sum(f.cash for f in industry.firms)
    return industry, a, b, old, x


def write_run(industry, out, run_id: str = "test") -> None:
    """Write the tables of a finished run to the folder `out`, as run.py does."""
    row = run.runs_row(industry, run_id, "test", "test", "test", 0.0)
    run.write(run.tables(industry, row), Path(out), "csv")
