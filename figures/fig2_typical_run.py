"""Figure 2: a typical run, with the E0 panel. Reads the period tables that the harness keeps.

    python -m experiments.harness E0 --keep-periods 0
    python -m experiments.harness E1 --keep-periods 0
    python -m figures.fig2_typical_run [seed] [rule]

With a rule (systematic, leader_follow), the same tables as experiments.price_rules keeps them
in outputs/<rule>/, and the figure takes the rule's name. Four panels on one time axis: the posted price of each label against the price of production
of the regulating technique; capacity over demand; the capacity share of the unit-cost label;
and, without technical change and with one rule (E0), the price against the price of production.
"""
import pathlib
import sys
from math import isclose

import matplotlib.pyplot as plt

from figures import style

MIXED = "E1/periods_defaults_mixed_{seed}.csv"
E0 = "E0/periods_no_draws_all_unit_cost_{seed}.csv"


def series(rows: list[dict], label: str, column: str) -> list[float]:
    return [style.number(row[column]) for row in rows if row["label"] == label]


def main(seed: int = 0, rule: str = ""):
    style.apply()
    folder = pathlib.Path("outputs") / rule
    mixed = style.read(folder / MIXED.format(seed=seed))
    without = style.read(folder / E0.format(seed=seed))
    where = style.PRICING[rule] + ", " if rule else ""
    periods = range(len(mixed) // 2)
    figure, (price, capacity, share, null) = plt.subplots(
        4, 1, figsize=(style.WIDTH, 6.6), sharex=True, constrained_layout=True,
        gridspec_kw={"height_ratios": [1.25, 1, 1, 1]})

    price.plot(periods, series(mixed, "shaikh", "reg_price"), color=style.MUTED,
               label="price of production of the regulating technique")
    unit_cost, profit_rate = series(mixed, "shaikh", "price"), series(mixed, "okishio", "price")
    if all(isclose(a, b) for a, b in zip(unit_cost, profit_rate)):     # one line, not two on top
        price.plot(periods, unit_cost, color=style.SECONDARY, label="posted price, the same for the two labels")
    else:
        price.plot(periods, profit_rate, color=style.PROFIT_RATE, label="profit-rate label")
        price.plot(periods, unit_cost, color=style.UNIT_COST, label="unit-cost label")
    price.set_title(f"Posted price by label (mixed population, {where}seed {seed})")
    price.set_ylim(top=1.22 * max(unit_cost + profit_rate))
    price.legend(loc="upper right", ncols=3, handlelength=1.6, columnspacing=1.2)

    both = [u + o for u, o in zip(series(mixed, "shaikh", "capacity"), series(mixed, "okishio", "capacity"))]
    demand = series(mixed, "shaikh", "demand")
    capacity.axhline(1.0, color=style.AXIS, linewidth=0.8)
    capacity.plot(periods, [k / d for k, d in zip(both, demand)], color=style.SECONDARY)
    capacity.set_title("Capacity over demand")

    share.axhline(0.5, color=style.AXIS, linewidth=0.8)
    share.plot(periods, [u / k if k else float("nan") for u, k in zip(series(mixed, "shaikh", "capacity"), both)],
               color=style.UNIT_COST)
    share.set_title("Capacity share of the unit-cost label")
    share.set_ylim(0.0, 1.0)

    regulating = series(without, "shaikh", "reg_price")
    ratio = series(without, "shaikh", "price_over_reg")
    null.plot(periods, regulating, color=style.MUTED, label="price of production")
    lowest = [r * p for r, p in zip(ratio, regulating)]
    null.plot(periods, lowest, color=style.SECONDARY, label="price")
    null.set_title("Without technical change, one rule (E0): price and price of production")
    null.set_ylim(min(regulating + lowest) - 3.0, 1.09 * max(lowest))
    null.legend(loc="upper right", ncols=2, handlelength=1.6)
    null.set_xlabel("Period")
    null.set_xlim(0, len(periods) - 1)
    return style.save(figure, "fig2_typical_run" + ("_" + rule if rule else ""))


if __name__ == "__main__":
    print(main(int(sys.argv[1]) if len(sys.argv) > 1 else 0, *sys.argv[2:3]))
