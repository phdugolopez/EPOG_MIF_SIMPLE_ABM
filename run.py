"""One run at the defaults: python3 run.py [seed] -> outputs/periods.csv.

The run row (outputs/run.csv) joins it when experiments/summary.py is written, in stage 3c.
"""
import csv
import pathlib
import sys

from model.model import run


def write(path: pathlib.Path, rows: list[dict]) -> None:
    """Write a table, one dictionary a row, as a csv file."""
    with open(path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    seed = 0
    if len(sys.argv) > 1:
        seed = int(sys.argv[1])
    industry = run(seed=seed)
    folder = pathlib.Path("outputs")
    folder.mkdir(exist_ok=True)
    write(folder / "periods.csv", industry.rows)
    print(f"seed {seed}: {len(industry.rows)} rows in {folder / 'periods.csv'}")
