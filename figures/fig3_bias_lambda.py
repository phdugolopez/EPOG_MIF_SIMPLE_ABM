"""Figure 3: the share of seeds won by the unit-cost label against the bias of technical
change (E2) and against the weight lambda of the price of production (E3), one series a
price rule. Reads the cells.csv of the harness.

    python3 -m experiments.harness E2
    python3 -m experiments.harness E3
    python -m figures.fig3_bias_lambda [folder]

The folder holds E2/cells.csv and E3/cells.csv; it is outputs by default. Dots are the
mixed population with 95 % Wilson intervals; the grey band is the range of the intervals of
the two controls over the price rules. Below the lambda panel, the mean hurdle of the
profit-rate label over the general rate in the same cells. The price rules take four steps
of one hue, from the rule under which only a cost leader cuts to the one under which every
firm does; each is also named at the end of its curve.
"""
import pathlib
import sys

import matplotlib.pyplot as plt

from experiments.cells import PRICE_RULES, THREE_RULES
from figures import style
from parameters import Parameters

BIAS = (("none", "no\ndraws"), ("neutral", "neutral\nset"), ("beta_0", "β = 0"),
        ("beta_0.5", "0.5"), ("beta_1.5", "1.5"), ("beta_3", "3"))
LAMBDAS = (0.0, 0.25, 0.5, 0.75, 1.0)
SHORT = {"cost_edge": "cost-edge", "normal_price": "normal-price", "systematic": "systematic",
         "universal": "universal"}


def by_cell(path) -> dict:
    return {(row["cell"], row["population"]): row for row in style.read(path)}


def column(rows: list[dict], name: str, scale: float = 1.0) -> list[float]:
    return [style.number(row[name]) / scale for row in rows]


def band(axis, cells: dict, groups: list[list[str]], x: list[float], label=None) -> None:
    """The range of the controls' intervals over the cells of each group, as a grey wash
    behind the dots: one value of x a group."""
    controls = [[cells[name, population] for name in names
                 for population in ("all_unit_cost", "all_profit_rate")] for names in groups]
    low = [min(style.number(row["won_low"]) for row in rows) for rows in controls]
    high = [max(style.number(row["won_high"]) for row in rows) for rows in controls]
    axis.fill_between(x, low, high, color=style.MUTED, alpha=0.18, linewidth=0, zorder=1,
                      label=label)


def spread(values: dict, gap: float) -> dict:
    """Heights for labels set beside the values: the same, moved apart where two values
    are closer than `gap`, so that no label sits on another."""
    heights = {}
    floor = None
    # From the lowest value up, each label at least `gap` above the one below it.
    for key in sorted(values, key=lambda key: values[key]):
        height = values[key] if floor is None else max(values[key], floor + gap)
        heights[key] = height
        floor = height
    return heights


def main(folder: str = "outputs"):
    style.apply()
    folder = pathlib.Path(folder)
    e2, e3 = by_cell(folder / "E2" / "cells.csv"), by_cell(folder / "E3" / "cells.csv")
    rbar = Parameters().rbar
    figure = plt.figure(figsize=(style.WIDTH, 4.6), constrained_layout=True)
    grid = figure.add_gridspec(2, 2, height_ratios=[1.35, 1], width_ratios=[1.3, 1])
    bias = figure.add_subplot(grid[:, 0])
    won = figure.add_subplot(grid[0, 1])
    hurdle = figure.add_subplot(grid[1, 1], sharex=won)

    # E2: one group of dots a cell, the four rules side by side.
    names = [[f"{cell}_{rule}" for rule in PRICE_RULES] for cell, _ in BIAS]
    edges = [-0.5, len(BIAS) - 0.5]
    band(bias, e2, [[name for group in names for name in group]] * 2, edges,
         label="range of the two controls")
    bias.axhline(0.5, color=style.AXIS, linewidth=0.8)
    for place, rule in enumerate(PRICE_RULES):
        rows = [e2[f"{cell}_{rule}", "mixed"] for cell, _ in BIAS]
        x = [index + 0.18 * (place - 1.5) for index in range(len(BIAS))]
        style.dots(bias, x, column(rows, "share_won"), style.RULE_COLOUR[rule],
                   column(rows, "won_low"), column(rows, "won_high"), line=False,
                   label=style.PRICING[rule])
    bias.set_xticks(range(len(BIAS)), [label for _, label in BIAS])
    bias.set_title("Share of seeds won by the unit-cost label,\nby technical change and "
                   "price rule")
    bias.set_ylim(0.0, 1.42)
    bias.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    bias.set_xlim(*edges)
    bias.grid(axis="x", visible=False)
    bias.legend(loc="upper left", ncols=2, handlelength=1.0, columnspacing=1.0,
                borderaxespad=0.1)

    # E3: the share won and the hurdle against lambda, one curve a rule.
    cells = {rule: [f"lam_{lam:g}_{rule}" for lam in LAMBDAS] for rule in THREE_RULES}
    band(won, e3, [[cells[rule][i] for rule in THREE_RULES] for i in range(len(LAMBDAS))],
         list(LAMBDAS))
    won.axhline(0.5, color=style.AXIS, linewidth=0.8)
    ends = {}
    for rule in THREE_RULES:
        rows = [e3[name, "mixed"] for name in cells[rule]]
        colour = style.RULE_COLOUR[rule]
        style.dots(won, LAMBDAS, column(rows, "share_won"), colour, column(rows, "won_low"),
                   column(rows, "won_high"))
        style.dots(hurdle, LAMBDAS, column(rows, "hurdle_okishio", rbar), colour,
                   column(rows, "hurdle_okishio_low", rbar),
                   column(rows, "hurdle_okishio_high", rbar))
        ends[rule] = style.number(rows[-1]["share_won"])
    # Each curve is named at its end in the upper panel; the lower one shares its colours.
    for rule, height in spread(ends, gap=0.07).items():
        won.annotate(SHORT[rule], (1.0, ends[rule]), xytext=(1.06, height), va="center",
                     fontsize=7, color=style.INK)
    won.set_title("Share won, by the weight λ of the\nprice of production")
    won.set_ylim(0.0, 1.02)
    won.tick_params(labelbottom=False)
    hurdle.axhline(1.0, color=style.AXIS, linewidth=0.8)
    hurdle.set_title("Hurdle of the profit-rate label over r̄")
    hurdle.set_xlabel("Weight λ")
    hurdle.set_xticks(LAMBDAS, ["0", "0.25", "0.5", "0.75", "1"])
    hurdle.set_xlim(-0.08, 1.42)
    return style.save(figure, "fig3_bias_lambda")


if __name__ == "__main__":
    print(main(*sys.argv[1:2]))
