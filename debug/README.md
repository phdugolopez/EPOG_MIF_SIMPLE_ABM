# Debugging plots

Each script answers one question about one run. It reads only the tables `run.py` wrote
to a run folder (CSV or Parquet: `runs`, `macro`, `groups`, `firms`, `plants`, `events`,
`flows`, described in `docs/design/collector.md`), never the model, and writes its PNGs
to `RUN_DIR/debug/`. Price-war periods are shaded on every time axis; a cross marks the
end of the line of a firm that left. Colours are those of `plot_outputs.py` (Shaikh blue,
Okishio orange; techniques C aqua, D1 violet, D2 red). Run from the repository root,
after `python run.py` (which writes `outputs/`):

| Script | Question | Command |
| --- | --- | --- |
| `checks.py` | Are the accounts and the bookkeeping sound? (one panel per check residual, tolerance dashed, failures in red; prints the first failure and the firm) | `python -m debug.checks outputs` |
| `firm_panel.py` | What did one firm see and do? (price and its anchor, floor and leader band; shares; utilisation; capacity by plant; cash, debt, net worth; hurdle, r_best and the techniques the two rules pick) | `python -m debug.firm_panel outputs [--firm ID ...] [--all]` |
| `plant_gantt.py` | How do vintages live and die? (one bar per plant with its retirement cause, the age structure, the vintage spread) | `python -m debug.plant_gantt outputs` |
| `merit_order.py` | Does dispatch run plants in the right order, and is the floor the right plant? | `python -m debug.merit_order outputs [--t T ...] [--firm ID]` |
| `events_timeline.py` | Who entered, left, ordered and scrapped, and when? | `python -m debug.events_timeline outputs` |
| `capacity_bridge.py` | Do the capacity flows add up, and which one moves the shares? (the identity by group, sections 4.2 and 4.3 of the brief) | `python -m debug.capacity_bridge outputs [--group LABEL]` |
| `flow_matrix.py` | Where does the money go? (the flow matrix at one period, rows and columns against the change in cash, each item over time) | `python -m debug.flow_matrix outputs [--t T]` |
| `compare_runs.py` | Where do two runs diverge? (max difference per table, column and period; first divergence printed; exit status 1 if they differ) | `python -m debug.compare_runs RUN_A RUN_B [--swap-labels] [--tol 1e-12]` |
| `report.py` | All of the above for one run, in one PDF (`RUN_DIR/debug/report.pdf`) | `python -m debug.report outputs` |

Use `.venv/bin/python` in place of `python` with the project's virtual environment.

## Typical uses

- **Something looks odd.** `python -m debug.checks outputs` first, then the firm or the
  period it names with `firm_panel` or `merit_order`.
- **A refactor must change nothing.** Write the old and the new run to two folders
  (`python run.py --out /tmp/old` on the old commit, `--out /tmp/new` on the new one)
  and `python -m debug.compare_runs /tmp/old /tmp/new`. Tables written before the
  collector used the brief's names (`time`, `mean_price`, `book_value`, ...) are
  renamed first, so the reference run of commit 49f7974 compares directly.
- **Label swap.** Run the model with the labels swapped in `INITIAL_FIRMS` and in
  `HURDLE_RULES` (`tests/helpers.swapped_config`, written with `tests/helpers.write_run`)
  and compare with `--swap-labels`: every table must come out identical.
  `tests/test_debug_plots.py` does exactly this.

## Conventions

One script per question, shared loading and style in `_common.py`; each script exposes
`figures(run, ...)`, a list of (name, figure), and `main(argv)`. Ties are never resolved
by firm order: lanes are sorted by entry period then firm id and merit-order segments of
equal cost by plant id, which fixes only the drawing. The group decomposed by
`capacity_bridge` is chosen by its rule (`unit_cost`), not by its label.
