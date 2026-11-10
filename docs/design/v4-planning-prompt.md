# Prompt: review the v4 proposal for coherence, then plan the rebuild

Paste everything below the line into a new Claude Code session started at the root of
`Projets/ABM-v3` (branch `v3`). Written 10 November 2026.

Before pasting, commit `docs/design/v4-final-model.md`: the session reads the working tree, and
the edit that scales the menu with the general rate is not committed yet.

The session writes documents only: a coherence review, then, after your answers, a plan. It
writes no code and starts no build. The tree in which version 4 is built is one of the points
it asks you to settle; the plan's first stage creates it.

---

You are working on the group's agent-based model of one industry in which firms that choose
techniques by the lowest unit cost (Shaikh, hurdle h = 0) compete with firms that choose by the
highest profit rate at an evaluation price (the profit-rate rule, labelled Okishio). Group
project, M2 EPOG, course MIP1 (Funalot and Bassi), Python. The group is Ugo, Jake, Pierre-Loup
and Vincent; you work with Ugo.

Version 3 is this tree: 769 lines of model code, built on 10 November, with its tests passing.
Its experiments showed that the model as specified does not behave like an industry under real
competition without technical change (experiment E0). A day of runs on v3's code, with rules
patched in from `experiments/price_rules.py`, led to a proposal for version 4:
`docs/design/v4-final-model.md`. A check of that proposal against the literature is in
`docs/design/v4-literature-check.md`. Version 4 is a second rebuild, for a reader this time.
Deadlines: code by 16 November, first experiments 17 to 19 November, seminar 20 November,
report 1 December.

Your task has two phases, in this order, and **no code in either**:

1. **Review** the proposal for coherence and write `docs/design/v4-review.md`. Then stop and
   put to Ugo the points that need his decision.
2. **Plan** the rebuild once he has answered: correct the proposal as agreed, start the
   register `docs/design/v4-choices.md`, write `docs/design/v4-plan.md`, commit, and stop.

`CLAUDE.md` at the root of this tree holds the rules of the v3 build. For this task this
prompt wins: you write no model code here, you do not start stage 6, and "build nothing
outside the specification" refers to a specification that version 4 replaces.

## 1. Read, in this order

1. `docs/design/v4-final-model.md`, whole. It is the specification of version 4: the model,
   the experiments, the sensitivity analysis, the build constraints and the decisions. Its
   numbers are provisional evidence from v3's code, not results.
2. `docs/design/v4-literature-check.md`, whole. It gives, for each mechanism, a verdict against
   the sources and, in its last table, ten changes it proposes. It was written at 12:56 on 10
   November against the proposal as it then stood: a default rate of 0.05, normal-price
   cutting as the default, the entrant at the lowest price, a shortage step of 0.5 and one
   menu at every rate. Each of these has changed since.
3. `docs/design/v3-plan.md`, section 9 only, from "Diagnosis" to the end: the record of every
   run behind the proposal. The last two blocks, "The settings proposed for version 4" and
   "The same settings with a shortage step of 0.25", are the evidence for the default.
4. `docs/design/v3-choices.md`: the decisions of v3 that version 4 keeps unless the proposal
   says otherwise, and the section "Analysis variants", which defines each rule that was run.
5. The code of v3, as the reference to port from: `parameters.py`, `model/`, `markets/`,
   `equations/`, `experiments/harness.py`, `experiments/summary.py`, `experiments/stats.py`,
   `experiments/cells.py`, `figures/style.py`, and `tests/`. Read
   `experiments/price_rules.py` closely: it holds, as patches, the rules that version 4 makes
   options of the model (overtime, the undercutting entrant, normal-price cutting,
   leader-follow, the operating-cost floor).

Not the specification: `final-model-proposal.md` and `v3-planning-prompt.md` (the v3
specification, which the proposal replaces and restates) and every other file of
`docs/design/` (version 2).

You may read `outputs/` and run an existing command to check a number, for example
`python -m experiments.price_rules v4_cost_edge E0`. Use `python3`; matplotlib is only in
`../ABM-sources/.venv/bin/python`. Install nothing.

## 2. Phase 1: the coherence review

Write `docs/design/v4-review.md`. The question is whether a careful reader could build the
model from the proposal alone and get one model, and whether what the proposal claims is what
the runs and the sources support.

Check four things.

- **The proposal against itself.** Every rule, default and count is stated once or stated the
  same way everywhere: "At a glance", the table of changes, the schedule, the parameter
  table, the experiments, the decisions. Every rule is complete enough to code: what it reads,
  what it writes, in which step, and what happens in a tie or at a boundary.
- **The proposal against its evidence.** Each number comes from a run whose settings are those
  the proposal now specifies. Mark each statement that rests on other settings, on 50 or 100
  seeds, or on no run.
- **The proposal against the literature check.** For each verdict of "departure", "no source"
  or "to reword", and for each of the ten proposed changes, say whether the proposal took it
  up, contradicts it or leaves it open. Say where the check judged a rule that is no longer
  the default, and whether its verdict still holds.
- **The proposal against its own build constraints.** Whether the model it describes fits in
  1,000 lines counted as it says, given v3's 769, and what the run viewer needs from the
  model.

Points already known, to verify and not to take on trust:

- "At a glance" announces six changes; the table of changes has fifteen rows.
- The menu scaled with the general rate (row 15, added last) is not run. Every number at a
  rate other than 0.16 comes from the fixed menu. The section "Why not 5 %", row 2 of the
  changes, the row r̄ = 0.05 of "What each setting does", the second row of E3 and the
  decision "The other level of r̄" argue from that menu. Under the scaled menu the price of
  production stays at 100, so the argument that 5 % puts it only 10 % above the unit cost no
  longer holds.
- A rate of 0.10 is not run under either menu. What β should be at a rate other than 0.16 is
  open in the decisions table.
- What the scaled menu changes at the start is not stated: the cost of a plant, the initial
  cash (the depreciation accumulated on the initial plants), the entrant's equity, and the
  floor on the rate (0.034).
- The literature check proposes to read E0's profit-rate line on r_new, to add single-rule
  runs with draws to E0, to rename leader-follow, to put the threshold of normal-price cutting
  on the regulating price of production, to say once that the model's "operating cost" is
  Shaikh's prime cost, and to present the reserve condition and idle scrapping as devices
  without a source. The proposal does none of these, and still says "Literature: unchanged".
- The proposal names the option for the entrant's price `params.entry_cut` in one place and
  describes it only as a robustness check in the parameter table.
- The default was run with the two labels realising the same profit rate (0.148 and 0.151);
  with a shortage step of 0.5 the unit-cost label realised the higher one. H6 changes sign
  with a parameter the proposal treats as a speed of adjustment.
- Under the accelerator the headline is within drift at the default step (0.56 on 100 seeds),
  where it was 0.84 with a step of 0.5. E4 crosses the investment rule.
- E3 under the three other price rules, E4, E6, Morris and most robustness checks are not run
  with the proposal's settings.

Format of the review:

- A summary of five lines at most: can the model be built from the proposal as it stands,
  and what must be settled first.
- One table of findings: where (section of the proposal), what, kind (contradiction, gap,
  stale evidence, against the literature check, unclear rule), the correction you propose,
  and whether it blocks the plan.
- A list of the questions for Ugo, each with your recommended answer and what it costs.
  Only the findings he must decide; settle the others yourself in the table.

Then stop. Ask Ugo the blocking questions and wait for his answers. Do not edit
`v4-final-model.md` in this phase.

## 3. Phase 2: the plan

After his answers:

1. Apply the agreed corrections to `docs/design/v4-final-model.md`, in one commit, so that the
   specification is coherent before anything is planned from it.
2. Start `docs/design/v4-choices.md`: one row per decision of the review (what, why, date,
   status), then an empty table "Departures from the specification".
3. Write `docs/design/v4-plan.md`. It must contain:
   - **Where version 4 is built** and how the tree is created, as decided.
   - **File tree**, one line per file with its purpose and its line count, and the total
     against 1,000 lines counted as the proposal says.
   - **What comes from v3**, file by file: ported as it is, rewritten for a reader, or
     dropped, with the reason. The patches of `experiments/price_rules.py` become options of
     the model; nothing in version 4 replaces a function of the model from outside.
   - **Data structures** for technique, plant, firm and industry.
   - **The period loop in pseudocode**, step by step: what each step reads and writes, and
     where overtime, the entrant's price, the reserve option and the scaled menu act.
   - **Every equation**: file name, signature, formula, and its paragraph of the proposal.
   - **`parameters.py` as it will be**: every parameter with its default and every option
     with its levels, matching the proposal's parameter table.
   - **Output tables**: the period table and the run row, with the E0 measures as columns.
   - **Experiments**: E0 to E6, the sensitivity over the reserve, Morris and the robustness
     checks, as cells of the harness with their run counts and priorities. E0 is the gate: it
     is run and read before any other experiment.
   - **The run viewer**: its command, its inputs, its files and its panels, and how it
     steps the model without a recorder in the model.
   - **Tests**, each with what it asserts, including the label swap and the firm order under
     every price rule and investment rule.
   - **Readability**: how the rules of "Rebuilding the code" are checked, and one step
     function written out in full as the example of the style.
   - **Stages**: an ordered build, each stage ending with its tests passing and a commit,
     with a time estimate, and the parts the four members can write in parallel. An early
     stage reruns, on the new code, what the proposal marks as not run under its own
     settings, starting with the scaled menu at the other level of the rate.
   - **Open questions**: anything still unclear, each with your proposed default.
4. Commit and stop. Do not start the build.

## 4. Rules for both phases

- The proposal is the source of truth for the model. Where it is silent, v3's decisions
  (`v3-choices.md`) hold. Where the review finds it wrong, the correction is proposed to Ugo
  and recorded, never applied silently.
- Do not present a provisional number as a result. Every number you quote names its run:
  rule, rate, seeds.
- Do not change the code, the tests or the outputs of v3. Do not rerun experiments beyond
  checking a number.
- Write as the proposal is written: plain English, short sentences, tables for comparisons,
  one idea per bullet. Give page or section references when you cite a source or a document.
- Commit on branch `v3`, never push. Commit messages end with the attribution line your
  session is configured with.
