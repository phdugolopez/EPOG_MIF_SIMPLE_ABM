"""One run at the defaults: python run.py [seed] -> outputs/periods.csv."""
import csv
import pathlib
import sys

from model.model import run

if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    rows = run(seed=seed).rows
    folder = pathlib.Path("outputs")
    folder.mkdir(exist_ok=True)
    with open(folder / "periods.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"seed {seed}: {len(rows)} rows in {folder / 'periods.csv'}")
