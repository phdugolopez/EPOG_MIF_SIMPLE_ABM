# Prompt: plan the v3 rebuild of the real-competition ABM

Paste everything below the line into a Claude Code session started at the root of the `v3`
worktree (`Projets/ABM-v3`, branch `v3` of `phdugolopez/EPOG_MIF_SIMPLE_ABM`), with the v2
checkout left beside it in `../ABM-sources` as a read-only reference. Written 9 November 2026.

The prompt asks for a plan only and stops. The addendum (section 4) holds proposed defaults for
everything the proposal leaves open: the group confirms or changes them before the plan is
accepted. Then build in the stages the plan defines, one session or one prompt per stage.

---

You are working on the group's agent-based model of one industry in which firms that choose
techniques by the lowest unit cost (Shaikh, hurdle h = 0) compete with firms that choose by the
highest profit rate at an evaluation price (Okishio). Group project, M2 EPOG, course MIP1
(Funalot and Bassi), Python, built on the course template `pierrefunalot/EPOG_MIF_SIMPLE_ABM`.
Version 2 (folder `../ABM-sources`, about 5,100 lines, 25 switches) was analysed with a full
sensitivity analysis; version 3 is a rebuild from a clean tree, about 700 lines of model, that
keeps only what moved the results. Deadlines: code by 16 November, first experiments 17–19
November, seminar 20 November, report 1 December.

Your task now is **a plan, not code**. Write `docs/design/v3-plan.md`, commit it, and stop.

## 1. Read, in this order

1. `docs/design/final-model-proposal.md`. Its sections "The simplified model", "What to drop",
   "Model analysis", "Sensitivity analysis" and "Decisions" are the specification. The other
   sections are rationale: read them, do not implement anything from them.
2. Section 4 of this prompt (addendum). Where it differs from the proposal, the addendum wins.
3. In `../ABM-sources` (v2, read-only), only these files, to port their *logic* (pure functions)
   and not v2's architecture: `equations/innovation_set.py`, `equations/new_technique.py`,
   `equations/technique_choice.py`, `equations/hurdle.py`, `equations/regulating_price.py`,
   `equations/real_competition_price.py`, `equations/market_shares.py`,
   `equations/competitiveness.py`, `markets/goods_market.py`, `equations/merit_order.py`,
   `equations/retirement.py`, `equations/idle_plants.py`, `equations/entry_probability.py`,
   `equations/new_plant_rate.py`, `equations/inherited_rule.py`, `create_entrant` in
   `markets/entry_exit.py`, `analysis/indicators.py` (the share decomposition), and in
   `experiments/sensitivity.py` the Wilson interval, the beyond-drift test and `takeover`.
   Do not read v2's collector, schema, debug suite or the rest of its scheduler.

## 2. What `docs/design/v3-plan.md` must contain

1. **File tree**, one line per file with its purpose and a line budget. Model code (everything
   but tests, experiments and figures) at most 700 lines. Keep the template layout:
   `equations/` (one rule per file, pure functions, named `<step>_<equation>.py`, see
   section 3), `markets/`, `model/` (`entities.py`,
   `model.py`, `scheduler.py`, `outputs.py`), `parameters.py`, `run.py`, `tests/`,
   `experiments/`, `figures/`.
2. **Data structures** (dataclasses) for technique, plant, firm and industry, with v2's names
   for state (`price`, `share`, `sales`, `capacity`, `util`, `kappa`, `hurdle`, `cash`).
3. **The period loop in pseudocode**, step by step: what each step reads, what it writes, when
   the hurdle, the regulating price and the construction lag act.
4. **Every equation** with its file name, its function signature, a one-line docstring and the
   v2 function it ports from (or "new").
5. **`parameters.py`** as it will be: every parameter with its default, matching the proposal's
   parameter table and the addendum; every switch with its levels.
6. **Output tables**: one row per period and label, one row per run. List the columns with
   their formulas, including the share decomposition ported from `analysis/indicators.py`, the
   mechanism observables of the proposal and the Marx-bias measures (growth of labour and of
   capital per unit, by label).
7. **Experiment harness**: cells × populations (mixed and the two controls) × seeds; parallel
   runs with `multiprocessing`, one industry per process, results in seed order; `runs.csv` and
   `cells.csv` appended as cells finish, with resume; Wilson intervals and the beyond-drift test;
   Morris screening with SALib; one script per report figure. Experiments E0–E7 of the proposal,
   with priorities: E0–E4 first, then Morris and E5, then E6, E7 and the robustness checks.
8. **Tests**, each with what it asserts: one per mechanism; the label swap (labels swapped
   everywhere except the hurdle mapping give identical trajectories); money conservation every
   period; reproducibility (same seed, same run); symmetric controls (per-firm streams).
9. **Stages**: an ordered build, each stage ending with the tests passing and a commit, with an
   estimate of its time. Mark the stages the four mechanism owners can do in parallel once the
   data structures and the loop exist (pricing: Jake; demand, entry and exit: Pierre-Loup;
   scrapping, accounts and outputs: Vincent; hurdle, technical change and investment: Ugo).
10. **Open questions**: anything still ambiguous after the addendum, each with your proposed
    default. Do not choose silently.

## 3. Rules for the build (copy them into a new, short `CLAUDE.md` as stage 1)

- The specification is the source of truth. Any departure goes into `docs/design/v3-choices.md`
  (what, why, date) before the code changes; never diverge silently.
- Neutrality: the type label is read only to look up the hurdle rule and in inheritance at
  entry. Ties are never broken by firm order or id. The label-swap test must always pass.
- Build nothing outside the specification: no debt, interest or bankruptcy, no overtime, no
  anchor pricing, no logit demand, no replacement of working plants, no capital advanced (τ), no
  plants without a maximum age, no debug suite, no switch that the proposal does not list.
- Equation files are named `equations/<step>_<equation>.py`, where `<step>` is the loop step
  that uses the equation: `setup` (initial population), `pricing`, `demand`, `accounts`
  (production and accounts), `scrapping`, `investment` (technical change included) and `entry`
  (entry and exit), plus `common` for a definition several steps use (unit cost, profit rate at
  a price, hurdle, technique choice, regulating price). Examples: `pricing_floor.py`,
  `demand_replicator.py`, `scrapping_idle_plants.py`, `investment_draw_marx.py`,
  `common_unit_cost.py`. Scheduler step functions and test files follow the same step names
  (`set_prices`, `tests/test_pricing.py`).
- Every step computes all firms from the state at the start of the step (simultaneous moves),
  so the order of firms never matters.
- One random stream per firm and one for the industry, from `numpy.random.SeedSequence(seed)`;
  no other source of randomness.
- Every money flow goes through one payment function; assert money conservation each period.
- Python 3.12 or later; dependencies numpy, pandas, matplotlib, SALib.
- Speed: a 200-period run must take no longer than v2's (0.11 s on one core); profile if it does.
- Commit at the end of each stage on branch `v3`; never push.

## 4. Addendum: proposed defaults for what the proposal leaves open

A1 **Units.** A technique stores labour per unit `l` and capital per unit `kappa`. Operating cost
   ucs = w_t·l with w_0 = 1 and w_t = (1 + g_w)^t, capital goods priced 1; g_w = 0 by default
   (E7 only varies it), which is v2's setting. Initial techniques (Shaikh 2016, Tables
   7.10–7.11): C l = 64.25, κ = 137.50; D1 l = 61.77, κ = 142.31; D2 l = 59.21, κ = 157.89.

A2 **Initial population.** k firms for each (technique, rule) pair, (C, D1, D2) × (unit-cost,
   profit-rate), identical within pairs: 6k firms, k = 1 by default (robustness: k = 2 and 5,
   that is 12 and 30 firms). Plants of S = 20; plants per firm = round(normal output / 20): C 6,
   D1 6, D2 7 (capacity 760 for k = 1). Price 100, cash 0, share = capacity share, previous
   sales = share × demand. Demand D_0 = k × (340/383) × 760 = k × 674.7: demand scales with k,
   so firm size and plant indivisibility stay the same and only the number of firms changes.

A3 **Plant life and initial ages.** T = 10 and δ = 1/T: depreciation is straight-line over the
   plant's life, so the book value is zero when it retires. δ is derived from T, so the Morris
   screening varies T (5–20) in place of δ, and the "plant life" robustness check of the
   proposal becomes "scrapping on unit cost (v2)". Initial plants get staggered ages
   a_k = floor(k·T/n) for plant k = 0…n−1 of each firm, with book value κS(1 − a_k/T), so that
   retirements spread over the first T periods instead of all falling at t = T.

A4 **Construction lag.** A plant ordered in period t produces from t + 1. Desired capacity and
   entry count plants on order.

A5 **Pricing.** R = lowest price posted last period (own price included when following, rivals
   only when undercutting). Shortage = last period's demand above total normal capacity. After a
   shortage a firm moves up to the next higher rival price; a firm with no rival above raises by
   0.5 × the excess-demand share. Otherwise: undercut to (1 − c)R if it has spare capacity (last
   period's utilisation below 1) and, under cost-edge cutting, a unit-cost edge over a firm
   posting R; else follow R. A price never rises except after a shortage. Floor in both regimes:
   the unit cost (w_t·l + δκ) of the firm's lowest-unit-cost plant in operation.

A6 **Demand.** `share` is the notional replicator share, kept separate from the realised sales
   share. Notional demand = share × D_t. Sales = min(notional demand, offered capacity), where
   offered capacity is the normal capacity of plants whose operating cost is at most the firm's
   price; unserved demand is re-allocated once, pro rata to spare offered capacity; the rest is
   lost and recorded.

A7 **Investment.** Retained earnings: funds = min(cumulative profit after depreciation, minus
   dividends, minus spending on plants; cash); buy floor(funds / (κ*·S)) plants of j*.
   Accelerator: desired capacity = notional demand / u*; buy ceil((desired − capacity − on
   order) / S) plants of j*, as far as cash pays.

A8 **Hurdle timing.** h is computed at the investment step from the evaluation price p^e built
   from the firm's price this period. The regulating technique R (lowest unit cost among plants
   in operation, at this period's wage) is computed once per period before scrapping, the same
   for every firm. An entrant computes h at its entry price.

A9 **Technical change.** Each period each firm with plants draws one design with probability π,
   relative to its best known technique by its own rule, and keeps it if its rule prefers it
   (ties keep the existing technique). A design becomes known to every firm L periods after its
   first plant enters production. An entrant knows the initial menu, every technique in use and
   the public designs.

A10 **Entry and exit.** r_new = capacity-weighted realised rate (plant profit / purchase cost) of
   the plants built in the last 5 periods. At most one entrant a period, with probability
   min(1, θ·max(0, r_new − r̄)/r̄); its rule is copied from an incumbent drawn by share and
   flipped with probability μ; its price = the lowest posted price; capacity = 0.5 × the average
   incumbent capacity, in whole plants, arriving next period; initial share = its capacity /
   (incumbents' next-period capacity + its capacity), incumbents' shares scaled down (v2
   `create_entrant`). Exit when the share falls below 1 % or no capacity is left, never below 2
   firms; an exiting firm's cash goes to the rest-of-economy account.

A11 **Winner.** A seed is decided if producing capacity is positive at t = 200; the unit-cost
   label wins if it holds more than half of it. Populations: mixed (each label on its own rule)
   and two controls (both labels on one rule), same seeds.

A12 **Invasion (E6), to confirm.** Ten firms on D1 with equal capacity: 9 residents of one rule
   and 1 mutant of the other; the control puts the mutant on the residents' rule. The measure is
   the mutant label's capacity share at t = 200 against its initial 0.1.
