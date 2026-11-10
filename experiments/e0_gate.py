"""Reads cells.csv of an experiment and says, cell by cell, whether E0 holds.

    python3 -m experiments.e0_gate outputs/E0

For each cell that was run in the two controls it prints the seeds that pass every line of
E0 in each population, whether E0 holds (at least 9 seeds of 10 pass, in both), and the
weakest line with the share of seeds that pass it in each population (v4-final-model.md,
"Experiments", E0; v4-choices.md, decisions 3 and 7).

The gate is on the default price rule: the command ends with status 1 when the cell
no_draws_cost_edge is in the file and E0 does not hold in it. Then no other experiment is
read. On any other cell the verdict is a report, outside the gate.
"""
import csv
import pathlib
import sys

from experiments.populations import CONTROLS
from experiments.summary import E0_LINES

DEFAULT_CELL = "no_draws_cost_edge"
HOLDS_AT = 0.9


def read_cells(folder) -> list[dict]:
    """The rows of cells.csv in a folder of the harness."""
    with open(pathlib.Path(folder) / "cells.csv", newline="") as file:
        return list(csv.DictReader(file))


def line_column(line: str) -> str:
    """The column of cells.csv that holds the share of seeds passing a line of E0."""
    return "e0_alive" if line == "alive" else f"e0_{line}_ok"


def verdicts(cells: list[dict]) -> list[dict]:
    """One verdict for each cell that has its two controls, in the order of the file."""
    by_cell = {}
    for row in cells:
        by_cell.setdefault(row["cell"], {})[row["population"]] = row
    out = []
    for cell, rows in by_cell.items():
        if all(control in rows for control in CONTROLS):
            controls = [rows[control] for control in CONTROLS]
            shares = [float(row["e0_pass"]) for row in controls]
            seeds = [int(row["n_seeds"]) - int(row["n_error"]) for row in controls]
            # The line that the fewest seeds pass, over the two populations.
            lines = {line: [float(row[line_column(line)]) for row in controls]
                     for line in E0_LINES}
            weakest = min(lines, key=lambda line: min(lines[line]))
            out.append({
                "cell": cell,
                "passed": [round(share * n) for share, n in zip(shares, seeds)],
                "seeds": seeds,
                "holds": all(share >= HOLDS_AT for share in shares),
                "weakest": weakest if min(lines[weakest]) < 1.0 else None,
                "weakest_shares": lines[weakest],
            })
    return out


def report(found: list[dict]) -> str:
    """The verdicts as lines of text, the two controls in the order unit cost, profit rate."""
    lines = []
    for verdict in found:
        passed = " and ".join(f"{k} of {n}" for k, n in zip(verdict["passed"], verdict["seeds"]))
        weakest = "every line passes in every seed"
        if verdict["weakest"]:
            shares = " and ".join(f"{share:.2f}" for share in verdict["weakest_shares"])
            weakest = f"weakest line: {verdict['weakest']} ({shares} of seeds)"
        holds = "holds" if verdict["holds"] else "does not hold"
        lines.append(f"{verdict['cell']:32s} {passed:20s} E0 {holds:14s} {weakest}")
    return "\n".join(lines)


def gate(found: list[dict]) -> bool | None:
    """Whether E0 holds at the default price rule; None when that cell is not in the file."""
    for verdict in found:
        if verdict["cell"] == DEFAULT_CELL:
            return verdict["holds"]
    return None


if __name__ == "__main__":
    found = verdicts(read_cells(sys.argv[1]))
    print(report(found))
    held = gate(found)
    if held is None:
        print("The default cell is not in this file: these verdicts are outside the gate.")
    elif held:
        print("The gate: E0 holds at the default price rule.")
    else:
        print("The gate: E0 does not hold at the default price rule. Read nothing else.")
        sys.exit(1)
