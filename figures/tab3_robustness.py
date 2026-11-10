"""Table 3: the robustness checks, each beside the cell it is a variant of.

    python3 -m figures.tab3_robustness [folder]

It reads the cells.csv of E1, E4, the reruns, the robustness checks, the reserve and the
fixed menu, and writes outputs/figures/tab3_robustness.csv and .md. A row is one check in
one cell: the share of seeds won by the unit-cost label with its interval, whether it is
beyond drift, the same for the cell it varies, and, where the check has a cell without
draws, the seeds of 50 that pass E0 in the two controls. Standard library only.
"""
import csv
import pathlib
import sys

from experiments.cells import GROWTH_CELLS, MARX_CELLS, PRICE_RULES, TWO_RULES

COLUMNS = ("check", "cell", "share_won", "interval", "beyond_drift", "base_cell", "base_share",
           "base_beyond_drift", "change", "e0_pass")
FOLDER = pathlib.Path("outputs") / "figures"


def checks() -> list[tuple]:
    """Each check as (what it changes, experiment, cell, experiment and cell it varies)."""
    rows = [("No overtime", "reruns", "no_overtime", "E1", "defaults_cost_edge")]
    rows += [("No overtime", "robustness", f"no_overtime_{rule}", "E1", f"defaults_{rule}")
             for rule in PRICE_RULES[1:]]
    rows += [("Entrant at the lowest price", "reruns", "entry_lowest", "E1", "defaults_cost_edge"),
             ("Shortage step of 0.5", "reruns", "step_0.5", "E1", "defaults_cost_edge"),
             ("Shortage step of 0.5", "reruns", "step_0.5_accelerator", "reruns", "accelerator")]
    for label, prefix in (("Entrant's parent drawn evenly", "entry_label_even"),
                          ("Operating-cost floor", "operating_cost_floor")):
        rows += [(label, "robustness", f"{prefix}_{rule}", "E1", f"defaults_{rule}")
                 for rule in TWO_RULES]
    rows += [("Fixed menu at 0.10", "fixed_menu", "fixed_menu_rbar_0.1", "E0r", "rbar_0.1"),
             ("Private designs", "robustness", "private_designs", "E1", "defaults_cost_edge"),
             ("Scrapping on unit cost", "robustness", "scrap_cost_unit_cost_defaults", "E1",
              "defaults_cost_edge")]
    rows += [("Scrapping on unit cost", "robustness", f"scrap_cost_unit_cost_{cell}", "E4", cell)
             for cell in MARX_CELLS]
    for firms in (2, 5):
        label = f"{6 * firms} firms"
        rows.append((label, "robustness", f"firms_per_pair_{firms}_defaults", "E1",
                     "defaults_cost_edge"))
        rows += [(label, "robustness", f"firms_per_pair_{firms}_{cell}", "E4", cell)
                 for cell in GROWTH_CELLS]
    return rows


def read(folder: pathlib.Path, experiment: str) -> dict:
    with open(folder / experiment / "cells.csv", newline="") as file:
        return {(row["cell"], row["population"]): row for row in csv.DictReader(file)}


def e0_pass(cells: dict, cell: str) -> str:
    """The seeds that pass E0 in the two controls of the cell without draws, if it has one."""
    controls = [cells.get(("no_draws_" + cell, population))
                for population in ("all_unit_cost", "all_profit_rate")]
    if not all(controls):
        return ""
    return " / ".join(f"{round(float(row['e0_pass']) * int(row['n_seeds']))}" for row in controls)


def table(folder: pathlib.Path) -> list[dict]:
    found = {}
    rows = []
    for label, experiment, cell, base_experiment, base_cell in checks():
        for name in (experiment, base_experiment):
            if name not in found:
                found[name] = read(folder, name)
        row = found[experiment][cell, "mixed"]
        base = found[base_experiment][base_cell, "mixed"]
        share, base_share = float(row["share_won"]), float(base["share_won"])
        rows.append({
            "check": label, "cell": cell, "share_won": f"{share:.2f}",
            "interval": f"{float(row['won_low']):.2f}–{float(row['won_high']):.2f}",
            "beyond_drift": "yes" if row["beyond_drift"] == "True" else "no",
            "base_cell": base_cell, "base_share": f"{base_share:.2f}",
            "base_beyond_drift": "yes" if base["beyond_drift"] == "True" else "no",
            "change": f"{share - base_share:+.2f}", "e0_pass": e0_pass(found[experiment], cell),
        })
    return rows


def main(folder: str = "outputs", target: pathlib.Path = FOLDER) -> pathlib.Path:
    rows = table(pathlib.Path(folder))
    target = pathlib.Path(target)
    target.mkdir(parents=True, exist_ok=True)
    with open(target / "tab3_robustness.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    header = ("Check", "Cell", "Share won", "Interval", "Beyond drift", "Cell it varies",
              "Its share", "Beyond drift", "Change", "Seeds of 50 that pass E0")
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * len(header)) + " |"]
    lines += ["| " + " | ".join(row[column] for column in COLUMNS) + " |" for row in rows]
    (target / "tab3_robustness.md").write_text("\n".join(lines) + "\n")
    return target / "tab3_robustness.md"


if __name__ == "__main__":
    print(main(*sys.argv[1:2]))
