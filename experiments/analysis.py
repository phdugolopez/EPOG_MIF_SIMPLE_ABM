"""Reading the first sensitivity analysis against the literature (step 5 of the plan in
docs/design/review-v2.md; the discussion is docs/design/sensitivity-discussion.md).

    python -m experiments.analysis b1 [--out DIR]
        Track B1 on the existing tables (no new runs): the regression of the realised
        profit-rate gap and of shaikh_wins over the decided mixed seeds of stage 2, the
        whole-run attribution of the cells of section 6 of sensitivity-results.md, the
        timing of takeovers, and the summary chart of the share won with the controls.
    python -m experiments.analysis story RUN_DIR [--name NAME]
        Two-panel seed story of one rerun folder (python -m experiments.sensitivity rerun
        RUN_ID writes it): capacity share of each label and price over time; orders of
        dearer techniques by profit-rate firms, entries and exits.
    python -m experiments.analysis grid --cells NAME ... --seeds N [--jobs J] [--budget S]
        Stage 4 (track B2 and the candidate rules of B3): runs the three populations of
        each named cell of STAGE4 over seeds 1..N and appends the rows to
        outputs/analysis/stage4_runs.csv in batches, skipping the run ids already there, and
        stops starting batches after --budget seconds (so that a call can be resumed).
    python -m experiments.analysis merge
        Appends the stage 4 rows to outputs/sensitivity/runs.csv in (cell, population, seed)
        order, rewrites runs.parquet and cells.csv (experiments.sensitivity.summarise).
    python -m experiments.analysis figures
        The figures of the discussion that read cells.csv (summary, anchor threshold,
        candidate rules), into outputs/analysis/figures/.

Nothing here changes the model: rows are produced by experiments.sensitivity.run_one, the
function every stage used; firm.type is a label and every winner is reported next to its
two neutral controls (both labels on one rule) over the same seeds.
"""

import argparse
import json
import math
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

import run
from experiments import sensitivity as sens
from experiments.neutral_control import POPULATIONS

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "analysis"
FIG = OUT / "figures"
SENS = sens.OUT

# --- Cells -------------------------------------------------------------------------------
# The cells of section 6 of sensitivity-results.md ("the cells the group should argue
# about") and their references, as (stage, cell, short label). The stage is the one with
# the most seeds for that cell.
SECTION6 = [
    ("3", "base", "base (rc, re, cat)"),
    ("3", "lf", "lf (leader-follow)"),
    ("1", "no_tech", "no_tech (fixed menu)"),
    ("1", "is_marx_15", "is_marx_15"),
    ("1", "anchor_r05", "anchor, rbar 0.05"),
    ("1", "anchor_r16", "anchor, rbar 0.16"),
    ("2", "rc-acd-static-cat-r05", "rc-acd-static-cat-r05"),
    ("2", "rc-acd-static-is15-r05", "rc-acd-static-is15-r05"),
    ("2", "rc-re-g01-cat-r16", "rc-re-g01-cat-r16"),
    ("2", "rc-acd-g01-cat-r16", "rc-acd-g01-cat-r16"),
    ("3", "lf-re-g01-cat-r16", "lf-re-g01-cat-r16"),
    ("3", "lf-acd-g01-cat-r16", "lf-acd-g01-cat-r16"),
    ("1", "lf_floor_ucs", "lf, operating-cost floor"),
]

ANCHOR = {"PRICING_RULE": "anchor"}
LF = {"PRICING_RULE": "leader_follow"}
IS = {"TECH_CHANGE": "innovation_set"}
ACD = {"INVESTMENT_RULE": "accelerator", "BORROWING": True}

# Stage 4: cells that stages 1-3 did not run (or not with these seeds). name -> (factor,
# overrides), the format of experiments.sensitivity's stage dictionaries. The anchor cells
# at rbar 0.05 and 0.16 are stage 1 cells (seeds 1-200) and are not run again: the model is
# deterministic per seed, so they would reproduce stage 1 row for row.
STAGE4 = {
    # B2: the real-competition twin of the second reversal (stage 2: 0.32 at 100 seeds).
    "rc-re-g01-cat-r16": ("twin", {"DEMAND_GROWTH": 0.01, "RBAR": 0.16}),
    # B2: where does the anchor reversal set in? (stage 1 has 0.05 and 0.16)
    "anchor_r08": ("anchor_rbar", dict(ANCHOR, RBAR=0.08)),
    "anchor_r10": ("anchor_rbar", dict(ANCHOR, RBAR=0.10)),
    "anchor_r12": ("anchor_rbar", dict(ANCHOR, RBAR=0.12)),
    "anchor_r14": ("anchor_rbar", dict(ANCHOR, RBAR=0.14)),
    # B2: the leader-follow reversal with the best plant's unit cost as the floor instead of
    # the markup on the average unit cost of all plants (old vintages included).
    "lf-re-g01-cat-r16-flooruc": ("lf_floor", dict(LF, LEADER_FOLLOW_FLOOR="unit_cost",
                                                   DEMAND_GROWTH=0.01, RBAR=0.16)),
    # B2: the anchor reversal with one anchor for all firms (the leader's target return).
    "anchor_r16-leader": ("anchor_kind", dict(ANCHOR, RBAR=0.16, PRICING_ANCHOR="leader")),
    # B2: the exit floor in the reversal cells (MIN_FIRMS = 2 is the default).
    "lf-re-g01-cat-r16-minf1": ("min_firms", dict(LF, DEMAND_GROWTH=0.01, RBAR=0.16,
                                                  MIN_FIRMS=1)),
    "anchor_r16-minf1": ("min_firms", dict(ANCHOR, RBAR=0.16, MIN_FIRMS=1)),
    # B2: finance x selection intensity (accelerator with borrowing at weak selection).
    "rc-acd-chi025": ("finance_chi", dict(ACD, CHI=0.25)),
    "rc-acd-chi05": ("finance_chi", dict(ACD, CHI=0.5)),
    "lf-acd-chi025": ("finance_chi", dict(LF, **ACD, CHI=0.25)),
    "lf-acd-chi05": ("finance_chi", dict(LF, **ACD, CHI=0.5)),
    # B2: TAU under both technical-change rules.
    "tau_005": ("tau", {"TAU": 0.05}),
    "tau_010": ("tau", {"TAU": 0.10}),
    "tau_015": ("tau", {"TAU": 0.15}),
    "is15-tau_010": ("tau", dict(IS, TECH_BIAS=1.5, TAU=0.10)),
    "is15-tau_025": ("tau", dict(IS, TECH_BIAS=1.5, TAU=0.25)),
}

POPULATION_ORDER = list(POPULATIONS)  # mixed, then the two controls


# --- Loading -----------------------------------------------------------------------------
def load_runs(columns=None) -> pd.DataFrame:
    """The runs table (parquet copy of runs.csv: the same rows)."""
    path = SENS / "runs.parquet"
    if path.exists():
        return pd.read_parquet(path, columns=columns)
    return sens.load_runs(SENS)[columns] if columns else sens.load_runs(SENS)


def load_cells() -> pd.DataFrame:
    return pd.read_csv(SENS / "cells.csv", dtype={"stage": str}, low_memory=False)


def cell_row(cells: pd.DataFrame, stage: str, cell: str, population: str = "mixed"):
    match = cells[(cells["stage"] == stage) & (cells["cell"] == cell)
                  & (cells["population"] == population)]
    return None if match.empty else match.iloc[0]


# --- B1: regression ----------------------------------------------------------------------
REGRESSORS = ["okishio_dearer", "price_to_pp", "hhi_mean", "n_firms_mean", "war_episodes",
              "d_share_price_all", "d_share_accum_all"]
SPECS = {
    # The regressors of the prompt.
    "full": REGRESSORS,
    # Without the two decomposition terms, which are parts of the outcome itself.
    "mechanism": ["okishio_dearer", "price_to_pp", "hhi_mean", "n_firms_mean", "war_episodes"],
    # Adds who won: does okishio_dearer still predict the gap among seeds with the same
    # winner (Shaikh's mechanism), or is the gap the winner's (market structure)?
    "winner": ["okishio_dearer", "price_to_pp", "hhi_mean", "n_firms_mean", "war_episodes",
               "shaikh_wins"],
}


def within(frame: pd.DataFrame, columns: list[str], group: str) -> pd.DataFrame:
    """Deviations from the group means (cell fixed effects absorbed)."""
    return frame[columns] - frame.groupby(group)[columns].transform("mean")


def ols_fe(frame: pd.DataFrame, y: str, xs: list[str], group: str = "cell") -> pd.DataFrame:
    """OLS of y on xs with group fixed effects (within transformation) and standard errors
    clustered by group (CR1). Returns one row per regressor: coefficient, standard error,
    95 % interval, the effect of a one within-group standard deviation of x, N, groups and
    the within R^2."""
    data = frame[[y] + xs + [group]].dropna()
    data = data.astype({c: float for c in [y] + xs})
    dm = within(data, [y] + xs, group)
    yv = dm[y].to_numpy()
    X = dm[xs].to_numpy()
    keep = X.std(axis=0) > 0
    X = X[:, keep]
    names = [x for x, k in zip(xs, keep) if k]
    beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
    resid = yv - X @ beta
    bread = np.linalg.pinv(X.T @ X)
    groups = data[group].to_numpy()
    meat = np.zeros((X.shape[1], X.shape[1]))
    labels = pd.unique(groups)
    for g in labels:
        idx = groups == g
        s = X[idx].T @ resid[idx]
        meat += np.outer(s, s)
    n, k, n_g = X.shape[0], X.shape[1], len(labels)
    factor = n_g / (n_g - 1) * (n - 1) / (n - k)
    se = np.sqrt(np.diag(factor * bread @ meat @ bread))
    sst = float(yv @ yv)
    r2 = 1.0 - float(resid @ resid) / sst if sst > 0 else float("nan")
    sd = X.std(axis=0)
    return pd.DataFrame({
        "y": y, "x": names, "coef": beta, "se": se,
        "ci_low": beta - 1.96 * se, "ci_high": beta + 1.96 * se,
        "effect_1sd": beta * sd, "sd_within": sd,
        "n": n, "groups": n_g, "r2_within": r2,
    })


def stage2_decided(runs: pd.DataFrame) -> pd.DataFrame:
    s2 = runs[(runs["stage"] == "2") & (runs["population"] == "mixed")
              & (~runs["undecided"].astype(bool))].copy()
    s2["gap"] = s2["profit_rate_shaikh"] - s2["profit_rate_okishio"]
    s2["shaikh_wins"] = s2["shaikh_wins"].astype(float)
    return s2


def b1_regressions(runs: pd.DataFrame, out: Path = OUT) -> pd.DataFrame:
    s2 = stage2_decided(runs)
    tables = []
    for y in ("gap", "shaikh_wins"):
        for spec, xs in SPECS.items():
            if y == "shaikh_wins" and spec == "winner":
                continue
            t = ols_fe(s2, y, xs)
            t.insert(0, "spec", spec)
            tables.append(t)
    table = pd.concat(tables, ignore_index=True)
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "b1_regression.csv", index=False)
    # Descriptive split: mean gap and mean okishio_dearer by winner and pricing rule.
    split = (s2.groupby(["pricing_rule", "shaikh_wins"])
             [["gap", "okishio_dearer", "profit_rate_shaikh", "profit_rate_okishio",
               "price_to_pp", "hhi_mean", "n_firms_mean"]].mean().reset_index())
    split.to_csv(out / "b1_gap_by_winner.csv", index=False)
    return table


def fig_gap_vs_dearer(runs: pd.DataFrame, path: Path) -> None:
    plt = sens._style()
    s2 = stage2_decided(runs).dropna(subset=["gap", "okishio_dearer"])
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for rule, colour in sens.RULE_COLOURS.items():
        part = s2[s2["pricing_rule"] == rule]
        if part.empty:
            continue
        ax.scatter(part["okishio_dearer"], part["gap"], s=5, alpha=0.25, color=colour,
                   linewidths=0, label=f"{sens.PRICING_NAMES[rule]} ({len(part)} seeds)")
        b, a = np.polyfit(part["okishio_dearer"], part["gap"], 1)
        xs = np.linspace(0, 1, 50)
        ax.plot(xs, a + b * xs, color=colour, linewidth=2.2)
        ax.text(0.98, a + b * 0.98, f"slope {b:.3f}", color=colour, ha="right",
                va="bottom", fontsize=8)
    ax.axhline(0, color="#52514e", linewidth=0.8)
    ax.set_xlabel("okishio_dearer: share of profit-rate orders that are not the cheapest "
                  "known technique")
    ax.set_ylabel("realised profit-rate gap, unit-cost label minus profit-rate label\n"
                  "(firms' profit rates, t = 100-199)")
    ax.set_title("Figure B1.1. The realised gap rises with the profit-rate firms' dearer orders\n"
                 "stage 2, mixed population, 176 cells x seeds 1-100, decided seeds; "
                 "lines: pooled OLS by pricing rule", fontsize=9)
    ax.legend(loc="upper left", markerscale=4)
    ax.set_xlim(-0.02, 1.02)
    lo, hi = s2["gap"].quantile([0.005, 0.995])
    ax.set_ylim(lo, hi)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# --- B1: attribution over the whole run --------------------------------------------------
CAPACITY_TERMS = [("d_share_accum_all", "accumulation", "#6250d6"),
                  ("d_share_entry_all", "entry", "#1baf7a"),
                  ("d_share_exit_all", "exit", "#e34948")]
SALES_TERMS = [("d_share_price_all", "price", "#6250d6"),
               ("d_share_entry_exit_all", "entry and exit", "#1baf7a"),
               ("d_share_rationing_all", "rationing", "#f2c14e")]


def attribution_table(cells: pd.DataFrame, entries=SECTION6) -> pd.DataFrame:
    rows = []
    for stage, cell, label in entries:
        r = cell_row(cells, stage, cell)
        if r is None:
            continue
        row = {"stage": stage, "cell": cell, "label": label, "n_seeds": r["n_seeds"],
               "share_won": r["share_won"]}
        for col, _, _ in CAPACITY_TERMS + SALES_TERMS:
            row[col] = r[f"{col}_mean"]
        row["cap_share_shaikh_end"] = r["cap_share_shaikh_end_mean"]
        rows.append(row)
    return pd.DataFrame(rows)


def fig_attribution(table: pd.DataFrame, path: Path) -> None:
    plt = sens._style()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.8), sharey=True)
    y = np.arange(len(table))[::-1]
    for ax, terms, title in ((axes[0], CAPACITY_TERMS, "capacity share of the unit-cost label"),
                             (axes[1], SALES_TERMS, "sales share of the unit-cost label")):
        left_pos = np.zeros(len(table))
        left_neg = np.zeros(len(table))
        for col, name, colour in terms:
            v = table[col].fillna(0.0).to_numpy()
            left = np.where(v >= 0, left_pos, left_neg)
            ax.barh(y, v, left=left, color=colour, label=name, height=0.7)
            left_pos = left_pos + np.where(v >= 0, v, 0)
            left_neg = left_neg + np.where(v < 0, v, 0)
        total = table[[c for c, _, _ in terms]].sum(axis=1).to_numpy()
        ax.scatter(total, y, color="#0b0b0b", s=14, zorder=3, label="sum")
        ax.axvline(0, color="#52514e", linewidth=0.8)
        ax.set_title(f"change in the {title}, t = 0-199", fontsize=9)
        ax.legend(loc="lower right", fontsize=8)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels([f"{l}  [{s}; {w:.2f}]" for l, s, w in
                             zip(table["label"], table["stage"], table["share_won"])],
                            fontsize=8)
    fig.suptitle("Figure B1.2. Whole-run attribution of the unit-cost label's share change "
                 "(cell means over seeds; [stage; share of seeds won])\n"
                 "mixed population; seeds 1-500 (stage 3), 1-200 (stage 1), 1-100 (stage 2)",
                 fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# --- B1: takeover timing -----------------------------------------------------------------
def takeover_table(runs: pd.DataFrame, entries=SECTION6) -> pd.DataFrame:
    rows = []
    for stage, cell, label in entries:
        part = runs[(runs["stage"] == stage) & (runs["cell"] == cell)
                    & (runs["population"] == "mixed")]
        if part.empty:
            continue
        t = part["takeover_t"]
        has = t.notna()
        rows.append({
            "stage": stage, "cell": cell, "n_seeds": len(part),
            "takeover_share": has.mean(),
            "by_shaikh": (part["takeover_label"] == "shaikh").mean(),
            "by_okishio": (part["takeover_label"] == "okishio").mean(),
            "before_100": (t < 100).sum() / max(1, has.sum()),
            "t_q25": t.quantile(0.25), "t_median": t.median(), "t_q75": t.quantile(0.75),
        })
    return pd.DataFrame(rows)


def fig_takeover(runs: pd.DataFrame, entries, path: Path) -> None:
    plt = sens._style()
    from style import TYPE_STYLE
    fig, ax = plt.subplots(figsize=(10, 5.5))
    labels = []
    for i, (stage, cell, label) in enumerate(entries):
        part = runs[(runs["stage"] == stage) & (runs["cell"] == cell)
                    & (runs["population"] == "mixed")]
        if part.empty:
            continue
        for who, offset in (("shaikh", -0.18), ("okishio", 0.18)):
            t = part.loc[part["takeover_label"] == who, "takeover_t"].dropna()
            jitter = np.random.default_rng(0).uniform(-0.1, 0.1, len(t))
            ax.scatter(t, np.full(len(t), i + offset) + jitter, s=5, alpha=0.35,
                       color=TYPE_STYLE[who]["color"], linewidths=0)
        labels.append(f"{label} [{stage}]")
    ax.axvline(100, color="#0b0b0b", linestyle="--", linewidth=1)
    ax.text(101, len(labels) - 0.5, "window starts (t = 100)", fontsize=8)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("takeover_t: first period after which one label holds > 90 % of capacity "
                  "to the end")
    ax.set_title("Figure B1.3. When takeovers happen (one dot per seed; blue: the unit-cost "
                 "label takes over, orange: the profit-rate label)\nmixed population, seeds "
                 "as in the stage named", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# --- Summary chart -----------------------------------------------------------------------
def fig_summary(cells: pd.DataFrame, entries, path: Path, title: str) -> None:
    """Share won by the unit-cost label with its Wilson interval, the two controls'
    intervals as grey bands behind it."""
    plt = sens._style()
    from style import TYPE_STYLE
    rows = []
    for stage, cell, label in entries:
        m = cell_row(cells, stage, cell)
        if m is None:
            continue
        uc = cell_row(cells, stage, cell, "all_unit_cost")
        pr = cell_row(cells, stage, cell, "all_profit_rate")
        rows.append((label, stage, m, uc, pr))
    fig, ax = plt.subplots(figsize=(9, 0.42 * len(rows) + 1.6))
    for i, (label, stage, m, uc, pr) in enumerate(rows):
        lo = min(uc["won_low"], pr["won_low"])
        hi = max(uc["won_high"], pr["won_high"])
        ax.add_patch(plt.Rectangle((lo, i - 0.32), hi - lo, 0.64, color="#d9d8d4",
                                   zorder=1, linewidth=0))
        colour = (TYPE_STYLE["shaikh"]["color"] if m["share_won"] > 0.5
                  else TYPE_STYLE["okishio"]["color"])
        if str(m["beyond_drift"]) not in ("True", "1", "1.0"):
            colour = "#52514e"
        ax.errorbar(m["share_won"], i, xerr=[[m["share_won"] - m["won_low"]],
                                             [m["won_high"] - m["share_won"]]],
                    fmt="o", color=colour, capsize=3, zorder=3)
        ax.text(1.02, i, f"{m['share_won']:.2f}  ({int(m['n_seeds'])} seeds, stage {stage})",
                va="center", fontsize=8)
    ax.axvline(0.5, color="#52514e", linewidth=0.8, linestyle=":")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("share of decided seeds in which the unit-cost label holds > 1/2 of "
                  "capacity at t = 199 (95 % Wilson interval)")
    ax.set_title(title, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# --- Seed stories ------------------------------------------------------------------------
def takeover_from_shares(t, share) -> float:
    above = (share > 0.9) | (share < 0.1)
    if not above.iloc[-1]:
        return float("nan")
    last_below = np.where(~above.to_numpy())[0]
    return float(t.iloc[0]) if len(last_below) == 0 else float(t.iloc[last_below[-1] + 1])


def story(run_dir: Path, name: str | None = None, out: Path = FIG,
          title: str | None = None) -> Path:
    """Two panels from a rerun folder: (1) capacity share of each label and the average and
    lowest posted price; (2) one row of marks per event type: orders of dearer techniques by
    profit-rate firms (not the cheapest known technique), orders of designs by unit-cost
    firms, entries and exits by label."""
    plt = sens._style()
    from style import TYPE_STYLE
    run_dir = Path(run_dir)
    macro = pd.read_csv(run_dir / "macro.csv")
    events = pd.read_csv(run_dir / "events.csv", low_memory=False)
    runs = pd.read_csv(run_dir / "runs.csv")
    run_id = runs["run_id"].iloc[0]
    t = macro["t"]
    cap = macro["capacity_total"].replace(0, np.nan)
    share_s = macro["capacity_shaikh"] / cap
    share_o = macro["capacity_okishio"] / cap
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True,
                                   gridspec_kw={"height_ratios": [1.3, 1]})
    ax1.plot(t, share_s, color=TYPE_STYLE["shaikh"]["color"], label="capacity share, label shaikh (unit cost)")
    ax1.plot(t, share_o, color=TYPE_STYLE["okishio"]["color"], linestyle="--",
             label="capacity share, label okishio (profit rate)")
    ax1.set_ylim(-0.02, 1.02)
    ax1.set_ylabel("capacity share")
    tk = takeover_from_shares(t, share_s.fillna(0.5))
    if not math.isnan(tk):
        ax1.axvline(tk, color="#0b0b0b", linestyle=":", linewidth=1)
        ax1.text(tk + 1, 0.93, f"takeover t = {tk:.0f}", fontsize=8)
    axp = ax1.twinx()
    axp.plot(t, macro["price_avg"], color="#52514e", linewidth=1, label="average price")
    axp.plot(t, macro["min_price"], color="#0b0b0b", linewidth=0.8, linestyle=":",
             label="lowest price")
    axp.set_ylabel("price (money wage = 1)")
    axp.grid(False)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = axp.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="lower left", fontsize=7)
    orders = events[events["event"] == "order"]
    dearer = orders[(orders["rule"] == "profit_rate") & orders["tech"].notna()
                    & (orders["tech"] != orders["other_tech"])]
    pr_orders = orders[orders["rule"] == "profit_rate"]
    rows = [
        ("dearer orders, profit-rate firms", dearer["t"], TYPE_STYLE["okishio"]["color"], "|"),
        ("other orders, profit-rate firms", pr_orders.loc[~pr_orders.index.isin(dearer.index), "t"],
         "#f3b49a", "|"),
        ("orders, unit-cost firms", orders.loc[orders["rule"] == "unit_cost", "t"],
         TYPE_STYLE["shaikh"]["color"], "|"),
    ]
    for label in ("shaikh", "okishio"):
        ent = events[(events["event"] == "entry") & (events["group"] == label)]["t"]
        ext = events[(events["event"] == "exit") & (events["group"] == label)]["t"]
        rows.append((f"entries, label {label}", ent, TYPE_STYLE[label]["color"], "^"))
        rows.append((f"exits, label {label}", ext, TYPE_STYLE[label]["color"], "x"))
    for i, (label, times, colour, marker) in enumerate(rows):
        ax2.scatter(times, np.full(len(times), i), marker=marker, color=colour, s=22,
                    linewidths=1)
        ax2.text(201, i, f"{len(times)}", va="center", fontsize=7)
    ax2.set_yticks(range(len(rows)))
    ax2.set_yticklabels([r[0] for r in rows], fontsize=8)
    ax2.invert_yaxis()
    ax2.set_xlabel("period t")
    ax2.set_xlim(-2, 206)
    first = dearer["t"].min() if len(dearer) else float("nan")
    note = (f"first dearer order t = {first:.0f}" if not math.isnan(first)
            else "no dearer order")
    row = runs.iloc[0]
    ax1.set_title(f"{title or name or run_id}\ncell {row['cell']}, population "
                  f"{row['population']}, seed {int(row['seed'])} (run {run_id}); {note}",
                  fontsize=9)
    fig.tight_layout()
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{name or ('story_' + run_id)}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


# --- Part A figures ----------------------------------------------------------------------
# (figure name, run id of the rerun folder in outputs/sensitivity/reruns/, title)
STORIES = [
    ("A1_story_base_s4", "1_base_mixed_s4",
     "Figure A1. A typical base seed: the unit-cost label takes over"),
    ("A2_story_base_s1", "1_base_mixed_s1",
     "Figure A2. A base seed the profit-rate rule wins"),
    ("A3_story_lf_s1", "1_lf_mixed_s1", "Figure A3. Leader-follow defaults"),
    ("A4_story_rc-re-static-is15-r16_s1", "2_rc-re-static-is15-r16_mixed_s1",
     "Figure A4. Innovation set (marx 1.5): dearer orders all along"),
    ("A5_story_anchor_r16_s3", "1_anchor_r16_mixed_s3",
     "Figure A5. First reversal: anchor pricing at rbar 0.16"),
    ("A6_story_lf-re-g01-cat-r16_s1", "3_lf-re-g01-cat-r16_mixed_s1",
     "Figure A6. Second reversal: leader-follow, retained earnings, growth 1 %, rbar 0.16"),
    ("A7_story_lf-acd-g01-cat-r16_s1", "3_lf-acd-g01-cat-r16_mixed_s1",
     "Figure A7. Its finance twin: the accelerator with borrowing, same seed"),
    ("B1_4_story_anchor_r16_s4", "1_anchor_r16_mixed_s4",
     "Figure B1.4. Anchor at rbar 0.16, seed 4 (profit-rate rule wins)"),
    ("B1_5_story_anchor_r16_s5", "1_anchor_r16_mixed_s5",
     "Figure B1.5. Anchor at rbar 0.16, seed 5 (profit-rate rule wins)"),
    ("B1_6_story_anchor_r05_s3", "1_anchor_r05_mixed_s3",
     "Figure B1.6. The same seed 3 at rbar 0.05: the unit-cost rule wins"),
]

CONTROL_CELLS = [("3", "base", "categories\n(base)"), ("1", "is_neutral", "neutral set"),
                 ("1", "is_marx_05", "marx 0.5"), ("1", "is_marx_15", "marx 1.5"),
                 ("1", "is_marx_3", "marx 3"), ("1", "no_tech", "fixed menu\n(no_tech)")]


def fig_controls_profit_rate(cells: pd.DataFrame, path: Path) -> pd.DataFrame:
    """Industry profit rate (mean over t = 100-199 and seeds, 95 % interval of the mean) in
    the two neutral controls and the mixed population, by technical-change rule."""
    plt = sens._style()
    from style import TYPE_STYLE
    fig, ax = plt.subplots(figsize=(9, 4.8))
    rows = []
    styles = [("all_unit_cost", -0.2, TYPE_STYLE["shaikh"]["color"], "every firm on the unit-cost rule"),
              ("mixed", 0.0, "#52514e", "mixed population"),
              ("all_profit_rate", 0.2, TYPE_STYLE["okishio"]["color"], "every firm on the profit-rate rule")]
    for i, (stage, cell, label) in enumerate(CONTROL_CELLS):
        for pop, dx, colour, name in styles:
            r = cell_row(cells, stage, cell, pop)
            if r is None:
                continue
            m, lo, hi = (r["profit_rate_total_mean"], r["profit_rate_total_ci_lo"],
                         r["profit_rate_total_ci_hi"])
            ax.errorbar(i + dx, 100 * m, yerr=[[100 * (m - lo)], [100 * (hi - m)]], fmt="o",
                        color=colour, capsize=3, label=name if i == 0 else None)
            rows.append({"stage": stage, "cell": cell, "population": pop, "mean": m,
                         "ci_lo": lo, "ci_hi": hi})
    ax.set_xticks(range(len(CONTROL_CELLS)))
    ax.set_xticklabels([f"{c[2]}\n[stage {c[0]}]" for c in CONTROL_CELLS], fontsize=8)
    ax.set_ylabel("industry profit rate, % (t = 100-199)")
    ax.set_title("Figure A8. Selection picks the rule that lowers the industry's profit rate\n"
                 "neutral controls (one rule for every firm) and mixed population; seeds 1-500 "
                 "(stage 3) or 1-200 (stage 1); 95 % interval of the mean", fontsize=9)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return pd.DataFrame(rows)


def part_a_figures() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    for name, run_id, title in STORIES:
        folder = SENS / "reruns" / run_id
        if not (folder / "macro.csv").exists():
            sens.rerun(run_id, folder, quiet=True)
        story(folder, name, title=title)
    table = fig_controls_profit_rate(load_cells(), FIG / "A8_controls_profit_rate.png")
    table.to_csv(OUT / "a8_controls_profit_rate.csv", index=False)


# --- Stage 4 -----------------------------------------------------------------------------
STAGE4_RUNS = OUT / "stage4_runs.csv"


def stage4_tasks(cells: list[str], seeds: int) -> list[tuple]:
    tasks = []
    for cell in cells:
        if cell not in STAGE4:
            raise SystemExit(f"unknown stage 4 cell {cell}")
        overrides = STAGE4[cell][1]
        for population in POPULATION_ORDER:
            for seed in range(1, seeds + 1):
                tasks.append(("4", cell, overrides, population, seed))
    return tasks


def done_ids(path: Path = STAGE4_RUNS) -> set:
    if not path.exists():
        return set()
    return set(pd.read_csv(path, usecols=["run_id"])["run_id"])


def append_rows(rows: list[dict], path: Path = STAGE4_RUNS) -> None:
    frame = pd.DataFrame(rows)
    if path.exists():
        columns = pd.read_csv(path, nrows=0).columns
        frame.reindex(columns=columns).to_csv(path, mode="a", header=False, index=False)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)


def grid4(cells: list[str], seeds: int, jobs: int, budget: float, batch: int = 48,
          path: Path | None = None) -> int:
    """Run what is missing of the named stage 4 cells, batch by batch, until the budget is
    spent. Returns the number of runs still missing."""
    path = path or STAGE4_RUNS
    done = done_ids(path)
    tasks = [t for t in stage4_tasks(cells, seeds)
             if run.make_run_id(t[0], t[1], t[3], t[4]) not in done]
    start = time.perf_counter()
    version = run.code_version()
    pool = Pool(jobs, initializer=sens._init_worker, initargs=(version,)) if jobs > 1 else None
    if pool is None:
        sens._init_worker(version)
    try:
        while tasks and time.perf_counter() - start < budget:
            chunk, tasks = tasks[:batch], tasks[batch:]
            rows = list(pool.imap(sens.run_one, chunk) if pool else map(sens.run_one, chunk))
            append_rows(rows, path)
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    elapsed = time.perf_counter() - start
    sens.log(path.parent, f"stage 4 {cells}: {len(tasks)} runs missing after {elapsed:.0f} s")
    return len(tasks)


def merge4(path: Path | None = None, sens_out: Path | None = None) -> None:
    """Append the stage 4 rows to runs.csv in (cell, population, seed) order; rewrite
    runs.parquet and cells.csv. Refuses if runs.csv already has stage 4 rows."""
    path = path or STAGE4_RUNS
    sens_out = sens_out or SENS
    new = pd.read_csv(path, dtype={"stage": str, "plant_life": object}, low_memory=False)
    done = sens.finished_cells(sens_out)
    if any(s == "4" for s, _ in done):
        raise SystemExit("runs.csv already has stage 4 rows")
    order = {c: i for i, c in enumerate(STAGE4)}
    new["_c"] = new["cell"].map(order)
    new["_p"] = new["population"].map({p: i for i, p in enumerate(POPULATION_ORDER)})
    new = new.sort_values(["_c", "_p", "seed"]).drop(columns=["_c", "_p"])
    if new["run_id"].duplicated().any():
        raise SystemExit("duplicated run ids in stage4_runs.csv")
    sens._append(sens_out, new.to_dict("records"))
    sens.write_parquet(sens_out)
    sens.summarise(sens_out)
    sens.log(sens_out, f"stage 4 merged: {len(new)} runs, cells {sorted(new['cell'].unique())}")


# --- Main --------------------------------------------------------------------------------
def b1(out: Path = OUT) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    runs = load_runs()
    cells = load_cells()
    table = b1_regressions(runs, out)
    print(table.round(4).to_string(index=False))
    fig_gap_vs_dearer(runs, FIG / "B1_1_gap_vs_dearer.png")
    att = attribution_table(cells)
    att.to_csv(out / "b1_attribution.csv", index=False)
    fig_attribution(att, FIG / "B1_2_attribution.png")
    tk = takeover_table(runs)
    tk.to_csv(out / "b1_takeover.csv", index=False)
    print(tk.round(3).to_string(index=False))
    fig_takeover(runs, SECTION6, FIG / "B1_3_takeover.png")
    fig_summary(cells, SECTION6, FIG / "A0_summary_section6.png",
                "Figure A0. Share of seeds won by the unit-cost label, cells of section 6 of "
                "the results\nmixed population; grey band: union of the two neutral controls' "
                "intervals; grey dot: not beyond drift")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("b1")
    sub.add_parser("parta")
    p = sub.add_parser("story")
    p.add_argument("run_dir")
    p.add_argument("--name")
    p = sub.add_parser("grid")
    p.add_argument("--cells", nargs="+", required=True)
    p.add_argument("--seeds", type=int, required=True)
    p.add_argument("--jobs", type=int, default=4)
    p.add_argument("--budget", type=float, default=150.0)
    sub.add_parser("merge")
    sub.add_parser("figures")
    args = parser.parse_args(argv)
    if args.command == "b1":
        b1()
    elif args.command == "parta":
        part_a_figures()
    elif args.command == "story":
        print(story(Path(args.run_dir), args.name))
    elif args.command == "grid":
        missing = grid4(args.cells, args.seeds, args.jobs, args.budget)
        print(f"missing {missing}")
    elif args.command == "merge":
        merge4()
    elif args.command == "figures":
        figures()


def figures() -> None:
    """Figures that read cells.csv after the stage 4 merge."""
    cells = load_cells()
    anchors = [("1", "anchor_r05", "rbar 0.05")] + [
        ("4", f"anchor_r{r}", f"rbar 0.{r}") for r in ("08", "10", "12", "14")
    ] + [("1", "anchor_r16", "rbar 0.16")]
    fig_summary(cells, anchors, FIG / "B2_1_anchor_threshold.png",
                "Figure B2.1. Anchor pricing (version 1): share won by the unit-cost label "
                "against rbar\nmixed population, seeds 1-200; grey band: the controls' "
                "intervals")


if __name__ == "__main__":
    main()
