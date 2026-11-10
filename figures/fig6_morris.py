"""Figure 6: the Morris screening. mu* of each parameter on each outcome, with its 95 %
interval, and sigma beside it.

    python3 -m experiments.morris
    python -m figures.fig6_morris [folder]

One panel an outcome, the parameters on a shared vertical axis in the order of their mu* on
the first outcome. A dot is mu*, the mean absolute effect of moving the parameter across
its range; the open mark is sigma, the spread of that effect over the trajectories.
"""
import pathlib
import sys

import matplotlib.pyplot as plt

from experiments.morris import OUTCOMES
from figures import style

TITLES = {"gap": "Share won less the\ncontrols' mean",
          "cap_share_end": "Final capacity share\nof the unit-cost label",
          "lost_share": "Share of\ndemand lost", "e0_lines": "Share of E0's\nlines that hold",
          "rate_gap": "Gap in realised rates,\nunit-cost less profit-rate"}
WORDS = {"bias": "bias β", "design_step": "design step A", "draw_prob": "draw probability π",
         "price_cut": "price cut c", "log2_chi": "selection χ (log)", "payout": "payout d",
         "plant_life": "plant life T", "plant_size": "plant size S",
         "entry_speed": "entry speed θ", "mutation": "mutation μ", "u_max": "overtime limit",
         "shortage_step": "shortage step"}


def main(folder: str = "outputs"):
    style.apply()
    rows = style.read(pathlib.Path(folder) / "morris" / "morris.csv")
    table = {(row["outcome"], row["parameter"]): row for row in rows}
    first = [row for row in rows if row["outcome"] == OUTCOMES[0]]
    # The parameters in the order of their effect on the first outcome, the largest on top.
    order = [row["parameter"] for row in sorted(first, key=lambda row: float(row["mu_star"]))]
    places = list(range(len(order)))
    figure, panels = plt.subplots(1, len(OUTCOMES), figsize=(style.WIDTH * 1.25, 3.4),
                                  sharey=True, constrained_layout=True)
    for axis, outcome in zip(panels, OUTCOMES):
        found = [table[outcome, parameter] for parameter in order]
        axis.hlines(places, [max(0.0, style.number(row["mu_star_low"])) for row in found],
                    [style.number(row["mu_star_high"]) for row in found],
                    color=style.SECONDARY, linewidth=1.0, zorder=2)
        axis.plot([style.number(row["sigma"]) for row in found], places, linestyle="none",
                  marker="o", markersize=style.MARKER - 2.0, markerfacecolor=style.SURFACE,
                  markeredgecolor=style.MUTED, markeredgewidth=1.0, zorder=3, label="σ")
        axis.plot([style.number(row["mu_star"]) for row in found], places, linestyle="none",
                  marker="o", markersize=style.MARKER - 1.5, color=style.SECONDARY,
                  markeredgecolor=style.SURFACE, markeredgewidth=style.RING, zorder=4,
                  label="μ*")
        axis.set_title(TITLES[outcome])
        axis.set_xlim(left=0.0)
        axis.grid(axis="y", visible=False)
    panels[0].set_yticks(places, [WORDS[parameter] for parameter in order])
    # The first panel has an empty corner below its smallest effects.
    panels[0].legend(loc="lower right", handlelength=1.0, borderaxespad=0.2)
    figure.supxlabel("Effect of moving the parameter across its range", fontsize=8.0,
                     color=style.SECONDARY)
    return style.save(figure, "fig6_morris")


if __name__ == "__main__":
    print(main(*sys.argv[1:2]))
