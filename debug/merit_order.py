"""Does dispatch run plants in the right order, and is the floor the right plant?

    python -m debug.merit_order RUN_DIR [--t T ...] [--firm ID]

For period T (default: the last), one panel per firm that produced: the merit-order step
curve of its plants in operation, ucs against cumulative capacity, with each plant's
overtime segment at (1 + OVERTIME_PREMIUM) ucs up to U_MAX capacity, segments sorted by
cost as dispatch sorts them and coloured by technique (overtime lighter). Vertical lines
at this period's sales (solid) and last period's sales (dotted, what the floor is computed
from); horizontal lines at the price (solid) and at the floor p_floor (dashed). The last
panel is the industry's supply curve of every plant in operation against demand, with the
sales-weighted price and the leader's price.

With --firm, one figure with a column per --t: that firm on top, the industry below.
"""

import math

import matplotlib.pyplot as plt

from debug._common import INK, MUTED, label_color, run_script, tech_color


def segments(plants, u_max: float, premium: float):
    """(cost, size, tech, overtime) per segment, cheapest first; ties keep plant-id order,
    which only fixes the drawing, never an allocation."""
    rows = []
    for _, p in plants.sort_values("plant_id").iterrows():
        rows.append((p["ucs"], p["capacity"], p["tech"], False))
        rows.append(((1.0 + premium) * p["ucs"], (u_max - 1.0) * p["capacity"], p["tech"],
                     True))
    return sorted(rows, key=lambda s: s[0])


def draw_curve(ax, segs, techs):
    x = 0.0
    previous = None
    for cost, size, tech, overtime in segs:
        if previous is not None:
            ax.plot([x, x], [previous, cost], color=MUTED, linewidth=0.6)
        ax.plot([x, x + size], [cost, cost], color=tech_color(tech, techs),
                linewidth=1.4 if overtime else 2.6, alpha=0.55 if overtime else 1.0,
                solid_capstyle="butt")
        x += size
        previous = cost
    return x


def firm_panel(ax, run, firm_row, t, techs, previous_sales):
    plants = run.plants[(run.plants["t"] == t) & (run.plants["firm_id"] == firm_row["firm_id"])]
    segs = segments(plants, run.param("u_max"), run.param("overtime_premium"))
    width = draw_curve(ax, segs, techs)
    color = label_color(firm_row["group"], run.firms["group"].unique())
    ax.axvline(firm_row["sales"], color=color, linewidth=1.4, label="sales")
    if previous_sales is not None and not math.isnan(previous_sales):
        ax.axvline(previous_sales, color=color, linewidth=1, linestyle=":",
                   label="last sales")
    ax.axhline(firm_row["price"], color=INK, linewidth=1, label="price")
    if not math.isnan(firm_row["p_floor"]):
        ax.axhline(firm_row["p_floor"], color=INK, linewidth=1, linestyle="--",
                   label="floor")
    ax.set_xlim(0, max(width, firm_row["sales"]) * 1.05 or 1.0)
    ax.set_title(f"firm {int(firm_row['firm_id'])} ({firm_row['group']}), t = {t}",
                 fontsize=8)


def industry_panel(ax, run, t, techs):
    plants = run.plants[run.plants["t"] == t]
    width = draw_curve(ax, segments(plants, run.param("u_max"),
                                    run.param("overtime_premium")), techs)
    m = run.macro[run.macro["t"] == t].iloc[0]
    ax.axvline(m["demand"], color=INK, linewidth=1.4, label="demand")
    ax.axhline(m["price_avg"], color=INK, linewidth=1, label="price_avg")
    ax.axhline(m["price_lead"], color=MUTED, linewidth=1, linestyle="-.", label="leader")
    ax.set_xlim(0, max(width, m["demand"]) * 1.05 or 1.0)
    ax.set_title(f"industry supply, t = {t}", fontsize=8)


def _previous_sales(run, firm_id, t):
    prev = run.firms[(run.firms["t"] == t - 1) & (run.firms["firm_id"] == firm_id)]
    return prev["sales"].iloc[0] if not prev.empty else None


def _legend(fig, axes, techs):
    handles, labels = [], []
    for ax in axes:
        for h, label in zip(*ax.get_legend_handles_labels()):
            if label not in labels:
                handles.append(h)
                labels.append(label)
    for tech in techs:
        handles.append(plt.Line2D([], [], color=tech_color(tech, techs), linewidth=2.6))
        labels.append(tech)
    handles.append(plt.Line2D([], [], color=MUTED, linewidth=1.4, alpha=0.55))
    labels.append("overtime")
    fig.legend(handles, labels, loc="lower center", ncol=len(labels), fontsize=7)


def period_figure(run, t, techs):
    firms = run.firms[(run.firms["t"] == t) & (run.firms["n_plants"] > 0)]
    firms = firms.sort_values("firm_id")
    n = len(firms) + 1
    ncols = min(4, n)
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.0 * ncols, 2.6 * nrows + 0.6),
                             squeeze=False)
    flat = list(axes.flat)
    for ax, (_, row) in zip(flat, firms.iterrows()):
        firm_panel(ax, run, row, t, techs, _previous_sales(run, row["firm_id"], t))
    industry_panel(flat[len(firms)], run, t, techs)
    for ax in flat[n:]:
        ax.set_visible(False)
    for ax in flat[:n]:
        ax.set_xlabel("cumulative capacity", fontsize=7)
        ax.set_ylabel("ucs", fontsize=7)
    _legend(fig, flat[:n], techs)
    fig.suptitle(f"Does dispatch run plants in the right order, and is the floor the right "
                 f"plant? (t = {t})", fontsize=10)
    fig.tight_layout(rect=(0, 0.05, 1, 0.97))
    return fig


def firm_figure(run, firm_id, ts, techs):
    fig, axes = plt.subplots(2, len(ts), figsize=(3.2 * len(ts), 5.6), squeeze=False)
    for j, t in enumerate(ts):
        rows = run.firms[(run.firms["t"] == t) & (run.firms["firm_id"] == firm_id)]
        if rows.empty or rows["n_plants"].iloc[0] == 0:
            axes[0, j].set_title(f"firm {firm_id}: no plant at t = {t}", fontsize=8)
        else:
            firm_panel(axes[0, j], run, rows.iloc[0], t, techs,
                       _previous_sales(run, firm_id, t))
        industry_panel(axes[1, j], run, t, techs)
    for ax in axes[:, 0]:
        ax.set_ylabel("ucs", fontsize=7)
    for ax in axes[1]:
        ax.set_xlabel("cumulative capacity", fontsize=7)
    _legend(fig, list(axes.flat), techs)
    fig.suptitle(f"Does firm {firm_id} dispatch its plants in the right order, and is its "
                 f"floor the right plant?", fontsize=10)
    fig.tight_layout(rect=(0, 0.06, 1, 0.96))
    return fig


def figures(run, t=None, firm=None):
    ts = t or [int(run.t.max())]
    known = set(run.t)
    missing = [x for x in ts if x not in known]
    if missing:
        raise SystemExit(f"periods {missing} are not in {run.path}")
    techs = sorted(set(run.plants["tech"]))
    if firm is not None:
        suffix = "_".join(str(x) for x in ts)
        return [(f"merit_order_firm{firm}_t{suffix}", firm_figure(run, firm, ts, techs))]
    return [(f"merit_order_t{x}", period_figure(run, x, techs)) for x in ts]


def add_arguments(p):
    p.add_argument("--t", type=int, action="append", help="period (repeatable)")
    p.add_argument("--firm", type=int, help="one firm, one column per --t")


def main(argv=None):
    return run_script(__doc__, figures, add_arguments, argv)


if __name__ == "__main__":
    main()
