# Prompt: reading the sensitivity results against the literature (between steps 4 and 5)

Paste everything below the line into a Cowork session started at the root of a checkout of
branch `feature/sensitivity` of the group's real-competition ABM, with the folder of papers
and books on the subject available to it. Written 8 November 2026, after the first full
sensitivity analysis (`docs/design/sensitivity-results.md`).

## Running it unattended (6 hours at most)

The prompt below has a reading part and a computing part. Paste this header first; it sets
the budget and answers in advance the questions the session would otherwise stop for.

> **Unattended run, 6 hours at most.** Nobody answers during the run. Decisions:
> (1) Time boxes, from the start of the run: inventory and reading until 0:45; Part A
> (findings against the literature) drafted by 2:15; Part B (computations) from 1:30 to
> 4:45, long runs started in the background while you write; figures and integration until
> 5:30; tests, commits and the summary until 6:00. Whatever is unfinished at a box's end is
> written up as unfinished, with what is missing, and the run goes on. (2) Of the three
> tracks of Part B, run track B1 (mechanism, on existing data) in full; run B2 (more
> cells) and B3 (rule changes) only as far as section 6's compute budget allows, B2 before
> B3, and only the items Part A made necessary; say in the discussion which items you did
> not reach and why. (3) A rule change (B3) is implemented only behind a new switch whose
> default reproduces the current model exactly (`python -m debug.compare_runs`), with the
> label-swap test, and is recorded in `choices.md` as a *candidate*, never as a decision.
> No default in `parameters.py` moves. (4) Where these instructions conflict with the code
> or with `choices.md`, follow the code, record the conflict in the discussion and go on.
> (5) Work on a branch `feature/analysis` cut from `feature/sensitivity`; one commit per
> part, tests passing before each commit; never push. (6) Cite the texts you have read in
> the library by page; a claim you make from memory about a text you could not open is
> marked "(from memory, not checked)". (7) The last 30 minutes are for the summary even if
> a computation is still running: report it as running and say how to read its output.

A laptop does about 7 runs a second per core on the version 2 defaults (0.14 s per
`Industry.run()`, 0.25 s with the innovation set, 3 s with 3 % demand growth), so 500 seeds
× 3 populations of one default cell take about 4 minutes on 10 workers. Section 6 sizes
the computations from that.

---

You are working in the group's real-competition ABM (Shaikh against Okishio), a Python
model built on the course template `pierrefunalot/EPOG_MIF_SIMPLE_ABM`. The first full
sensitivity analysis of version 2 has been run (86 400 runs, 220 cells, three stages) and
written up in `docs/design/sensitivity-results.md`. Your task is to **make sense of those
results**: read them against the literature the group works from and against the research
question, illustrate each finding with concrete runs and figures so that the group
understands what the model does and why, and then go further where the results leave a
hole, in one of three directions: more sensitivity cells, a deeper look at a mechanism, or
rule changes under which the profit-rate rule can dominate. The outcome is a discussion
document the group reads before the simulated seminar of 20 November and the choice of the
fixed version (step 5 of `docs/design/review-v2.md`).

## 0. Read first, then inventory

In this order:

1. `CLAUDE.md`: the neutrality rule, the conventions, who owns which file, and "Adding an
   alternative rule behind a switch". It binds you, in particular for track B3.
2. `docs/design/sensitivity-results.md` in full, then `docs/design/sensitivity-plan.md`
   (section 7: the decisions the run followed) and the "Sensitivity analysis" section of
   `docs/design/choices.md` (factor table with its "Result" column; "Choices made running
   it"; the two neutral-control records).
3. The seven figures in `outputs/sensitivity/figures/` and the four `debug.report` runs in
   `outputs/sensitivity/reruns/` (regenerate a PDF with `python -m debug.report
   outputs/sensitivity/reruns/RUN_ID` if it is missing; `debug/README.md` says what each
   page shows).
4. `docs/design/mechanism-briefs.md` (the research question, the notation, the six
   mechanisms and the *trap* each one names: the anchor price, χ, the quantity and finance
   rules, entry as a third choice of technique) and `docs/design/review-v2.md` sections 2.2
   (the contest version 2 sets up) and 4 (the innovation set).
5. `parameters.py` in full, `equations/hurdle.py`, `equations/technique_choice.py`,
   `equations/innovation_set.py`, `equations/new_technique.py`, `markets/entry_exit.py`
   and the pricing equations, so that you describe rules as they are coded, not as the
   briefs proposed them.
6. **The library.** Inventory the papers and books you have access to and list, in the
   discussion's appendix, which of these you could open with the pages you used: Shaikh
   (2016) *Capitalism*, chapter 7 (real competition, Table 7.3, pp. 264–290, pp. 313–321 on
   the choice of technique, Tables 7.10–7.11) and chapter 8 (turbulent equalisation);
   Okishio (1961) and the later debate on the theorem (Roemer; Shaikh 1978; Duménil & Lévy
   on the "classical–Marxian" rule of technical change and on the viability of innovations
   at expected prices; Foley; Michl 2023 on the two adoption rules and when they
   conflict); Salter (1966) on vintages and the replacement margin; Nelson & Winter (1982)
   and Metcalfe (1998) on replicator selection and the gap between selection on costs and
   selection on profitability; Dosi et al. (2015) and Foster, Haltiwanger & Syverson (2008)
   on how weak selection is in the data; Dosi & Roventini (2025) on K+S investment, finance
   and entry; Seppecher, Salle & Lavoie (2018); Silverberg, Dosi & Orsenigo (1988) on
   diffusion; Botwinick (1993) and Tsoulfidis & Tsaliki (2019) on regulating capitals;
   Marx, *Capital* III, chapters 13–15 and the "cheapening" passages on technique choice
   at prices of production; and anything else in the library that bears on the contest.
   Add what you find that this list misses. Read the pages that matter before writing
   Part A; do not write Part A from memory.

Then set up the environment if needed (`python3 -m venv .venv && .venv/bin/python -m pip
install -r requirements.txt`), run `python -m unittest discover -s tests` (229 tests must
pass) and `python run.py`, and check that `outputs/sensitivity/runs.csv` is present and
has 86 400 rows (if only `runs.csv.gz` is there, decompress it; `runs.parquet` is the
same table).

## 1. The question and what the literature predicts

Open the discussion with a table that turns the literature into predictions the results
can meet or fail, one row per claim: the claim, who makes it and where, the observable of
`runs.csv` or `cells.csv` that bears on it, what the results say, verdict (met, failed,
not testable with this design). At least these rows, with the pages:

- Shaikh: in real competition the firm with the lowest unit cost sets the price and
  survives even when its technique earns a lower profit rate at the going price; a
  capital-using, cost-reducing technique spreads through price cutting and the general
  profit rate falls (chapter 7, section on the choice of technique; the regulating
  capital). Observables: share won, `d_share_price`, `leader_lowest_cost_share`,
  `price_to_pp`, `profit_rate_total`, `price_rise_after_adoption`.
- Okishio: a technique that raises the profit rate at current prices cannot lower the
  general profit rate once prices settle, at a constant real wage; a technique that does
  not pass this test is never adopted by a rational capitalist. Observables:
  `okishio_dearer`, `profit_rate_okishio` against `profit_rate_shaikh`, `price_end` against
  `price_mean_50`, the price signature of figure 5.
- Duménil & Lévy and Michl: whether the two rules conflict depends on the direction of
  technical change (Marx bias) and on the price at which the rule is evaluated; the
  profit-rate rule is right if prices do not fall after adoption. Observables: the zone
  shares, `marx_biased_*`, `gamma_*`, `chi_*`, and the anchor cells where prices are held.
- Nelson & Winter, Metcalfe: selection on realised profitability drives accumulation,
  selection on price drives market share; the balance depends on finance and on the
  intensity of selection. Observables: `d_share_accum` against `d_share_price`, the
  finance arm, CHI (which did not move the outcome, against the briefs' trap: explain).
- Salter: the vintage spread and the replacement margin; who replaces first. Observables:
  `ucs_spread_mean`, `capital_age_*`, `replacements_*`.
- Shaikh on entry: entry equalises the profit rate on new investment and is the carrier of
  the winning rule in the long run. Observables: `entries`, `d_share_entry`, `d_share_exit`,
  `r_new_mean`, `periods_above_rbar`, the rbar 0.16 cells.

## 2. Part A: the findings read against the literature

One section per finding of `sensitivity-results.md`, in this order: the base result and
its controls; no technical change means no contest; categories against the innovation set;
the channel (prices, then exits, not accumulation); the mechanism (`okishio_dearer`);
realised profit rates and prices (the unit-cost firms earn more and sell dearer); the two
reversals (`anchor_r16`; `lf-re-g01-cat-r16` against its finance twin); the factors that
move nothing; demand met and turnover; Marx bias as an outcome; the price signature.

For each: what the result is (numbers with their cell and seeds, from `cells.csv`), what
the literature predicted (section 1's row), whether it agrees, and **one concrete
example**: a seed-level story told from a rerun (`python -m experiments.sensitivity rerun
RUN_ID` writes the run's tables to `outputs/sensitivity/reruns/RUN_ID/`; then
`debug.report`, `debug.firm_panel`, `debug.events_timeline`, `debug.capacity_bridge` on
that folder), with the periods at which things happen: when the first dearer technique is
ordered, what the price does afterwards, who exits and why. Use the four reruns already
there first (base seed 1 is a seed the profit-rate rule wins, base seed 4 a typical
takeover at t = 93, `1_lf_mixed_s1`, `2_rc-re-static-is15-r16_mixed_s1`) and add the
reruns the reversals need (a seed of `anchor_r16` and one of `lf-re-g01-cat-r16` and its
twin `lf-acd-g01-cat-r16`, same seed).

Where a result contradicts the literature or the briefs' expectations, say so plainly and
propose a reading; where the model cannot test a claim (for example the real wage is fixed
by the numéraire, so Okishio's constant-real-wage condition holds by construction), say
that too. Two points deserve their own paragraphs because they decide how the group will
present the model: (a) the profit-rate rule does not realise the higher profit rate,
although it maximises it at the current price: is this Shaikh's argument (prices fall
after the cost-cutters' adoptions, so the dearer technique's rate is never earned), or a
market-structure effect (the winners are leaders in a less competitive market)? Track B1
answers this with data; Part A states the two hypotheses. (b) `no_tech` at drift: the
research question is about technical change, so the technical-change rule is the model,
not a detail; what the categories rule and the innovation set each assume about the
direction of innovation, and which the literature supports.

## 3. Part B: going further

Pick the items Part A made necessary, in the order B1, B2, B3, within section 6's budget.

**B1. Mechanism, on existing data** (no new runs except reruns):

- Open question 2 of the results: regress, over the decided mixed seeds of stage 2
  (`runs.csv`, `stage == 2`, `population == "mixed"`), the realised profit-rate gap
  `profit_rate_shaikh − profit_rate_okishio` and `shaikh_wins` on `okishio_dearer`,
  `price_to_pp`, `hhi_mean`, `n_firms_mean`, `war_episodes`, `d_share_price_all`,
  `d_share_accum_all`, with cell fixed effects or the cell's factor levels as controls.
  Report coefficients with intervals; a plot of the gap against `okishio_dearer`, coloured
  by pricing rule.
- Attribution over the whole run (`_all` columns) rather than the window, per cell, as a
  stacked bar for the cells of section 6 of the results.
- The anchor reversal (open question 1): rerun three seeds of `anchor_r16` the profit-rate
  rule wins, with `debug.report`, and tell the story: when the anchor sets the price, which
  technique each rule orders, what happens to the unit-cost firm's margin, and why entry
  stops. Then the same cell at rbar 0.05 for one seed, where the result is at drift.
- The finance twin (`lf-re-g01-cat-r16` against `lf-acd-g01-cat-r16`): the same seed in
  both, side by side (capacity shares, debt, investment, prices), to say what borrowing
  changes for the profit-rate firms.
- Takeover timing: the distribution of `takeover_t` per cell, and the share of takeovers
  before t = 100, which decides whether the window statistics mean anything.

**B2. More sensitivity cells** (each with both neutral controls, seeds 1..N, through
`python -m experiments.sensitivity grid --cells ... --seeds N` or, if the cell is not in
the script's cell lists, by adding it to a new stage `4` in `experiments/sensitivity.py`
without touching stages 1–3; append to `runs.csv` and `cells.csv` with `stage = 4`):

- `rc-re-g01-cat-r16` at 500 seeds (the real-competition twin of the second reversal,
  0.32 at 100 seeds, not run at 500).
- The rbar threshold of the anchor reversal: anchor at rbar ∈ {0.05, 0.08, 0.11, 0.16},
  200 seeds, to see whether the reversal sets in gradually or at a threshold.
- A finance × CHI block if B1 suggests the accumulation channel needs weak selection:
  `acd` with CHI ∈ {0.25, 0.5} under both pricing rules, 200 seeds.
- A TAU sweep (τ ∈ {0.05, 0.10, 0.15, 0.25}, categories and innovation set), 200 seeds.
  On the fixed menu, τ above about 0.12 makes D2 stop being a conflict case (the briefs);
  yet stage 1's `tau_025` still gives 0.78 beyond drift under the categories rule. Explain
  why drawn designs keep a conflict zone that the menu loses, before spending runs on it.

**B3. Rules under which the profit-rate rule can dominate.** The research question asks
under which conditions each rule wins, so a map of where the profit-rate rule dominates is
part of the answer, provided the condition is a legitimate feature of the economy and not
a construction that hands it the win. Candidates to assess first on paper (what the
literature says, which trap of the briefs it is near), then to implement, at most two,
each behind a new switch with the current behaviour as the default:

- **The price at which the hurdle is evaluated** (`choices.md`: "own"). Okishio's theorem
  is about prices of production, and Duménil & Lévy's capitalist evaluates at expected
  prices. A switch that evaluates the profit-rate hurdle at the leader's price, at the
  industry average, or at the expected price after the cut (the firm's own price times the
  mean ratio of price to cost over a window) changes what the rule sees. Record which price
  Shaikh's text and Okishio's paper each imply.
- **A hurdle at the general rate** (h = rbar instead of the best rate on offer): the
  target-return reading of the profit-rate rule, the K+S payback rule with b = 3 read as
  δ + h. Legitimate if the literature has it; note that it stops being "the best rate at the
  current price".
- **Weak selection with borrowing** is a condition, not a rule: B2's finance × CHI block
  already covers it; report it here if the profit-rate rule wins there.
- **Demand conditions where capacity is the constraint**, where the accumulation channel
  should dominate. Stage 1 says: initially unmet demand alone 0.76 (beyond drift, for the
  unit-cost rule); unmet and growing 2 % 0.46 and 3 % growth 0.43 (at drift, 500 seeds),
  never a reversal. Say why growth only dilutes the contest instead of reversing it.
- **An evolving hurdle** (firms adjust h towards the realised profit rate of their recent
  plants): the plan's "when h evolves". Assess on paper only unless the two implemented
  candidates are done and tested with time to spare.

Each implemented candidate follows the six steps of `CLAUDE.md` ("Adding an alternative
rule behind a switch"): one function in `equations/`, a switch in `parameters.py` with the
current default, a branch in the scheduler step, tests including the label swap and the
switch in `test_switches_run`, a row in `choices.md` marked *candidate (analysis, 8
November 2026)*, and the neutrality check written out (does the new rule hand one type an
advantage by construction?). Prove with `python -m debug.compare_runs` that `run.py` at the
defaults writes identical tables before and after. Then run the candidate's cell with both
controls, 200 seeds, at the base and at the leader-follow defaults, and report the share
won next to the controls. A candidate that reverses the outcome by construction (for
example because it reads `firm.type` anywhere but the hurdle lookup) is a finding about the
model, not a result: say so.

## 4. Figures

Every figure in `outputs/analysis/figures/`, numbered, PNG, with the colours of `style.py`
(Shaikh blue `#2a78d6`, Okishio orange `#eb6834`; techniques as in `debug/_common.py`),
titled with the cell and the seeds, and referenced from the discussion where it is
discussed. Expected at least:

1. A **summary chart of the share won** for the cells of section 6 of the results, with
   the controls' intervals as grey bands, so that the reader sees "beyond drift" at a
   glance.
2. **Seed stories**: for each example of Part A, a two-panel figure (capacity share of
   each label and price over time; orders of dearer techniques and exits marked), from the
   rerun's `macro` and `events` tables.
3. **Profit-rate gap against `okishio_dearer`** (B1), coloured by pricing rule, one marker
   per stage 2 seed, with the regression line.
4. **Whole-run attribution** (B1) as stacked bars for the cells of section 6.
5. **The anchor threshold** (B2) if run: share won against rbar with controls.
6. **The candidate rules** (B3) if run: share won with controls, next to the base.

Make a figure only when it says something a sentence cannot; say in one line under each
what it shows.

## 5. Deliverables and commits

Branch `feature/analysis` from `feature/sensitivity`; never push.

1. `docs/design/sensitivity-discussion.md`: sections 1 (prediction table), 2 (Part A), 3
   (Part B, with what was run and what was not), 4 (what this means for step 5: which
   switches the discussion argues should be fixed choices and which treatments, in the
   form of proposed rows for `choices.md`, not decisions), 5 (open questions left), and an
   appendix listing the texts opened with the pages used and the texts not available.
   Every number carries its cell, population and seeds. Commit after Part A, again after
   Part B.
2. `experiments/analysis.py` (regressions, seed-story figures, stage 4 cells if any) or
   additions to `experiments/sensitivity.py` that leave stages 1–3 unchanged; tests for new
   code in `tests/`.
3. `outputs/analysis/` (tables and figures); new rows appended to
   `outputs/sensitivity/runs.csv` and `cells.csv` with `stage = 4` when cells were run
   (recompress `runs.csv.gz` if `runs.csv` changed; `runs.csv` itself is not committed).
4. Rows in `docs/design/choices.md` for every choice made here and every candidate rule.
5. A final summary (in the chat, not a file): what the literature confirms, what it
   contradicts, which reversal mechanism you can explain, what was run in Part B and what
   it found, what you left undone, and the commits.

## 6. Budget

Compute, at 10 workers: a default cell at 200 seeds with both controls ≈ 1.5 min; 500
seeds ≈ 4 min; innovation-set cells ×1.8; leader-follow cells are a little faster; 3 %
growth ×20 (do not run it). B1 is minutes. B2 in full is about 4 cells × 500 + 12 cells ×
200 ≈ 35 min. B3 is two rules × 2 cells × 200 seeds ≈ 6 min of compute, but most of its
time goes to writing and testing the rule (count 45 minutes per rule). Start every grid in
the background and write while it runs. Measure the first grid's wall time and rescale the
rest; if the machine is slower than this, cut seeds in B2 from 500 to 200 and from 200 to
100 before dropping items, and say so.

## Ground rules

- **No change in behaviour at the defaults.** Model files change only for B3 candidates,
  behind a switch, with `compare_runs` proof and the label-swap test; no default in
  `parameters.py` moves; `firm.type` is read only in the hurdle lookup and entrant
  inheritance.
- **Neutrality.** Every new cell runs its two neutral controls over the same seeds; a
  winner is beyond drift only when the mixed interval is disjoint from both controls'.
- **Seeds 1..N** everywhere; ties never resolved by firm order.
- **Every number carries its configuration**: cell, population, seeds, and the `runs.csv`
  row behind every example.
- **Literature by the page.** What you read, cite; what you could not open, mark.
- One commit per part on `feature/analysis`, tests before each commit, no push. Record every
  choice in `docs/design/choices.md`. Where these instructions conflict with the code or
  with `choices.md`, follow the code, record the conflict and go on.
