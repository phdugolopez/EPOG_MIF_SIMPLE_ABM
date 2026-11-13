# Version 4 choices: decisions and departures from the specification

The specification of version 4 is `v4-final-model.md`, as corrected on 10 November 2026 after
the coherence review (`v4-review.md`). `v4-plan.md` says how each rule is built and in which
stage. This file is the register: a decision counts once it has a row here, and any later
departure from the specification gets a row (what, why, date) before the code changes.

Order of authority: a row of this file wins over the proposal; the proposal wins over the rows
of `v3-choices.md` listed under "Kept from v3"; nothing else in `docs/design/` is a
specification of version 4.

## Decisions of the review (10 November 2026)

Ugo answered the six questions of `v4-review.md` on 10 November by taking every recommended
answer. The group still has to confirm them. "Row" is the row of the review's table of
findings.

| # | What | Why | Date | Status |
| --- | --- | --- | --- | --- |
| 1 | The general rate leaves E3. E0 and E1 on the scaled menu at r̄ = 0.10, then 0.05, are the first runs after E0 (E0r). r̄ stays in E4 at the level that meets E0, and leaves it if none does (question 1; rows 1, 25) | On the scaled menu the two rules rank the initial techniques alike at every rate, so λ crossed with r̄ has lost its reason. What r̄ still varies, the pace of accumulation and of technical change, is a condition of E4 | 10 Nov | Decided by Ugo; to confirm |
| 2 | β stays at 1.5 at every rate, and the share of designs kept is reported (row 2) | The thresholds move by a factor of 6.0 on C and 7.7 on D2: no single β restores the share on every technique | 10 Nov | Decided by Ugo; to confirm |
| 3 | E0 is counted by seed: a seed passes when every line is true in it, and E0 holds when at least 9 seeds of 10 pass in both populations (question 2; row 17) | The rule was stated by line and by seed. By seed is the stricter one and the one the tables count | 10 Nov | Decided by Ugo; to confirm |
| 4 | E0's rate line is read on the mean of r_new, with the band of 0.6 to 2 times r̄. The industry rate is reported (question 2) | The rate on new investment is the one that is equalised (Shaikh 2016, pp. 264, 268–271). At the default r_new averages 0.159 and 0.158, the industry rate 0.132 and 0.130 (cost-edge, r̄ = 0.16, 50 seeds) | 10 Nov | Decided by Ugo; to confirm |
| 5 | The spread of rates across firms is reported and is no longer a line of E0 (question 2; row 19) | It is above 0 as soon as two firms differ and cannot fail | 10 Nov | Decided by Ugo; to confirm |
| 6 | E0's lines are also read on the two controls of E1, which have draws, and reported beside E0, outside the gate (question 2) | E0 has no technical change and tests gravitation only. With draws the firm posting the lowest price is the cost leader in 0.67 and 0.73 of periods (cost-edge, r̄ = 0.16, 50 seeds) | 10 Nov | Decided by Ugo; to confirm |
| 7 | The gate is on the default price rule: if E0 fails there on the new code, no other experiment is read. Under the other rules E0's verdict is reported beside every result (row 20) | E0 fails under systematic cutting and universal undercutting, which are levels of the first treatment | 10 Nov | Settled in the review, accepted by Ugo |
| 8 | Every E0 measure is read on periods 20 to 199, is defined as in the proposal's E0 table, and is a column of the run row (row 18) | The tables mixed two windows, and the script that computed the measures was not in the tree | 10 Nov | Settled in the review, accepted by Ugo |
| 9 | v2's leader-follow rule is named universal undercutting, `pricing = "universal"`, with "leader-follow in v2 and the notebook" at its first mention (question 3) | Every firm cuts whatever its cost. Price leadership in Shaikh and in Hall and Hitch is what cost-edge cutting does | 10 Nov | Decided by Ugo; to confirm |
| 10 | Version 4 is built in a clean tree `../ABM-v4`: a git worktree on a new branch `v4` cut from the head of `v3` and emptied in its first commit. `docs/design/` comes with its history. v3 stays read-only (question 4; row 31). First decided as cut from `main`; changed by Ugo the same day, on the plan's open question 1 | As v3 was built beside v2, from the head of `v2`: what does not change is ported, not inherited, and no document is copied by hand | 10 Nov | Decided by Ugo; to confirm |
| 11 | One option `entry_label`: the incumbent whose label is copied is drawn by market share (default) or evenly, one vote a firm. One robustness check on E1, at the default and under universal undercutting (question 5) | Through entry and exit 0.16 of the market moves to the unit-cost label, against 0.21 through the price (cost-edge, r̄ = 0.16, 500 seeds). The review said "even odds"; a coin between the two labels would break the label swap, so the plan draws the incumbent evenly (plan, open question 2) | 10 Nov | Decided by Ugo; to confirm |
| 12 | The scaled menu: κ_j(r̄) = κ^S_j × 0.16 / r̄ and ucs_j(r̄) = ucs^S_j − δ (κ_j(r̄) − κ^S_j), with δ = 1/T of the run. A run with an operating cost that is not positive is refused (row 3) | At 0.16 it is Shaikh's table at any T, the menu of every run so far, and unit costs move with T as in v3 | 10 Nov | Settled in the review, accepted by Ugo |
| 13 | The schedule opens with a start of the period: D_t, deliveries, publication of designs. An entrant of t − 1 has a plant in operation at step 1 of t (row 8) | It decides which prices count in P and in L | 10 Nov | Settled in the review, accepted by Ugo |
| 14 | A firm without a plant in operation keeps its price under every price rule (row 9) | One sentence for the four rules. **It differs from v3's code**, where under the cutting rules such a firm followed the lowest rival price | 10 Nov | Settled in the review, accepted by Ugo |
| 15 | The cutting rules, as run: rivals are the other firms with a plant in operation; a firm without a rival keeps its price or takes its floor, and after a shortage rises by the step without a cap; the excess-demand share is (D − K) / D; the entrant's evaluation price is p^e with the lowest posted price as its own (row 10) | The proposal did not say | 10 Nov | Settled in the review, accepted by Ugo |
| 16 | Normal-price cutting, as run: a cut is a full (1 − c)P and can end up to c below the firm's own price of production, that of its best plant (row 11) | The variant that stops above it gives another industry. The firm's own price of production is a small departure from Shaikh, kept because it is what was run | 10 Nov | Settled in the review, accepted by Ugo |
| 17 | Universal undercutting, as run: the floor applies to a cut only. After a shortage, and for a firm alone, a price can be below the floor (row 12) | It is v2's rule. The assertion "no price below the floor" covers the three cutting rules | 10 Nov | Settled in the review, accepted by Ugo |
| 18 | Only the plants a firm offered at step 2 run at step 3, overtime included (row 13) | The text could be read both ways. **It differs from the patch behind the runs**, which ran every plant to normal capacity before any overtime | 10 Nov | Settled in the review, accepted by Ugo |
| 19 | The operating-cost floor is the operating cost of the dearest plant the firm ran last period, or of its cheapest plant if none ran. The cost edge stays on unit cost (row 14) | The proposal did not define it; this is v2's floor, as `v3-choices.md` records it | 10 Nov | Settled in the review, accepted by Ugo |
| 20 | Every option has a name and its levels in the proposal's table of options. The entrant's price is `entry_price`: undercut (default) or lowest; the cut is c (row 15) | `params.entry_cut` appeared once and nowhere else | 10 Nov | Settled in the review, accepted by Ugo |
| 21 | Robustness checks added: a shortage step of 0.5 (E0, E1 and the accelerator cell), the fixed menu at the second level of r̄ if one is kept. Morris gains a fifth outcome, the gap in realised rates between the labels (rows 16, 23) | The sign of H6 and the headline under the accelerator both turn with the step | 10 Nov | Settled in the review, accepted by Ugo |
| 22 | H5 has two parts: the outcome (met) and the mechanism (not met, open). E5 reads E3 at λ = 0 and 1 for another mechanism. H2 says that the advantage needs a menu on which the rules disagree (rows 21, 22) | The hurdle rises between λ = 0 and 1 while the advantage falls; without any draw the unit-cost label wins 0.98 | 10 Nov | Settled in the review, accepted by Ugo |
| 23 | The 1,000 lines are counted without blank lines, comment lines and docstrings (row 29) | It was stated three ways. v3 counts 651 that way | 10 Nov | Settled in the review, accepted by Ugo |
| 24 | The model's period is a tuple of step functions; flows are tallied by firm and summed by label. The viewer runs the same tuple and adds nothing to the model (row 30) | The viewer cannot read a firm's flows, or a firm that has left, from the firms after a period | 10 Nov | Settled in the review, accepted by Ugo |
| 25 | The rows of `v3-choices.md` hold where the proposal is silent; they are listed below (row 6) | The proposal said it restated every rule and did not | 10 Nov | Settled in the review, accepted by Ugo |
| 26 | The two labels keep v3's names in the code, `shaikh` and `okishio`; the rules are `unit_cost` and `profit_rate`. The text names Okishio once, as the theorem (annex A) | Outputs compare with v3's; a label is not a rule, since in a control both labels follow one rule | 10 Nov | Settled in the review, accepted by Ugo |
| 27 | Numbers at r̄ = 0.05 are marked "fixed menu", shares from the script outside the tree "100 seeds", and the rest "not run". The first runs of version 4 redo them (rows 24 to 26) | Nothing provisional is read as a result | 10 Nov | Settled in the review, accepted by Ugo |
| 28 | The report presents as devices of the model: the scaled menu, the reserve condition, idle scrapping, the shortage step, the cap of a firm alone, the value of u_max, the weight of market share in the entrant's label. It gives the depth of the wars and the size of the cycle as the model's own, and H5 and H6 as results against Shaikh (annex A) | Asked by the literature check | 10 Nov | Settled in the review, accepted by Ugo |

## Decisions of the build

| # | What | Why | Date | Status |
| --- | --- | --- | --- | --- |
| 29 | The general rate enters E4 at 0.10, beside 0.16 | The rule of decision 1 and of section 9 of the plan: on the scaled menu E0 holds at 0.10 at the default rule, in 50 and 50 seeds of 50 (commit `d58d9c0`, plan, section 15). It holds at 0.05 too (48 and 50), but the rule takes 0.10 first; with draws the unit-cost label wins 0.80 at 0.10 and 0.59, within drift, at 0.05, where 28 % of demand is lost | 10 Nov | By the rule of decision 1; to confirm |

## Kept from v3

Rows of `v3-choices.md` that hold in version 4. The others are replaced by the proposal: no
overtime, one price rule with two regimes, the accelerator's target, E3 crossed with r̄, the
line count of 770.

| Row of `v3-choices.md` | What holds |
| --- | --- |
| Technical change (9 Nov) | The innovation set, β = 1.5, is the model; the neutral set and "no draws" are its controls; the categories rule is a robustness switch |
| Scrapping (9 Nov) | On operating cost, with a plant life of T = 10 |
| Investment (9 Nov) | No debt: retained earnings, or the accelerator |
| Financing of replacement | The reserve of a plant that leaves is released when r_new ≥ r̄ or when no plant is in the window, else paid out; expansion out of retained profits |
| E7 dropped; ties; final capacity share | No wage path. Exact ties are counted apart. The mean final capacity share is reported beside the share won |
| Q3 | Exits are applied before entry; the entrant is sized among the survivors |
| Q4 | Label swap: every label is swapped and every firm keeps its rule; trajectories are identical |
| Q5 | Private diffusion: one robustness check with `public_lag = None` |
| Q6 | Morris on S: each initial firm keeps its normal output (120, 120, 140) and gets output / S plants; D_0 = (340/383) × initial capacity |
| Q7 | Homogeneous start: six firms of 6 plants of D1, D_0 = 639.2 |
| Q8 | The entrant has 0.5 × the survivors' mean capacity after scrapping, in plants of S, rounded half up, at least 1; its first utilisation is 1; r_new counts the initial plants aged 5 or less |
| Q10 | The excess-demand share is (D − K) / D |
| Q11 | At λ = 1 the hurdle is r̄ or just above it |
| A13 a | The entrant chooses on the public menu only |
| A13 b | The owner's posted price is compared with the operating cost; the 2 periods are consecutive; idle is no output for 2 consecutive periods; plants of equal cost run youngest first |
| A13 c, j, k | The entrant is funded by equity from the rest of the economy; a withdrawn reserve is paid to it; initial cash is the depreciation accumulated on the initial plants |
| A13 e | Ties between techniques go to the lower κ, then the lower operating cost; a design that ties is not kept; prices are equal by `math.isclose`; exit candidates with the same share stay or leave together |
| A13 f, g | Morris on T: 7, 11, 15, 19. Scrapping on unit cost keeps the maximum age |
| A13 h, i | Distinct names in the code; every constant in `parameters.py` |
| Q2 | The floor wins over "a price never rises": price = max(min(previous, target), floor), under the three cutting rules |
| Q9 | Every firm takes four uniforms and one normal a period, and the industry three uniforms, used or not. With `entry_label = "even"` the same uniform draws the parent, each incumbent weighing one |
| Q12 | The realised rate is profit after depreciation over the purchase cost of the plants in operation |
| Q13 | The two categories of the categories rule are defined at the evaluation price |
| A13 d | E6: D_0 = 1,065.3, μ = 0, entry as in the base; the measures are the mutant label's mean final capacity share against 0.1 and the share of seeds in which it ends above 0.1, each against the control |
| Q17 | The reserve condition is the same under both investment rules |
| Q18, A13 l | The cost test is kept and reported before "idle"; the run row gives the shares of plants leaving by age, cost and idleness |
| Q19 | The pilot's numbers are a reference, not a gate |

## Open

- The group confirms the decisions above.
- The group confirms the level of r̄ in E4 (decision 29), and says whether the homogeneous
  start should also have a public menu of D1 alone (plan, section 15).
- After stages 7 to 9 (plan, sections 16 to 18): whether the diffusion of designs is stated
  as a condition of the headline, which falls to drift when designs stay private; whether a
  cell varies the spread of hurdles alone, to test the candidate mechanism of H5; and how
  H1 is worded, the price being set by an entrant in most periods in which the cost leader
  does not post the lowest price.
- Questions for Funalot and Bassi, as in `v3-choices.md`: do references and appendices count
  in the 10 pages, how long is each presentation, is the template layout required?

## Departures from the specification

| What | Why | Date |
| --- | --- | --- |
| A third level of the option `price_floor`, `mean_unit_cost`: a firm's floor is the mean unit cost of its plants, weighted by their normal capacity, in place of the unit cost of its best plant. The cost edge is still read on the best plant; an entrant has one plant, so its floor is unchanged. Default unchanged (`unit_cost`) | Asked by Ugo, to see how the price paths change when a firm will not cut below the average cost of its whole stock of plants. Run outside the registered plan: one seed, the four price rules, Marx-biased and neutral designs (`docs/results/scripts/firm_prices.py --floor mean_unit_cost`) | 12 Nov |
| The run viewer shows the variability of prices: a file `prices.csv` (dispersion of the posted prices across the firms in operation, log change of the industry price), a block of the read-out, and two panels (spread of prices, volatility of prices), so twelve panels in place of ten (plan, section 10). Outside the model code: no rule, parameter or period table changes | Asked by Ugo, to see how much prices vary across firms and over time in a run | 13 Nov |
| An option `bankruptcy` (off, on) with `bankruptcy_loss` = 0.5: when on, a firm also leaves at step 6 once its losses since entry, profit cumulated less the book value written off, exceed bankruptcy_loss times the capital it entered with (the purchase cost of its initial plants, or an entrant's equity). Dividends and the reserve withdrawn are paid to the owners and are not losses. min_firms still protects the largest candidates. Two fields of Firm, `capital_in` and `result`. Default off: no run of stages 1 to 9 changes | Asked by Ugo: the model has no debt, so a firm can lose for many periods without leaving (seed 7, universal undercutting, all firms on the unit-cost rule: six firms, no exit); the proposal says "no bankruptcy" | 13 Nov |
