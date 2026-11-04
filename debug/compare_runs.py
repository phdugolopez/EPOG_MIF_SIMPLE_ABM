"""Where do two runs diverge? Column by column, period by period.

    python -m debug.compare_runs RUN_A RUN_B [--swap-labels] [--tol 1e-12] [--out DIR]

For each table (macro, groups, firms, plants, events, flows) and each column the two runs
share, the largest absolute difference per period, rows matched on their keys: (t) for
macro, (t, group) for groups, (t, firm_id) for firms, (t, plant_id) for plants, (t, step,
event, firm_id, plant_id, n-th such row) for events and (t, item) for flows. Text columns
count as different (inf) when they differ; NaN equals NaN; a row found in one run only
counts under the pseudo-column "(rows)". run_id and the runs table are not compared.

--swap-labels exchanges the two labels in RUN_B before comparing: the values of type,
firm_type and group, and the label tokens in column names (share_shaikh <->
share_okishio). rule is left as it is, so that a run with swapped labels and swapped
hurdle mapping must come out identical: the label-swap test on every table.

Tables written before the brief's names (the reference run of commit 49f7974: time,
mean_price, book_value, ...) are renamed to the current names first.

Output: a heatmap of the columns x periods where the difference exceeds --tol, written
to --out (default RUN_A/debug), and the first divergence printed (period, table, column,
firm). Exit status 1 when the runs differ.
"""

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from debug._common import INK, load

KEYS = {
    "macro": ["t"],
    "groups": ["t", "group"],
    "firms": ["t", "firm_id"],
    "plants": ["t", "plant_id"],
    "events": ["t", "step", "event", "firm_id", "plant_id", "_n"],
    "flows": ["t", "item"],
}
LABEL_COLUMNS = ("type", "firm_type", "group")
ROWS = "(rows)"

# Names before the collector used the brief's (collector-plan.md, D1).
LEGACY = {
    "macro": {"time": "t", "sales": "sales_total", "unserved": "unmet_total",
              "capacity": "capacity_total", "mean_price": "price_avg",
              "leader_price": "price_lead", "n_at_war": "n_cutting",
              "investment": "invest_total", "roe_cash": "roe_balance"},
    "firms": {"time": "t", "at_war": "cutting", "profit_rate": "r_avg",
              "write_offs": "write_off", "investment": "invest_spend",
              "book_value": "k_book", "exit_reason": "exit_cause"},
    "plants": {"time": "t", "technique": "tech", "book_value": "k_book",
               "periods_below_cost": "below_cost"},
    "flows": {"time": "t"},
}


def modernise(table: str, frame: pd.DataFrame) -> pd.DataFrame:
    if "time" in frame and "t" not in frame:
        return frame.rename(columns=LEGACY.get(table, {"time": "t"}))
    return frame


def labels_of(run) -> list[str]:
    for table, column in (("groups", "group"), ("firms", "group"), ("firms", "type")):
        frame = run.tables.get(table)
        if frame is not None and column in frame:
            return sorted(frame[column].dropna().unique())
    return []


def swap_labels(table: str, frame: pd.DataFrame, pair) -> pd.DataFrame:
    a, b = pair
    swap = {a: b, b: a}
    frame = frame.copy()
    for column in LABEL_COLUMNS:
        if column in frame:
            frame[column] = frame[column].map(lambda v: swap.get(v, v))
    frame.columns = ["_".join(swap.get(tok, tok) for tok in str(c).split("_"))
                     for c in frame.columns]
    return frame


def _prepare(table: str, frame: pd.DataFrame) -> pd.DataFrame:
    frame = modernise(table, frame).drop(columns=["run_id"], errors="ignore").copy()
    for column in frame.columns:  # empty text reads as NaN from CSV, "" from the model
        if not (pd.api.types.is_numeric_dtype(frame[column])
                or pd.api.types.is_bool_dtype(frame[column])):
            frame[column] = frame[column].fillna("").astype(str)
    if table == "events":
        base = [k for k in KEYS["events"] if k != "_n"]
        frame["_n"] = frame.groupby(base, sort=False).cumcount()
    return frame


def _diff(a: pd.Series, b: pd.Series) -> np.ndarray:
    """|a - b| per row: NaN = NaN gives 0, a number against NaN or unequal text inf."""
    both_na = a.isna().to_numpy() & b.isna().to_numpy()
    numeric = (pd.api.types.is_numeric_dtype(a) or pd.api.types.is_bool_dtype(a)) and (
        pd.api.types.is_numeric_dtype(b) or pd.api.types.is_bool_dtype(b))
    if numeric:
        x, y = a.astype(float).to_numpy(), b.astype(float).to_numpy()
        with np.errstate(invalid="ignore"):
            d = np.abs(x - y)
        d[np.isnan(d)] = np.inf
        d[np.isinf(x) & np.isinf(y) & (x == y)] = 0.0
    else:
        d = np.where(a.astype(str).to_numpy() == b.astype(str).to_numpy(), 0.0, np.inf)
    d[both_na] = 0.0
    return d


@dataclass
class Comparison:
    tol: float
    diffs: dict = field(default_factory=dict)  # table -> DataFrame (t x column), max |d|
    only_a: dict = field(default_factory=dict)  # table -> columns found in A only
    only_b: dict = field(default_factory=dict)
    first: dict | None = None  # the first divergence

    @property
    def identical(self) -> bool:
        return self.first is None

    def diverging(self) -> pd.DataFrame:
        """Rows table.column, columns periods, only where some period exceeds tol."""
        parts = []
        for table, frame in self.diffs.items():
            bad = frame.loc[:, (frame > self.tol).any()]
            parts += [bad[c].rename(f"{table}.{c}") for c in bad.columns]
        return pd.concat(parts, axis=1).T if parts else pd.DataFrame()


def compare_table(table: str, a: pd.DataFrame, b: pd.DataFrame, tol: float, result):
    keys = KEYS[table]
    a, b = _prepare(table, a), _prepare(table, b)
    keys = [k for k in keys if k in a and k in b]
    common = [c for c in a.columns if c in b.columns and c not in keys]
    result.only_a[table] = [c for c in a.columns if c not in b.columns]
    result.only_b[table] = [c for c in b.columns if c not in a.columns]
    merged = a[keys + common].merge(b[keys + common], on=keys, how="outer",
                                    suffixes=("__a", "__b"), indicator=True)
    per_row = {c: _diff(merged[f"{c}__a"], merged[f"{c}__b"]) for c in common}
    per_row[ROWS] = np.where(merged["_merge"] == "both", 0.0, np.inf)
    rows = pd.DataFrame(per_row)
    rows["t"] = merged["t"].to_numpy()
    by_t = rows.groupby("t").max()
    result.diffs[table] = by_t
    bad = by_t > tol
    if not bad.to_numpy().any():
        return
    t = int(by_t.index[bad.any(axis=1)].min())
    column = next(c for c in by_t.columns if bad.at[t, c])
    hit = merged[(merged["t"] == t) & (rows[column].to_numpy() > tol)].iloc[0]
    where = {k: hit[k] for k in keys if k not in ("t", "_n")}
    first = {"t": t, "table": table, "column": column, "where": where}
    if column != ROWS:
        first["a"], first["b"] = hit[f"{column}__a"], hit[f"{column}__b"]
    if result.first is None or t < result.first["t"]:
        result.first = first


def compare(run_a, run_b, swap: bool = False, tol: float = 1e-12) -> Comparison:
    result = Comparison(tol)
    pair = None
    if swap:
        labels = labels_of(run_b)
        if len(labels) != 2:
            raise SystemExit(f"--swap-labels needs two labels, {run_b.path} has {labels}")
        pair = labels
    for table in KEYS:
        a, b = run_a.tables.get(table), run_b.tables.get(table)
        if a is None or b is None:
            continue
        if pair:
            b = swap_labels(table, modernise(table, b), pair)
        compare_table(table, a, b, tol, result)
    return result


def describe(result: Comparison, name_a: str, name_b: str) -> str:
    lines = []
    for side, cols in (("only in " + name_a, result.only_a), ("only in " + name_b,
                                                               result.only_b)):
        listed = {t: c for t, c in cols.items() if c}
        if listed:
            lines.append(f"Columns {side}: " + "; ".join(
                f"{t}: {', '.join(c)}" for t, c in listed.items()))
    if result.identical:
        lines.append(f"Identical: every shared column of every table within {result.tol:g}.")
        return "\n".join(lines)
    f = result.first
    where = ", ".join(f"{k} {v}" for k, v in f["where"].items()) or "industry"
    values = f" ({f['a']!r} against {f['b']!r})" if "a" in f else ""
    lines.append(f"First divergence: t = {f['t']}, table {f['table']}, column "
                 f"{f['column']}, {where}{values}.")
    diverging = result.diverging()
    lines.append(f"{len(diverging)} columns differ somewhere: " + ", ".join(diverging.index))
    return "\n".join(lines)


def figure(result: Comparison, name_a: str, name_b: str, swap: bool):
    diverging = result.diverging()
    title = f"Where do {name_a} and {name_b}{' (labels swapped)' if swap else ''} diverge?"
    if diverging.empty:
        fig, ax = plt.subplots(figsize=(7, 2))
        ax.axis("off")
        ax.text(0.5, 0.5, f"No difference above {result.tol:g} in any shared column.",
                ha="center", va="center", color=INK)
        ax.set_title(title, fontsize=10)
        return fig
    values = diverging.where(diverging > result.tol)
    finite = values.replace(np.inf, np.nan)
    top = np.log10(finite.max().max()) if finite.notna().any().any() else 0.0
    shown = np.log10(values.clip(lower=result.tol)).replace(np.inf, top + 1)
    fig, ax = plt.subplots(figsize=(10, 1.5 + 0.18 * len(shown)))
    periods = shown.columns.to_numpy()
    image = ax.imshow(shown.to_numpy(dtype=float), aspect="auto", cmap="magma_r",
                      interpolation="nearest",
                      extent=(periods.min() - 0.5, periods.max() + 0.5, len(shown) - 0.5,
                              -0.5))
    ax.set_yticks(range(len(shown)), shown.index, fontsize=6)
    ax.grid(False)
    ax.set_xlabel("Period")
    fig.colorbar(image, ax=ax, pad=0.01,
                 label="log10 max |difference| (top = text, rows or NaN)")
    f = result.first
    ax.set_title(f"{title}\nfirst: t = {f['t']}, {f['table']}.{f['column']}", fontsize=9)
    fig.tight_layout()
    return fig


def main(argv=None) -> Comparison:
    p = argparse.ArgumentParser(description=__doc__.strip().split("\n\n")[0])
    p.add_argument("run_a", type=Path)
    p.add_argument("run_b", type=Path)
    p.add_argument("--swap-labels", action="store_true")
    p.add_argument("--tol", type=float, default=1e-12)
    p.add_argument("--out", type=Path, help="folder of the PNG (default RUN_A/debug)")
    args = p.parse_args(argv)
    run_a, run_b = load(args.run_a), load(args.run_b)
    result = compare(run_a, run_b, args.swap_labels, args.tol)
    print(describe(result, run_a.name, run_b.name))
    out = args.out or run_a.out_dir()
    out.mkdir(parents=True, exist_ok=True)
    fig = figure(result, run_a.name, run_b.name, args.swap_labels)
    suffix = "_swapped" if args.swap_labels else ""
    path = out / f"compare_{run_a.name}_vs_{run_b.name}{suffix}.png"
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(path)
    return result


if __name__ == "__main__":
    sys.exit(0 if main().identical else 1)
