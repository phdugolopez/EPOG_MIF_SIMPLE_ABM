# Version 3 choices: decisions and departures from the specification

The specification of version 3 is `final-model-proposal.md` (sections "The simplified model",
"What to drop", "Model analysis", "Sensitivity analysis" and "Decisions") with the addendum of
`v3-planning-prompt.md`. This file is its register: a decision counts once it has a row here, and
any later departure from the specification gets a row (what, why, date) before the code changes.
`choices.md` is the version 2 record, frozen on 9 November 2026.

## Decisions agreed on 9 November 2026

| Decision | Why | Status |
| --- | --- | --- |
| Technical change: the innovation set (Marx-biased, β = 1.5) is the model; the neutral set and "no draws" are its controls; the categories rule is a robustness switch | Both reversals exist only under categories; the innovation set makes the conflict zone an outcome | Agreed |
| Scrapping on operating cost, with a plant life of T = 10 periods | Salter's and Shaikh's margin: capital is sunk, so a plant runs while it covers its operating cost; the finite life retires old vintages, which v2 lacked | Agreed |
| Pricing: one rule with two regimes (cost-edge cutting, systematic cutting) and a common unit-cost floor | The markup floor never lets the hurdle reach 0; one floor makes the regimes differ only in how often firms cut | Agreed |
| Investment rule without debt (retained earnings; accelerator) | Borrowing is inert under leader-follow and close to inert under real competition | Agreed |
| No overtime: output stops at normal capacity | Demand above capacity goes to firms with spare capacity or is lost | Agreed |
| Evaluation price: continuous λ, 5 levels | A dose-response curve is the cleanest exhibit for question B | Agreed |
| r̄ presented as "open against closed industry" | That is what it does in the model: the industry rate is above r̄ in 95 of 100 periods at 0.05, in fewer than 3 at 0.16 | Agreed |
| No docking against v2: E0 is the check of the rebuilt code | v3 changes scrapping, the price floor and overtime at once | Agreed |
| 20 November seminar: v2 results and the rebuild plan | v3 results will be at most two days old by then | Agreed |

## Decisions of the review of 9 November 2026

Taken by Ugo after the review of the proposal against the literature and the v2 runs; the group
still has to confirm them.

| Decision | Why | Status |
| --- | --- | --- |
| Mechanism test: H5 reworded, E3 crossed with r̄ (0.05, 0.16) | At prices of production the hurdle falls to r̄, not to 0: v2 gives drift under categories but 0.78 under the innovation set and 0.715 at r̄ = 0.16. r̄ = 0.16 also closes entry, so that arm is read against E4 | To confirm |
| Financing of replacement: the depreciation reserve of a plant is released when it leaves; net expansion out of retained profits | With a plant life of 10 periods, profits alone hold capacity only at r = δ/(1 − d) = 20 % | To confirm |
| The v2 numbers are predictions to retest; a pilot of 8 v2 cells is run before the spec is frozen | 0.81, 0.94 and 0.32 come from unit-cost scrapping, no maximum age and the markup floor; the closest v2 cells give 0.75 and 0.43 | To confirm |
| E7 dropped; H7 goes to the discussion as an extension | A rising money wage with prices that rise only after a shortage squeezes margins to zero, so h → 0 and the rules coincide | To confirm |

## Open

- The v2 pilot (proposal, section "Pilot in v2"): to run and read before the spec is frozen.
- Open points (a) to (i) of the addendum (`v3-planning-prompt.md`, A13): the plan proposes a
  default for each.
- Questions for Funalot and Bassi: do references and appendices count in the 10 pages, how long
  is each presentation, is the template layout required?

## Departures from the specification

| What | Why | Date |
| --- | --- | --- |
| None yet |  |  |
