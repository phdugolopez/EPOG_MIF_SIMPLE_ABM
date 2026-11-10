"""Runs an experiment: cells x populations x seeds, in parallel, one industry per process.

    python3 -m experiments.harness E1 [--seeds 500] [--jobs 10] [--resume] [--keep-periods 0,1]

outputs/<experiment>/runs.csv is the log, one row a run in the order cell, population, seed
whatever the number of workers; the rows of a (cell, population) are appended when its last
seed returns. cells.csv, one row per (cell, population), is rebuilt after each append.
--resume keeps the complete (cell, population) groups of runs.csv and runs what is missing.
--keep-periods also writes the period table of the seeds named. Standard library only.
"""
import argparse
import csv
import json
import multiprocessing
import os
import pathlib
import subprocess
import time
from dataclasses import replace

from experiments.cells import EXPERIMENTS
from experiments.populations import CONTROLS, POPULATIONS
from experiments.stats import beyond_drift, mean_interval, wilson
from experiments.summary import run_row
from model.model import run
from parameters import Parameters

META = ("experiment", "cell", "population", "seed", "overrides", "commit")
TEXT = META + ("outcome", "takeover_label", "error")


def write_csv(path: pathlib.Path, rows: list[dict], columns: list[str],
              append: bool = False) -> None:
    """Write rows with a fixed header; a new file goes through a temporary file."""
    target = path if append else path.with_suffix(".tmp")
    with open(target, "a" if append else "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns, restval="", extrasaction="ignore")
        if not append or file.tell() == 0:
            writer.writeheader()
        writer.writerows(rows)
    if not append:
        os.replace(target, path)


def run_one(task: dict) -> dict:
    """One run in a worker: its run row, or a row with `error` set, which counts in no
    share."""
    start = time.perf_counter()
    row = {key: task[key] for key in ("experiment", "cell", "population", "seed", "commit")}
    row["overrides"] = json.dumps(task["overrides"], sort_keys=True)
    try:
        params = replace(Parameters(), **task["overrides"])
        industry = run(params, task["seed"])
        row.update(run_row(industry.rows, params, task["seed"], task["mutant"]), error="")
        if task["periods_file"]:
            write_csv(pathlib.Path(task["periods_file"]), industry.rows, list(industry.rows[0]))
    except Exception as exception:      # the run is reported, the experiment goes on
        row["error"] = f"{type(exception).__name__}: {exception}"
    row["wall_s"] = round(time.perf_counter() - start, 4)
    return row


def columns() -> list[str]:
    """The header of runs.csv: the columns of the run row, between the run's identity and
    its wall time and error."""
    template = replace(Parameters(), periods=2)
    row = run_row(run(template, 0).rows, template, 0)
    return list(META) + [key for key in row if key != "seed"] + ["wall_s", "error"]


def number(value) -> float | None:
    """A cell of runs.csv as a number: None when empty or not a number, 1 or 0 for a
    boolean."""
    if value in ("", None):
        return None
    if value in (True, "True"):
        return 1.0
    if value in (False, "False"):
        return 0.0
    try:
        return float(value)
    except ValueError:
        return None


def summarise(runs: list[dict], header: list[str]) -> list[dict]:
    """cells.csv: per (cell, population) the seeds won, lost and tied by the unit-cost
    label, the share won (ties apart) with its Wilson interval, and the mean of every numeric
    column with its 95 % interval. The mean of a column of true and false is the share of
    seeds in which it is true. Mixed rows add the controls' shares, the gap to their mean and
    whether the share won is beyond drift."""
    groups = {}
    for row in runs:
        groups.setdefault((row["cell"], row["population"]), []).append(row)
    cells = {}
    for (cell, population), group in groups.items():
        done = [row for row in group if not row["error"]]
        tally = {key: sum(row["outcome"] == key for row in done)
                 for key in ("win", "loss", "tie", "undecided")}
        decided = tally["win"] + tally["loss"]
        low, high = wilson(tally["win"], decided)
        out = {"cell": cell, "population": population, "n_seeds": len(group),
               "n_error": len(group) - len(done), "n_undecided": tally["undecided"],
               "won": tally["win"], "lost": tally["loss"], "tied": tally["tie"],
               "share_won": tally["win"] / decided if decided else "",
               "won_low": low, "won_high": high}
        for column in header:
            if column not in TEXT:
                values = [value for value in (number(row[column]) for row in done)
                          if value is not None]
                mean, mean_low, mean_high = mean_interval(values)
                out[column] = mean
                out[column + "_low"] = mean_low
                out[column + "_high"] = mean_high
        cells[cell, population] = out
    for (cell, population), out in cells.items():
        controls = [cells.get((cell, control)) for control in CONTROLS]
        if population == "mixed" and all(controls) and out["share_won"] != "":
            shares = [control["share_won"] for control in controls]
            out["ctrl_uc_share_won"], out["ctrl_pr_share_won"] = shares
            if "" not in shares:
                out["gap"] = out["share_won"] - sum(shares) / 2
            out["beyond_drift"] = beyond_drift(
                (out["won_low"], out["won_high"]),
                *((control["won_low"], control["won_high"]) for control in controls))
    return list(cells.values())


def cell_columns(header: list[str]) -> list[str]:
    numeric = [column for column in header if column not in TEXT]
    return (["cell", "population", "n_seeds", "n_error", "n_undecided", "won", "lost", "tied",
             "share_won", "won_low", "won_high", "ctrl_uc_share_won", "ctrl_pr_share_won",
             "gap", "beyond_drift"]
            + [column + suffix for column in numeric for suffix in ("", "_low", "_high")])


def commit() -> str:
    """The short hash of the commit the runs are made on, with + if the tree has changes."""
    try:
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                               text=True, check=True).stdout.strip()
        return head + ("+" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return ""


def groups_of(experiment: dict, seeds: int | None) -> list[tuple[str, str, int, dict]]:
    """The (cell, population) groups of an experiment in their order, each with its number
    of seeds and its cell. `seeds` replaces the number of every cell when it is given."""
    return [(cell, population, seeds or spec["seeds"], spec)
            for cell, spec in experiment.items() for population in spec["populations"]]


def run_experiment(name: str, seeds: int | None = None, jobs: int = 1, resume: bool = False,
                   keep_periods: tuple = (), folder: pathlib.Path | None = None,
                   experiments: dict = EXPERIMENTS, quiet: bool = False) -> pathlib.Path:
    """Run every (cell, population, seed) of the experiment that runs.csv does not hold yet,
    and return the folder of its files."""
    groups = groups_of(experiments[name], seeds)
    sizes = {(cell, population): size for cell, population, size, _ in groups}
    folder = pathlib.Path(folder or pathlib.Path("outputs") / name)
    folder.mkdir(parents=True, exist_ok=True)
    runs_file = folder / "runs.csv"
    header = columns()

    # With --resume, the groups of runs.csv that have all their seeds are kept.
    runs = []
    if resume and runs_file.exists():
        with open(runs_file, newline="") as file:
            logged = {}
            for row in csv.DictReader(file):
                logged.setdefault((row["cell"], row["population"]), []).append(row)
        runs = [row for key, group in logged.items() if len(group) == sizes.get(key)
                for row in group]
    write_csv(runs_file, runs, header)
    held = {(row["cell"], row["population"]) for row in runs}

    # One task a run, in the order cell, population, seed.
    version = commit()
    todo = [group for group in groups if (group[0], group[1]) not in held]
    tasks = [
        {"experiment": name, "cell": cell, "population": population, "seed": seed,
         "overrides": {**spec["overrides"], **POPULATIONS[population]}, "commit": version,
         "mutant": spec.get("mutant"),
         "periods_file": (str(folder / f"periods_{cell}_{population}_{seed}.csv")
                          if seed in keep_periods else "")}
        for cell, population, size, spec in todo for seed in range(size)]

    # The rows come back in the order of the tasks; a group is written when it is complete.
    start = time.perf_counter()
    with multiprocessing.get_context("spawn").Pool(jobs) as pool:
        results = pool.imap(run_one, tasks, chunksize=8)
        for cell, population, size, _ in todo:
            group = [next(results) for _ in range(size)]
            write_csv(runs_file, group, header, append=True)
            runs += group
            write_csv(folder / "cells.csv", summarise(runs, header), cell_columns(header))
            if not quiet:
                won = sum(row.get("outcome") == "win" for row in group)
                print(f"{name} {cell:32s} {population:16s} won {won:4d} of {size}   "
                      f"{time.perf_counter() - start:6.1f} s", flush=True)
    write_csv(folder / "cells.csv", summarise(runs, header), cell_columns(header))
    return folder


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("experiment", choices=sorted(EXPERIMENTS))
    parser.add_argument("--seeds", type=int, help="seeds per cell (default: the cell's)")
    parser.add_argument("--jobs", type=int, default=os.cpu_count(), help="worker processes")
    parser.add_argument("--resume", action="store_true", help="keep the complete groups")
    parser.add_argument("--keep-periods", default="", help="seeds whose period table is kept")
    arguments = parser.parse_args()
    kept = tuple(int(seed) for seed in arguments.keep_periods.split(",") if seed)
    print(run_experiment(arguments.experiment, arguments.seeds, arguments.jobs,
                         arguments.resume, kept))
