# Real competition ABM: Shaikh against Okishio

An agent-based model of one industry in which firms that choose techniques by the lowest
unit cost (Shaikh) compete with firms that choose by the highest profit rate at the current
price (Okishio). Group project, M2 EPOG, MIP1 (Funalot & Bassi), built on the course
template [pierrefunalot/EPOG_MIF_SIMPLE_ABM](https://github.com/pierrefunalot/EPOG_MIF_SIMPLE_ABM).

- Specification: `docs/design/mechanism-briefs.md`; open choices: `docs/design/choices.md`.
- Output tables, column by column: `docs/design/collector.md`; debugging plots:
  `debug/README.md`.
- Report: `docs/main.tex` (built by CI as an artifact).
- Conventions, ownership and how to extend the model: `CLAUDE.md`.

## Install and run

macOS or Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python run.py                  # options: --out DIR --format csv|parquet --seed N
                                         #          --experiment E --population P --cell C
.venv/bin/python plot_outputs.py         # reads outputs/macro.csv
.venv/bin/python -m debug.report outputs # debugging plots -> outputs/debug/report.pdf
cd docs && latexmk -pdf main.tex
```

Windows: replace `.venv/bin/python` with `.venv\Scripts\python.exe`.

## Outputs and the debugging report

`run.py` runs the model once and writes seven tables to a run folder (`outputs/` by
default): `runs` (one row: seed, commit, every parameter, wall time), `macro` (one row per
period: prices, shares, profit rates, price-war flags and every check residual), `groups`
(one row per period and label: capacity flows, shares, technique mix, designs), `firms`,
`plants`, `events` (orders, retirements, entries, exits, designs, price wars) and `flows`
(the transaction-flow matrix). Every column is described in `docs/design/collector.md`,
generated from `model/schema.py`. The collector observes and never decides: it draws no
random number and writes nothing a mechanism reads, so adding a column never changes a
trajectory.

```bash
.venv/bin/python run.py                                   # baseline -> outputs/*.csv
.venv/bin/python run.py --seed 7 --out runs/s7            # another seed, another folder
.venv/bin/python run.py --format parquet                  # needs pyarrow
.venv/bin/python -m debug.report outputs                  # every debugging plot -> outputs/debug/report.pdf
.venv/bin/python -m debug.checks outputs                  # are the accounts sound? (run this first when something looks odd)
.venv/bin/python -m debug.firm_panel outputs --firm 3     # what one firm saw and did
.venv/bin/python -m debug.compare_runs runs/old runs/new  # where two runs diverge (exit 1 if they do)
.venv/bin/python -m experiments.neutral_control --seeds 50   # mixed population against two neutral controls
.venv/bin/python -m analysis.schema_doc                   # regenerate docs/design/collector.md after a schema change
```

The report gathers, for one run folder, the check residuals, one page per firm, the
plant Gantt, the merit order at three periods, the event timeline, the capacity bridge
(the decomposition of each type's share into price-driven, accumulation, entry and exit
terms) and the flow matrix. Each script also runs alone and writes PNGs to
`RUN_DIR/debug/`; `debug/README.md` lists them with the question each one answers. To
check that a change left the model untouched, write the old and the new run to two
folders and compare them; `--swap-labels` does the same for the label-swap test. The
neutral control runs the mixed population and two populations with both labels on one
rule over the same seeds, and writes `outputs/experiments/neutral_control.csv`; its
overrides are parameter assignments (`PRICING_RULE=leader_follow`, `CHI=2`).

## Architecture

```text
parameters.py            all parameters and switches
run.py                   runs the model, writes outputs/{runs,macro,groups,firms,plants,events,flows}.csv
analysis/                indicators computed from the tables; schema_doc generates docs/design/collector.md
experiments/             experiment scripts over seeds (neutral_control), outputs in outputs/experiments/
plot_outputs.py          draws outputs/*.png
style.py                 colours and rcParams shared by plot_outputs.py and debug/
debug/                   debugging plots, one script per question, from a run folder's tables

model/
    entities.py          Technique, Plant, Firm, RestOfEconomy
    model.py             Industry: initial population and menu
    scheduler.py         the six steps of a period and the stock-flow check
    collector.py         outputs and check_stock_flow
    schema.py            every output column: meaning, unit, step, mechanism

equations/               one equation or behavioural rule per file
markets/                 goods market, credit, plants, payments, entry and exit
tests/                   one test file per mechanism, plus the full model
docs/                    LaTeX report and design reference
```

One period: pricing, demand, production and accounts, scrapping, investment, entry and
exit, then the collector. Every payment goes through one rest-of-economy account, so money
is conserved and the scheduler asserts stock-flow consistency every period.
