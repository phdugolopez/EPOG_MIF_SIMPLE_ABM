# Prompt: plan the v3 rebuild of the real-competition ABM

Paste everything below the line into a Claude Code session started at the root of the `v3`
worktree (`Projets/ABM-v3`, branch `v3` of `phdugolopez/EPOG_MIF_SIMPLE_ABM`), with the v2
checkout left beside it in `../ABM-sources` as a read-only reference. Written 9 November 2026;
revised the same day after the review of the proposal (E7 dropped, E3 crossed with r̄,
depreciation reserve in A7, open points in A13) and on 10 November after the v2 pilot (replacement
condition in A7, ties in A11).

The prompt asks for a plan only and stops. The addendum (section 4) holds proposed defaults for
everything the proposal leaves open: the group confirms or changes them before the plan is
accepted. The v2 pilot of the proposal (section "Pilot in v2") was run on 10 November: do not
paste the prompt before the group has confirmed the specification. Then build in the stages the
plan defines, one session or one prompt per stage.

---

You are working on the group's agent-based model of one industry in which firms that choose
techniques by the lowest unit cost (Shaikh, hurdle h = 0) compete with firms that choose by the
highest profit rate at an evaluation price (Okishio). Group project, M2 EPOG, course MIP1 (Funalot
and Bassi), Python, built on the course template `pierrefunalot/EPOG_MIF_SIMPLE_ABM`. Version 2
(folder `../ABM-sources`, about 5,100 lines, 25 switches) was analysed with a full sensitivity
analysis; version 3 is a rebuild from a clean tree, about 600 lines of model (700 at most), that
keeps only what moved the results. Deadlines: code by 16 November, first experiments 17–19
November, seminar 20 November, report 1 December.

Your task now is **a plan, not code**. Write `docs/design/v3-plan.md`, commit it, and stop.

## 1. Read, in this order

1. `docs/design/final-model-proposal.md`. Its sections "The simplified model", "What to drop",
   "Model analysis", "Sensitivity analysis" and "Decisions" are the specification. The other
   sections are rationale: read them, do not implement anything from them. The section "Pilot in
   v2" concerns version 2 only: nothing in it is built in v3.
2. Section 4 of this prompt (addendum). Where it differs from the proposal, the addendum wins.
3. In `../ABM-sources` (v2, read-only), only these files, to port their *logic* (pure functions)
   and not v2's architecture: `equations/innovation_set.py`, `equations/new_technique.py`,
   `equations/technique_choice.py`, `equations/hurdle.py`, `equations/regulating_price.py`,
   `equations/real_competition_price.py`, `equations/market_shares.py`,
   `equations/competitiveness.py`, `markets/goods_market.py`, `equations/merit_order.py`,
   `equations/retirement.py`, `equations/idle_plants.py`, `equations/entry_probability.py`,
   `equations/new_plant_rate.py`, `equations/inherited_rule.py`, `create_entrant` in
   `markets/entry_exit.py`, `analysis/indicators.py` (the share decomposition), `wilson` in
   `experiments/neutral_control.py`, and in `experiments/sensitivity.py` the beyond-drift test and
   `takeover`. Do not read v2's collector, schema, debug suite or the rest of its scheduler.
4. `docs/design/v3-choices.md`, the register of the decisions already taken. Nothing else: the
   other files of `docs/design/` and the `README.md` describe version 2 (`choices.md` is its
   frozen record) and are not the specification.

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
6. **Output tables**: one row per period and label, one row per run. List the columns with their
   formulas, including the share decomposition ported from `analysis/indicators.py`, the mechanism
   observables of the proposal and the Marx-bias measures (growth of operating cost and of capital
   per unit, by label).
7. **Experiment harness**: cells × populations (mixed and the two controls) × seeds; parallel runs
   with `multiprocessing`, one industry per process, results in seed order; `runs.csv` and
   `cells.csv` appended as cells finish, with resume; Wilson intervals and the beyond-drift test;
   Morris screening with SALib; one script per report figure. Experiments E0–E6 of the proposal,
   with priorities: E0–E3 first (they are shown at the 20 November seminar), then E4, E5 and
   Morris, then E6 and the robustness checks.
8. **Tests**, each with what it asserts: one per mechanism; the label swap (labels swapped
   everywhere except the hurdle mapping give identical trajectories); money conservation every
   period; the depreciation reserve (with r_new ≥ r̄ a firm with no profit still replaces a plant
   that retires at age T; with r_new < r̄ the reserve is paid out and the plant is not replaced;
   funds never exceed cash); reproducibility (same seed, same run); symmetric controls (per-firm
   streams).
9. **Stages**: an ordered build, each stage ending with the tests passing and a commit, with an
   estimate of its time. Stage 1 also writes the new `CLAUDE.md` (section 3) and replaces the
   version 2 `README.md`. Mark the stages the four mechanism owners can do in parallel once the
   data structures and the loop exist (pricing: Jake; demand, entry and exit: Pierre-Loup;
   scrapping, accounts and outputs: Vincent; hurdle, technical change and investment: Ugo).
10. **Open questions**: anything still ambiguous after the addendum, each with your proposed
    default. Do not choose silently.

## 3. Rules for the build (copy them into a new, short `CLAUDE.md` as stage 1)

- Four documents are authoritative: `docs/design/final-model-proposal.md`,
  `docs/design/v3-planning-prompt.md`, `docs/design/v3-plan.md` and `docs/design/v3-choices.md`.
  Everything else in `docs/design/` describes version 2: take no rule, default or file layout from
  it.
- The specification is the source of truth. Any departure goes into `docs/design/v3-choices.md`
  (what, why, date) before the code changes; never diverge silently.
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

A1 **Units.** The money wage is the numéraire (w = 1) and capital goods are priced 1, as in v2. A
   technique stores its operating cost per unit `ucs` and its capital per unit `kappa`; there is
   no wage path (E7 was dropped on 9 November). Initial techniques (Shaikh 2016, Tables 7.10–7.11,
   p. 315, with δ = 0.10): C ucs = 64.25, κ = 137.50; D1 ucs = 61.77, κ = 142.31; D2 ucs = 59.21,
   κ = 157.89.

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
   the unit cost (ucs + δκ) of the firm's lowest-unit-cost plant in operation.

A6 **Demand.** `share` is the notional replicator share, kept separate from the realised sales
   share. Notional demand = share × D_t. Sales = min(notional demand, offered capacity), where
   offered capacity is the normal capacity of plants whose operating cost is at most the firm's
   price; unserved demand is re-allocated once, pro rata to spare offered capacity; the rest is
   lost and recorded.

A7 **Investment.** Investible funds F accumulate profit after depreciation, minus dividends, minus
   spending on plants, plus the depreciation reserve of a plant that leaves (retired at age T,
   scrapped or idle: its purchase cost minus its book value; the remaining book value is a
   write-off, as v2's `firm.write_offs`) if r_new ≥ r̄ in that period. r_new is the signal of
   entry (A10), computed once per period before any plant retires, the same for every firm; with
   no plant in its window the reserve is released. If r_new < r̄ the reserve is withdrawn: the
   firm pays it to the rest-of-economy account, as far as its cash allows, and it is never
   invested. Retained earnings: funds = min(F, cash); buy floor(funds / (κ*·S)) plants of j*.
   Replacement is thus paid out of depreciation when new plants earn the general rate, and net
   expansion out of retained profit. Decided 10 November after the v2 pilot (proposal, section
   "Pilot in v2"): with profits alone the profit rate settles at (δ + g)/(1 − d), with the reserve
   always released at g/(1 − d), with this condition around r̄; a condition on the firm's own
   technique favours the profit-rate rule and was rejected. An initial plant releases its full
   purchase cost although part of it was depreciated before t = 0; the cash cap covers that.
   Accelerator: desired capacity = notional demand / u*; buy ceil((desired − capacity − on order)
   / S) plants of j*, as far as cash pays.

A8 **Hurdle timing.** h is computed at the investment step from the evaluation price p^e built
   from the firm's price this period. The regulating technique R (lowest unit cost among plants in
   operation) is computed once per period before scrapping, the same for every firm. An entrant
   computes h at its entry price.

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
   label wins if it holds more than half of it, loses with less than half, and an exact tie at one
   half is counted apart: the share won is wins over wins plus losses, and the mean final capacity
   share is reported beside it (decided 10 November: the pilot had up to 73 ties in 200 seeds).
   Populations: mixed (each label on its own rule) and two controls (both labels on one rule),
   same seeds.

A12 **Invasion (E6), to confirm.** Ten firms on D1 with equal capacity: 9 residents of one rule
   and 1 mutant of the other; the control puts the mutant on the residents' rule. The measure is
   the mutant label's capacity share at t = 200 against its initial 0.1.

A13 **Open points from the review of 9 November.** Not decided: the plan must list each under
   "Open questions" with a proposed default.
   (a) Entrant's menu: the proposal says the public menu, A9 says every technique in use, which
       lets entry bypass the lag L.
   (b) Scrapping: which price is compared with ucs (proposed: the owner's posted price), whether
       the 2 periods are consecutive, and what "idle" means (proposed: no output for 2 consecutive
       periods).
   (c) Entrant's funding: who pays for its plants (proposed: equity from the rest-of-economy
       account, as v2's `equity_in`); money conservation needs it.
   (d) E6: the demand for ten firms on D1, and μ = 0 during invasion runs so that entry adds no
       mutant.
   (e) Ties: equal technique costs, equal prices, and several firms meeting the exit test when
       only some may leave (floor of 2 firms).
   (f) Morris on T: δ = 1/T moves the unit costs of the initial menu, and below T ≈ 6.1 D1, not
       D2, has the lowest unit cost (proposed: range 7–20).
   (g) "Scrapping on unit cost (v2)" as a robustness check: with or without the maximum age.
   (h) Names: R is both the lowest posted price (A5) and the regulating technique (A8); k is the
       firms per pair (A2), a plant index (A3) and the bias draw in the proposal. Use distinct
       names in the code.
   (i) Constants outside the proposal's parameter table (0.5 × the excess-demand share in A5, the
       1 % exit share, the 5-period entry window, the 2 scrapping periods, the entrant's size of
       0.5): list them in `parameters.py`.
   (j) The withdrawn reserve (A7): paid to the rest-of-economy account (proposed), or left in the
       firm's cash as in the pilot.
   (k) Initial cash: 0 (A2), or the depreciation already accumulated on the initial plants, which
       would back the reserves they release (proposed).
   (l) In the pilot no plant left through the operating-cost test (40 seeds of three cells):
       plants leave by age or idleness. Check whether the test ever binds in v3.
