# Real competition ABM, version 4: the unit-cost rule against the profit-rate rule

An agent-based model of one industry in which firms that choose techniques by the lowest unit
cost (Shaikh) compete with firms that choose by the highest profit rate at an evaluation price
(the criterion of Okishio's theorem). Group project, M2 EPOG, MIP1 (Funalot & Bassi), built on
the course template
[pierrefunalot/EPOG_MIF_SIMPLE_ABM](https://github.com/pierrefunalot/EPOG_MIF_SIMPLE_ABM).

Version 4 is the second rebuild from a clean tree. It is written for a reader: at most 1,000
lines of model code, comments and docstrings excluded, and every rule that varies is an option
of `parameters.py`. It is being built in stages (section 13 of `docs/design/v4-plan.md`);
**stages 1 to 6 are done**: the model, the harness with the E0 gate, the run viewer and
figures 1 to 3. E0 holds at the default on this code (`docs/design/v4-plan.md`, section 15);
E1 to E3 are stage 7 and are not run yet.

- Specification: `docs/design/v4-final-model.md`.
- Decisions and departures: `docs/design/v4-choices.md`.
- Files, interfaces, tests and build order: `docs/design/v4-plan.md`.
- Coherence review and literature check: `docs/design/v4-review.md`,
  `docs/design/v4-literature-check.md`.
- Rules for the build: `CLAUDE.md`.

The other files of `docs/design/` are the records of versions 2 and 3.

## The model in one equation

Two rules choose a technique j = (ucs, κ), operating cost and capital per unit of normal
output, by the same line and differ only by the hurdle h:

```text
j* = argmin over the menu of  ucs + (δ + h) κ
h  = 0                                          unit-cost rule
h  = max(0, best rate on the menu at p^e)       profit-rate rule
p^e = (1 − λ) own price + λ price of production of the regulating technique
```

A period opens with the deliveries and has six steps: pricing, demand, production and
accounts, scrapping, technical change and investment, entry and exit.

## Install and test

Python 3.12 or later. The model and the tests need only numpy:

```bash
python3 -m unittest discover -s tests
python3 run.py                # one run at the defaults -> outputs/periods.csv, run.csv
python3 run.py 7              # another seed
python3 -m experiments.harness E0 --jobs 10      # outputs/E0/runs.csv and cells.csv
python3 -m experiments.harness E1 --resume       # runs what is missing
python3 -m experiments.e0_gate outputs/E0        # does E0 hold, price rule by price rule?
python3 -m experiments.show_run --seed 7 pricing=universal population=all_unit_cost
```

The run viewer writes `outputs/runs/<name>/`: the period table, one row per firm and period,
the run row and a read-out. Its figure and the figure scripts need matplotlib:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m experiments.show_run --seed 7 --firms
.venv/bin/python -m figures.fig1_conflict_zone   # outputs/figures/
.venv/bin/python -m figures.fig2_typical_run 0
.venv/bin/python -m figures.fig3_bias_lambda     # after E2 and E3
```

## Layout

```text
parameters.py     every parameter, constant and option
equations/        one rule per file, pure functions, named <step>_<equation>.py
markets/          the transactions: payments, goods, plants, entry and exit
model/            entities.py, model.py (the industry at t = 0, one run), scheduler.py (the
                  period: STEPS and close_period), outputs.py (the tally, the period table)
run.py            one run at the defaults
experiments/      summary.py (the run row, with the measures of E0), cells.py,
                  populations.py, stats.py, harness.py, e0_gate.py, show_run.py (the viewer)
figures/          style.py and one script per exhibit (figures 1 to 3 so far)
tests/            one test file per step; test_budget.py and test_readability.py
docs/design/      the specification of version 4 and the records of versions 2 and 3
```
