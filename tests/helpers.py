"""Shared helpers for the tests: modified copies of parameters.py and small industries."""

from types import SimpleNamespace

import run
from model import Industry
from model.entities import Technique


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
    (Okishio) has a tiny share, orders a large plant and exits on its share at step 6."""
    config = make_config(
        INITIAL_FIRMS=(("C", "shaikh"), ("D1", "okishio")), MIN_FIRMS=1,
        DEMAND_TO_CAPACITY=1.6, ENTRY_SPEED=0.0,
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
