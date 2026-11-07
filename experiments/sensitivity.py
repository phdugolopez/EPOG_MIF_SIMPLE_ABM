"""The first full sensitivity analysis (step 4 of the plan in docs/design/review-v2.md).

    python -m experiments.sensitivity grid --stage {1,2,3} [--seeds N] [--jobs J] [--resume]
                                           [--cells NAME ...] [--out DIR]
    python -m experiments.sensitivity summarise [--out DIR]
    python -m experiments.sensitivity rerun RUN_ID [--out DIR] [--runs FILE]
    python -m experiments.sensitivity figures [--out DIR]

`grid` runs every cell of a stage for three populations (the mixed one of parameters.py and
the two neutral controls, both labels on one rule) over seeds 1..N, one Industry per task
in a multiprocessing pool. The results are gathered and written in (cell, population,
seed) order, so that the tables never depend on scheduling: each finished cell is appended
to DIR/runs.csv (and DIR/runs.parquet rewritten), with a line in DIR/progress.log;
--resume skips the cells already in runs.csv. One row per run: run.runs_row (every
parameter as the runs table of run.py has it), plus stage, overrides (the cell's, as JSON)
and the observables of docs/design/sensitivity-plan.md section 3, computed in the worker
from run.tables and discarded after. `summarise` writes DIR/cells.csv (one row per stage,
cell and population). `rerun` reruns one row through run.py --set and checks that it
reproduces the row. `figures` draws the six figures into DIR/figures/. The model is not
changed: firm.type is a label, and every winner is reported next to its two controls.
"""

import argparse
import itertools
import json
import math
import os
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd

import run
from analysis.indicators import capacity_share_terms, cumulate, sales_share_terms
from experiments.neutral_control import POPULATIONS, parse_overrides, wilson
from model import Industry

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs" / "sensitivity"
WINDOW = (100, 199)  # means over t = 100..199 unless stated (first 100 periods: burn-in)
WINDOW_50 = (50, 199)
LABELS = ("shaikh", "okishio")

# --- Cells -------------------------------------------------------------------------------
LF = {"PRICING_RULE": "leader_follow"}
IS = {"TECH_CHANGE": "innovation_set"}

# Stage 1: one factor at a time around the version 2 defaults (plan, section 2 and 7).
# Each cell: name -> (factor, overrides). The leader-follow sub-factors are read against
# `lf`, diffusion and timing against `is_marx_15` (inert under categories).
STAGE1 = {
    "base": ("default", {}),
    "lf": ("pricing", dict(LF)),
    "anchor_r16": ("pricing", {"PRICING_RULE": "anchor", "RBAR": 0.16}),
    "anchor_r05": ("pricing", {"PRICING_RULE": "anchor"}),
    "rc_floor_ucs": ("floor", {"PRICE_FLOOR": "operating_cost"}),
    "lf_floor_uc": ("lf_floor", dict(LF, LEADER_FOLLOW_FLOOR="unit_cost")),
    "lf_floor_ucs": ("lf_floor", dict(LF, LEADER_FOLLOW_FLOOR="operating_cost")),
    "lf_no_cut": ("lf_shortage", dict(LF, SHORTAGE_RULE="no_cut")),
    "excess_unserved": ("excess_demand", {"EXCESS_DEMAND": "unserved"}),
    "accel_debt": ("finance", {"INVESTMENT_RULE": "accelerator", "BORROWING": True}),
    "accel_cash": ("finance", {"INVESTMENT_RULE": "accelerator", "BORROWING": False}),
    "grow_01": ("demand", {"DEMAND_GROWTH": 0.01}),
    "grow_03": ("demand", {"DEMAND_GROWTH": 0.03}),
    "unmet": ("demand", {"DEMAND_TO_CAPACITY": 1.2}),
    "unmet_grow_02": ("demand", {"DEMAND_TO_CAPACITY": 1.2, "DEMAND_GROWTH": 0.02}),
    "chi_025": ("chi", {"CHI": 0.25}),
    "chi_05": ("chi", {"CHI": 0.5}),
    "chi_2": ("chi", {"CHI": 2.0}),
    "chi_4": ("chi", {"CHI": 4.0}),
    "logit": ("demand_form", {"DEMAND_FORM": "logit"}),
    "cat_q0": ("tech", {"TECH_CONFLICT": 0.0}),
    "is_marx_05": ("tech", dict(IS, TECH_BIAS=0.5)),
    "is_marx_15": ("tech", dict(IS, TECH_BIAS=1.5)),
    "is_marx_3": ("tech", dict(IS, TECH_BIAS=3.0)),
    "is_neutral": ("tech", dict(IS, TECH_SET="neutral")),
    "is_private": ("diffusion", dict(IS, TECH_DIFFUSION="private")),
    "is_per_invest": ("diffusion", dict(IS, TECH_DRAW_TIMING="investment")),
    "is_frontier": ("diffusion", dict(IS, TECH_REFERENCE="frontier")),
    "no_tech": ("tech", {"TECH_DRAWS": False}),
    "entry_theta1": ("entry", {"ENTRY_SPEED": 1.0}),
    "rbar_16": ("entry", {"RBAR": 0.16}),
    "scrap_4": ("scrapping", {"IDLE_PERIODS": 4, "OBSOLESCENCE_PERIODS": 4}),
    "depr_use": ("depreciation", {"DEPRECIATION": "use"}),
    "plant_40": ("plant_size", {"PLANT_SIZE": 40.0}),
    "tau_025": ("tau", {"TAU": 0.25}),
    "hurdle_no_floor": ("hurdle_floor", {"HURDLE_FLOOR_AT_ZERO": False}),
}

# Stage 2: the factorial on the movers of stage 1 (plan, section 7, applied to the stage 1
# results in docs/design/sensitivity-results.md). Each factor: level name -> overrides; the
# cell name joins the level names with "-". CHI moved no level beyond the base cell's
# interval in stage 1, so it leaves the factorial (held at 1); the entry factor (rbar 0.16
# moved) and the per-investment draw timing (moved) join it.
ACD = {"INVESTMENT_RULE": "accelerator", "BORROWING": True}
STAGE2_FACTORS = {
    "pricing": {"rc": {}, "lf": dict(LF)},
    "finance": {"re": {}, "acd": dict(ACD)},
    "demand": {"static": {}, "g01": {"DEMAND_GROWTH": 0.01},
               "unmet": {"DEMAND_TO_CAPACITY": 1.2}},
    "tech": {"cat": {}, "is15": dict(IS, TECH_BIAS=1.5), "is3": dict(IS, TECH_BIAS=3.0),
             "isneu": dict(IS, TECH_SET="neutral"),
             "is15inv": dict(IS, TECH_BIAS=1.5, TECH_DRAW_TIMING="investment")},
    "entry": {"r05": {}, "r16": {"RBAR": 0.16}},
}
# The phase block for the headline figure (selection intensity x technical change, one
# panel per pricing and investment rule), static demand, rbar 0.05. Cells whose overrides
# equal a factorial cell's are not run twice.
PHASE_FACTORS = {
    "pricing": {"rc": {}, "lf": dict(LF)},
    "finance": {"re": {}, "acd": dict(ACD)},
    "chi": {"chi025": {"CHI": 0.25}, "chi1": {}, "chi4": {"CHI": 4.0}},
    "tech": {"catq0": {"TECH_CONFLICT": 0.0}, "cat": {}, "is05": dict(IS, TECH_BIAS=0.5),
             "is15": dict(IS, TECH_BIAS=1.5), "is3": dict(IS, TECH_BIAS=3.0),
             "isneu": dict(IS, TECH_SET="neutral")},
}


def _cross(factors: dict, prefix: str, factor_name: str) -> dict:
    cells = {}
    for combo in itertools.product(*(factors[f].items() for f in factors)):
        overrides = {}
        for _, levels in combo:
            overrides.update(levels)
        cells[prefix + "-".join(level for level, _ in combo)] = (factor_name, overrides)
    return cells


def stage2_cells() -> dict:
    cells = _cross(STAGE2_FACTORS, "", "factorial")
    seen = {json.dumps(o, sort_keys=True) for _, o in cells.values()}
    for name, (factor, overrides) in _cross(PHASE_FACTORS, "ph-", "phase").items():
        if json.dumps(overrides, sort_keys=True) not in seen:
            cells[name] = (factor, overrides)
    return cells


# Stage 3: base, lf and six cells chosen from stage 2 by the rule of the plan (section 7),
# written by choose_stage3 to OUT/stage3_cells.json so that the choice is on file.
def choose_stage3(cells: pd.DataFrame, out: Path = OUT) -> dict:
    """The largest |gap| (mixed against the mean of the controls) for each pricing rule,
    the largest and the smallest share won, the finance arm where it changes the share won
    most (the accelerator + borrowing cell against its retained-earnings twin), and one
    3 % growth cell (the version 2 defaults with DEMAND_GROWTH = 0.03)."""
    s2 = cells[(cells["stage"] == "2") & (cells["population"] == "mixed")].copy()
    s2 = s2.set_index("cell")
    chosen = {}

    def add(name, why):
        if name not in chosen:
            chosen[name] = {"overrides": json.loads(s2.loc[name, "overrides"]), "why": why}

    for pricing in ("rc", "lf"):
        part = s2[s2.index.str.startswith(pricing + "-")]
        add(part["gap"].abs().idxmax(), f"largest |gap| under {pricing}")
    add(s2["share_won"].idxmax(), "largest share won by the unit-cost rule")
    add(s2["share_won"].idxmin(), "smallest share won by the unit-cost rule")
    acd = [c for c in s2.index if "-acd-" in c and c.replace("-acd-", "-re-") in s2.index]
    diff = {c: abs(s2.loc[c, "share_won"] - s2.loc[c.replace("-acd-", "-re-"), "share_won"])
            for c in acd}
    if diff:
        add(max(diff, key=diff.get), "finance arm: largest change from retained earnings")
    chosen["grow_03"] = {"overrides": {"DEMAND_GROWTH": 0.03}, "why": "one 3 % growth cell"}
    out.mkdir(parents=True, exist_ok=True)
    (out / "stage3_cells.json").write_text(json.dumps(chosen, indent=2, sort_keys=True))
    return chosen


def stage3_cells(out: Path = OUT) -> dict:
    cells = {"base": STAGE1["base"], "lf": STAGE1["lf"]}
    path = out / "stage3_cells.json"
    if path.exists():
        for name, spec in json.loads(path.read_text()).items():
            cells[name] = ("decisive", spec["overrides"])
    return cells


def stage_cells(stage: str, out: Path = OUT) -> dict:
    if stage == "1":
        return dict(STAGE1)
    if stage == "2":
        return stage2_cells()
    if stage == "3":
        return stage3_cells(out)
    if stage == "smoke":
        return {"base": STAGE1["base"], "lf": STAGE1["lf"]}
    raise SystemExit(f"unknown stage {stage}")


# --- One run -----------------------------------------------------------------------------
def configuration(overrides: dict, population: str, seed: int):
    config = run.configure(seed, **overrides)
    rules = POPULATIONS[population]
    if rules is not None:
        config.HURDLE_RULES = dict(rules)
    return config


def _window(frame: pd.DataFrame, window=WINDOW) -> pd.DataFrame:
    return frame[(frame["t"] >= window[0]) & (frame["t"] <= window[1])]


def _num(series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _mean(series) -> float:
    s = _num(series)
    return float(s.mean()) if s.notna().any() else math.nan


def _ratio(a, b) -> float:
    return float(a) / float(b) if b and b > 0 else math.nan


def _share(k, n) -> float:
    return k / n if n else math.nan


def _group_series(groups: pd.DataFrame, label: str, column: str) -> pd.Series:
    g = groups[groups["group"] == label].set_index("t")[column]
    return _num(g)


def takeover(cap_share: pd.Series) -> tuple[float, str | None]:
    """First period after which one label holds more than 90 % of producing capacity in
    every remaining period (NaN, None if never). cap_share: shaikh's share indexed by t."""
    s = cap_share.sort_index()
    for label, held in (("shaikh", s > 0.9), ("okishio", s < 0.1)):
        if len(held) and bool(held.iloc[-1]):
            # the last run of True values that reaches the end
            not_held = held[~held]
            start = s.index[0] if not_held.empty else s.index[s.index > not_held.index[-1]][0]
            return float(start), label
    return math.nan, None


def observables(frames: dict, config) -> dict:
    """The observables of sensitivity-plan.md section 3, from the tables of one run."""
    m = frames["macro"].sort_values("t").reset_index(drop=True)
    g = frames["groups"]
    f = frames["firms"]
    p = frames["plants"]
    e = frames["events"]
    last = m.iloc[-1]
    mw = _window(m)
    m50 = _window(m, WINDOW_50)
    o = {}

    # Who dominates.
    cap = _num(m["capacity_shaikh"]) + _num(m["capacity_okishio"])
    sales = _num(m["sales_shaikh"]) + _num(m["sales_okishio"])
    cap_share = (_num(m["capacity_shaikh"]) / cap).where(cap > 0)
    cap_share.index = m["t"]
    o["cap_share_shaikh_end"] = float(cap_share.iloc[-1])
    o["sales_share_shaikh_end"] = _ratio(last["sales_shaikh"], sales.iloc[-1])
    o["undecided"] = bool(not cap.iloc[-1] > 0)
    o["shaikh_wins"] = bool(o["cap_share_shaikh_end"] > 0.5)
    o["takeover_t"], o["takeover_label"] = takeover(cap_share.dropna())
    o["n_shaikh_end"] = int(last["n_shaikh"])
    o["n_okishio_end"] = int(last["n_okishio"])
    one = g.drop(columns=["run_id"], errors="ignore")  # one run: decompose by group only
    sales_t = sales_share_terms(one)
    cap_t = capacity_share_terms(one)
    # window t = 100-199 (no suffix) and the whole run t = 0-199 (suffix _all): most
    # takeovers happen before or around t = 100, so the window alone misses them
    for start, suffix in ((WINDOW[0], ""), (0, "_all")):
        sales_terms = cumulate(sales_t, start=start)
        cap_terms = cumulate(cap_t, start=start)
        st = sales_terms.loc["shaikh"] if "shaikh" in sales_terms.index else None
        ct = cap_terms.loc["shaikh"] if "shaikh" in cap_terms.index else None
        nan = math.nan
        o["d_share_price" + suffix] = float(st["term_price"]) if st is not None else nan
        o["d_share_rationing" + suffix] = float(st["term_rationing"]) if st is not None else nan
        o["d_share_entry_exit" + suffix] = float(st["term_entry_exit"]) if st is not None else nan
        o["d_share_accum" + suffix] = (
            float(ct["term_ordered"] + ct["term_retired"] + ct["term_cancelled"])
            if ct is not None else nan)
        o["d_share_entry" + suffix] = float(ct["term_entry"]) if ct is not None else nan
        o["d_share_exit" + suffix] = float(ct["term_exit"]) if ct is not None else nan
    gw = _window(g)
    for label in LABELS:
        o[f"hurdle_mean_{label}"] = _mean(gw.loc[gw["group"] == label, "hurdle_mean"])

    # Is demand met.
    o["unmet_share"] = _mean(_num(mw["unmet_total"]) / _num(mw["demand"]))
    o["shortage_periods"] = int((_num(mw["unmet_total"]) > 1e-9).sum())
    o["util_mean"] = _mean(mw["util"])
    o["capacity_to_demand"] = _mean(_num(mw["capacity_total"]) / _num(mw["demand"]))
    o["excess_capacity_periods"] = int((_num(mw["util"]) < 0.9).sum())

    # Entry and exit.
    for col in ("entries", "exits", "exits_share", "exits_bankruptcy", "exits_non_renewal"):
        o[col] = int(_num(m[col]).sum())
        o[f"{col}_w"] = int(_num(mw[col]).sum())
    o["n_firms_mean"] = _mean(mw["n_firms"])
    o["n_firms_end"] = int(last["n_firms"])
    o["n_firms_min"] = int(_num(mw["n_firms"]).min())
    o["n_active_mean"] = _mean(mw["n_active"])
    o["hhi_mean"] = _mean(mw["hhi_sales"])
    born = f.groupby("firm_id")["born"].first()
    present = set(zip(f["firm_id"], f["t"]))
    entrants = born[(born > 0) & (born <= config.PERIODS - 21)]
    survived = sum((fid, b + 20) in present for fid, b in entrants.items())
    o["entrant_survival"] = _share(survived, len(entrants))
    exits = e[e["event"] == "exit"]
    ages = exits["t"] - exits["firm_id"].map(born)
    o["exit_age_median"] = float(ages.median()) if len(ages) else math.nan

    # Price and profit.
    price = _num(m["price_avg"])
    price.index = m["t"]
    o["price_mean"] = _mean(mw["price_avg"])
    o["price_mean_50"] = _mean(m50["price_avg"])
    o["price_end"] = float(price.iloc[-1])
    o["price_min"] = float(_num(mw["price_avg"]).min())
    o["price_max"] = float(_num(mw["price_avg"]).max())
    t_end = int(m["t"].iloc[-1])
    running = p[(p["t"] == t_end) & (p["running"].astype(bool))]
    if len(running):
        best = running.loc[_num(running["uc"]).idxmin()]
        o["price_to_pp"] = _ratio(price.iloc[-1], best["uc"] + config.RBAR * best["kappa"])
    else:
        o["price_to_pp"] = math.nan
    o["price_rise_after_adoption"] = bool(price.get(t_end, math.nan) > price.get(WINDOW[0], math.nan))
    o["cut_periods"] = int(mw["war_on"].astype(bool).sum())
    starts = e[e["event"] == "war_start"].set_index("other_id")
    ends = e[e["event"] == "war_end"].set_index("other_id")
    o["war_episodes"] = int(len(starts))
    o["war_episodes_w"] = int((starts["t"] >= WINDOW[0]).sum())
    deep = starts[starts["t"] > 0][["value"]].merge(
        ends[["value"]], left_index=True, right_index=True, suffixes=("", "_end"))
    depth = 1.0 - _num(deep["value_end"]) / _num(deep["value"])
    o["war_depth_mean"] = _mean(depth)
    o["cutting_share_mean"] = _mean(_num(mw["n_cutting"]) / _num(mw["n_active"]).where(_num(mw["n_active"]) > 0))
    for label in LABELS:
        o[f"profit_rate_{label}"] = _mean(mw[f"profit_rate_{label}"])
        o[f"profit_rate_{label}_50"] = _mean(m50[f"profit_rate_{label}"])
    o["profit_rate_total"] = _mean(mw["profit_rate"])
    o["profit_rate_total_50"] = _mean(m50["profit_rate"])
    o["r_new_mean"] = _mean(mw["r_new"])
    o["periods_above_rbar"] = int((_num(mw["profit_rate"]) > config.RBAR).sum())
    o["leader_lowest_cost_share"] = _mean(mw["leader_is_lowest_cost"].astype(float))
    cv = _num(mw["uc_cv_w"])
    o["price_cv_over_uc_cv"] = _mean((_num(mw["price_cv_w"]) / cv)[cv > 0])
    fw = _window(f)
    fw = fw[_num(fw["capacity"]) > 0]
    if len(fw):
        margin = fw.assign(margin=_num(fw["margin"])).groupby("t")["margin"]
        o["margin_spread"] = _mean(margin.max() - margin.min())
        w = fw.assign(w=_num(fw["capacity"]), x=_num(fw["ucs_spread"]) * _num(fw["capacity"]))
        w = w[w["x"].notna()].groupby("t")[["x", "w"]].sum()
        o["ucs_spread_mean"] = _mean(w["x"] / w["w"])
    else:
        o["margin_spread"] = o["ucs_spread_mean"] = math.nan

    # Technical change (whole run).
    design = e[e["event"] == "design"]
    adopt = e[e["event"] == "adopt"]
    orders = e[e["event"] == "order"]
    menu = set(config.MENU)
    o["designs_offered"] = int(len(design))
    for label in LABELS:
        o[f"designs_adopted_{label}"] = int((adopt["group"] == label).sum())
    o["designs_built"] = int((~orders["tech"].isin(menu) & orders["tech"].notna()).sum())
    for zone in ("both", "unit_cost", "profit_rate", "none"):
        name = {"unit_cost": "zone_conflict", "profit_rate": "zone_profit_rate"}.get(zone, f"zone_{zone}")
        o[name] = _share(int((design["cause"] == zone).sum()), len(design))
    conflict = design[(design["cause"] == "unit_cost") & (design["rule"] == "unit_cost")]
    adopted = set(zip(adopt["t"], adopt["firm_id"], adopt["tech"]))
    o["conflict_adopted_shaikh"] = _share(
        sum(k in adopted for k in zip(conflict["t"], conflict["firm_id"], conflict["tech"])),
        len(conflict))
    pr_orders = orders[(orders["rule"] == "profit_rate") & orders["other_tech"].notna()]
    o["okishio_dearer"] = _share(int((pr_orders["tech"] != pr_orders["other_tech"]).sum()),
                                 len(pr_orders))
    for label in LABELS:
        ucs = _group_series(g, label, "ucs_mean")
        kap = _group_series(g, label, "kappa_mean")
        a, b = WINDOW
        if a in ucs and b in ucs and ucs[a] > 0 and ucs[b] > 0:
            o[f"gamma_{label}"] = -math.log(ucs[b] / ucs[a]) / (b - a)
            o[f"chi_{label}"] = math.log(kap[b] / kap[a]) / (b - a)
            o[f"marx_biased_{label}"] = bool(o[f"gamma_{label}"] > 0 and o[f"chi_{label}"] > 0)
        else:
            o[f"gamma_{label}"] = o[f"chi_{label}"] = math.nan
            o[f"marx_biased_{label}"] = False
        o[f"uc_end_{label}"] = float(_num(pd.Series([last[f"unit_cost_{label}"]])).iloc[0])
        o[f"replacements_{label}"] = int(_num(g.loc[g["group"] == label, "n_replace"]).sum())
    run_p = p[p["running"].astype(bool)]
    by_tech = run_p.groupby(["tech", "t"])["capacity"].sum()
    total = run_p.groupby("t")["capacity"].sum()
    lags, n_designs = [], 0
    for tech in run_p["tech"].unique():
        if tech in menu:
            continue
        n_designs += 1
        share = by_tech.loc[tech] / total.reindex(by_tech.loc[tech].index)
        reached = share[share >= 0.5]
        if len(reached):
            lags.append(reached.index[0] - share.index[0])
    o["diffusion_lag_mean"] = float(np.mean(lags)) if lags else math.nan
    o["diffusion_reached_share"] = _share(len(lags), n_designs)
    techs = _window(run_p).groupby("t")["tech"].nunique()
    o["n_techniques_in_use_mean"] = _mean(techs)
    o["capacity_designs_share_end"] = _ratio(last["capacity_designs"], last["capacity_total"])
    alive = p[(p["t"] == t_end) & ~(p["retired"].astype(bool))]
    for label in LABELS:
        a = alive[alive["group"] == label]
        o[f"capital_age_{label}"] = _ratio((_num(a["age"]) * _num(a["capacity"])).sum(),
                                           _num(a["capacity"]).sum())

    # Finance and soundness.
    revenue = _num(mw["price_avg"]) * _num(mw["sales_total"])
    o["debt_to_sales_mean"] = _mean(_num(mw["debt"]) / revenue.where(revenue > 0))
    o["defaults"] = int((e["event"] == "default").sum())
    o["unpaid_bills_end"] = float(_num(pd.Series([last["unpaid_bills"]])).iloc[0])
    o["dividends_total"] = float(_num(m["dividends"]).sum())
    o["floor_viol_periods"] = int((_num(m["floor_viol"]) > 0).sum())
    return o


OBSERVABLE_COLUMNS: list[str] = []  # filled on first use (keys of observables())


def run_one(task: tuple) -> dict:
    """One run: (stage, cell, overrides, population, seed) -> its row."""
    stage, cell, overrides, population, seed = task
    config = configuration(overrides, population, seed)
    run_id = run.make_run_id(stage, cell, population, seed)
    industry = Industry(config)
    error = None
    start = time.perf_counter()
    try:
        industry.run()
    except Exception as exc:  # a failing check (CHECKS_RAISE) or a crash: kept as a row
        error = f"{type(exc).__name__}: {exc}"
    wall = time.perf_counter() - start
    row = run.runs_row(industry, run_id, stage, population, cell, wall)
    row["stage"] = stage
    row["overrides"] = json.dumps(overrides, sort_keys=True)
    row["error"] = error
    if error is None:
        row.update(observables(run.tables(industry, row), config))
    return row


_CODE_VERSION = None


def _init_worker(code_version: str) -> None:
    """runs_row asks git for the code version at every run; ask once per grid instead
    (the value is the same: the grid runs on one checkout)."""
    run.code_version = lambda: code_version


# --- Grid --------------------------------------------------------------------------------
def tasks_for(stage: str, cells: dict, seeds: int) -> dict:
    return {cell: [(stage, cell, overrides, population, seed)
                   for population in POPULATIONS for seed in range(1, seeds + 1)]
            for cell, (_, overrides) in cells.items()}


def finished_cells(out: Path) -> set:
    path = out / "runs.csv"
    if not path.exists():
        return set()
    done = pd.read_csv(path, usecols=["stage", "cell"], dtype=str)
    return set(zip(done["stage"], done["cell"]))


def _append(out: Path, rows: list[dict]) -> None:
    frame = pd.DataFrame(rows)
    path = out / "runs.csv"
    if path.exists():
        columns = pd.read_csv(path, nrows=0).columns
        missing = [c for c in frame.columns if c not in columns]
        if missing:
            raise RuntimeError(f"new columns not in runs.csv: {missing}")
        frame.reindex(columns=columns).to_csv(path, mode="a", header=False, index=False)
    else:
        frame.to_csv(path, index=False)


def write_parquet(out: Path) -> None:
    try:
        load_runs(out).to_parquet(out / "runs.parquet", index=False)
    except Exception as exc:  # never lose a grid over the parquet copy
        log(out, f"parquet not written: {exc}")


def load_runs(out: Path = OUT, path: Path | None = None) -> pd.DataFrame:
    return pd.read_csv(path or out / "runs.csv",
                       dtype={"stage": str, "plant_life": object}, low_memory=False)


def log(out: Path, line: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(out / "progress.log", "a") as fh:
        fh.write(f"{stamp} {line}\n")
    print(f"{stamp} {line}", flush=True)


def grid(stage: str, seeds: int, jobs: int, out: Path = OUT, resume: bool = False,
         only: list[str] | None = None, cells: dict | None = None) -> None:
    out.mkdir(parents=True, exist_ok=True)
    cells = cells if cells is not None else stage_cells(stage, out)
    if only:
        cells = {k: v for k, v in cells.items() if k in only}
    done = finished_cells(out)
    if not resume and any((stage, c) in done for c in cells):
        raise SystemExit(f"stage {stage} already has cells in {out / 'runs.csv'}: use --resume")
    todo = {c: v for c, v in cells.items() if (stage, c) not in done}
    tasks = tasks_for(stage, todo, seeds)
    flat = [t for cell in todo for t in tasks[cell]]
    log(out, f"stage {stage}: {len(todo)} cells to run ({len(cells) - len(todo)} done), "
             f"{len(flat)} runs, {jobs} jobs, seeds 1-{seeds}")
    start = time.perf_counter()
    version = run.code_version()
    results = iter(())
    pool = None
    if jobs > 1:
        pool = Pool(jobs, initializer=_init_worker, initargs=(version,))
        results = pool.imap(run_one, flat, chunksize=1)
    else:
        _init_worker(version)
        results = map(run_one, flat)
    n_done = 0
    try:
        for i, cell in enumerate(todo):
            rows = [next(results) for _ in tasks[cell]]  # imap keeps the task order
            _append(out, rows)
            n_done += len(rows)
            elapsed = time.perf_counter() - start
            remaining = elapsed / n_done * (len(flat) - n_done)
            errors = sum(r["error"] is not None for r in rows)
            log(out, f"stage {stage} cell {cell} ({i + 1}/{len(todo)}): {len(rows)} runs, "
                     f"{n_done}/{len(flat)} done, elapsed {elapsed:.0f} s, "
                     f"est. remaining {remaining:.0f} s, errors {errors}")
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    write_parquet(out)
    log(out, f"stage {stage} finished in {time.perf_counter() - start:.0f} s")


# --- Summary -----------------------------------------------------------------------------
ID_COLUMNS = {"run_id", "stage", "cell", "population", "seed", "overrides", "error"}


def observable_names(runs: pd.DataFrame) -> list[str]:
    start = list(runs.columns).index("error") + 1
    return list(runs.columns[start:])


def summarise_cell(rows: pd.DataFrame, names: list[str]) -> dict:
    ok = rows[rows["error"].isna()].copy()
    # macro writes unit_cost_{label} = 0 when the label has no producing capacity: no value
    if "uc_end_shaikh" in ok:
        share = pd.to_numeric(ok["cap_share_shaikh_end"], errors="coerce")
        ok.loc[~(share > 0), "uc_end_shaikh"] = math.nan
        ok.loc[~(share < 1), "uc_end_okishio"] = math.nan
    decided = ok[~ok["undecided"].astype(bool)]
    won = int(decided["shaikh_wins"].astype(bool).sum())
    low, high = wilson(won, len(decided))
    out = {"n_seeds": len(rows), "n_error": len(rows) - len(ok),
           "n_undecided": len(ok) - len(decided), "won": won,
           "share_won": _share(won, len(decided)), "won_low": low, "won_high": high}
    for name in names:
        values = pd.to_numeric(ok[name].map(lambda v: float(v) if isinstance(v, (bool, np.bool_)) else v),
                               errors="coerce").dropna()
        n = len(values)
        out[f"{name}_mean"] = float(values.mean()) if n else math.nan
        out[f"{name}_lo"] = float(values.quantile(0.025)) if n else math.nan
        out[f"{name}_hi"] = float(values.quantile(0.975)) if n else math.nan
        half = 1.96 * float(values.std(ddof=1)) / math.sqrt(n) if n > 1 else math.nan
        out[f"{name}_ci_lo"] = out[f"{name}_mean"] - half
        out[f"{name}_ci_hi"] = out[f"{name}_mean"] + half
    return out


def _disjoint(a_low, a_high, b_low, b_high) -> bool:
    return bool(a_low > b_high or a_high < b_low)


def summarise(out: Path = OUT, runs: pd.DataFrame | None = None) -> pd.DataFrame:
    runs = load_runs(out) if runs is None else runs
    names = [n for n in observable_names(runs) if n != "takeover_label"]
    rows = []
    for (stage, cell, population), frame in runs.groupby(["stage", "cell", "population"],
                                                         sort=False):
        rows.append({"stage": stage, "cell": cell, "population": population,
                     "overrides": frame["overrides"].iloc[0],
                     **summarise_cell(frame, names)})
    cells = pd.DataFrame(rows)
    key = cells.set_index(["stage", "cell", "population"])
    extra = {c: [] for c in ("ctrl_uc_share_won", "ctrl_pr_share_won", "gap",
                             "beyond_drift", "beyond_base")}
    for _, r in cells.iterrows():
        if r["population"] != "mixed":
            for c in extra:
                extra[c].append(math.nan if c != "beyond_drift" and c != "beyond_base" else None)
            continue
        uc = key.loc[(r["stage"], r["cell"], "all_unit_cost")]
        pr = key.loc[(r["stage"], r["cell"], "all_profit_rate")]
        extra["ctrl_uc_share_won"].append(uc["share_won"])
        extra["ctrl_pr_share_won"].append(pr["share_won"])
        extra["gap"].append(r["share_won"] - (uc["share_won"] + pr["share_won"]) / 2)
        extra["beyond_drift"].append(
            _disjoint(r["won_low"], r["won_high"], uc["won_low"], uc["won_high"])
            and _disjoint(r["won_low"], r["won_high"], pr["won_low"], pr["won_high"]))
        base = (r["stage"], "base", "mixed") if (r["stage"], "base", "mixed") in key.index \
            else ("1", "base", "mixed")
        if base in key.index and r["cell"] != "base":
            b = key.loc[base]
            extra["beyond_base"].append(_disjoint(r["won_low"], r["won_high"],
                                                  b["won_low"], b["won_high"]))
        else:
            extra["beyond_base"].append(None)
    for c, values in extra.items():
        cells[c] = values
    front = ["stage", "cell", "population", "overrides", "n_seeds", "n_error",
             "n_undecided", "won", "share_won", "won_low", "won_high", *extra]
    cells = cells[front + [c for c in cells.columns if c not in front]]
    cells.to_csv(out / "cells.csv", index=False)
    return cells


# --- Rerun -------------------------------------------------------------------------------
def rerun_args(row) -> list[str]:
    overrides = json.loads(row["overrides"])
    rules = POPULATIONS[row["population"]]
    if rules is not None:
        overrides["HURDLE_RULES"] = rules
    args = ["--experiment", str(row["stage"]), "--cell", row["cell"],
            "--population", row["population"], "--seed", str(int(row["seed"]))]
    for name, value in overrides.items():
        args += ["--set", f"{name}={value!r}" if not isinstance(value, str) else f"{name}={value}"]
    return args


def same(a, b) -> bool:
    if isinstance(a, float) and math.isnan(a):
        return isinstance(b, float) and math.isnan(b) or b is None or (
            isinstance(b, str) and b == "") or pd.isna(b)
    if pd.isna(b) if not isinstance(b, (list, dict)) else False:
        return a is None or (isinstance(a, float) and math.isnan(a))
    if isinstance(a, (bool, np.bool_)) or isinstance(b, (bool, np.bool_)):
        return bool(a) == bool(b)
    if isinstance(a, (int, float, np.number)) and isinstance(b, (int, float, np.number)):
        return float(a) == float(b)
    return str(a) == str(b)


def rerun(run_id: str, out_dir: Path | None = None, runs_path: Path | None = None,
          quiet: bool = False) -> tuple[dict, list[str]]:
    """Rerun one row of runs.csv with run.py --set; return the new row and the columns
    that differ from the stored one (wall_seconds and code_version are not compared)."""
    runs = load_runs(path=runs_path or OUT / "runs.csv")
    match = runs[runs["run_id"] == run_id]
    if match.empty:
        raise SystemExit(f"no run {run_id} in {runs_path or OUT / 'runs.csv'}")
    row = match.iloc[0]
    out_dir = out_dir or OUT / "reruns" / run_id
    args = rerun_args(row) + ["--out", str(out_dir)]
    if quiet:
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            frames = run.main(args)
    else:
        frames = run.main(args)
    new = dict(frames["runs"].iloc[0])
    config = configuration(json.loads(row["overrides"]), row["population"], int(row["seed"]))
    new.update(observables(frames, config))
    skip = {"wall_seconds", "code_version", "python_version"}
    diff = [c for c in new if c in row.index and c not in skip and not same(new[c], row[c])]
    if not quiet:
        print(f"\nrun.py {' '.join(args)}")
        print("Reproduces the row exactly." if not diff else f"Differs in: {diff}")
        print(f"Debugging report: {sys.executable} -m debug.report {out_dir}")
    return new, diff


# --- Figures -----------------------------------------------------------------------------
# Rules that are not labels get neutral colours, so that blue and orange always mean the
# labels "shaikh" and "okishio" (style.py).
RULE_COLOURS = {"real_competition": "#6250d6", "leader_follow": "#1baf7a", "anchor": "#52514e"}
PRICING_NAMES = {"real_competition": "real competition", "leader_follow": "leader-follow",
                 "anchor": "anchor"}


def cell_parameters(cells: pd.DataFrame) -> pd.DataFrame:
    """The parameters the figures read, from each cell's overrides over parameters.py."""
    base = run.configure()
    names = ["PRICING_RULE", "INVESTMENT_RULE", "BORROWING", "DEMAND_GROWTH",
             "DEMAND_TO_CAPACITY", "CHI", "TECH_CHANGE", "TECH_SET", "TECH_BIAS",
             "TECH_CONFLICT", "TECH_DRAWS"]
    rows = []
    for text in cells["overrides"]:
        o = json.loads(text)
        rows.append({n.lower(): o.get(n, getattr(base, n)) for n in names})
    out = pd.DataFrame(rows, index=cells.index)
    out["finance"] = np.where(out["investment_rule"] == "retained_earnings", "retained earnings",
                              np.where(out["borrowing"], "accelerator + debt",
                                       "accelerator, no debt"))
    out["demand"] = [("unmet" if d > 1 else "static") if g == 0 else
                     (f"growing {g:g}" if d <= 1 else f"unmet, growing {g:g}")
                     for g, d in zip(out["demand_growth"], out["demand_to_capacity"])]
    out["tech"] = [("no draws" if not draws else f"categories q={q:g}") if tc == "categories"
                   else (f"innovation set, marx {b:g}" if ts == "marx" else "innovation set, neutral")
                   for tc, ts, b, q, draws in zip(out["tech_change"], out["tech_set"],
                                                  out["tech_bias"], out["tech_conflict"],
                                                  out["tech_draws"])]
    return out


def _style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from style import RC_PARAMS
    plt.rcParams.update(RC_PARAMS)
    return plt


def _diverging():
    from matplotlib.colors import LinearSegmentedColormap
    from style import TYPE_STYLE
    return LinearSegmentedColormap.from_list(
        "okishio_shaikh", [TYPE_STYLE["okishio"]["color"], "#d9d8d4", TYPE_STYLE["shaikh"]["color"]])


def fig_tornado(cells: pd.DataFrame, path: Path) -> None:
    plt = _style()
    from style import MUTED, TYPE_STYLE
    s1 = cells[cells["stage"] == "1"]
    mixed = s1[s1["population"] == "mixed"].set_index("cell")
    order = [c for c in STAGE1 if c in mixed.index]
    factors = [STAGE1[c][0] for c in order]
    fig, ax = plt.subplots(figsize=(7.5, 0.24 * len(order) + 1.4))
    y = np.arange(len(order))[::-1]
    for yi, cell in zip(y, order):
        ctrl = s1[(s1["cell"] == cell) & (s1["population"] != "mixed")]
        ax.fill_betweenx([yi - 0.38, yi + 0.38], ctrl["won_low"].min(), ctrl["won_high"].max(),
                         color="#d9d8d4", lw=0)
        r = mixed.loc[cell]
        filled = bool(r["beyond_drift"])
        colour = TYPE_STYLE["shaikh" if r["share_won"] >= 0.5 else "okishio"]["color"]
        ax.errorbar(r["share_won"], yi, xerr=[[r["share_won"] - r["won_low"]],
                                              [r["won_high"] - r["share_won"]]],
                    fmt="o", ms=6, color=colour, mfc=colour if filled else "white",
                    lw=1.2, capsize=0)
    ax.axvline(mixed.loc["base", "share_won"], color=MUTED, ls="--", lw=1)
    ax.axvline(0.5, color=MUTED, lw=0.6)
    labels = [f"{c}  [{f}]" for c, f in zip(order, factors)]
    ax.set_yticks(y, labels, fontsize=7)
    ax.set_xlim(0, 1)
    ax.set_xlabel("share of seeds won by the label \"shaikh\" (> 1/2 of capacity at t = 199),\n"
                  "95 % Wilson interval; orange: the profit-rate rule wins most seeds")
    ax.set_title("Stage 1: which factor levels move the share of seeds won by the unit-cost rule?\n"
                 "grey: the two neutral controls' intervals; filled: beyond drift; dashed: base",
                 fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_phase(cells: pd.DataFrame, path: Path, y_mode: str = "design") -> None:
    plt = _style()
    s2 = cells[(cells["stage"] == "2") & (cells["population"] == "mixed")].copy()
    if s2.empty:
        return
    s2 = s2.join(cell_parameters(s2))
    keep = [json.loads(o).get("RBAR", 0.05) == 0.05
            and json.loads(o).get("TECH_DRAW_TIMING", "period") == "period" for o in s2["overrides"]]
    s2 = s2[keep]  # the plane at rbar 0.05 and draws per period
    pricing = list(dict.fromkeys(s2["pricing_rule"]))
    finance = list(dict.fromkeys(s2["finance"]))
    demands = list(dict.fromkeys(s2["demand"]))
    tech_order = ["categories q=0", "categories q=0.5", "innovation set, marx 0.5",
                  "innovation set, marx 1.5", "innovation set, marx 3", "innovation set, neutral"]
    techs = [t for t in tech_order if t in set(s2["tech"])] + \
        [t for t in dict.fromkeys(s2["tech"]) if t not in tech_order]
    markers = ["o", "s", "^", "D"]
    cmap = _diverging()
    fig, axes = plt.subplots(len(pricing), len(finance), figsize=(4.2 * len(finance), 3.6 * len(pricing)),
                             squeeze=False, sharex=True, sharey=True)
    chis = sorted(s2["chi"].unique())
    for i, pr in enumerate(pricing):
        for j, fi in enumerate(finance):
            ax = axes[i][j]
            sub = s2[(s2["pricing_rule"] == pr) & (s2["finance"] == fi)]
            for k, d in enumerate(demands):
                part = sub[sub["demand"] == d]
                x = np.array([chis.index(c) for c in part["chi"]], dtype=float) + (k - (len(demands) - 1) / 2) * 0.18
                if y_mode == "design":
                    yv = np.array([techs.index(t) for t in part["tech"]], dtype=float)
                else:
                    yv = part["zone_conflict_mean"].to_numpy()
                    x = x + 0.0
                beyond = part["beyond_drift"].astype(bool).to_numpy()
                sc = ax.scatter(x, yv, c=part["share_won"], cmap=cmap, vmin=0, vmax=1,
                                marker=markers[k % 4], s=70, edgecolors=np.where(beyond, "#0b0b0b", "white"),
                                linewidths=np.where(beyond, 1.2, 0.6), label=d)
            ax.set_xticks(range(len(chis)), [f"{c:g}" for c in chis])
            ax.set_xlim(-0.6, len(chis) - 0.4)
            if y_mode == "design":
                ax.set_yticks(range(len(techs)), techs, fontsize=7)
            ax.set_title(f"{PRICING_NAMES.get(pr, pr)}, {fi}", fontsize=8, loc="left")
            if i == len(pricing) - 1:
                ax.set_xlabel("selection intensity CHI")
            if j == 0 and y_mode != "design":
                ax.set_ylabel("realised conflict share of draws")
    axes[0][0].legend(title="demand", fontsize=7, title_fontsize=7, loc="best")
    fig.colorbar(sc, ax=axes, shrink=0.6, label="share of seeds won by \"shaikh\" (blue: unit cost)")
    what = "technical-change rule" if y_mode == "design" else "realised conflict share"
    fig.suptitle(f"Stage 2: where does the unit-cost rule win? Selection intensity × {what}, "
                 "per pricing and investment rule\n(rbar 0.05, draws per period; demand levels other than static only at CHI = 1; "
                 "black edge: beyond both neutral controls)",
                 fontsize=9, x=0.02, ha="left")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_channels(cells: pd.DataFrame, path: Path) -> None:
    plt = _style()
    from style import MUTED
    mixed = cells[cells["population"] == "mixed"].copy()
    mixed = mixed.join(cell_parameters(mixed))
    colours = RULE_COLOURS
    fig, ax = plt.subplots(figsize=(6.5, 5))
    for pr, part in mixed.groupby("pricing_rule"):
        ax.scatter(part["d_share_price_all_mean"], part["d_share_accum_all_mean"], s=22, alpha=0.8,
                   color=colours.get(pr, MUTED), label=PRICING_NAMES.get(pr, pr),
                   edgecolors="white", linewidths=0.5)
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.axvline(0, color=MUTED, lw=0.6)
    ax.set_xlabel("price channel: cumulated price-driven change in Shaikh's sales share, t = 0-199")
    ax.set_ylabel("accumulation channel: cumulated order/retire/cancel\nchange in Shaikh's capacity share")
    ax.legend(title="pricing rule (colour, not a label)", fontsize=7, title_fontsize=7)
    ax.set_title("Does the unit-cost rule win through prices or through accumulation?\n"
                 "one point per cell (mixed population, mean over seeds), stages 1-3",
                 fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_demand(cells: pd.DataFrame, path: Path) -> None:
    plt = _style()
    from style import MUTED
    stage = "2" if (cells["stage"] == "2").any() else "1"
    mixed = cells[(cells["population"] == "mixed") & (cells["stage"] == stage)].copy()
    mixed = mixed.join(cell_parameters(mixed))
    s1 = cells[(cells["population"] == "mixed") & (cells["stage"] == "1")].copy()
    s1 = s1.join(cell_parameters(s1))
    s1 = s1[s1["cell"].isin(["base", "grow_01", "grow_03", "unmet", "unmet_grow_02",
                             "accel_debt", "accel_cash"])]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    panels = [("unmet_share_mean", "mean unmet demand / demand, t = 100-199"),
              ("entries_w_mean", "entries per period, t = 100-199")]
    combined = pd.concat([s1, mixed[~mixed.index.isin(s1.index)]]) if stage == "2" else s1
    groups = combined.groupby(["demand", "finance"])
    finances = list(dict.fromkeys(combined["finance"]))
    demands = list(dict.fromkeys(combined["demand"]))
    shades = ["#6250d6", "#1baf7a", "#52514e"]
    for ax, (col, label) in zip(axes, panels):
        width = 0.8 / len(finances)
        for k, fi in enumerate(finances):
            vals = []
            for d in demands:
                v = combined[(combined["demand"] == d) & (combined["finance"] == fi)][col]
                vals.append(v.mean() / (100.0 if col == "entries_w_mean" else 1.0) if len(v) else np.nan)
            ax.bar(np.arange(len(demands)) + (k - (len(finances) - 1) / 2) * width, vals,
                   width * 0.92, color=shades[k % 3], label=fi)
        ax.set_xticks(range(len(demands)), demands, rotation=20, fontsize=7)
        ax.set_ylabel(label)
    axes[0].legend(title="investment rule", fontsize=7, title_fontsize=7)
    fig.suptitle("Is demand met, and how much turnover? By demand condition and investment rule\n"
                 "(mixed population, mean over cells and seeds of stages 1-2)", fontsize=9,
                 x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_price(cells: pd.DataFrame, path: Path) -> None:
    plt = _style()
    from style import MUTED
    mixed = cells[cells["population"] == "mixed"].copy()
    mixed = mixed.join(cell_parameters(mixed))
    sub = mixed[(mixed["tech_change"] == "innovation_set") & (mixed["tech_set"] == "marx")]
    colours = RULE_COLOURS
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for pr, part in sub.groupby("pricing_rule"):
        agg = part.groupby("tech_bias")[["price_to_pp_mean", "price_rise_after_adoption_mean"]].mean()
        axes[0].plot(agg.index, agg["price_to_pp_mean"], marker="o", color=colours.get(pr, MUTED),
                     label=PRICING_NAMES.get(pr, pr))
        axes[0].scatter(part["tech_bias"], part["price_to_pp_mean"], s=10, alpha=0.4,
                        color=colours.get(pr, MUTED))
        axes[1].plot(agg.index, agg["price_rise_after_adoption_mean"], marker="o",
                     color=colours.get(pr, MUTED), label=PRICING_NAMES.get(pr, pr))
    axes[0].axhline(1, color=MUTED, lw=0.6)
    axes[0].set_xlabel("median capital-using bias of the innovation set (TECH_BIAS)")
    axes[0].set_ylabel("price at t = 199 / price of production\nof the lowest-uc technique in use")
    axes[1].set_xlabel("median capital-using bias of the innovation set (TECH_BIAS)")
    axes[1].set_ylabel("share of seeds with price(199) > price(100)")
    axes[0].legend(title="pricing rule", fontsize=7, title_fontsize=7)
    fig.suptitle("Price signature: does the long-run price rise after capital-using adoptions?\n"
                 "(innovation set, marx; mixed population; line: mean over cells, dots: cells)",
                 fontsize=9, x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def fig_marx(cells: pd.DataFrame, path: Path) -> None:
    plt = _style()
    from style import MUTED, TYPE_STYLE
    mixed = cells[cells["population"] == "mixed"].copy()
    mixed = mixed.join(cell_parameters(mixed))
    family = np.where(mixed["tech_change"] == "categories",
                      np.where(mixed["tech_draws"].astype(bool), "categories", "no draws"),
                      np.where(mixed["tech_set"] == "marx", "innovation set, marx",
                               "innovation set, neutral"))
    markers = {"categories": "o", "innovation set, marx": "^", "innovation set, neutral": "s",
               "no draws": "x"}
    fig, ax = plt.subplots(figsize=(6.5, 5))
    for label in LABELS:
        for fam, mk in markers.items():
            part = mixed[family == fam]
            if part.empty:
                continue
            ax.scatter(part[f"chi_{label}_mean"] * 100, part[f"gamma_{label}_mean"] * 100,
                       marker=mk, s=24, alpha=0.75, color=TYPE_STYLE[label]["color"],
                       label=f"{TYPE_STYLE[label]['label']}, {fam}")
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.axvline(0, color=MUTED, lw=0.6)
    ax.set_xlabel("χ: realised rise of capital per unit (kappa_mean), % per period, t = 100-199")
    ax.set_ylabel("γ: realised fall of operating cost (ucs_mean), % per period")
    ax.legend(fontsize=6, ncol=1, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    ax.set_title("Is realised technical change Marx-biased (γ > 0, χ > 0), and for which rule?\n"
                 "one point per cell and label (mixed population, mean over seeds)",
                 fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def figures(out: Path = OUT) -> None:
    cells = pd.read_csv(out / "cells.csv", dtype={"stage": str}, low_memory=False)
    fdir = out / "figures"
    fdir.mkdir(parents=True, exist_ok=True)
    fig_tornado(cells, fdir / "1_tornado_stage1.png")
    fig_phase(cells, fdir / "2_phase_stage2.png", "design")
    fig_phase(cells, fdir / "2b_phase_stage2_conflict_share.png", "conflict")
    fig_channels(cells, fdir / "3_channels.png")
    fig_demand(cells, fdir / "4_demand_turnover.png")
    fig_price(cells, fdir / "5_price_signature.png")
    fig_marx(cells, fdir / "6_marx_bias.png")
    print(f"Figures saved in: {fdir}")


# --- Command line ------------------------------------------------------------------------
def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    g = sub.add_parser("grid")
    g.add_argument("--stage", required=True, choices=("1", "2", "3", "smoke"))
    g.add_argument("--seeds", type=int, default=None, help="seeds 1..N (200 / 100 / 500)")
    g.add_argument("--jobs", type=int, default=os.cpu_count())
    g.add_argument("--resume", action="store_true")
    g.add_argument("--cells", nargs="*", default=None)
    g.add_argument("--out", type=Path, default=OUT)
    s = sub.add_parser("summarise")
    s.add_argument("--out", type=Path, default=OUT)
    r = sub.add_parser("rerun")
    r.add_argument("run_id")
    r.add_argument("--out", type=Path, default=None)
    r.add_argument("--runs", type=Path, default=None, help="runs.csv to read (default OUT)")
    ch = sub.add_parser("choose3", help="choose the stage 3 cells from cells.csv")
    ch.add_argument("--out", type=Path, default=OUT)
    fg = sub.add_parser("figures")
    fg.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    if args.command == "grid":
        seeds = args.seeds or {"1": 200, "2": 100, "3": 500, "smoke": 2}[args.stage]
        grid(args.stage, seeds, args.jobs, args.out, args.resume, args.cells)
    elif args.command == "summarise":
        cells = summarise(args.out)
        mixed = cells[cells["population"] == "mixed"]
        print(mixed[["stage", "cell", "share_won", "won_low", "won_high", "ctrl_uc_share_won",
                     "ctrl_pr_share_won", "gap", "beyond_drift", "beyond_base",
                     "n_undecided"]].to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    elif args.command == "rerun":
        _, diff = rerun(args.run_id, args.out, args.runs)
        sys.exit(1 if diff else 0)
    elif args.command == "choose3":
        cells = pd.read_csv(args.out / "cells.csv", dtype={"stage": str}, low_memory=False)
        for name, spec in choose_stage3(cells, args.out).items():
            print(f"{name}: {spec['why']} {spec['overrides']}")
    elif args.command == "figures":
        figures(args.out)


if __name__ == "__main__":
    main()
