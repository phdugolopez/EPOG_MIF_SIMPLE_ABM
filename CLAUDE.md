# CLAUDE.md

Version 4 of the group's agent-based model (M2 EPOG, MIP1): one industry in which firms that
choose techniques by the lowest unit cost (Shaikh, h = 0) compete with firms that choose by the
highest profit rate at an evaluation price (the criterion of Okishio's theorem). It is the
second rebuild from a clean tree. Version 3 is in `../ABM-v3` (branch `v3`) and version 2 in
`../ABM-sources`; both are read-only.

## Authority

- Five documents are the specification: `docs/design/v4-final-model.md` (the proposal),
  `docs/design/v4-choices.md` (the register), `docs/design/v4-plan.md` (files, interfaces,
  tests and stages), `docs/design/v4-review.md` and `docs/design/v4-literature-check.md`.
  Everything else in `docs/design/` is a record of version 2 or 3: take no rule, default or
  file layout from it.
- Order: a row of `v4-choices.md` wins over the proposal, and the proposal over the rows of
  `v3-choices.md` that the register lists under "Kept from v3". The plan says how each rule is
  built, and in which stage.
- The specification is the source of truth. Any departure goes into the last table of
  `docs/design/v4-choices.md` (what, why, date) before the code changes; never diverge silently.
- The five documents are edited in this tree only, not in `../ABM-v3`.

## Rules for the build

- **Neutrality.** The label is read only to look up the rule and in inheritance at entry; a
  rule only to look up the hurdle. Ties are never broken by a firm's place or serial number.
  The label-swap and firm-order tests must always pass.
- **Nothing outside the specification.** No debt, interest or bankruptcy, no overtime
  premium, no target utilisation, no anchor pricing, no logit demand, no replacement of
  working plants, no capital advanced (τ), no wage path or labour units, no plants without a
  maximum age, no debug suite, no recorder for the viewer, and no option that the proposal's
  table of options does not list.
- **Rules as options, not patches.** A rule that varies is chosen in one place by a field of
  `Parameters`. No experiment replaces a function of the model.
- **Names of files.** Equation files are `equations/<step>_<equation>.py`, where `<step>` is
  `setup`, `pricing`, `demand`, `accounts`, `scrapping`, `investment`, `entry`, or `common`
  for a definition several steps use. Step functions and test files carry the same names
  (`set_prices`, `tests/test_pricing.py`).
- **Equations are pure functions**: no state, no random draw. What moves cash, plants or firms
  is a transaction in `markets/`.
- **Simultaneous moves.** Every step computes all firms from the state at the start of the
  step, so the order of firms never matters. Sums over firms or plants use `math.fsum`.
- **Randomness.** One stream per firm and one for the industry, from
  `numpy.random.SeedSequence(seed)`; no other source.
- **Money.** Every flow of cash goes through `markets.payments.pay`; all cash, the rest of the
  economy included, sums to zero in every period, and `check` asserts it.
- **Constants.** Every constant is in `parameters.py`.
- **Python.** The model, the harness and the tests run on `python3` (3.12 or later) with numpy
  alone. The figures, the figure of the viewer and Morris need matplotlib and SALib, which are
  in `../ABM-sources/.venv/bin/python`.
- **Speed.** A run at the defaults takes at most 0.2 s; profile only if it is slower.
- **Commits.** One commit at the end of each stage on branch `v4`; never push.

## Readability comes before the line count

The model code is `parameters.py`, `run.py`, `equations/`, `markets/` and `model/`.
`tests/test_budget.py` and `tests/test_readability.py` enforce what a machine can check
(plan, section 12); the rest is for the reader of stage 4.

- At most 1,000 lines, counted without blank lines, comment lines and docstrings. No line is
  saved at the cost of a name, a step or a comment.
- A comprehension that filters, a sort key or a `lambda` has a comment line above its
  statement that says in plain words what it selects and why.
- No statement does two things: no `a, b = x, y`, no `;`, no conditional expression inside a
  call.
- A step function reads top to bottom like its paragraph of the schedule, one stage a block,
  each block opened by a comment.
- Names say what a thing is in the model's words. A name of one letter is a symbol of the
  proposal or a loop index: `p` (the parameters), `c`, `z`, `t`, `u`, `i`, `j`, `k`, `n`.
- Each equation file opens with its formula and its source: `v4-final-model.md` and a section.
- Lines of at most 100 characters.

## Commands

```bash
python3 -m unittest discover -s tests     # every test; test_budget prints the line count
python3 run.py                            # one run at the defaults -> outputs/periods.csv
```

## Where the build stands

The stages are in section 13 of `docs/design/v4-plan.md`. Stage 1 (scaffold) is done:
`parameters.py`, `model/entities.py`, the five `common_` equations, `setup_menu.py` and
`setup_initial_plants.py`, with `test_common`, the menu part of `test_setup`, `test_budget`
and `test_readability`. The model code counts 207 lines.

`parameters.py` has two constants more than section 7 of the plan first listed: `OPTIONS`,
the levels of every option, and `MONEY_EPS`, the tolerance of `check`. The plan now lists
them.

Next is stage 2, the skeleton of the period loop.
