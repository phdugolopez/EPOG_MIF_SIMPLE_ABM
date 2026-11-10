# CLAUDE.md

Version 3 of the group's agent-based model (M2 EPOG, MIP1): one industry in which firms that
choose techniques by the lowest unit cost (Shaikh, h = 0) compete with firms that choose by the
highest profit rate at an evaluation price (Okishio). It is a rebuild from a clean tree. Version 2
is in `../ABM-sources`, read-only.

## Authority

- Four documents are authoritative: `docs/design/final-model-proposal.md`,
  `docs/design/v3-planning-prompt.md`, `docs/design/v3-plan.md` and `docs/design/v3-choices.md`.
  Everything else in `docs/design/` describes version 2: take no rule, default or file layout from
  it.
- Order: a row of `v3-choices.md` wins over the addendum (section 4 of the planning prompt), and
  the addendum over the proposal. The plan says how each rule is built, and in which stage.
- The specification is the source of truth. Any departure goes into `docs/design/v3-choices.md`
  (what, why, date) before the code changes; never diverge silently.

## Rules for the build

- Neutrality: the type label is read only to look up the hurdle rule and in inheritance at
  entry. Ties are never broken by firm order or id. The label-swap test must always pass.
- Build nothing outside the specification: no debt, interest or bankruptcy, no overtime, no anchor
  pricing, no logit demand, no replacement of working plants, no capital advanced (τ), no wage
  path or labour units (E7 is dropped), no plants without a maximum age, no debug suite, no switch
  that the proposal does not list.
- Equation files are named `equations/<step>_<equation>.py`, where `<step>` is the loop step
  that uses the equation: `setup` (initial population), `pricing`, `demand`, `accounts`
  (production and accounts), `scrapping`, `investment` (technical change included) and `entry`
  (entry and exit), plus `common` for a definition several steps use (unit cost, profit rate at
  a price, hurdle, technique choice, regulating price). Scheduler step functions and test files
  follow the same step names (`set_prices`, `tests/test_pricing.py`).
- Equations are pure functions: no state, no random draw. What moves cash, plants or firms is a
  transaction in `markets/`.
- Every step computes all firms from the state at the start of the step (simultaneous moves),
  so the order of firms never matters. Sums over firms or plants use `math.fsum`.
- One random stream per firm and one for the industry, from `numpy.random.SeedSequence(seed)`;
  no other source of randomness.
- Every money flow goes through one payment function; assert money conservation each period.
- Python 3.12 or later; dependencies numpy, pandas, matplotlib, SALib.
- Speed: a 200-period run must take no longer than v2's (0.11 s on one core); profile if it does.
- Line count: the model code (`parameters.py`, `run.py`, `equations/`, `markets/`, `model/`) is
  counted without blank lines. Target 700, at most 770; `tests/test_budget.py` enforces it.
- Commit at the end of each stage on branch `v3`; never push.

## Commands

```bash
python -m unittest discover -s tests     # every test; test_budget prints the line count
python run.py                            # one run at the defaults -> outputs/periods.csv
```

## Where the build stands

The stages are in section 9 of `docs/design/v3-plan.md`. Stages 1 to 5 are done: the whole model
is written and every test passes (`python -m unittest discover -s tests`), the label-swap and
firm-order tests included. A run at the defaults takes 0.09 s. The model code counts 769 lines
without blank lines, against a limit of 770: a change that adds a line has to remove one.
`parameters.py` is frozen: a new constant is a departure to register.

The harness (`python -m experiments.harness E1`) writes `outputs/<experiment>/runs.csv` and
`cells.csv`; it uses the standard library only. The figure scripts (`python -m figures.fig1_...`)
need matplotlib and write to `outputs/figures/`. `outputs/` is not versioned.

`python -m experiments.price_rules leader_follow` repeats E0 to E3 under v2's leader-follow rule
with the unit-cost floor (outputs in `outputs/leader_follow/`), `leader_follow_ucs` under the
same rule with v2's operating-cost floor, `leader_follow_overtime` and
`leader_follow_ucs_overtime` with output up to 1.2 times normal capacity without a premium,
`overtime` with the same overtime on v3's own pricing, and `systematic` under v3's
systematic cutting. It is an analysis variant, registered in `docs/design/v3-choices.md`: the
rule is patched in from the script and the model is not changed. Its read is in the plan,
section 9: under leader-follow E0 is met on the price and the profit rate but not on capacity,
and the unit-cost label no longer wins beyond drift at the defaults. The operating-cost floor
gives the same E0 to E3: the floor almost never binds. Overtime cuts the demand lost from 9 to
1 % at the defaults and brings the pilot's reference numbers within range; E0 is still not met
on capacity and the headline does not change. The plan also says why: under leader-follow
every firm posts the same price, so a cost advantage no longer moves market shares. With
overtime on v3's own pricing the unit-cost label wins 0.92 of seeds at the defaults (0.98
without), the demand lost falls from 3.2 to 0.5 %, and E0 is still not met.

`docs/design/v4-final-model.md` (10 November) is the proposal for version 4: overtime, the
accelerator without a target utilisation, normal-price cutting as the default price rule
(systematic cutting above the firm's price of production, cost-edge cutting below it) with
cost-edge cutting, leader-follow and systematic cutting as options, E0 read on averages, a
sensitivity over the reserve, a budget of 1,000 lines with comments excluded and a run viewer.
That default is the best joint fit of E0 and the headline among fifteen rules; none fits both. It is not the specification of this tree: version 3's four documents stay
authoritative here until the group decides, and version 4 is a rebuild.

Next is stage 6: the E4 cells, `experiments/e5_channels.py`, `experiments/morris.py` (SALib) and
figures 4 to 6.

Known after stage 5 (plan, section 9): E0 is not met. At the defaults the industry cycles
between a deep shortage and a long overcapacity, and without technical change cost-edge cutting
stops after two periods, so capacity ends at 1.6 to 2.5 times demand. The diagnosis is in the
plan and in `experiments/diagnosis.py`. The rules are those of the specification. Do not tune a
rule without a decision recorded in `docs/design/v3-choices.md`, and do not present E1 to E6 as
results before the group has decided: the runs of stage 5 are provisional.
