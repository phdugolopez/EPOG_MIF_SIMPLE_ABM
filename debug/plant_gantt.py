"""How do vintages live and die? One bar per cohort of plants, then the age structure.

    python -m debug.plant_gantt RUN_DIR

Top: one horizontal bar per cohort, the plants a firm ordered for the same arrival
period with the same technique (one plant, in the usual case), from the cohort's first to
its last period in operation, grouped by firm (firms in order of entry, cohorts by
vintage) and coloured by technique; the bar's thickness grows with the cohort's capacity.
A marker at the end of each plant's life gives its retirement cause: age x, obsolescence
v, replacement diamond, exit square; a plant still running at the horizon has none.
Plants ordered and cancelled at their owner's exit never ran: a hollow circle at the
period of the order. The figure's height follows the number of lanes. Middle: the
capacity-weighted age distribution (share of capacity in operation at each age, per
period). Bottom: the vintage spread, max/min ucs over the plants that ran, for the
industry and for the firm where it is widest.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from debug._common import INK, MUTED, run_script, shade_wars, tech_color

CAUSE_MARKER = {"age": "x", "obsolescence": "v", "replacement": "D", "exit": "s"}


def plant_spans(run) -> pd.DataFrame:
    """One row per plant: firm, technique, vintage, capacity, first and last period in
    operation, retirement cause; cancelled orders (never in operation) included."""
    plants = run.plants.sort_values("t")
    spans = plants.groupby("plant_id").agg(
        firm_id=("firm_id", "first"), tech=("tech", "first"), vintage=("vintage", "first"),
        capacity=("capacity", "first"), start=("t", "min"), end=("t", "max"),
        cause=("retire_cause", "last"),
    ).reset_index()
    events = run.tables.get("events")
    if events is not None:
        cancels = events[events["event"] == "cancel"]
        orders = events[events["event"] == "order"].set_index("plant_id")
        rows = []
        for _, c in cancels.iterrows():
            ordered = orders["t"].get(c["plant_id"], c["t"])
            rows.append({"plant_id": c["plant_id"], "firm_id": c["firm_id"],
                         "tech": c["tech"], "vintage": c["t"] + 1, "capacity": c["capacity"],
                         "start": ordered, "end": ordered, "cause": "cancelled"})
        if rows:
            spans = pd.concat([spans, pd.DataFrame(rows)], ignore_index=True)
    born = run.firms.groupby("firm_id")["born"].first()
    spans["born"] = spans["firm_id"].map(born)
    return spans


def lanes(run) -> pd.DataFrame:
    """One row per lane: a cohort (firm, vintage, technique), with its plants' ids, its
    capacity, first and last period, and the set of its plants' retirement causes.
    Sorted by the owner's entry, firm id, vintage and technique: never by plant order."""
    spans = plant_spans(run)
    cohorts = spans.groupby(["firm_id", "vintage", "tech"], sort=False).agg(
        born=("born", "first"), capacity=("capacity", "sum"), start=("start", "min"),
        end=("end", "max"), n_plants=("plant_id", "size"),
        causes=("cause", lambda c: sorted(set(c) - {""})),
    ).reset_index()
    cohorts = cohorts.sort_values(["born", "firm_id", "vintage", "tech"]).reset_index(drop=True)
    cohorts["lane"] = cohorts.index
    return cohorts


def figures(run):
    spans = plant_spans(run)
    cohorts = lanes(run)
    lane_of = {key: lane for key, lane in zip(
        zip(cohorts["firm_id"], cohorts["vintage"], cohorts["tech"]), cohorts["lane"])}
    spans["lane"] = [lane_of[k] for k in zip(spans["firm_id"], spans["vintage"], spans["tech"])]
    techs = sorted(set(cohorts["tech"]))
    n = len(cohorts)
    lane_height = min(max(0.09 * n, 4.0), 30.0)  # inches: readable lanes, bounded page
    fig = plt.figure(figsize=(9, lane_height + 5.5))
    grid = fig.add_gridspec(3, 1, height_ratios=[lane_height, 3.2, 2.3])
    ax = fig.add_subplot(grid[0])
    shade_wars(ax, run, label=True)
    y = cohorts["lane"].to_numpy()
    ran = cohorts["causes"].map(lambda c: c != ["cancelled"])
    # Bar thickness: 0.35 for the smallest cohort to 0.9 for the largest.
    cap = cohorts["capacity"].astype(float)
    thick = 0.35 + 0.55 * (cap / cap.max() if cap.max() > 0 else 0.0)
    for tech in techs:
        mask = (ran & (cohorts["tech"] == tech)).to_numpy()
        ax.barh(y[mask], (cohorts["end"] - cohorts["start"] + 1)[mask],
                left=cohorts["start"][mask] - 0.5, height=thick[mask],
                color=tech_color(tech, techs), linewidth=0)
    for cause, marker in CAUSE_MARKER.items():
        mask = spans["cause"] == cause
        ax.scatter(spans["end"][mask] + 0.5, spans["lane"][mask], marker=marker, s=14,
                   color=INK, linewidths=0.8, zorder=4)
    mask = spans["cause"] == "cancelled"
    ax.scatter(spans["start"][mask], spans["lane"][mask], marker="o", s=22,
               facecolors="none", edgecolors=INK, linewidths=1, zorder=4)
    # Firm separators and labels.
    edges = cohorts.index[cohorts["firm_id"] != cohorts["firm_id"].shift()].tolist()
    ticks, labels = [], []
    for i, start in enumerate(edges):
        end = edges[i + 1] if i + 1 < len(edges) else n
        ax.axhline(start - 0.5, color=MUTED, linewidth=0.4)
        ticks.append((start + end - 1) / 2)
        labels.append(f"firm {int(cohorts['firm_id'][start])}")
    ax.set_yticks(ticks, labels, fontsize=7)
    ax.set_ylim(n - 0.5, -0.5)
    ax.grid(axis="y", visible=False)
    handles = [Patch(color=tech_color(t, techs), label=t) for t in techs]
    handles += [Line2D([], [], marker=m, color=INK, linestyle="none", label=c)
                for c, m in CAUSE_MARKER.items()]
    handles.append(Line2D([], [], marker="o", markerfacecolor="none", color=INK,
                          linestyle="none", label="cancelled"))
    ax.legend(handles=handles + ax.get_legend_handles_labels()[0], loc="lower center",
              bbox_to_anchor=(0.5, 1.0), ncol=9, fontsize=7)
    ax.set_title(f"How do vintages live and die? ({n} cohorts, {len(spans)} plants)",
                 pad=22)

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
    top = 1.0 - 0.9 / fig.get_figheight()
    fig.subplots_adjust(left=0.09, right=0.93, top=top, bottom=0.6 / fig.get_figheight(),
                        hspace=0.12)
    return [("plant_gantt", fig)]


def main(argv=None):
    return run_script(__doc__, figures, argv=argv)


if __name__ == "__main__":
    main()
