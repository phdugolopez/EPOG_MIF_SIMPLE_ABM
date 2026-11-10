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
| Mechanism test: H5 reworded, E3 crossed with r̄ (0.05, 0.16) | At prices of production the hurdle falls to r̄ or just above it (17.05 % at r̄ = 0.16 on the initial menu), not to 0: v2 gives drift under categories but 0.78 under the innovation set and 0.715 at r̄ = 0.16. r̄ = 0.16 also closes entry, so that arm is read against E4 | To confirm |
| Financing of replacement: the depreciation reserve of a plant that leaves is released only when r_new ≥ r̄ (the signal of entry), else withdrawn and paid out; net expansion out of retained profits (9 Nov, revised 10 Nov after the pilot) | Profits alone give a profit rate of 20 %, the reserve always released a rate near zero; with the condition the rate gravitates around r̄, and the condition is the same for every firm | To confirm |
| The v2 numbers are predictions to retest; a pilot of 8 v2 cells is run before the spec is frozen (run 10 Nov, four arms) | 0.81, 0.94 and 0.32 come from unit-cost scrapping, no maximum age and the markup floor; the closest v2 cells give 0.75 and 0.43 | To confirm |
| E7 dropped; H7 goes to the discussion as an extension | A rising money wage with prices that rise only after a shortage squeezes margins to zero, so h → 0 and the rules coincide | To confirm |
| r̄ presented as the level of the general rate, centre of gravity of the profit rate and entry gate (10 Nov; replaces "open against closed industry", agreed 9 Nov) | With the replacement condition the rate gravitates around r̄ and entry stays active at 0.16 (47–52 entries a run in the pilot) | To confirm |
| Winner: exact ties counted apart; mean final capacity share reported beside the share won (10 Nov) | With six stable firms the pilot had up to 73 ties in 200 seeds, which v2 counted as losses | To confirm |

## Decisions on the plan's open questions (10 November 2026)

Taken by Ugo on the first plan (`v3-plan.md` of 9 November, section 10) and, for the last eight
rows, on the second plan of 10 November; the group still has to confirm them. A row here wins over the addendum, and the addendum over the proposal. Q and letter
numbers are those of the plan and of A13.

| Decision | Why | Status |
| --- | --- | --- |
| Line count (Q1): model code is counted without blank lines; target 700, with a tolerance of 10 % (770 at most) | Counted with `wc -l` the first plan stood at 698, with no margin | To confirm |
| Step 6 (Q3): exits are applied before entry; the entrant is sized and given its share among the survivors | No entrant leaves in the period it enters | To confirm |
| Label-swap test (Q4): every firm's label is swapped and every firm keeps its rule (the two mapping fields are exchanged with the labels); trajectories must be identical | Read literally, the swap changes each firm's rule, hence its trajectory, by design | To confirm |
| Private diffusion (Q5): no switch; one robustness check on E1 with `public_lag = None` | "What to drop" and the sensitivity table disagreed; the proposal is reworded | To confirm |
| Morris on S (Q6): each initial firm keeps its normal output (120, 120, 140) and gets output / S plants; D_0 = (340/383) × initial capacity | The plant counts and D_0 were stated for S = 20 only | To confirm |
| Homogeneous start (Q7): six identical firms of 6 D1 plants, D_0 = 639.2 | No initial cost edge and no size difference | To confirm |
| Entrant (Q8): plants = 0.5 × the survivors' mean capacity after scrapping, in plants of S, rounded half up, at least 1; its first utilisation is 1; r_new counts the initial plants aged 5 or less | Details A10 leaves open | To confirm |
| Excess-demand share (Q10): (D − K) / D, with K the total normal capacity in operation | A5 names the share without a formula | To confirm |
| Hurdle at λ = 1 (Q11): r̄ or just above it; the proposal's text is changed | The regulating technique earns r̄ at its price of production, another technique can earn more: 17.05 % at r̄ = 0.16 on the initial menu | To confirm |
| Work in stages 3a to 3d (Q14): one branch per part from the stage 2 commit, exchanged by the owners; build sessions never push | Four owners on four machines | To confirm |
| v2 leftovers (Q15): stage 1 reduces the workflow file to the tests and `run.py` on Python 3.12 | It runs files that are not in this tree | To confirm |
| Entrant's menu (A13 a): the public menu only; overrides A9 ("every technique in use") | One rule for who knows what; entry cannot bypass the lag L | To confirm |
| Scrapping (A13 b): the owner's posted price is compared with ucs; the 2 periods are consecutive; idle = no output for 2 consecutive periods; equal-cost plants run youngest first | Makes "idle" exact without v2's second ordering | To confirm |
| Entrant's funding (A13 c): equity from the rest-of-economy account | Money conservation | To confirm |
| Ties (A13 e): technique costs go to the lower κ, then the lower ucs, and a design that ties is not kept; prices are equal by `math.isclose`; exit candidates with the same share stay or leave together | No tie is broken by firm order or id | To confirm |
| Morris on T (A13 f): 7 to 19 (levels 7, 11, 15, 19) | Below T = 6.09 D1, not D2, has the lowest unit cost | To confirm |
| Scrapping on unit cost (A13 g): with the maximum age T | The rules forbid plants without a maximum age | To confirm |
| Names and constants (A13 h, i): distinct names in the code; every constant in `parameters.py` | R and k each had several meanings | To confirm |
| Withdrawn reserve (A13 j): paid to the rest-of-economy account | Capital leaves the industry when new plants earn less than the general rate | To confirm |
| Initial cash (A13 k): the depreciation already accumulated on the initial plants; overrides A2 (cash 0) | It backs the reserves these plants release | To confirm |
| Floor against "a price never rises" (Q2): the floor wins, price = max(min(previous, target), floor); it is the one rise without a shortage | v2 does it in its follow branch, so the pilot's numbers come from it; "no price below the floor" can be asserted every period; otherwise a firm can sell below its unit cost until the next shortage | To confirm |
| Random numbers (Q9): every firm takes four uniforms and one normal from its stream in every period, and the industry three uniforms, used or not; a firm draws a design only if it had a plant in operation in the period | A stream's position then depends on the period alone, so populations and cells are compared on the same random numbers | To confirm |
| Realised rate (Q12): profit after depreciation over the purchase cost of the plants in operation | The base of the hurdle and of r_new; over the book value the rate of an old plant grows without bound | To confirm |
| Categories rule (Q13): the two categories are defined at the evaluation price p^e, for every firm | "Conflict" then always means refused by the profit-rate rule as the firm applies it; the same as v2 at λ = 0, the only case planned | To confirm |
| E6 (A13 d): D_0 = (340/383) × 1,200 = 1,065.3; μ = 0; entry as in the base; measures = the mutant label's mean final capacity share against 0.1 and the share of seeds in which it ends above 0.1, each against the control | Same initial utilisation as E1; entry creates no mutant | To confirm |
| Reserve condition under the accelerator (Q17): step 4 is the same under both investment rules; when r_new < r̄ the reserve is paid out under the accelerator too | A7 states the condition before it separates the two rules; the investment factor of E4 then changes only the number of plants ordered | To confirm |
| Operating-cost test (Q18, A13 l): kept; "cost" is reported before "idle", and the run row gives the shares of plants leaving by age, cost and idleness | In v3 the idle test implies it, since a plant with ucs above the price is not offered; it binds alone only under scrapping on unit cost, which the robustness check needs | To confirm |
| Pilot numbers (Q19): a reference, not a gate; only E0 gates the runs | The pilot is not a docking: v2 keeps overtime, its own shortage rule and leader-follow, and leaves the withdrawn reserve in cash | To confirm |

## Open

- The v2 pilot was run on 10 November (proposal, section "Pilot in v2"): the group reads it before
  the spec is frozen.
- E0 is not met by the model as built (`v3-plan.md`, section 9, "Diagnosis", 10 November): the
  group decides, before E1 is read, whether to restore overtime and lower the shortage step,
  what E0 should check under cost-edge cutting, and whether the cycle is acceptable as it is.
- Questions for Funalot and Bassi: do references and appendices count in the 10 pages, how long
  is each presentation, is the template layout required?

## Analysis variants

Runs made beside the experiments, from a script that patches one rule or changes one parameter.
No file of the model changes and none of these is a rule of version 3: adopting one is a
departure, to be decided by the group and entered below.

| What | Why | Date |
| --- | --- | --- |
| E0 to E3 repeated under two other price rules (`experiments/price_rules.py`, outputs in `outputs/<rule>/`). `leader_follow`: v2's leader-follow rule with the floor at the unit cost of the firm's best plant, put in place of step 1 from the script. L is the lowest price posted last period by a firm with a plant in operation. A firm alone raises its price by 3 % a period, up to 3 times its floor; after excess demand every firm posts 1.03 L; otherwise every firm posts (1 − c) L, or its floor if that is higher, whatever its utilisation. `systematic`: version 3's own regime in every cell, as a comparison | Asked by Ugo after the comparison of price functions in E0 (`outputs/pricing_compare/`), where this rule comes closest to the thresholds. The proposal replaced its shortage rule and monopoly cap by the common ones ("What to drop"), so this is not systematic cutting as specified | 10 November 2026 |

## Departures from the specification

| What | Why | Date |
| --- | --- | --- |
| None yet |  |  |
