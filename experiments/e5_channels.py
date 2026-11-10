"""E5: through which channel does a label win? No run of the harness: it reads E4 and E3
(v4-plan.md, section 9; v4-choices.md, decision 22).

    python3 -m experiments.e5_channels [folder]

It writes three tables in <folder>/E5/, where folder is outputs by default:

  decompositions.csv  E4, mixed population, cell by cell: the share won, the change in the
                      capacity share by flow and in the sales share by channel
  regression.csv      E4, mixed population: the gap in realised rates between the labels
                      regressed on the share of the profit-rate label's orders that are not
                      the cheapest, with an effect for each cell (H6)
  lambda.csv          E3 at lambda = 0 and 1, by price rule: the share won, those orders, the
                      realised rates, the hurdle, and the spread of hurdles across the firms
                      of the profit-rate label, read on a few runs of the viewer (H5)
"""
import csv
import pathlib
import sys
from dataclasses import replace
from math import fsum, sqrt

from experiments.cells import EXPERIMENTS, THREE_RULES
from experiments.harness import write_csv
from experiments.show_run import trace
from parameters import Parameters

DECOMPOSITION = ("share_won", "won_low", "won_high", "beyond_drift", "cap_share_end",
                 "dk_accumulation", "dk_entry", "dk_exit", "ds_price", "ds_entry_exit",
                 "ds_rationing", "rate_gap", "okishio_dearer", "hurdle_okishio")
LAMBDA = ("share_won", "won_low", "won_high", "beyond_drift", "okishio_dearer", "rate_shaikh",
          "rate_okishio", "rate_gap", "hurdle_okishio")
SPREAD_SEEDS = 20


def read(path) -> list[dict]:
    with open(path, newline="") as file:
        return list(csv.DictReader(file))


def slope_with_cell_effects(rows: list[dict], x: str, y: str) -> dict:
    """The slope of y on x once each cell has its own intercept: both are measured from
    their mean in the cell. Returns the slope, its standard error and the counts."""
    groups = {}
    for row in rows:
        if row[x] not in ("", None) and row[y] not in ("", None):
            groups.setdefault(row["cell"], []).append((float(row[x]), float(row[y])))
    centred = []
    for pairs in groups.values():
        mean_x = fsum(a for a, _ in pairs) / len(pairs)
        mean_y = fsum(b for _, b in pairs) / len(pairs)
        centred += [(a - mean_x, b - mean_y) for a, b in pairs]
    spread = fsum(a * a for a, _ in centred)
    slope = fsum(a * b for a, b in centred) / spread
    residual = fsum((b - slope * a) ** 2 for a, b in centred)
    freedom = len(centred) - len(groups) - 1
    return {"slope": slope, "se": sqrt(residual / freedom / spread), "runs": len(centred),
            "cells": len(groups)}


def hurdle_spread(overrides: dict, seeds: int = SPREAD_SEEDS) -> float:
    """The spread of hurdles across the firms of the profit-rate label: the standard
    deviation over those firms in a period, averaged over the periods that have at least
    two of them and over the seeds."""
    params = replace(Parameters(), **overrides)
    spreads = []
    for seed in range(seeds):
        by_period = {}
        for row in trace(params, seed)[1]:
            if row["label"] == "okishio" and row["hurdle"] is not None:
                by_period.setdefault(row["t"], []).append(row["hurdle"])
        for hurdles in by_period.values():
            if len(hurdles) > 1:
                mean = fsum(hurdles) / len(hurdles)
                spreads.append(sqrt(fsum((h - mean) ** 2 for h in hurdles) / len(hurdles)))
    return fsum(spreads) / len(spreads)


def main(folder: str = "outputs", spread_seeds: int = SPREAD_SEEDS) -> pathlib.Path:
    folder = pathlib.Path(folder)
    target = folder / "E5"
    target.mkdir(parents=True, exist_ok=True)

    cells = [row for row in read(folder / "E4" / "cells.csv") if row["population"] == "mixed"]
    table = [{"cell": row["cell"], **{name: row[name] for name in DECOMPOSITION}}
             for row in cells]
    write_csv(target / "decompositions.csv", table, ["cell", *DECOMPOSITION])

    runs = [row for row in read(folder / "E4" / "runs.csv")
            if row["population"] == "mixed" and not row["error"]]
    samples = {"all cells": runs}
    for part in ("rbar0.16", "rbar0.1", "marx", "categories", "retained", "accelerator"):
        samples[part] = [row for row in runs if part in row["cell"].split("_")
                         or row["cell"].endswith(part)]
    regression = [{"sample": name, **slope_with_cell_effects(rows, "okishio_dearer", "rate_gap")}
                  for name, rows in samples.items()]
    write_csv(target / "regression.csv", regression, list(regression[0]))

    e3 = {row["cell"]: row for row in read(folder / "E3" / "cells.csv")
          if row["population"] == "mixed"}
    by_lambda = []
    for rule in THREE_RULES:
        for lam in ("0", "1"):
            cell = f"lam_{lam}_{rule}"
            spread = hurdle_spread(EXPERIMENTS["E3"][cell]["overrides"], spread_seeds)
            by_lambda.append({"cell": cell, **{name: e3[cell][name] for name in LAMBDA},
                              "hurdle_spread_across_firms": spread})
    write_csv(target / "lambda.csv", by_lambda, list(by_lambda[0]))
    return target


if __name__ == "__main__":
    print(main(*sys.argv[1:2]))
