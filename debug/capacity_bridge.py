"""Do the capacity flows add up, and which one moves the shares?

    python -m debug.capacity_bridge RUN_DIR [--group LABEL]

Top, one panel per group: signed stacked bars per period of ordered, entry, -retired,
-exit and -cancelled, the change in capacity K_{g,t+1} - K_{g,t} as a line, and the
identity residual cap_resid on a twin axis. Middle: the five terms of section 4.2 for the
group's capacity share (analysis.indicators.capacity_share_terms), stacked, with the
actual change in the share as a black line: the two must coincide. Bottom: the three
terms of section 4.3 for its sales share (sales_share_terms).

The group decomposed is --group, by default the group whose rule is unit_cost (the
Shaikh rule, whatever its label), else the first label.
"""

import matplotlib.pyplot as plt
import numpy as np

from analysis.indicators import capacity_share_terms, sales_share_terms
from debug._common import INK, MUTED, run_script, shade_wars

FLOW_COLORS = {"ordered": "#2a78d6", "entry": "#1baf7a", "retired": "#8a6d3b",
               "exit": "#e34948", "cancelled": "#c2549d"}
SALES_COLORS = {"price": "#2a78d6", "entry_exit": "#e34948", "rationing": "#f2a33a"}


def signed_stack(ax, t, series: dict, colors: dict):
    """Positive values stacked up from zero, negative ones down, one colour per series."""
    up = np.zeros(len(t))
    down = np.zeros(len(t))
    for name, values in series.items():
        v = np.nan_to_num(np.asarray(values, dtype=float))
        pos, neg = np.clip(v, 0.0, None), np.clip(v, None, 0.0)
        ax.bar(t, pos, bottom=up, width=0.9, color=colors[name], label=name, linewidth=0)
        ax.bar(t, neg, bottom=down, width=0.9, color=colors[name], linewidth=0)
        up += pos
        down += neg


def default_group(groups) -> str:
    rules = groups.drop_duplicates("group").set_index("group")["rule"]
    shaikh = sorted(rules[rules == "unit_cost"].index)
    return shaikh[0] if shaikh else sorted(rules.index)[0]


def figures(run, group=None):
    groups = run.groups
    labels = sorted(groups["group"].unique())
    group = group or default_group(groups)
    if group not in labels:
        raise SystemExit(f"no group {group!r} in {run.path}: {labels}")
    fig, axes = plt.subplots(len(labels) + 2, 1, figsize=(10, 2.6 * (len(labels) + 2)),
                             sharex=True)
    for ax, label in zip(axes, labels):
        g = groups[groups["group"] == label].sort_values("t")
        t = g["t"].to_numpy()
        shade_wars(ax, run)
        signed_stack(ax, t, {
            "ordered": g["cap_ordered"], "entry": g["cap_entry"],
            "retired": -g["cap_retired"], "exit": -g["cap_exit"],
            "cancelled": -g["cap_cancelled"],
        }, FLOW_COLORS)
        ax.plot(t, g["capacity_next"] - g["capacity"], color=INK, linewidth=1.2,
                label="ΔK")
        twin = ax.twinx()
        twin.plot(t, g["cap_resid"], color=MUTED, linewidth=0.8, linestyle=":")
        twin.set_ylabel("cap_resid", color=MUTED, fontsize=7)
        twin.tick_params(labelsize=7)
        twin.grid(False)
        ax.set_ylabel(f"{label}: capacity flow")
        ax.legend(loc="upper left", ncol=6, fontsize=7)

    ax = axes[-2]
    k = capacity_share_terms(groups)
    k = k[k["group"] == group].sort_values("t")
    shade_wars(ax, run)
    signed_stack(ax, k["t"].to_numpy(),
                 {flow: k[f"term_{flow}"] for flow in FLOW_COLORS}, FLOW_COLORS)
    ax.plot(k["t"], k["d_share_k"], color=INK, linewidth=1.2, label="ΔS (actual)")
    ax.set_ylabel(f"{group}: Δ capacity share")
    ax.legend(loc="upper left", ncol=6, fontsize=7)
    ax.set_title(f"Section 4.2: max |resid| = {np.nanmax(np.abs(k['resid'])):.1e}"
                 if k["resid"].notna().any() else "Section 4.2", fontsize=8)

    ax = axes[-1]
    s = sales_share_terms(groups)
    s = s[s["group"] == group].sort_values("t")
    shade_wars(ax, run)
    signed_stack(ax, s["t"].to_numpy(),
                 {name: s[f"term_{name}"] for name in SALES_COLORS}, SALES_COLORS)
    ax.plot(s["t"], s["d_sales_share"], color=INK, linewidth=1.2, label="Δσ (actual)")
    ax.set_ylabel(f"{group}: Δ sales share")
    ax.set_xlabel("Period")
    ax.legend(loc="upper left", ncol=4, fontsize=7)
    ax.set_title(f"Section 4.3: max |resid| = {np.nanmax(np.abs(s['resid'])):.1e}"
                 if s["resid"].notna().any() else "Section 4.3", fontsize=8)

    fig.suptitle("Do the capacity flows add up, and which one moves the shares?",
                 fontsize=10)
    fig.tight_layout()
    return [("capacity_bridge", fig)]


def add_arguments(p):
    p.add_argument("--group", help="label decomposed (default: the unit_cost rule's)")


def main(argv=None):
    return run_script(__doc__, figures, add_arguments, argv)


if __name__ == "__main__":
    main()
