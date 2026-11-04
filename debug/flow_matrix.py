"""Where does the money go? The transaction-flow matrix at one period, then over time.

    python -m debug.flow_matrix RUN_DIR [--t T]

Top: a heatmap of the flow matrix at period T (default: the last), rows the items,
columns the two sectors, with each row's sum (must be 0). Beside it, each column's sum
against the change in that sector's cash (macro `cash` for firms, `roe_balance` for the
rest of the economy), so that a broken row or column stands out. Below: each item's flow
to firms over time, and the column residual (column sum - change in cash) per period,
NaN in the first period (no earlier cash in the tables).
"""

import matplotlib.pyplot as plt
import numpy as np

from debug._common import INK, MUTED, run_script, shade_wars

SECTORS = ("firms", "roe")
CASH = {"firms": "cash", "roe": "roe_balance"}
ITEM_COLORS = ("#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#e34948", "#8a6d3b",
               "#c2549d", "#4c9a2a", "#7f7f7f")


def cash_change(macro):
    m = macro.set_index("t")
    return {s: m[CASH[s]].diff() for s in SECTORS}


def figures(run, t=None):
    flows, macro = run.flows, run.macro
    t = int(macro["t"].max()) if t is None else t
    if t not in set(macro["t"]):
        raise SystemExit(f"period {t} is not in {run.path}")
    items = list(dict.fromkeys(flows["item"]))
    now = flows[flows["t"] == t].set_index("item")[list(SECTORS)]
    matrix = now.reindex(items).fillna(0.0)
    row_sum = matrix.sum(axis=1)
    delta = cash_change(macro)

    fig = plt.figure(figsize=(10, 9))
    grid = fig.add_gridspec(3, 2, height_ratios=[1.3, 1, 0.7], width_ratios=[2, 1])
    ax = fig.add_subplot(grid[0, 0])
    table = np.column_stack([matrix.to_numpy(), row_sum.to_numpy()])
    scale = np.abs(table).max() or 1.0
    ax.imshow(table, cmap="RdBu", vmin=-scale, vmax=scale, aspect="auto")
    broken = (row_sum.abs() > 1e-9 * max(1.0, scale)).to_numpy()
    for i in range(table.shape[0]):
        for j in range(table.shape[1]):
            bad = j == 2 and broken[i]
            dark = abs(table[i, j]) > 0.55 * scale
            ax.text(j, i, f"{table[i, j]:,.1f}", ha="center", va="center", fontsize=7,
                    color="#d0021b" if bad else "white" if dark else INK,
                    weight="bold" if bad else "normal")
    ax.set_xticks(range(3), [*SECTORS, "row sum"])
    ax.set_yticks(range(len(items)), items, fontsize=7)
    ax.grid(False)
    ax.set_title(f"Flow matrix at t = {t} (+ = inflow to the sector)", fontsize=8)

    ax = fig.add_subplot(grid[0, 1])
    sums = matrix.sum(axis=0)
    changes = [delta[s].get(t, np.nan) for s in SECTORS]
    x = np.arange(len(SECTORS))
    ax.bar(x - 0.18, sums, width=0.36, color=MUTED, label="column sum")
    ax.bar(x + 0.18, changes, width=0.36, color="#2a78d6", label="Δ cash")
    ax.set_xticks(x, SECTORS)
    ax.legend(fontsize=7)
    ax.set_title("Columns against the change in cash", fontsize=8)

    ax = fig.add_subplot(grid[1, :])
    shade_wars(ax, run, label=True)
    wide = flows.pivot_table(index="t", columns="item", values="firms", aggfunc="sum")
    wide = wide.reindex(index=macro["t"], columns=items).fillna(0.0)
    for i, item in enumerate(items):
        ax.plot(wide.index, wide[item], color=ITEM_COLORS[i % len(ITEM_COLORS)],
                linewidth=1.2, label=item)
    ax.axvline(t, color=MUTED, linewidth=0.8, linestyle=":")
    ax.set_ylabel("flow to firms (w.u.)")
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=7)

    ax = fig.add_subplot(grid[2, :], sharex=fig.axes[-1])
    totals = flows.groupby("t")[list(SECTORS)].sum().reindex(macro["t"]).fillna(0.0)
    for sector, style in zip(SECTORS, ("-", "--")):
        resid = totals[sector] - delta[sector].reindex(totals.index)
        ax.plot(totals.index, resid.abs() + 1e-18, color=INK, linestyle=style,
                linewidth=1, label=f"|column sum - Δ cash|, {sector}")
    worst_row = flows[list(SECTORS)].sum(axis=1).abs().groupby(flows["t"]).max()
    ax.plot(worst_row.index, worst_row + 1e-18, color=MUTED, linewidth=1,
            label="max |row sum|")
    if "check_tol" in macro:
        ax.plot(macro["t"], macro["check_tol"], color=MUTED, linestyle=":", linewidth=1,
                label="tolerance")
    ax.set_yscale("log")
    ax.set_xlabel("Period")
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=7)
    fig.suptitle("Where does the money go?", fontsize=10)
    fig.tight_layout()
    return [(f"flow_matrix_t{t}", fig)]


def add_arguments(p):
    p.add_argument("--t", type=int, help="period of the heatmap (default: the last)")


def main(argv=None):
    return run_script(__doc__, figures, add_arguments, argv)


if __name__ == "__main__":
    main()
