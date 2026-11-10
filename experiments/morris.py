"""Morris screening of the default (v4-plan.md, section 9; v4-final-model.md, "Sensitivity
analysis").

    python3 -m experiments.morris [--seeds 100] [--jobs 10] [--trajectories 10] [--resume]

Twelve parameters move on a grid of four levels along 10 trajectories: 130 points, each run
as a cell of the harness in the three populations. For every outcome the elementary effect
of a parameter is the change of the outcome when that parameter alone moves, per unit of its
range. mu* is the mean of its absolute value over the trajectories, sigma its spread: a
large mu* says the parameter matters, a large sigma that its effect depends on the others.

The files are in outputs/morris/: runs.csv and cells.csv of the harness, sample.csv (the
points) and morris.csv (mu*, its 95 % interval, mu and sigma by parameter and outcome).

The method is written here with numpy, as Morris (1991) gives it: the plan named SALib, which
is not installed beside this tree.
"""
import argparse
import csv
import os
import pathlib

import numpy as np

from experiments.harness import run_experiment, write_csv
from experiments.populations import ALL

# Name, lowest and highest value. chi moves on a logarithmic scale; the plant life is whole.
PARAMETERS = (
    ("bias", 0.5, 3.0), ("design_step", 0.02, 0.10), ("draw_prob", 0.1, 0.4),
    ("price_cut", 0.01, 0.05), ("log2_chi", -2.0, 2.0), ("payout", 0.25, 0.75),
    ("plant_life", 7.0, 19.0), ("plant_size", 10.0, 40.0), ("entry_speed", 1.0, 10.0),
    ("mutation", 0.0, 0.05), ("u_max", 1.0, 1.4), ("shortage_step", 0.1, 0.5),
)
NAMES = tuple(name for name, _, _ in PARAMETERS)
LEVELS = 4
OUTCOMES = ("gap", "cap_share_end", "lost_share", "e0_lines", "rate_gap")
SAMPLE_SEED = 0
FOLDER = pathlib.Path("outputs") / "morris"


def trajectories(count: int, parameters: int, levels: int, rng) -> np.ndarray:
    """`count` trajectories of parameters + 1 points on the grid of [0, 1]: from one point
    to the next a single coordinate moves, by delta = levels / (2 (levels - 1)), and each
    coordinate moves once. Shape (count, parameters + 1, parameters)."""
    delta = levels / (2.0 * (levels - 1))
    low_half = np.arange(levels // 2) / (levels - 1)
    points = np.empty((count, parameters + 1, parameters))
    for index in range(count):
        base = rng.choice(low_half, size=parameters)
        direction = rng.choice((-1.0, 1.0), size=parameters)
        # A coordinate that moves down starts from the upper half of the grid.
        point = base + (direction < 0.0) * delta
        points[index, 0] = point
        for step, moved in enumerate(rng.permutation(parameters), start=1):
            point = point.copy()
            point[moved] += direction[moved] * delta
            points[index, step] = point
    return points


def overrides(point: np.ndarray) -> dict:
    """The parameters of the model at a point of the grid."""
    values = {name: low + float(x) * (high - low)
              for (name, low, high), x in zip(PARAMETERS, point)}
    values["chi"] = 2.0 ** values.pop("log2_chi")
    values["plant_life"] = int(round(values["plant_life"]))
    return {name: round(value, 10) if isinstance(value, float) else value
            for name, value in values.items()}


def elementary_effects(points: np.ndarray, outcome: np.ndarray) -> np.ndarray:
    """The elementary effect of each parameter in each trajectory: the change of the outcome
    over the change of the coordinate that moved. Shape (trajectories, parameters)."""
    count, steps, parameters = points.shape
    effects = np.full((count, parameters), np.nan)
    for index in range(count):
        for step in range(1, steps):
            change = points[index, step] - points[index, step - 1]
            moved = int(np.argmax(np.abs(change)))
            difference = outcome[index, step] - outcome[index, step - 1]
            effects[index, moved] = difference / change[moved]
    return effects


def screen(effects: np.ndarray, rng, resamples: int = 1000) -> list[dict]:
    """mu*, its 95 % interval by resampling the trajectories, mu and sigma of each
    parameter."""
    count = effects.shape[0]
    rows = []
    for column, name in enumerate(NAMES):
        values = effects[:, column]
        drawn = rng.integers(0, count, size=(resamples, count))
        half = 1.96 * np.abs(values)[drawn].mean(axis=1).std(ddof=1)
        mu_star = float(np.abs(values).mean())
        rows.append({"parameter": name, "mu_star": mu_star, "mu_star_low": mu_star - half,
                     "mu_star_high": mu_star + half, "mu": float(values.mean()),
                     "sigma": float(values.std(ddof=1))})
    return rows


def cell_name(index: int) -> str:
    return f"point_{index:03d}"


def experiment(points: np.ndarray, seeds: int) -> dict:
    """The points as cells of the harness, in the order trajectory, step."""
    flat = points.reshape(-1, points.shape[2])
    return {cell_name(index): {"overrides": overrides(point), "populations": ALL,
                               "seeds": seeds} for index, point in enumerate(flat)}


def outcomes(folder: pathlib.Path, shape: tuple) -> dict:
    """Each outcome at each point, read on the mixed rows of cells.csv: the share won less
    the mean of the two controls, then four means over the seeds of the mixed population."""
    with open(folder / "cells.csv", newline="") as file:
        mixed = {row["cell"]: row for row in csv.DictReader(file)
                 if row["population"] == "mixed"}
    count = shape[0] * shape[1]
    return {name: np.array([float(mixed[cell_name(index)][name] or "nan")
                            for index in range(count)]).reshape(shape)
            for name in OUTCOMES}


def main(seeds: int = 100, jobs: int = 1, count: int = 10, resume: bool = False,
         folder: pathlib.Path = FOLDER, quiet: bool = False) -> pathlib.Path:
    """Sample, run, and write morris.csv; returns its path."""
    rng = np.random.default_rng(SAMPLE_SEED)
    points = trajectories(count, len(PARAMETERS), LEVELS, rng)
    cells = experiment(points, seeds)
    folder = pathlib.Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    sample = [{"cell": name, "trajectory": index // points.shape[1],
               "step": index % points.shape[1], **cell["overrides"]}
              for index, (name, cell) in enumerate(cells.items())]
    write_csv(folder / "sample.csv", sample, list(sample[0]))
    run_experiment("morris", jobs=jobs, resume=resume, folder=folder,
                   experiments={"morris": cells}, quiet=quiet)
    found = outcomes(folder, points.shape[:2])
    rows = [{"outcome": name, **row} for name in OUTCOMES
            for row in screen(elementary_effects(points, found[name]), rng)]
    write_csv(folder / "morris.csv", rows, list(rows[0]))
    return folder / "morris.csv"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, default=100)
    parser.add_argument("--jobs", type=int, default=os.cpu_count())
    parser.add_argument("--trajectories", type=int, default=10)
    parser.add_argument("--resume", action="store_true")
    arguments = parser.parse_args()
    print(main(arguments.seeds, arguments.jobs, arguments.trajectories, arguments.resume))
