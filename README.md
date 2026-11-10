# Real competition ABM, version 4: the unit-cost rule against the profit-rate rule

An agent-based model of one industry in which firms that choose techniques by the lowest unit
cost (Shaikh) compete with firms that choose by the highest profit rate at an evaluation price
(the criterion of Okishio's theorem). Group project, M2 EPOG, MIP1 (Funalot & Bassi), built on
the course template
[pierrefunalot/EPOG_MIF_SIMPLE_ABM](https://github.com/pierrefunalot/EPOG_MIF_SIMPLE_ABM).

Version 4 is the second rebuild from a clean tree. It is written for a reader: at most 1,000
lines of model code, comments and docstrings excluded, and every rule that varies is an option
of `parameters.py`. It is being built in stages (section 13 of `docs/design/v4-plan.md`);
**stage 1 is done**: the parameters, the entities and the equations that several steps share.

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
```

## Layout

```text
parameters.py     every parameter, constant and option
equations/        one rule per file, pure functions, named <step>_<equation>.py
model/            entities.py
tests/            one test file per step; test_budget.py and test_readability.py
docs/design/      the specification of version 4 and the records of versions 2 and 3
```
