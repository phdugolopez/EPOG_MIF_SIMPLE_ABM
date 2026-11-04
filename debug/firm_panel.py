"""What did one firm see and do? Six panels on one time axis, one page per firm.

    python -m debug.firm_panel RUN_DIR [--firm ID ...] [--all]

1. price, with its anchor p_normal (dotted), its floor p_floor (dashed) and the leader
   band [leader, (1 + PRICE_BAND) leader];
2. share_demand (step 2), share_end (step 6) and its share of sales;
3. utilisation, with U_WAR and U_MAX;
4. capacity in operation stacked by plant (one band per plant id, coloured by technique),
   with the capacity ordered this period (arriving next period) hatched on top;
5. cash, debt and net worth, with write-offs as bars;
6. hurdle and r_best (best profit rate on offer at its price, before the zero floor);
   on periods with an order, a circle in the colour of the technique ordered (tech_new),
   filled when the other rule would have picked the same (tech_other), hollow with a dot
   in tech_other's colour when it would not.

Price-war periods are shaded; a cross marks the end of the lines of a firm that left.
Without --firm or --all: the first firm of each label, in firm-id order within a label.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from debug._common import (INK, MUTED, firm_title, label_color, mark_exit, run_script,
                           shade_wars, tech_color)


def default_firms(firms: pd.DataFrame) -> list[int]:
    return sorted(int(rows["firm_id"].min()) for _, rows in firms.groupby("group"))


def _plant_stack(ax, run, firm_id, t_index):
    plants = run.plants[run.plants["firm_id"] == firm_id]
    techs = sorted(run.plants["tech"].unique())
    base = int(t_index[0])
    bottom = np.zeros(len(t_index))
    # One bar segment per plant and period, plants stacked by vintage (then id); the
    # opacity alternates along the stack so that neighbouring plants stay apart.
    for n, (_, rows) in enumerate(plants.groupby(["vintage", "plant_id"])):
        at = rows["t"].to_numpy() - base
        ax.bar(rows["t"], rows["capacity"], bottom=bottom[at], width=1.0,
               color=tech_color(rows["tech"].iloc[0], techs),
               alpha=0.95 if n % 2 == 0 else 0.6, linewidth=0)
        bottom[at] += rows["capacity"].to_numpy()
    events = run.tables.get("events")
    if events is not None:
        orders = events[(events["event"] == "order") & (events["firm_id"] == firm_id)]
        on_order = orders.groupby("t")["capacity"].sum().reindex(t_index).fillna(0.0)
        if on_order.any():
            ax.bar(t_index, on_order.to_numpy(), bottom=bottom, width=1.0,
                   facecolor="none", edgecolor=MUTED, hatch="////", linewidth=0.3)
    present = sorted(plants["tech"].unique()) if not plants.empty else []
    handles = [Patch(color=tech_color(n, techs), label=n) for n in present]
    handles.append(Patch(facecolor="none", edgecolor=MUTED, hatch="////",
                         label="on order"))
    ax.legend(handles=handles, loc="upper left", ncol=len(handles), fontsize=7)
    ax.set_ylabel("Capacity")


def _choices(ax, rows, techs):
    orders = rows[rows["tech_new"] != ""]
    for _, r in orders.iterrows():
        agree = r["tech_new"] == r["tech_other"]
        color = tech_color(r["tech_new"], techs)
        ax.plot(r["t"], r["hurdle"], marker="o", markersize=7, linestyle="none",
                markeredgecolor=color, markerfacecolor=color if agree else "white",
                markeredgewidth=1.5, zorder=5)
        if not agree:
            ax.plot(r["t"], r["hurdle"], marker=".", markersize=5, linestyle="none",
                    color=tech_color(r["tech_other"], techs), zorder=6)


def page(run, firm_id: int):
    firms, macro = run.firms, run.macro
    rows = firms[firms["firm_id"] == firm_id].sort_values("t")
    if rows.empty:
        raise SystemExit(f"no firm {firm_id} in {run.path}")
    color = label_color(rows["group"].iloc[0], firms["group"].unique())
    t = rows["t"]
    t_index = pd.Index(range(int(t.min()), int(t.max()) + 1), name="t")
    m = macro.set_index("t").reindex(t)
    techs = sorted(set(run.plants["tech"]))
    fig, axes = plt.subplots(6, 1, figsize=(8.5, 11), sharex=True)
    for ax in axes:
        shade_wars(ax, run, label=ax is axes[0])

    ax = axes[0]
    lead = m["price_lead"].to_numpy()
    ax.fill_between(t, lead, (1.0 + run.param("price_band")) * lead, color=MUTED,
                    alpha=0.15, linewidth=0, label="leader band")
    ax.plot(t, rows["price"], color=color, label="price")
    ax.plot(t, rows["p_normal"], color=color, linestyle=":", linewidth=1.2,
            label="anchor p_normal")
    ax.plot(t, rows["p_floor"], color=INK, linestyle="--", linewidth=1, label="floor p_floor")
    mark_exit(ax, rows, "price")
    ax.set_ylabel("Price")
    ax.legend(loc="lower left", ncol=5, fontsize=7)

    ax = axes[1]
    sales_share = rows["sales"].to_numpy() / m["sales_total"].replace(0.0, np.nan).to_numpy()
    ax.plot(t, rows["share_demand"], color=color, label="share_demand (step 2)")
    ax.plot(t, rows["share_end"], color=color, linestyle=":", linewidth=1.2,
            label="share_end (step 6)")
    ax.plot(t, sales_share, color=INK, linewidth=1, label="sales share")
    mark_exit(ax, rows.assign(sales_share=sales_share), "sales_share")
    ax.set_ylabel("Share")
    ax.legend(loc="upper left", ncol=3, fontsize=7)

    ax = axes[2]
    ax.plot(t, rows["util"], color=color)
    for value, name in ((run.param("u_war"), "U_WAR"), (run.param("u_max"), "U_MAX")):
        ax.axhline(value, color=MUTED, linestyle="--", linewidth=1)
        ax.annotate(name, (t.iloc[-1], value), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=7, color=MUTED)
    mark_exit(ax, rows, "util")
    ax.set_ylabel("Utilisation")

    _plant_stack(axes[3], run, firm_id, t_index)

    ax = axes[4]
    ax.bar(t, rows["write_off"], color=MUTED, alpha=0.6, width=0.8, label="write-offs")
    ax.plot(t, rows["cash"], color=color, linewidth=1.4, label="cash")
    ax.plot(t, rows["debt"], color=INK, linewidth=1.2, linestyle="--", label="debt")
    ax.plot(t, rows["net_worth"], color=color, linewidth=1.2, linestyle=":",
            label="net worth")
    mark_exit(ax, rows, "net_worth")
    ax.set_ylabel("w.u.")
    ax.legend(loc="upper left", ncol=4, fontsize=7)

    ax = axes[5]
    ax.plot(t, rows["hurdle"], color=color, label="hurdle h")
    ax.plot(t, rows["r_best"], color=INK, linewidth=1, linestyle=":", label="r_best")
    _choices(ax, rows, techs)
    mark_exit(ax, rows, "hurdle")
    handles = ax.get_legend_handles_labels()[0] + [
        Line2D([], [], marker="o", color=MUTED, linestyle="none", label="order: rules agree"),
        Line2D([], [], marker="o", markerfacecolor="white", color=MUTED, linestyle="none",
               label="order: rules differ"),
    ]
    ax.legend(handles=handles, loc="upper left", ncol=4, fontsize=7)
    ax.set_ylabel("Rate")
    ax.set_xlabel("Period")

    exit_note = ""
    if bool(rows["exited"].iloc[-1]):
        exit_note = f", left at t = {rows['t'].iloc[-1]} ({rows['exit_cause'].iloc[-1]})"
    fig.suptitle(f"What did {firm_title(rows, firm_id)} see and do?{exit_note}", fontsize=10)
    fig.tight_layout()
    return fig


def figures(run, firm=None, all=False):  # noqa: A002 (the option is --all)
    ids = (sorted(int(i) for i in run.firms["firm_id"].unique()) if all
           else firm or default_firms(run.firms))
    return [(f"firm_{i}", page(run, i)) for i in ids]


def add_arguments(p):
    p.add_argument("--firm", type=int, action="append", help="firm id (repeatable)")
    p.add_argument("--all", action="store_true", help="one page per firm")


def main(argv=None):
    return run_script(__doc__, figures, add_arguments, argv)


if __name__ == "__main__":
    main()
