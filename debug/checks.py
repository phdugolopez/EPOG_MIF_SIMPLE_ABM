"""Are the accounts and the bookkeeping sound? One panel per check residual.

    python -m debug.checks RUN_DIR

Each panel shows |residual| + 1e-18 against time on a log scale, the tolerance the
collector used as a dashed line and failing periods in red. Prints the first failing
period, the check and, where the tables say, the firm. Run it first whenever something
looks odd.
"""

import math

import matplotlib.pyplot as plt
import pandas as pd

from debug._common import FAIL, INK, MUTED, run_script, shade_wars

FLOOR = 1e-18
SHARE_TOL = 1e-12

# column -> (title, kind): money checks use check_tol, quantity checks 1e-9 max(1, demand),
# share checks 1e-12, counts fail from 1.
CHECKS = {
    "money_resid": ("money conserved", "money"),
    "debt_resid": ("debt = loans", "money"),
    "nw_resid": ("net worth identity (worst firm)", "money"),
    "tfm_row_resid": ("flow matrix rows (worst)", "money"),
    "tfm_col_resid": ("flow matrix columns vs cash (worst)", "money"),
    "share_resid_demand": ("shares sum to 1 after step 2", "share"),
    "share_resid_end": ("shares sum to 1 after step 6", "share"),
    "share_min": ("negative share (step 2 or 6)", "negative"),
    "sales_resid": ("sales + unserved = demand", "quantity"),
    "cap_resid": ("capacity identity", "quantity"),
    "cap_resid_group": ("capacity identity (worst group)", "quantity"),
    "util_max_viol": ("firms above u_max capacity", "count"),
    "floor_viol": ("firms priced below their floor", "count"),
}


def tolerance(macro: pd.DataFrame, kind: str) -> pd.Series:
    if kind == "money":
        return macro["check_tol"]
    if kind == "quantity":
        return 1e-9 * macro["demand"].clip(lower=1.0)
    if kind in ("share", "negative"):
        return pd.Series(SHARE_TOL, index=macro.index)
    return pd.Series(0.5, index=macro.index)


def magnitude(macro: pd.DataFrame, column: str, kind: str) -> pd.Series:
    values = macro[column].astype(float)
    if kind == "negative":
        return (-values).clip(lower=0.0)
    return values.abs()


def failures(macro: pd.DataFrame) -> pd.DataFrame:
    """One row per (period, check) that fails, in time order."""
    rows = []
    for column, (title, kind) in CHECKS.items():
        if column not in macro:
            continue
        bad = magnitude(macro, column, kind) > tolerance(macro, kind)
        for t, value in zip(macro["t"][bad], macro[column][bad]):
            rows.append({"t": t, "check": column, "title": title, "value": value})
    return pd.DataFrame(rows, columns=["t", "check", "title", "value"]).sort_values(
        ["t", "check"], kind="stable")


def culprit(run, t: int, check: str) -> str:
    """The firm(s) behind a failing firm-level check, recomputed from the firms table."""
    firms = run.tables.get("firms")
    if firms is None:
        return "—"
    now = firms[firms["t"] == t]
    if check == "floor_viol":
        bad = now[(now["n_plants"] > 0) & (now["price"] < now["p_floor"]
                                           - 1e-9 * now["p_floor"].clip(lower=1.0))]
    elif check == "util_max_viol":
        u_max = run.param("u_max")
        bad = now[now["output"] > u_max * now["capacity"] * (1 + 1e-9) + 1e-9]
    elif check == "nw_resid":
        before = firms[firms["t"] == t - 1].set_index("firm_id")["net_worth"]
        rows = now[(now["born"] < t) & ~now["exited"].astype(bool)
                   & now["firm_id"].isin(before.index)]
        change = rows["net_worth"] - rows["firm_id"].map(before)
        resid = change - (rows["profit"] - rows["dividends"] - rows["write_off"])
        if resid.empty:
            return "—"
        return f"firm {int(rows.loc[resid.abs().idxmax(), 'firm_id'])}"
    else:
        return "industry"
    ids = sorted(int(i) for i in bad["firm_id"])
    return "firm " + ", ".join(map(str, ids)) if ids else "—"


def figures(run):
    macro = run.macro
    present = [c for c in CHECKS if c in macro]
    ncols = 3
    nrows = math.ceil(len(present) / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(11, 2.2 * nrows), sharex=True,
                             squeeze=False)
    t = macro["t"]
    for ax, column in zip(axes.flat, present):
        title, kind = CHECKS[column]
        y = magnitude(macro, column, kind) + FLOOR
        tol = tolerance(macro, kind)
        bad = y - FLOOR > tol
        shade_wars(ax, run)
        ax.plot(t, y, color=INK, linewidth=1)
        ax.scatter(t[bad], y[bad], color=FAIL, s=12, zorder=4)
        ax.plot(t, tol, color=MUTED, linestyle="--", linewidth=1)
        ax.set_yscale("log")
        ax.set_title(f"{title}\n{column}" + (f": {int(bad.sum())} failing" if bad.any()
                                              else ""),
                     fontsize=8, color=FAIL if bad.any() else INK)
    for ax in list(axes.flat)[len(present):]:
        ax.set_visible(False)
    for ax in axes[-1]:
        ax.set_xlabel("Period")
    fails = failures(macro)
    verdict = "no check fails" if fails.empty else (
        f"first failure at t = {fails.iloc[0]['t']}: {fails.iloc[0]['check']}")
    fig.suptitle(f"Are the accounts and the bookkeeping sound? ({run.name}: {verdict})",
                 fontsize=10)
    fig.tight_layout()
    return [("checks", fig)]


def report(run) -> str:
    fails = failures(run.macro)
    if fails.empty:
        n = len(run.macro)
        return f"All checks pass in the {n} periods of {run.name}."
    first = fails.iloc[0]
    where = culprit(run, int(first["t"]), first["check"])
    return (f"First failure: t = {first['t']}, check {first['check']} ({first['title']}), "
            f"value {first['value']:.3e}, {where}. {len(fails)} failing (period, check) "
            f"pairs in {fails['t'].nunique()} periods.")


def _figures_and_report(run):
    print(report(run))
    return figures(run)


def main(argv=None):
    return run_script(__doc__, _figures_and_report, argv=argv)


if __name__ == "__main__":
    main()
