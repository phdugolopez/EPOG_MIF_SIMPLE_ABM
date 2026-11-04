"""Indicators computed after the run from the stored tables (collector brief, section 4).

Each function takes the tables as written by run.py (pandas DataFrames) and never reads
the model. Only the exact decompositions of sections 4.2 and 4.3 are written so far.
"""

import pandas as pd

# Flows of the capacity identity, with the sign they enter K_{g,t+1}.
CAPACITY_FLOWS = {"ordered": 1.0, "retired": -1.0, "entry": 1.0, "exit": -1.0,
                  "cancelled": -1.0}


def _sorted(groups: pd.DataFrame) -> pd.DataFrame:
    return groups.sort_values(["t", "group"]).reset_index(drop=True)


def _neighbour(g: pd.DataFrame, column: str, lag: int) -> pd.Series:
    """column of the same group lag rows away (lag = -1: next period, 1: previous),
    NaN where that row is not period t - lag."""
    by_group = g.groupby("group", sort=False)
    t = by_group["t"].shift(lag)
    return by_group[column].shift(lag).where(t == g["t"] - lag)


def capacity_share_terms(groups: pd.DataFrame) -> pd.DataFrame:
    """Section 4.2: the change in each group's capacity share, split by flow.

    S_{g,t} = K_{g,t} / K_t with K producing capacity at the start of t (`capacity`);
    K_{g,t+1} is next period's row, or `capacity_next` in the last period. For each flow
    c in ordered, -retired, entry, -exit, -cancelled:

        term_c = (D^c K_{g,t} - S_{g,t} D^c K_t) / K_{t+1},

    and the terms sum to S_{g,t+1} - S_{g,t} exactly when the capacity identity holds.
    `resid` is d_share_k minus the sum of the terms.
    """
    g = _sorted(groups)
    by_t = g.groupby("t")
    k_next_g = _neighbour(g, "capacity", -1).fillna(g["capacity_next"])
    k = by_t["capacity"].transform("sum")
    k_next = k_next_g.groupby(g["t"]).transform("sum")
    out = g[["t", "group"]].copy()
    if "rule" in g:
        out["rule"] = g["rule"]
    out["share_k"] = (g["capacity"] / k).where(k > 0.0)
    out["share_k_next"] = (k_next_g / k_next).where(k_next > 0.0)
    out["d_share_k"] = out["share_k_next"] - out["share_k"]
    total = 0.0
    for flow, sign in CAPACITY_FLOWS.items():
        column = f"cap_{flow}"
        term = sign * (g[column] - out["share_k"] * by_t[column].transform("sum")) / k_next
        out[f"term_{flow}"] = term.where(k_next > 0.0)
        total = total + out[f"term_{flow}"]
    out["resid"] = out["d_share_k"] - total
    return out


def sales_share_terms(groups: pd.DataFrame) -> pd.DataFrame:
    """Section 4.3: the change in each group's sales share, split in three.

    sigma = the group's share of sales, f = its replicator share (`share_demand`, step 2)
    and f_end its share after entry and exit (`share_end`, step 6):

        sigma_t - sigma_{t-1} = (f_t - f_end_{t-1})                       price-driven
                              + (f_end_{t-1} - f_{t-1})                   entry and exit
                              + ((sigma_t - f_t) - (sigma_{t-1} - f_{t-1}))   rationing

    NaN in the first period of each group. `resid` is d_sales_share minus the terms.
    """
    g = _sorted(groups)
    sales = g.groupby("t")["sales"].transform("sum")
    g = g.assign(sales_share=(g["sales"] / sales).where(sales > 0.0))
    sigma_prev = _neighbour(g, "sales_share", 1)
    f_prev = _neighbour(g, "share_demand", 1)
    f_end_prev = _neighbour(g, "share_end", 1)
    out = g[["t", "group"]].copy()
    if "rule" in g:
        out["rule"] = g["rule"]
    out["sales_share"] = g["sales_share"]
    out["d_sales_share"] = g["sales_share"] - sigma_prev
    out["term_price"] = g["share_demand"] - f_end_prev
    out["term_entry_exit"] = f_end_prev - f_prev
    out["term_rationing"] = (g["sales_share"] - g["share_demand"]) - (sigma_prev - f_prev)
    out["resid"] = out["d_sales_share"] - (
        out["term_price"] + out["term_entry_exit"] + out["term_rationing"]
    )
    return out


def cumulate(terms: pd.DataFrame, start: int = 0) -> pd.DataFrame:
    """Sum of each term column per group from period `start` on (one bar per run);
    NaN terms (first period, empty industry) count as zero."""
    columns = [c for c in terms.columns if c.startswith("term_")]
    kept = terms[terms["t"] >= start]
    return kept.groupby("group")[columns].sum()
