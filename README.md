# Real competition ABM, version 3: Shaikh against Okishio

An agent-based model of one industry in which firms that choose techniques by the lowest unit
cost (Shaikh) compete with firms that choose by the highest profit rate at an evaluation price
(Okishio). Group project, M2 EPOG, MIP1 (Funalot & Bassi), built on the course template
[pierrefunalot/EPOG_MIF_SIMPLE_ABM](https://github.com/pierrefunalot/EPOG_MIF_SIMPLE_ABM).

Version 3 is a rebuild from a clean tree of about 700 lines, which keeps only what moved the
results of version 2. It is being built in stages; **stages 1 to 3 are done**: the whole model
is written and runs. Stage 4 (neutrality tests, profile, the check of the industry without
technical change) comes before any experiment is read.

- Specification: `docs/design/final-model-proposal.md` and the addendum in
  `docs/design/v3-planning-prompt.md`.
- Decisions and departures: `docs/design/v3-choices.md`.
- Files, interfaces, tests and build order: `docs/design/v3-plan.md`.
- Rules for the build: `CLAUDE.md`.

The other files of `docs/design/` describe version 2.

## Install and test

Python 3.12 or later. macOS or Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python run.py                  # one run at the defaults -> outputs/periods.csv, run.csv
.venv/bin/python run.py 7                # another seed
```

Windows: replace `.venv/bin/python` with `.venv\Scripts\python.exe`.

## The model in one equation

Two rules choose a technique j = (ucs, κ), operating cost and capital per unit of output, by the
same line and differ only by the hurdle h:

```text
j* = argmin over the menu of  ucs + (δ + h) κ
h  = 0                                          unit-cost rule (Shaikh)
h  = max(0, best rate on the menu at p^e)       profit-rate rule (Okishio)
p^e = (1 − λ) own price + λ price of production of the regulating technique
```

A period has six steps: pricing, demand, production and accounts, scrapping, technical change
and investment, entry and exit.

## Layout

```text
parameters.py     every parameter, constant and switch
equations/        one rule per file, pure functions, named <step>_<equation>.py
markets/          the transactions: payments, goods, plants, entry and exit
model/            entities.py, model.py, scheduler.py, outputs.py (the period table)
run.py            one run at the defaults
experiments/      summary.py, the run row; cells, harness, Morris screening     (from stage 5)
tests/            one test file per step
figures/          one script per report exhibit                                  (from stage 5)
docs/design/      specification, plan and decisions
```
