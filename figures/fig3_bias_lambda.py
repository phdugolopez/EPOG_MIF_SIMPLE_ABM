"""Figure 3: the share of seeds won by the unit-cost label against the bias of technical change
(E2) and against the evaluation-price weight lambda (E3). Reads the cells.csv of the harness.

    python -m experiments.harness E2
    python -m experiments.harness E3
    python -m figures.fig3_bias_lambda [rule]

With a rule (leader_follow, overtime), the same cells as experiments.price_rules runs them,
read from outputs/<rule>/, and the figure takes the rule's name; under a price rule E3 has one
regime. Dots are the mixed population with 95 % Wilson intervals; the grey band is the range of the
intervals of the two controls. Below the two lambda panels, the mean hurdle of the profit-rate
label in the same cells.
"""
import pathlib
import sys

import matplotlib.pyplot as plt

from figures import style

BIAS = (("none", "no\ndraws"), ("neutral", "neutral\nset"), ("beta_0", "β = 0"),
        ("beta_0.5", "0.5"), ("beta_1.5", "1.5"), ("beta_3", "3"))
LAMBDAS = (0.0, 0.25, 0.5, 0.75, 1.0)
RATES = ((0.05, style.LOW), (0.16, style.HIGH))


def by_cell(path) -> dict:
    return {(row["cell"], row["population"]): row for row in style.read(path)}


def band(axis, cells: dict, groups: list[list[str]], x: list[float]) -> None:
    """The range of the controls' intervals over the cells of each group, as a grey wash
    behind the dots: one value of x a group."""
    controls = [[cells[name, population] for name in names
                 for population in ("all_unit_cost", "all_profit_rate")] for names in groups]
    low = [min(style.number(row["won_low"]) for row in rows) for rows in controls]
    high = [max(style.number(row["won_high"]) for row in rows) for rows in controls]
    axis.fill_between(x, low, high, color=style.MUTED, alpha=0.18, linewidth=0, zorder=1)


def main(rule: str = ""):
    style.apply()
    folder = pathlib.Path("outputs") / rule
    regimes = ("cost_edge", "systematic") if rule in ("", "overtime") else (rule,)
    e2, e3 = by_cell(folder / "E2/cells.csv"), by_cell(folder / "E3/cells.csv")
    figure = plt.figure(figsize=(style.WIDTH, 4.3), constrained_layout=True)
    grid = figure.add_gridspec(2, 1 + len(regimes), height_ratios=[1.35, 1],
                               width_ratios=[1.25] + [1] * len(regimes))
    bias = figure.add_subplot(grid[:, 0])
    won = [figure.add_subplot(grid[0, 1 + i]) for i in range(len(regimes))]
    hurdle = [figure.add_subplot(grid[1, 1 + i], sharex=won[i]) for i in range(len(regimes))]

    x = list(range(len(BIAS)))
    band(bias, e2, [[cell for cell, _ in BIAS]] * 2, [-0.6, len(BIAS) - 0.4])
    rows = [e2[cell, "mixed"] for cell, _ in BIAS]
    bias.axhline(0.5, color=style.AXIS, linewidth=0.8)
    style.dots(bias, x, [style.number(r["share_won"]) for r in rows], style.UNIT_COST,
               [style.number(r["won_low"]) for r in rows], [style.number(r["won_high"]) for r in rows],
               line=False)
    bias.set_xticks(x, [label for _, label in BIAS])
    bias.set_title("Share of seeds won by the\nunit-cost label, by technical change"
                   + (f"\n({style.PRICING[rule]})" if rule else ""))
    bias.set_ylim(0.0, 1.02)
    bias.set_xlim(-0.6, len(BIAS) - 0.4)
    bias.grid(axis="x", visible=False)
    bias.text(len(BIAS) - 0.5, 0.36, "range of the two controls", ha="right", va="top", fontsize=7,
              color=style.SECONDARY)

    for column, regime in enumerate(regimes):
        names = {rbar: [f"lam_{lam:g}_{regime}_rbar_{rbar:g}" for lam in LAMBDAS] for rbar, _ in RATES}
        band(won[column], e3, [[names[rbar][i] for rbar, _ in RATES] for i in range(len(LAMBDAS))],
             list(LAMBDAS))
        won[column].axhline(0.5, color=style.AXIS, linewidth=0.8)
        for rbar, colour in RATES:
            rows = [e3[name, "mixed"] for name in names[rbar]]
            style.dots(won[column], LAMBDAS, [style.number(r["share_won"]) for r in rows], colour,
                       [style.number(r["won_low"]) for r in rows],
                       [style.number(r["won_high"]) for r in rows], label=f"r̄ = {rbar:g}")
            style.dots(hurdle[column], LAMBDAS, [style.number(r["hurdle_okishio"]) for r in rows], colour,
                       [style.number(r["hurdle_okishio_low"]) for r in rows],
                       [style.number(r["hurdle_okishio_high"]) for r in rows])
        won[column].set_title(f"Share won, {style.PRICING[regime]}")
        won[column].set_ylim(0.0, 1.02)
        won[column].tick_params(labelbottom=False)
        hurdle[column].set_title("Mean hurdle of the profit-rate label" if column == 0 else "")
        hurdle[column].set_xlabel("Weight λ of the price of production")
        hurdle[column].set_xticks(LAMBDAS, ["0", "0.25", "0.5", "0.75", "1"])
        hurdle[column].set_ylim(0.0, 0.35)
    for axis in won[1:] + hurdle[1:]:
        axis.tick_params(labelleft=False)
    won[0].legend(loc="best", handlelength=1.2, borderaxespad=0.2)
    return style.save(figure, "fig3_bias_lambda" + ("_" + rule if rule else ""))


if __name__ == "__main__":
    print(main(*sys.argv[1:2]))
