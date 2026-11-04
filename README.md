# Real competition ABM: Shaikh against Okishio

An agent-based model of one industry in which firms that choose techniques by the lowest
unit cost (Shaikh) compete with firms that choose by the highest profit rate at the current
price (Okishio). Group project, M2 EPOG, MIP1 (Funalot & Bassi), built on the course
template [pierrefunalot/EPOG_MIF_SIMPLE_ABM](https://github.com/pierrefunalot/EPOG_MIF_SIMPLE_ABM).

- Specification: `docs/design/mechanism-briefs.md`; open choices: `docs/design/choices.md`.
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
cd docs && latexmk -pdf main.tex
```

Windows: replace `.venv/bin/python` with `.venv\Scripts\python.exe`.

## Architecture

```text
parameters.py            all parameters and switches
run.py                   runs the model, writes outputs/{runs,macro,groups,firms,plants,events,flows}.csv
analysis/                indicators computed from the tables; schema_doc generates docs/design/collector.md
plot_outputs.py          draws outputs/*.png

model/
    entities.py          Technique, Plant, Firm, RestOfEconomy
    model.py             Industry: initial population and menu
    scheduler.py         the six steps of a period and the stock-flow check
    collector.py         outputs and check_stock_flow

equations/               one equation or behavioural rule per file
markets/                 goods market, credit, plants, payments, entry and exit
tests/                   one test file per mechanism, plus the full model
docs/                    LaTeX report and design reference
```

One period: pricing, demand, production and accounts, scrapping, investment, entry and
exit, then the collector. Every payment goes through one rest-of-economy account, so money
is conserved and the scheduler asserts stock-flow consistency every period.
