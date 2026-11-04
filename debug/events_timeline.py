"""Who entered, left, ordered and scrapped, and when? One lane per firm.

    python -m debug.events_timeline RUN_DIR

Lanes in order of entry (born, then firm id), each firm's lifespan coloured by its label.
Markers: entry (triangle), exit by cause (bankruptcy X, share v, non-renewal square),
orders as circles coloured by technique with area proportional to capacity, retirements
as short ticks (cancelled orders hollow). Industry price wars are shaded across all lanes.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from debug._common import INK, MUTED, label_color, run_script, shade_wars, tech_color

EXIT_MARKER = {"bankruptcy": "X", "share": "v", "non-renewal": "s"}


def figures(run):
    firms, events = run.firms, run.events
    spans = firms.groupby("firm_id").agg(group=("group", "first"), born=("born", "first"),
                                         end=("t", "max")).reset_index()
    spans = spans.sort_values(["born", "firm_id"]).reset_index(drop=True)
    lane = {int(f): i for i, f in enumerate(spans["firm_id"])}
    labels = sorted(spans["group"].unique())
    techs = sorted(set(events["tech"]) - {""})
    height = 2.0 + 0.42 * len(spans)
    fig, ax = plt.subplots(figsize=(10, height))
    shade_wars(ax, run, label=True)
    for _, s in spans.iterrows():
        ax.barh(lane[int(s["firm_id"])], s["end"] - s["born"] + 1, left=s["born"] - 0.5,
                height=0.5, color=label_color(s["group"], labels), alpha=0.35, linewidth=0)

    def y(frame):
        return frame["firm_id"].map(lane).to_numpy()

    orders = events[events["event"] == "order"]
    if not orders.empty:
        size = 160.0 * orders["capacity"] / orders["capacity"].max()
        ax.scatter(orders["t"], y(orders), s=size,
                   c=[tech_color(x, techs) for x in orders["tech"]], alpha=0.8,
                   edgecolors="white", linewidths=0.4, zorder=3)
    retires = events[events["event"] == "retire"]
    ax.scatter(retires["t"], y(retires) + 0.32, marker="|", s=30, color=INK,
               linewidths=0.8, zorder=4)
    cancels = events[events["event"] == "cancel"]
    ax.scatter(cancels["t"], y(cancels), marker="o", s=60, facecolors="none",
               edgecolors=INK, linewidths=1, zorder=4)
    entries = events[events["event"] == "entry"]
    ax.scatter(entries["t"] - 0.5, y(entries), marker=">", s=50, color=INK, zorder=5)
    exits = events[events["event"] == "exit"]
    for cause, marker in EXIT_MARKER.items():
        rows = exits[exits["cause"] == cause]
        ax.scatter(rows["t"] + 0.5, y(rows), marker=marker, s=55, color=INK, zorder=5)

    ax.set_yticks(np.arange(len(spans)),
                  [f"firm {int(f)}" for f in spans["firm_id"]], fontsize=7)
    ax.set_ylim(len(spans) - 0.5, -0.8)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Period")
    handles = [Patch(color=label_color(g, labels), alpha=0.35, label=g) for g in labels]
    handles += [Line2D([], [], marker="o", color=tech_color(n, techs), linestyle="none",
                       label=f"order {n}") for n in techs]
    handles += [Line2D([], [], marker="|", color=INK, linestyle="none", label="retire"),
                Line2D([], [], marker="o", markerfacecolor="none", color=INK,
                       linestyle="none", label="cancel"),
                Line2D([], [], marker=">", color=INK, linestyle="none", label="entry")]
    handles += [Line2D([], [], marker=m, color=INK, linestyle="none", label=f"exit: {c}")
                for c, m in EXIT_MARKER.items()]
    handles += [h for h in ax.get_legend_handles_labels()[0]]
    fig.legend(handles=handles, loc="lower center", ncol=8, fontsize=7)
    ax.set_title("Who entered, left, ordered and scrapped, and when?")
    fig.tight_layout(rect=(0, 0.75 / height, 1, 1))
    return [("events_timeline", fig)]


def main(argv=None):
    return run_script(__doc__, figures, argv=argv)


if __name__ == "__main__":
    main()
