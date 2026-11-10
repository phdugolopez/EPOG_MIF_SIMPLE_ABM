"""One run at the defaults: python run.py [seed] -> outputs/periods.csv and outputs/run.csv."""
import csv
import pathlib
import sys

from experiments.summary import run_row
from model.model import run


def write(path: pathlib.Path, rows: list[dict]) -> None:
    with open(path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    industry = run(seed=seed)
    folder = pathlib.Path("outputs")
    folder.mkdir(exist_ok=True)
    write(folder / "periods.csv", industry.rows)
    write(folder / "run.csv", [run_row(industry.rows, industry.params, seed)])
    print(f"seed {seed}: {len(industry.rows)} rows in {folder / 'periods.csv'}, 1 in {folder / 'run.csv'}")
