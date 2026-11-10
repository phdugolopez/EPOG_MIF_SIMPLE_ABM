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
| No docking against v2: E0 is the check of the rebuilt code | v3 changes scrapping, the price floor and overtime at once | Agreed |
| 20 November seminar: v2 results and the rebuild plan | v3 results will be at most two days old by then | Agreed |

## Decisions of the review and of the pilot (9 and 10 November 2026)

Taken by Ugo after the review of the proposal against the literature and the v2 runs (9 November)
and after the v2 pilot (10 November; proposal, section "Pilot in v2"); the group still has to
confirm them.

| Decision | Why | Status |
| --- | --- | --- |
| Mechanism test: H5 reworded, E3 crossed with r̄ (0.05, 0.16) | At prices of production the hurdle falls to r̄, not to 0: v2 gives drift under categories but 0.78 under the innovation set and 0.715 at r̄ = 0.16. r̄ = 0.16 also closes entry, so that arm is read against E4 | To confirm |
| Financing of replacement: the depreciation reserve of a plant that leaves is released only when r_new ≥ r̄ (the signal of entry), else withdrawn and paid out; net expansion out of retained profits (9 Nov, revised 10 Nov after the pilot) | Profits alone give a profit rate of 20 %, the reserve always released a rate near zero; with the condition the rate gravitates around r̄, and the condition is the same for every firm | To confirm |
| The v2 numbers are predictions to retest; a pilot of 8 v2 cells is run before the spec is frozen (run 10 Nov, four arms) | 0.81, 0.94 and 0.32 come from unit-cost scrapping, no maximum age and the markup floor; the closest v2 cells give 0.75 and 0.43 | To confirm |
| E7 dropped; H7 goes to the discussion as an extension | A rising money wage with prices that rise only after a shortage squeezes margins to zero, so h → 0 and the rules coincide | To confirm |
| r̄ presented as the level of the general rate, centre of gravity of the profit rate and entry gate (10 Nov; replaces "open against closed industry", agreed 9 Nov) | With the replacement condition the rate gravitates around r̄ and entry stays active at 0.16 (47–52 entries a run in the pilot) | To confirm |
| Winner: exact ties counted apart; mean final capacity share reported beside the share won (10 Nov) | With six stable firms the pilot had up to 73 ties in 200 seeds, which v2 counted as losses | To confirm |

## Open

- The v2 pilot was run on 10 November (proposal, section "Pilot in v2"): the group reads it before
  the spec is frozen.
- Open points (a) to (l) of the addendum (`v3-planning-prompt.md`, A13): the plan proposes a
  default for each.
- Questions for Funalot and Bassi: do references and appendices count in the 10 pages, how long
  is each presentation, is the template layout required?

## Departures from the specification

| What | Why | Date |
| --- | --- | --- |
| None yet |  |  |
