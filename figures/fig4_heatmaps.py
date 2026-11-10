"""Figure 4: where each rule wins. The share of seeds won by the unit-cost label in every
cell of E4, as two tables of coloured cells: the Marx-biased set and the categories rule.

    python3 -m experiments.harness E4
    python -m figures.fig4_heatmaps [folder]

Rows are the price rule and the investment rule, columns the general rate and the growth of
demand. Blue is a cell the unit-cost label wins and orange one the profit-rate label wins;
the midpoint, one half, is neutral. A share in brackets is within drift: its interval
overlaps that of a control.
"""
import pathlib
import sys

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from experiments.cells import E4_RATES, INVESTMENT_RULES, THREE_RULES, name
from figures import style

TECH = (("marx", "Marx-biased set"), ("categories", "categories rule"))
GROWTH = (0.0, 0.01)
# Tints of the two label colours around a neutral midpoint, light enough for ink on top.
SCALE = LinearSegmentedColormap.from_list("labels", ["#f0a07c", "#ecebe6", "#86b4ec"])


def main(folder: str = "outputs"):
    style.apply()
    cells = {row["cell"]: row for row in style.read(pathlib.Path(folder) / "E4" / "cells.csv")
             if row["population"] == "mixed"}
    rows = [(rule, investment) for rule in THREE_RULES for investment in INVESTMENT_RULES]
    columns = [(rbar, g) for rbar in E4_RATES for g in GROWTH]
    figure, panels = plt.subplots(1, 2, figsize=(style.WIDTH, 3.0), sharey=True,
                                  constrained_layout=True)
    for axis, (tech, title) in zip(panels, TECH):
        grid = [[style.number(cells[f"{tech}_{rule}_{investment}_g{name(g)}_rbar{name(rbar)}"]
                              ["share_won"]) for rbar, g in columns]
                for rule, investment in rows]
        image = axis.imshow(grid, cmap=SCALE, vmin=0.0, vmax=1.0, aspect="auto")
        for i, (rule, investment) in enumerate(rows):
            for j, (rbar, g) in enumerate(columns):
                cell = cells[f"{tech}_{rule}_{investment}_g{name(g)}_rbar{name(rbar)}"]
                text = f"{grid[i][j]:.2f}"
                if cell["beyond_drift"] != "True":
                    text = f"({text})"
                axis.text(j, i, text, ha="center", va="center", fontsize=7.5, color=style.INK)
        axis.set_title(f"Share won by the unit-cost label, {title}")
        axis.set_xticks(range(len(columns)),
                        [f"r̄ = {name(rbar)}\ng = {name(g)}" for rbar, g in columns])
        axis.set_yticks(range(len(rows)),
                        [f"{style.PRICING[rule].split()[0]}, {investment}"
                         for rule, investment in rows])
        axis.grid(visible=False)
        axis.tick_params(length=0)
        # A surface gap between the cells.
        axis.set_xticks([j - 0.5 for j in range(1, len(columns))], minor=True)
        axis.set_yticks([i - 0.5 for i in range(1, len(rows))], minor=True)
        axis.grid(which="minor", color=style.SURFACE, linewidth=2.0)
        axis.tick_params(which="minor", length=0)
        for side in axis.spines.values():
            side.set_visible(False)
    bar = figure.colorbar(image, ax=panels, location="bottom", shrink=0.4, aspect=30, pad=0.04)
    bar.set_label("share of seeds won by the unit-cost label; in brackets: within drift")
    bar.set_ticks([0.0, 0.25, 0.5, 0.75, 1.0])
    bar.outline.set_visible(False)
    return style.save(figure, "fig4_heatmaps")


if __name__ == "__main__":
    print(main(*sys.argv[1:2]))
