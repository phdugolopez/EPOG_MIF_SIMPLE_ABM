"""Figure 5: through which channel a label wins. The two decompositions of the run row in
the twelve cells of E4 under the Marx-biased set at the default rate.

    python3 -m experiments.harness E4
    python -m figures.fig5_decomposition [folder]

One panel a term, the cells on a shared vertical axis: the change in the sales share of the
unit-cost label through the price, through entry and exit and through rationing, and the
change in its capacity share through accumulation (orders less retirements), entry and
exit. Dots are means over the seeds of the mixed population with their 95 % intervals.
"""
import pathlib
import sys

import matplotlib.pyplot as plt

from experiments.cells import MARX_CELLS
from figures import style

TERMS = (("ds_price", "Sales share:\nthe price"), ("ds_entry_exit", "Sales share:\nentry and exit"),
         ("ds_rationing", "Sales share:\nrationing"),
         ("dk_accumulation", "Capacity share:\naccumulation"),
         ("dk_entry", "Capacity share:\nentry"), ("dk_exit", "Capacity share:\nexit"))


def label(cell: str) -> str:
    """A cell of E4 in words: its price rule, its investment rule and its growth."""
    overrides = MARX_CELLS[cell]
    growth = "g = 1 %" if overrides["growth"] > 0.0 else "g = 0"
    return f"{style.PRICING[overrides['pricing']].split()[0]}, {overrides['investment']}, {growth}"


def main(folder: str = "outputs"):
    style.apply()
    cells = {row["cell"]: row for row in style.read(pathlib.Path(folder) / "E4" / "cells.csv")
             if row["population"] == "mixed"}
    names = list(MARX_CELLS)[::-1]
    places = list(range(len(names)))
    figure, panels = plt.subplots(1, len(TERMS), figsize=(style.WIDTH * 1.25, 3.6), sharey=True,
                                  sharex=True, constrained_layout=True)
    for axis, (term, title) in zip(panels, TERMS):
        rows = [cells[cell] for cell in names]
        values = [style.number(row[term]) for row in rows]
        axis.axvline(0.0, color=style.AXIS, linewidth=0.8)
        axis.hlines(places, [style.number(row[term + "_low"]) for row in rows],
                    [style.number(row[term + "_high"]) for row in rows],
                    color=style.SECONDARY, linewidth=1.0, zorder=2)
        axis.plot(values, places, linestyle="none", marker="o", markersize=style.MARKER - 1.5,
                  color=style.SECONDARY, markeredgecolor=style.SURFACE,
                  markeredgewidth=style.RING, zorder=3)
        axis.set_title(title)
        axis.grid(axis="y", visible=False)
    panels[0].set_yticks(places, [label(cell) for cell in names])
    figure.supxlabel("Change in the share of the unit-cost label over the run", fontsize=8.0,
                     color=style.SECONDARY)
    return style.save(figure, "fig5_decomposition")


if __name__ == "__main__":
    print(main(*sys.argv[1:2]))
