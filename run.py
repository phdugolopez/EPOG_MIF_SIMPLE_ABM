"""Run the model and write its tables: runs, macro (the brief's industry table), groups,
firms, plants, events and flows, each with run_id as the first column.

    python run.py [--out DIR] [--format csv|parquet] [--experiment E] [--population P]
                  [--cell C] [--seed N] [--set NAME=value ...]

Defaults reproduce the baseline: outputs/*.csv, parameters.py as it stands. --set replaces
an upper-case parameter (repeatable; values parsed as Python literals, strings as is, e.g.
--set CHI=2 --set PRICING_RULE=leader_follow
--set 'HURDLE_RULES={"shaikh": "unit_cost", "okishio": "unit_cost"}').
"""

import argparse
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

import parameters
from model import Industry
from model.collector import EVENT_COLUMNS, events_table
from model.schema import RUN_ALIASES, parameter_columns

ROOT = Path(__file__).resolve().parent


def configure(seed: int | None = None, **overrides) -> SimpleNamespace:
    """The parameters of parameters.py, with SEED replaced when seed is given and any
    other upper-case parameter replaced by `overrides` (the tests' make_config)."""
    values = {k: v for k, v in vars(parameters).items() if k.isupper()}
    if seed is not None:
        values["SEED"] = seed
    values.update(overrides)
    return SimpleNamespace(**values)


def _plain(value):
    """Tuples, lists and dicts as JSON; everything else as it is."""
    return json.dumps(value) if isinstance(value, (tuple, list, dict)) else value


def param_hash(config) -> str:
    values = {k: getattr(config, k) for k in parameter_columns(config)}
    return hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()


def code_version() -> str:
    """HEAD's hash, with -dirty if tracked files have uncommitted changes."""
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                               cwd=ROOT, capture_output=True, text=True,
                               check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return head + ("-dirty" if dirty else "")


def make_run_id(experiment: str, cell: str, population: str, seed: int) -> str:
    return f"{experiment}_{cell}_{population}_s{seed}"


def runs_row(industry, run_id: str, experiment: str, population: str, cell: str,
             wall_seconds: float) -> dict:
    config = industry.parameters
    row = {
        "run_id": run_id,
        "seed": config.SEED,
        "code_version": code_version(),
        "param_hash": param_hash(config),
        "experiment": experiment,
        "population": population,
        "cell": cell,
        "anchor": config.PRICING_ANCHOR,
        "okishio_price": "own",  # choices.md: Okishio h is evaluated at the firm's price
        "menu": _plain(config.MENU),
        "horizon": len(industry.history),
        "burn_in": 0,
        "n_check_fail": industry.n_check_fail,
        "wall_seconds": wall_seconds,
        "python_version": platform.python_version(),
    }
    for name, column in parameter_columns(config).items():
        if name not in RUN_ALIASES:
            row[column] = _plain(getattr(config, name))
    return row


def tables(industry, run: dict) -> dict[str, pd.DataFrame]:
    """Every output table of a finished run, run_id first."""
    frames = {
        "runs": pd.DataFrame([run]),
        "macro": pd.DataFrame(industry.history),
        "groups": pd.DataFrame(industry.group_history),
        "firms": pd.DataFrame(industry.firm_history),
        "plants": pd.DataFrame(industry.plant_history),
        "events": pd.DataFrame(events_table(industry), columns=list(EVENT_COLUMNS)),
        "flows": pd.DataFrame(industry.flow_history),
    }
    for name, frame in frames.items():
        if name != "runs":
            frame.insert(0, "run_id", run["run_id"])
    return frames


def write(frames: dict[str, pd.DataFrame], out: Path, fmt: str) -> None:
    """Write every table in `fmt`; a stale copy of the same table in the other format
    (from an earlier run into the same folder) is removed, so that readers of the folder
    never find two versions of one table."""
    out.mkdir(parents=True, exist_ok=True)
    other = "csv" if fmt == "parquet" else "parquet"
    for name, frame in frames.items():
        if fmt == "parquet":
            frame.to_parquet(out / f"{name}.parquet", index=False)
        else:
            frame.to_csv(out / f"{name}.csv", index=False)
        (out / f"{name}.{other}").unlink(missing_ok=True)


def main(argv=None) -> dict[str, pd.DataFrame]:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", type=Path, default=ROOT / "outputs",
                        help="output folder (default: outputs/, read by docs/main.tex)")
    parser.add_argument("--format", choices=("csv", "parquet"), default="csv")
    parser.add_argument("--experiment", default="baseline")
    parser.add_argument("--population", default="baseline")
    parser.add_argument("--cell", default="baseline")
    parser.add_argument("--seed", type=int, default=None,
                        help="master seed (default: SEED in parameters.py)")
    parser.add_argument("--set", dest="overrides", action="append", default=[],
                        metavar="NAME=value",
                        help="replace a parameter of parameters.py (repeatable)")
    args = parser.parse_args(argv)
    from experiments.neutral_control import parse_overrides  # imports run: import here
    overrides = parse_overrides(args.overrides)
    unknown = sorted(set(overrides) - set(vars(configure())))
    if unknown:
        parser.error(f"--set: no such parameter in parameters.py: {', '.join(unknown)}")
    if args.format == "parquet":
        try:
            import pyarrow  # noqa: F401
        except ImportError:
            parser.error("--format parquet needs pyarrow: pip install -r requirements.txt")

    industry = Industry(configure(args.seed, **overrides))
    start = time.perf_counter()
    industry.run()  # the scheduler checks stock-flow consistency every period
    wall = time.perf_counter() - start
    run_id = make_run_id(args.experiment, args.cell, args.population,
                         industry.parameters.SEED)
    frames = tables(industry, runs_row(industry, run_id, args.experiment,
                                       args.population, args.cell, wall))
    write(frames, args.out, args.format)

    columns = ["t", "n_firms", "price_avg", "share_shaikh", "share_okishio",
               "capacity_total", "profit_rate", "entries", "exits"]
    print(frames["macro"][columns].tail().to_string(index=False))
    print(f"\nRun {run_id} ({wall:.3f} s). Outputs saved in: {args.out}")
    return frames


if __name__ == "__main__":
    main()
