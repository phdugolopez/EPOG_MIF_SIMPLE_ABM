# ABM version 4: coherence review of the proposal

Review of 10 November 2026, on `v4-final-model.md` as committed at 13:50 (`2808c68`), against
`v4-literature-check.md` (13:59, `30dca29`), section 9 of `v3-plan.md`, `v3-choices.md` and the
code of v3. Nothing in the proposal, the code, the tests or the outputs was changed. The numbers
quoted name their run: price rule, general rate, seeds. "The default runs" are those of
`outputs/v4_cost_edge/` (commit `90942ad`): cost-edge cutting, r̄ = 0.16, overtime, the
undercutting entrant, a shortage step of 0.25.

## Summary

- **At r̄ = 0.16 the model can be built from the proposal and v3's code.** Eleven points are
  incomplete or read two ways (rows 3, 8 to 16 and 20); each has a correction, and all but
  two follow the runs.
- **Away from 0.16 it cannot be built as one model.** The scaled menu is not run, its formula
  is ambiguous, and under it the general rate no longer varies what E3 crosses it for (row 1).
- **The evidence at the default holds.** The stored runs give every number checked, and a
  recomputation of E0 gives 50 and 49 seeds of 50. E0's lines are not defined to the point of
  coding, and its tables mix two windows (rows 17 to 19).
- **The literature check in the tree is newer than the prompt says** and judges the current
  defaults. Of its ten changes the proposal takes up none in full (annex A).
- **To settle first:** the general rate in E3 and E4, how E0 is read, and where the tree goes.
  The budget of 1,000 lines fits: v3 counts 651 that way, version 4 about 850 (annex C).

## Findings

Kinds: contradiction, gap, stale evidence, against the literature check, unclear rule. "Blocks"
says whether the plan can be written before the row is settled. A row without a question
number is settled by the correction given, unless Ugo objects (question 6).

| # | Where in the proposal | What | Kind | Correction proposed | Blocks |
| --- | --- | --- | --- | --- | --- |
| 1 | "Initial industry"; "Why not 5 %"; rows 2 and 15 of the changes; E3 and E4; decisions "The other level of r̄" and "β" | Under the scaled menu the two rules rank the initial techniques the same way at every rate. The cost a rule compares is uc_j + (h / r̄) × 0.16 κ^S_j, and at a given price the hurdle h is proportional to r̄. The price of production stays at 98.8 to 100.3 and the rules part above a price of 85.1 at every rate. So r̄ no longer varies what E3 crossed it for, the hurdle at the price of production (`v3-choices.md`, "Mechanism test"). It varies the pace of accumulation and the share of designs kept. Every argument of "Why not 5 %" comes from the fixed menu and no longer holds: the price of production is a third above the unit cost at every rate | Contradiction; stale evidence | Question 1 | Yes |
| 2 | "Initial industry", bullet "What moves with r̄"; decision "β" | The example is on C: 92 % of designs kept at 0.16, 20 % at 0.05. Unit-cost firms hold D2 after two periods, and there it is 87 % and 8 %. The two thresholds move by different factors (6.0 on C, 7.7 on D2), so no single β gives the same share on every technique | Gap | Keep β = 1.5 at every rate and report the share of designs kept. Drop the option "rescale it". Part of question 1 | With 1 |
| 3 | "Initial industry", the formula | (a) With unit costs of exactly 76 and 75 the formula gives operating costs of 61.769 and 59.211 at 0.16, not the 61.77 and 59.21 of Shaikh's table that every run used. (b) It does not say which δ applies when T is not 10 (Morris: 7 to 19). With the unit cost fixed, the menu at 0.16 is then no longer Shaikh's table, and v3's rule that unit costs move with T (A13 f) is reversed without a row. (c) The limit of 0.034 holds at T = 10 only; it is 0.044 at T = 7 | Unclear rule | ucs_j(r̄) = ucs^S_j − δ (κ_j(r̄) − κ^S_j), with δ = 1/T of the run. At 0.16 it is Shaikh's table at every T, as run. The code refuses a run in which an operating cost is not positive | No |
| 4 | "Initial industry" | What the scaled menu changes at the start is not stated. At 0.05 a plant of C costs 8,800. The initial cash and the entrant's equity are 3.2 times those at 0.16. Profits are not: a plant is paid by 40 plant-periods of retained profit at a price of 100, against 12.5, so growth out of profits is 3.2 times slower while the entry gate, relative to r̄, does not move. The operating cost (24 to 34) is far below any price, so scrapping on cost and the offer test of step 2 never bind | Gap | Add these four lines to "What moves with r̄" | No |
| 5 | "Initial industry", first bullet | "The two rules part on D2 when the hurdle is above 0.92 r̄." They part above 0.40 r̄ (0.064 at 0.16, a price of 85.1), where the profit-rate rule prefers D1 to D2. At 0.92 r̄ it also prefers C to D2. "Why not 5 %" itself says "above 85" | Contradiction | "The rules part above a hurdle of 0.40 r̄, a price of 85.1" | No |
| 6 | Opening paragraph | It says the document replaces the rows of `v3-choices.md` and restates every rule. Not restated: the excess-demand share (Q10), ties (A13 e), the entrant's size and first utilisation (Q8), deliveries and publication at the start of a period (A4, A9), funds against cash (A7), D_0 of the homogeneous start (Q7), Morris on S (Q6), the measures of E6 (A13 d), the label swap (Q4), the share q of the categories rule | Gap | The opening says that the rows of `v3-choices.md` hold where the document is silent. `v4-choices.md` lists them under "Kept from v3" and the plan restates each beside its equation | No |
| 7 | "At a glance", first bullet; table of changes | Six changes announced, fifteen rows. Seven change a rule or a default (rows 1, 2, 3, 4, 5 with 6, 14, 15), two add an option (7, 13), three concern the experiments (8 to 10), two the build (11, 12) | Contradiction | "Seven changes to the model and two options added"; the table in three blocks | No |
| 8 | "Schedule" | "Six steps a period", and the start of the period is missing: D_t, the plants ordered in t − 1 delivered (the entrant's included), designs made public. It decides who has a plant in operation at step 1: an entrant of t − 1 does, so its price counts in P and in L | Gap | Add "Start of the period" before step 1 | No |
| 9 | Step 1 | "A firm without a plant in operation keeps its price." In v3's code, which ran the three cutting rules, such a firm follows the lowest rival price down and rises after a shortage. Only the leader-follow patch keeps its price | Contradiction with the code behind the runs | Keep the proposal's sentence for the four rules. The case is rare: every plant retired, orders pending. Recorded as a difference from the runs | No |
| 10 | Step 1, the cutting rules; step 6 | Not stated: who the rivals are (the other firms with a plant in operation); the case without a rival (the firm keeps its price, or takes its floor if higher; after a shortage it rises by the step, without a cap); the excess-demand share ((D − K) / D, K the normal capacity in operation); the entrant's evaluation price (p^e with the lowest posted price as its own price) | Gap | State the four, as run | No |
| 11 | Step 1, normal-price cutting | Silent on where a cut stops. As run, a cut is a full (1 − c)P and can end up to c below the firm's price of production. The variant that stops above it was scored apart and differs (plan, section 9: E0 in 0 and 12 seeds of 50 against 43 and 12; r̄ = 0.05, step 0.5, entrant at the lowest price). "Best plant" means the lowest unit cost, ties to the lower κ | Unclear rule | State both, as run | No |
| 12 | Step 1, leader-follow | As run, the floor applies to a cut only. After a shortage a firm posts (1 + z)L even below its floor, and a firm alone posts the smaller of (1 + z) times its price and 3 times its floor. "Its price rises only after a shortage or to reach its floor" is written for the cutting rules | Unclear rule | State it as run: row 6 restores v2's rule. The assertion "no price below the floor" covers the three cutting rules | No |
| 13 | Steps 2 and 3, overtime | Step 2 offers the plants whose operating cost is at most the price. Step 3 as patched runs every plant of the firm to normal capacity before any overtime, so a plant that was not offered can produce, at a loss. The text can be read both ways | Unclear rule | Step 3 runs the offered plants only. It differs from the runs for a plant in its last two periods, before the cost test of step 4 removes it | No |
| 14 | Row 7; parameter table; robustness | The operating-cost floor is not defined. `v3-choices.md` defines it for leader-follow: the operating cost of the dearest plant the firm ran last period, or of its cheapest plant if none ran. Under a cutting rule one number serves as the floor and in the cost edge, and the floor was never run there. Row 7's "no share moved by more than 0.06" is from leader-follow at r̄ = 0.05 with the entrant at the lowest price | Gap; stale evidence | Define it in step 1; the cost edge stays on unit cost; mark the evidence of row 7 | No |
| 15 | "Rules as options"; parameter table | `params.entry_cut` appears once. The table names no option and gives the entrant's price a robustness level only. Missing rows: periods (200), D_0 over initial capacity (340/383), the initial price (100), q (0.5), the first period of the E0 measures (20) | Gap | A column "Name in the code". `entry_price`: undercut (default) or lowest; the cut is c. Add the rows | No |
| 16 | Parameter table against the robustness table; total of "Experiments"; row 9 | "Initial menu: robustness, the fixed menu" has no check. The shortage step of 0.5 has evidence and no check. "No overtime: E0 and E1, 500 seeds", and E0 has 50. Row 9 crosses the price rule with E0 to E4; E3 and E4 have three rules, without normal-price cutting. The total of 71,600 leaves out Morris (39,000), the reserve (6,400) and the checks (about 36,000, of which 15,000 for scrapping on unit cost): about 153,000 runs, a little over half an hour on 10 workers at v3's speed | Gap | Add the two checks; correct row 9; give the full total | No |
| 17 | "Experiments", E0 | The pass rule is stated two ways. By line: "each line true in at least 9 seeds of 10". By seed: "a seed passes when every line is true in it", and "46 and 44, where 45 are needed" | Contradiction | Question 2 | Yes |
| 18 | E0 table; "E0 and the headline" | The measures are not defined to the point of coding: which price, what a crossing is, how the rate is averaged. The script that computed them is not in the tree. The tables mix two windows: capacity is read from period 20, demand lost and the price over the whole run (leader-follow, r̄ = 0.16, 50 seeds: 0.061 and 0.069 lost over the run, 0.067 and 0.077 from period 20). With every measure from period 20 the default gives 50 and 49 seeds, leader-follow 46 and 43 (annex D) | Unclear rule; stale evidence | The definitions of annex D go into the E0 table. Every measure is read from period 20 and is a column of the run row | No |
| 19 | E0, line "Profit rates stay unequal" | A spread above 0 is true as soon as two firms differ. It passes in every seed under every rule and cannot fail | Unclear rule | Report the spread; do not count it as a line. Part of question 2 | With 2 |
| 20 | E0 as "the gate" | E0 fails under systematic cutting (2 and 0 seeds of 50) and under leader-follow, which are levels of the first treatment. What the gate stops is not said | Gap | The gate is on the default: if E0 fails there on the new code, no other experiment is read. Under the other rules E0's verdict is reported beside every result | No |
| 21 | H5; "What holds at the default" | H5 says the hurdle falls and the advantage shrinks. In the runs the advantage shrinks, 0.93 to 0.61, and the hurdle rises, 0.170 to 0.183 (cost-edge, r̄ = 0.16, 200 seeds). "Met as to the outcome" hides that the mechanism it names is refuted. Nothing in E3 or E5 looks for another | Against the evidence; against the literature check | H5 in two parts: the outcome, met; the mechanism, open. E5 reads at λ = 0 and 1 the orders that are not the cheapest (0.80 and 0.73), the realised rates by label (0.148 / 0.151 and 0.153 / 0.159) and the spread of hurdles across firms. No run added | No |
| 22 | "At a glance"; H2 | "The advantage needs the Marx bias (0.52 without it)." Without any draw the unit-cost label wins 0.98; at β = 0 it wins 0.52 (cost-edge, r̄ = 0.16, 200 seeds each). What it needs is a menu on which the rules disagree: the initial one, or biased draws | Unclear claim | Reword. The homogeneous start (six firms on D1) separates the two: give it priority 1 | No |
| 23 | H6; decision "Shortage step"; Morris | The sign of H6 turns with the step: 0.148 / 0.151 at 0.25 and 0.183 / 0.172 at 0.5 (cost-edge, r̄ = 0.16, 500 seeds each). Under the accelerator the unit-cost label wins 0.56 at 0.25 and 0.84 at 0.5 (100 seeds each). The step is screened by Morris only, and Morris has no outcome for the gap in realised rates | Gap | A robustness check at a step of 0.5: E0, E1 and the accelerator cell, 500 seeds. Morris gains a fifth outcome, the gap in realised rates. Slide 6 waits for E4 before it names the price rule alone | No |
| 24 | "What each setting does"; "What holds at the default" | One cell, two values: cost-edge at r̄ = 0.05 and λ = 0 gives 0.51 on 100 seeds and 0.57 on 200. The default gives 0.92 on 500 seeds and 0.93 on 200 and on 100 | Stale evidence | Quote the largest sample and name it | No |
| 25 | "Why not 5 %" | Its header gives r̄ = 0.05 and the entrant at the lowest price. The runs also have a shortage step of 0.5 and the fixed menu, and the last row has the undercutting entrant | Stale evidence | Retitle it "What the v3 runs gave at 5 % on the fixed menu"; then as question 1 decides | With 1 |
| 26 | "What each setting does"; reserve table; robustness table; H3 | Shares on 100 seeds, from a script that is not in the tree: the entrant at the lowest price (0.94), no overtime (0.78), the accelerator (0.56), growth (0.97), the reserve always released (0.80) and never released (0.42). On 100 seeds "within drift" is an interval of about ± 0.10 | Stale evidence | Mark them "100 seeds, to rerun". The first runs of the plan redo them as cells of the harness | No |
| 27 | "Literature: unchanged" | The check proposes ten changes. The proposal takes up none in full and contradicts the last (annex A) | Against the literature check | Questions 2, 3 and 5; the others are wording, settled in annex A | Partly |
| 28 | The prompt's account of the check | The check in the tree was saved at 13:57, after the prompt (13:48). It judges the current defaults: 0.16, cost-edge cutting, the undercutting entrant, a step of 0.25, the scaled menu. No verdict rests on a default that has changed. Its header dates the proposal 12:39; the file is of 13:39. One claim needs a qualifier: "close to half of the headline passes through" the entrant's label. The 0.16 is the whole entry-and-exit term of the sales-share decomposition, exits included | — | None in the proposal. In phase 2, a note at the head of the check | No |
| 29 | "At a glance"; row 11; "Rebuilding the code"; decisions | The count is stated three ways: comments excluded (twice), comments and docstrings excluded (once), and "to confirm" | Contradiction | Blank lines, comment lines and docstrings are all excluded. v3 counts 651 that way | No |
| 30 | "The run viewer", "How" | "The model needs no recorder." The model keeps a period table and a tally of flows by label (`model/outputs.py`), and the run row, the E0 measures and most panels read them. Three things the viewer cannot read from the firms after a period: the flows of one firm (orders, plants leaving by reason, reserve withdrawn), a firm that left in step 6, and the state between steps (the share before and after entry). matplotlib is not in the system Python | Gap | The model tallies flows by firm, and the period table sums them by label (about 3 lines). `period` runs a tuple of step functions, and the viewer runs the same tuple and reads the firms after steps 3, 5 and 6. The viewer's tables are tested everywhere, its figure where matplotlib is | No |
| 31 | Decisions, "Where version 4 is built" | Open | Gap | Question 4 | Yes |

## Questions for Ugo

Questions 1, 2 and 4 block the plan. The others can be answered with them or later.

1. **The general rate away from 0.16 (rows 1, 2, 25).** *Recommended:* r̄ leaves E3. The first
   runs on the new code are E0 and E1 on the scaled menu at 0.10, then at 0.05, with β = 1.5
   and the share of designs kept reported. r̄ stays in E4 at the level that meets E0, and
   leaves it if none does.
   - *Why.* Under the scaled menu the rules rank the initial techniques alike at every rate,
     so λ crossed with r̄ has lost its reason. What r̄ still varies, the pace of accumulation
     and of technical change, is a condition of E4.
   - *Cost.* RQ2 names the general rate only if a level passes. E3 falls from 18,000 to 9,000
     runs. "Why not 5 %" becomes a record of the v3 runs on the fixed menu. The reason for
     0.16 becomes "the rate of Shaikh's table and of every run".
   - *Other answers.* Keep E3 and E4 crossed as written: the plan carries a level still to
     choose and β stays open. Or go back to the fixed menu: it is what was run, and 5 % is
     then known not to give a working industry.
2. **How E0 is read (rows 17, 19, 27).** *Recommended:* four changes, no run added.
   - E0 holds when at least 9 seeds of 10 pass every line, in both populations.
   - The profit-rate line is read on the mean of r_new, with the same band; the industry
     rate is reported beside it. At the default r_new averages 0.159 and 0.158 against a
     rate of 0.132 and 0.130 (cost-edge, r̄ = 0.16, 50 seeds, annex D).
   - The spread of rates is reported and no longer counts as a line.
   - E0's lines are also read on the two controls of E1, which have draws, outside the gate.
   - *Cost.* Leader-follow reads 46 and 43 seeds. The read with draws will show that the firm
     posting the lowest price has the lowest unit cost in 0.67 and 0.73 of periods, and that
     no seed of 50 passes that line (controls of E1, cost-edge, r̄ = 0.16, annex D). The
     report must then say what "the lowest-cost firm sets the price" means in H1.
   - *Other answer.* Keep E0 as written, by line, and say that it tests gravitation only.
3. **The name of leader-follow (annex A, change 5).** *Recommended:* rename it "universal
   undercutting" in the text and `pricing = "universal"` in the code, with "leader-follow in
   v2 and the notebook" at its first mention.
   - *Why.* Every firm cuts whatever its cost. In Shaikh and in Hall and Hitch the followers
     match the leader's cut, which is what cost-edge cutting does.
   - *Cost.* The group's word changes; v2's documents and the pilot keep the old one.
   - *Other answer.* Keep the name and say once what the rule does.
4. **Where version 4 is built (row 31).** *Recommended:* a clean tree `../ABM-v4`, a git
   worktree on a new branch `v4` cut from `main`, as v3 was. The proposal, the register, the
   plan and this review are copied in at its first commit. v3 stays as it is, read-only.
   - *Cost.* The tests and the harness are ported, not inherited.
   - *Other answer.* A branch cut from `v3` in this tree: the history is kept, and the
     patches and v3's code stay in the way.
5. **A check on the entrant's label (annex A, change 3).** *Recommended:* an option
   `entry_label`, by market share (default) or even odds, and one robustness check on E1 at
   the default and under leader-follow: 3,000 runs.
   - *Why.* Through entry and exit 0.16 of the market moves to the unit-cost label, against
     0.21 through the price (cost-edge, r̄ = 0.16, 500 seeds).
   - *Cost.* One option, about 3 lines and a test.
6. **The rows without a question.** They are applied to the proposal in phase 2 unless you
   object. Two change a rule against the code that ran: row 9 (a firm without a plant keeps
   its price) and row 13 (only offered plants run). Rows 11 and 12 write down what ran.

## Annex A. The literature check, item by item

The ten changes of its last table:

| # | Change proposed by the check | In the proposal | Here |
| --- | --- | --- | --- |
| 1 | H5: report it against Shaikh, isolate the mechanism | Open: "met as to the outcome" | Row 21 |
| 2 | H6: report it against Table 7.3, line 5 | Partly: "not met", slide 9 changed; the source is not named and the sign turns with the step | Row 23 |
| 3 | A robustness check on the entrant's label | Not taken up | Question 5 |
| 4 | Say that the depth of the wars and the size of the cycle are the model's | Partly: "The cost" gives the sizes and no source | Wording, phase 2 |
| 5 | Rename leader-follow | Not taken up | Question 3 |
| 6 | Read E0's profit-rate line on r_new | Not taken up | Question 2 |
| 7 | E0 with draws, or say it tests gravitation only | Not taken up | Question 2 |
| 8 | Present the scaled menu, the reserve condition and idle scrapping as devices | Not taken up | Wording, phase 2 |
| 9 | "Operating cost" is Shaikh's prime cost | Not taken up | One sentence in "Setting", phase 2 |
| 10 | Replace "Literature: unchanged" | Contradicted | Phase 2: Shaikh 2016, pp. 264 and 274–282; Hall and Hitch 1939; Nakatani 1980 to add |

Its other verdicts of "departure", "no source" or "to reword":

| Verdict | In the proposal | Here |
| --- | --- | --- |
| Label "Okishio": to reword | Partly: "profit-rate rule" in the text; "Okishio" in RQ1, in the formula of the hurdle and as a label in v3's code | The text names Okishio once, as the theorem. The code keeps v3's two labels, so its outputs compare |
| Menu scaled by 0.16 / r̄: no source | Left open | Question 1; presented as a construction |
| β kept at 1.5 under the scaled menu: no source | In the decisions | Row 2 |
| War down to the rivals' unit cost: departure in degree | Not said | Wording, with change 4 |
| No replacement during a war: no source | Not said | It follows from the reserve condition: wording, with change 8 |
| Normal-price cutting on the firm's own price of production: small departure | Left open | Keep it as run, 50 and 50 seeds of 50 and 0.92 (r̄ = 0.16); name the departure. The variant on the regulating price was run at r̄ = 0.05 only |
| Systematic cutting as a normal regime: departure | Consistent: it is an option and fails E0 | None |
| Leader-follow: departure in the name and the rule | Not taken up | Question 3 |
| Shortage step, cap of a firm alone, value of u_max: no source | Not said | Wording, with change 8 |
| No overtime premium: simplification with a cost | In the decisions | None |
| A working plant is never replaced: departure | Kept from v3, not said | One sentence in "The model" |
| Reserve condition and its two other levels; idle scrapping: no source | Not said | Change 8 |
| Marx-biased draws: departure from Duménil and Lévy | Consistent: the neutral set is an option of E2 | None |
| Entrant's label by market share: no source | Not taken up | Question 5 |
| Industry profit rate in E0: departure | Not taken up | Question 2 |
| Demand lost at most 10 %: no source | Said: "set after the runs" | None |
| E0 without technical change: departure | Not taken up | Question 2 |
| H5 and H6 against Shaikh | Rows 21 and 23 | — |

## Annex B. What each statement rests on

| Basis | Statements of the proposal |
| --- | --- |
| A stored run with the proposal's settings at 0.16, by a command of the tree (`python3 -m experiments.price_rules v4_<rule>`), checked here | E1 under the four rules (500 seeds); E2 under the four rules (200 seeds); E3 at the default rule (200 seeds); the hurdles, realised rates, share decompositions and demand lost of "What holds at the default"; capacity at the last period in the band in 34 and 37 seeds of 50 |
| The same runs, read by a script that is not in the tree | The seeds that pass E0 under each rule; the range of capacity within a run; the crossings; the turbulence of the mixed population (0.29 to 1.49 times demand, a price of 1.9 times the price of production). Recomputed here for the default and leader-follow (annex D) |
| 100 seeds of the mixed population and 50 of E0, from that script | "What each setting does"; the reserve table; the robustness checks with a result; H3 on the reserve; the accelerator in the decision on the shortage step |
| Other settings | Everything at r̄ = 0.05: the fixed menu. "Why not 5 %": also a step of 0.5 and the entrant at the lowest price. Row 7 on the floor: leader-follow at 0.05. H6 "met with a step of 0.5". "Against the pilot": v2 |
| No run | The scaled menu at any rate but 0.16; r̄ = 0.10 under either menu; E3 under systematic cutting and leader-follow; E4; E6; Morris; the operating-cost floor, scrapping on unit cost, private diffusion, the homogeneous start, 12 and 30 firms and the categories rule with these settings |

Checked and found right: the arithmetic of the menu at 0.16, 0.10 and 0.05, the prices of
production and the limit of 0.034 at T = 10; the shares of designs kept on C; the run counts
of E0 to E6 (71,600), of Morris (39,000) and of the reserve (6,400); the initial capacity
(760) and D_0 (674.7).

## Annex C. The budget of 1,000 lines

Counted as the proposal says: without blank lines, comment lines and docstrings.

| Part | v3 | Version 4, estimate | What adds lines |
| --- | --- | --- | --- |
| `parameters.py` | 47 | 58 | The options: overtime, entrant's price, floor, reserve, menu; u* leaves |
| `equations/` | 147 | 215 | Four price rules in four files with their shared shortage and floor rules (about 45); overtime in the merit order; the scaled menu; the levels of the reserve; the entrant's price |
| `markets/` | 83 | 100 | The entrant's price and label; statements split for reading |
| `model/entities.py`, `model/model.py` | 110 | 120 | The menu built from r̄ |
| `model/outputs.py` | 68 | 80 | The tally by firm |
| `model/scheduler.py` | 178 | 250 | One stage a block, no statement doing two things, the choice of the price rule and of the floor |
| `run.py` | 18 | 20 | — |
| **Total** | **651** | **about 845** | A margin of about 150 |

- **It fits.** The margin is spent first by the scheduler, where the rule "no statement does
  two things" costs most.
- **The count needs a parser.** The test of v3 counts non-blank lines. Version 4's test must
  drop comment lines and docstrings: about 25 lines, in `tests/`.
- **Outside the count.** The run row and the E0 measures (`experiments/summary.py`), the
  harness and the viewer.
- **Speed.** With the proposal's settings v3's code takes 0.085 s of processor time a run
  (11,200 runs, 955 s), under the 0.2 s asked.

## Annex D. The recomputation of E0

A script outside the tree ran v3's code with the patches of `experiments/price_rules.py`:
r̄ = 0.16, a step of 0.25, 50 seeds a population, 100 for the mixed population. Every measure
is read on periods 20 to 199.

| Line | Definition used |
| --- | --- |
| The lowest-cost firm leads the price | Share of periods in which a firm posting the lowest price has the lowest unit cost among the best plants of the firms in operation |
| Price over the price of production | Mean over periods of the sales-weighted price over the price of production of the regulating technique |
| Crossings | Times that ratio passes from one side of 1 to the other between two periods, either way |
| Capacity over demand | Mean over periods of the normal capacity in operation over demand |
| Industry rate | Sum of profits over the sum of the purchase costs of the plants in operation |
| r_new | Mean over the periods in which it is defined |
| Spread | Mean over periods of the highest less the lowest rate of a firm |
| Demand lost | Sum of the demand lost over the sum of demand |

Each cell gives the all-unit-cost and the all-profit-rate population.

| Run | Seeds that pass every line | Weakest lines, seeds that pass | Capacity over demand, mean (range within a run) | Crossings | Industry rate | r_new | Demand lost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E0, cost-edge | 50 / 49 | Capacity: 50 / 49 | 1.08 (0.70–1.39) / 1.09 (0.70–1.43) | 24.5 / 23.5 | 0.132 / 0.130 | 0.159 / 0.158 | 0.003 / 0.003 |
| E0, normal-price | 50 / 50 | — | 1.07 (0.71–1.34) / 1.07 (0.71–1.35) | 25.8 / 26.6 | 0.133 / 0.133 | 0.158 / 0.158 | 0.003 / 0.003 |
| E0, leader-follow | 46 / 43 | Capacity: 46 / 44; demand lost: 48 / 44 | 0.93 (0.33–1.31) / 0.92 (0.29–1.31) | 21.7 / 23.1 | 0.132 / 0.132 | 0.151 / 0.152 | 0.067 / 0.077 |
| Controls of E1 (with draws), cost-edge | 0 / 0 | Leader: 0 / 0 (0.67 / 0.73 of periods); demand lost: 37 / 47; capacity: 42 / 50 | 0.93 (0.31–1.40) / 0.95 (0.32–1.58) | 21.0 / 24.0 | 0.154 / 0.148 | 0.181 / 0.168 | 0.079 / 0.071 |

- **The default is confirmed:** 50 and 49 seeds, the means and the ranges of the proposal.
- **Leader-follow is 46 and 43, not 46 and 44.** The proposal's count reads the demand lost
  over the whole run (47 seeds pass in the all-profit-rate population) and capacity from
  period 20.
- **r_new sits on r̄ and the industry rate below it**, as the literature check expects.
- **The mixed population** (cost-edge, 100 seeds): capacity between 0.30 and 1.48 times
  demand in an average run, a price up to 1.88 times the price of production, as the
  proposal says.
