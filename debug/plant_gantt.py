"""How do vintages live and die? One bar per plant, then the age structure.

    python -m debug.plant_gantt RUN_DIR

Top: one horizontal bar per plant from its first to its last period in operation,
grouped by firm (firms in order of entry, plants by vintage) and coloured by technique.
The marker at the end of a bar is the retirement cause: age x, obsolescence v,
replacement diamond, exit square; a plant still running at the horizon has none. Plants
ordered and cancelled at their owner's exit never ran: a hollow circle at the period of
the order. Middle: the capacity-weighted age distribution (share of capacity in operation
at each age, per period). Bottom: the vintage spread, max/min ucs over the plants that
ran, for the industry and for the firm where it is widest.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from debug._common import INK, MUTED, run_script, shade_wars, tech_color

CAUSE_MARKER = {"age": "x", "obsolescence": "v", "replacement": "D", "exit": "s"}


def lanes(run) -> pd.DataFrame:
    """One row per plant: firm, technique, first and last period, retirement cause."""
    plants = run.plants.sort_values("t")
    spans = plants.groupby("plant_id").agg(
        firm_id=("firm_id", "first"), tech=("tech", "first"), vintage=("vintage", "first"),
        start=("t", "min"), end=("t", "max"), cause=("retire_cause", "last"),
    ).reset_index()
    events = run.tables.get("events")
    if events is not None:
        cancels = events[events["event"] == "cancel"]
        orders = events[events["event"] == "order"].set_index("plant_id")
        rows = []
        for _, c in cancels.iterrows():
            ordered = orders["t"].get(c["plant_id"], c["t"])
            rows.append({"plant_id": c["plant_id"], "firm_id": c["firm_id"],
                         "tech": c["tech"], "vintage": c["t"] + 1, "start": ordered,
                         "end": ordered, "cause": "cancelled"})
        if rows:
            spans = pd.concat([spans, pd.DataFrame(rows)], ignore_index=True)
    born = run.firms.groupby("firm_id")["born"].first()
    spans["born"] = spans["firm_id"].map(born)
    return spans.sort_values(["born", "firm_id", "vintage", "plant_id"]).reset_index(drop=True)


def figures(run):
    spans = lanes(run)
    techs = sorted(set(spans["tech"]))
    fig = plt.figure(figsize=(9, 12))
    grid = fig.add_gridspec(3, 1, height_ratios=[4, 1.3, 1])
    ax = fig.add_subplot(grid[0])
    shade_wars(ax, run, label=True)
    y = np.arange(len(spans))
    ran = spans["cause"] != "cancelled"
    for tech in techs:
        mask = ran & (spans["tech"] == tech)
        ax.barh(y[mask], spans["end"][mask] - spans["start"][mask] + 1,
                left=spans["start"][mask] - 0.5, height=0.8, color=tech_color(tech, techs),
                linewidth=0)
    for cause, marker in CAUSE_MARKER.items():
        mask = spans["cause"] == cause
        ax.scatter(spans["end"][mask] + 0.5, y[mask], marker=marker, s=14, color=INK,
                   linewidths=0.8, zorder=4)
    mask = spans["cause"] == "cancelled"
    ax.scatter(spans["start"][mask], y[mask], marker="o", s=22, facecolors="none",
               edgecolors=INK, linewidths=1, zorder=4)
    # Firm separators and labels.
    edges = spans.index[spans["firm_id"] != spans["firm_id"].shift()].tolist()
    ticks, labels = [], []
    for i, start in enumerate(edges):
        end = edges[i + 1] if i + 1 < len(edges) else len(spans)
        ax.axhline(start - 0.5, color=MUTED, linewidth=0.4)
        ticks.append((start + end - 1) / 2)
        labels.append(f"firm {int(spans['firm_id'][start])}")
    ax.set_yticks(ticks, labels, fontsize=7)
    ax.set_ylim(len(spans) - 0.5, -0.5)
    ax.grid(axis="y", visible=False)
    handles = [Patch(color=tech_color(n, techs), label=n) for n in techs]
    handles += [Line2D([], [], marker=m, color=INK, linestyle="none", label=c)
                for c, m in CAUSE_MARKER.items()]
    handles.append(Line2D([], [], marker="o", markerfacecolor="none", color=INK,
                          linestyle="none", label="cancelled"))
    ax.legend(handles=handles + ax.get_legend_handles_labels()[0], loc="upper center",
              bbox_to_anchor=(0.5, 1.06), ncol=9, fontsize=7)
    ax.set_title("How do vintages live and die?", pad=24)

    ax = fig.add_subplot(grid[1], sharex=ax)
    plants = run.plants
    ages = plants.pivot_table(index="age", columns="t", values="capacity", aggfunc="sum")
    ages = ages.reindex(index=range(int(ages.index.min()), int(ages.index.max()) + 1),
                        columns=run.t).fillna(0.0)
    share = ages / ages.sum().replace(0.0, np.nan)
    image = ax.imshow(share.to_numpy(), aspect="auto", origin="lower", cmap="Blues",
                      extent=(run.t.min() - 0.5, run.t.max() + 0.5,
                              ages.index.min() - 0.5, ages.index.max() + 0.5))
    fig.colorbar(image, cax=ax.inset_axes([1.005, 0.0, 0.012, 1.0]),
                 label="share of capacity")
    ax.set_ylabel("Age")
    ax.grid(False)

    ax = fig.add_subplot(grid[2], sharex=ax)
    shade_wars(ax, run)
    running = plants[plants["running"].astype(bool)]
    by_t = running.groupby("t")["ucs"]
    spread = (by_t.max() / by_t.min()).reindex(run.t)
    ax.plot(run.t, spread, color=INK, linewidth=1.4, label="industry")
    if "ucs_spread" in run.firms:
        widest = run.firms.groupby("t")["ucs_spread"].max().reindex(run.t)
        ax.plot(run.t, widest, color=MUTED, linewidth=1, linestyle=":",
                label="widest firm")
    ax.set(xlabel="Period", ylabel="max / min ucs")
    ax.legend(loc="upper left", fontsize=7)
    fig.subplots_adjust(left=0.09, right=0.93, top=0.93, bottom=0.05, hspace=0.25)
    return [("plant_gantt", fig)]


def main(argv=None):
    return run_script(__doc__, figures, argv=argv)


if __name__ == "__main__":
    main()
