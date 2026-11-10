"""Figure 2: a typical run, with the E0 panel. Two runs of the viewer, on the same seed.

    python -m figures.fig2_typical_run [seed]

Four panels on one time axis. The first three are the mixed population at the defaults: the
posted price of each label against the price of production of the regulating technique;
capacity and sales over demand; the capacity share and the market share of the unit-cost
label. The fourth is E0: one rule, no technical change, the price against the price of
production. The runs are stepped by experiments.show_run.trace, as the viewer steps them.
"""
import sys
from dataclasses import replace
from math import isclose

import matplotlib.pyplot as plt

from experiments.populations import POPULATIONS
from experiments.show_run import over, series, trace
from figures import style
from parameters import Parameters


def main(seed: int = 0):
    style.apply()
    params = Parameters()
    control = replace(params, tech_change="none", **POPULATIONS["all_unit_cost"])
    mixed = trace(params, seed)[0].rows
    without = trace(control, seed)[0].rows
    u = [row for row in mixed if row["label"] == "shaikh"]
    o = [row for row in mixed if row["label"] == "okishio"]
    periods = [row["t"] for row in u]
    capacity = [a + b for a, b in zip(series(u, "capacity"), series(o, "capacity"))]
    sales = [a + b for a, b in zip(series(u, "sales"), series(o, "sales"))]
    demand = series(u, "demand")

    figure, (price, volume, share, null) = plt.subplots(
        4, 1, figsize=(style.WIDTH, 7.0), sharex=True, constrained_layout=True,
        gridspec_kw={"height_ratios": [1.25, 1, 1, 1]})
    legend = dict(loc="upper right", handlelength=1.6, columnspacing=1.2, borderaxespad=0.1)

    price.plot(periods, series(u, "reg_price"), color=style.MUTED, label="price of production")
    unit_cost, profit_rate = series(u, "price"), series(o, "price")
    together = all(isclose(a, b, rel_tol=0.005) for a, b in zip(unit_cost, profit_rate)
                   if a == a and b == b)
    if together:      # one line, not two on top of each other
        price.plot(periods, unit_cost, color=style.SECONDARY, label="price of both labels")
    else:
        price.plot(periods, profit_rate, color=style.PROFIT_RATE, label="profit-rate label")
        price.plot(periods, unit_cost, color=style.UNIT_COST, label="unit-cost label")
    price.set_title(f"Posted price by label and price of production of the regulating "
                    f"technique\n(mixed population at the defaults, seed {seed})")
    highest = max(value for value in unit_cost + profit_rate if value == value)
    price.set_ylim(top=1.25 * highest)
    price.legend(ncols=3, **legend)

    volume.axhspan(1.0, params.u_max, color=style.MUTED, alpha=0.15, linewidth=0,
                   label="overtime band")
    volume.plot(periods, over(capacity, demand), color=style.INK, label="capacity over demand")
    volume.plot(periods, over(sales, demand), color=style.MUTED, linewidth=1.0,
                label="sales over demand")
    volume.set_title("Normal capacity and sales over demand")
    volume.set_ylim(top=2.0)
    volume.legend(ncols=3, **legend)

    share.axhline(0.5, color=style.AXIS, linewidth=0.8)
    share.plot(periods, over(series(u, "capacity"), capacity), color=style.UNIT_COST,
               label="capacity share")
    share.plot(periods, series(u, "share"), color=style.LOW, label="market share")
    share.set_title("Capacity share and market share of the unit-cost label")
    share.set_ylim(0.0, 1.3)
    share.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    share.legend(ncols=2, **legend)

    rows = [row for row in without if row["label"] == "shaikh"]
    regulating = series(rows, "reg_price")
    posted = [ratio * level for ratio, level in zip(series(rows, "price_over_reg"), regulating)]
    null.plot(periods, regulating, color=style.MUTED, label="price of production")
    null.plot(periods, posted, color=style.SECONDARY, label="price, weighted by sales")
    null.set_title("Without technical change, every firm on the unit-cost rule (E0)")
    lowest = min(value for value in posted if value == value)
    null.set_ylim(lowest - 3.0, 1.12 * max(value for value in posted if value == value))
    null.legend(ncols=2, **legend)
    null.set_xlabel("Period")
    null.set_xlim(0, periods[-1])
    return style.save(figure, "fig2_typical_run")


if __name__ == "__main__":
    print(main(int(sys.argv[1]) if len(sys.argv) > 1 else 0))
