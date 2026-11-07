# Results of the first full sensitivity analysis (step 4 of the plan)

Run on 7 November 2026, branch `feature/sensitivity`, on the version 2 defaults frozen that
day, following `sensitivity-plan.md` (section 7) and `sensitivity-prompt.md`. Every number
below comes from `outputs/sensitivity/runs.csv` (one row per run with every parameter;
committed as `runs.csv.gz`) and `outputs/sensitivity/cells.csv` (one row per stage, cell and
population); figures in `outputs/sensitivity/figures/`. The choices made running the
analysis are in `choices.md` ("Choices made running it").

**How to read the numbers.** For every cell, three populations over the same seeds: `mixed`
(label "shaikh" on the unit-cost rule, "okishio" on the profit-rate rule) and the two neutral
controls (both labels on one rule). *Share won* is the share of seeds in which the label
"shaikh" holds more than half of producing capacity at t = 199, seeds with no producing
capacity left excluded (`undecided`), with its 95 % Wilson interval. A mixed result is
**beyond drift** when its interval is disjoint from both controls' intervals; a level
**moves** the outcome when its mixed interval is disjoint from that of its reference cell
(`base`; `lf` for the leader-follow sub-factors; `is_marx_15` for the innovation-set levels
and diffusion). The controls sit at 0.38–0.56 everywhere, as drift should (the label listed
first draws first from the single random stream, hence the small departures from 0.5).

## 1. Design actually run

| Stage | Cells | Seeds | Runs | Wall time (10 workers) |
|---|---|---|---|---|
| 1, one factor at a time | 36 (the 32 of the plan and the four additions) | 1–200 | 21 600 | 1 376 s (23 min); run twice, see below |
| 2, factorial and phase block | 176 (120 factorial + 56 phase block) | 1–100 | 52 800 | 2 206 s (37 min) |
| 3, the cells that decide | 8 | 1–500 | 12 000 | 1 582 s (26 min; 1 300 s of it the 3 % growth cell) |

No run failed a check or raised (`n_check_fail` = 0 and `error` empty in every row). Stage 1
was run a second time, before stage 2, to add the decomposition over the whole run
(`d_share_*_all`); the second grid reproduced every observable of the first, row for row,
which is a test of determinism across processes and schedules on its own. `rerun` reproduces
its row exactly (tested on random rows of the smoke grid and on the four rows behind the
`debug.report` PDFs). Seeds were never halved: every stage ran with the seeds of the plan.

The stage 2 design departs from the plan's 144-cell cross in one way, by the plan's own rule
(`choices.md`): CHI moved at no level in stage 1, so the factorial holds it at 1, while the
entry factor (rbar 0.16) and the per-investment draw timing, which did move, join it.
Factorial: pricing {real competition `rc`, leader-follow `lf`} × finance {retained earnings
`re`, accelerator with borrowing `acd`} × demand {static, growing 0.01 `g01`, initially
unmet `unmet`} × technical change {categories q = 0.5 `cat`, innovation set marx 1.5 `is15`,
marx 3 `is3`, neutral `isneu`, marx 1.5 with draws per investment `is15inv`} × rbar {0.05
`r05`, 0.16 `r16`}; the cell name lists the levels in that order. CHI enters a phase block
for the headline figure: pricing × finance × CHI {0.25, 1, 4} × six technical-change levels,
static demand, rbar 0.05 (cells `ph-...`).

## 2. Stage 1: which factors move the share of seeds won (figure 1)

The version 2 defaults: the unit-cost rule wins **0.805** of seeds (0.74–0.85), against
0.48 (0.41–0.55) for both controls. The advantage is beyond drift at 200 seeds, which the
20-seed record of `choices.md` could not show. Mean final capacity share of "shaikh" 0.80.

| Factor | Level (cell) | Share won (95 %) | Controls (uc / pr) | Beyond drift | Moves (vs reference) |
|---|---|---|---|---|---|
| Pricing | leader-follow (`lf`) | 0.66 (0.59–0.72) | 0.47 / 0.43 | yes | yes, down |
| | anchor, rbar 0.16 (`anchor_r16`) | **0.26** (0.20–0.33), 13 undecided | 0.53 / 0.51 | yes, **for the profit-rate rule** | yes |
| | anchor, rbar 0.05 (`anchor_r05`) | 0.66 (0.59–0.72), 8 undecided | 0.48 / 0.56 | no | yes, down |
| Floor (real competition) | operating cost (`rc_floor_ucs`) | 0.74 (0.68–0.80) | 0.47 / 0.51 | yes | no |
| Floor (leader-follow, vs `lf`) | unit cost (`lf_floor_uc`) | 0.83 (0.77–0.87) | 0.46 / 0.45 | yes | yes, up |
| | operating cost (`lf_floor_ucs`) | 0.65 (0.56–0.73), **81 of 200 undecided** | 0.44 / 0.51 | no | no |
| Shortage branch (vs `lf`) | `no_cut` (`lf_no_cut`) | 0.66, identical to `lf` | | | no: inert, leader-follow never has a shortage period |
| Excess demand signal | `unserved` | 0.76 (0.70–0.81) | 0.43 / 0.47 | yes | no |
| Finance | accelerator + borrowing (`accel_debt`) | 0.63 (0.56–0.69) | 0.50 / 0.49 | no | yes, down |
| | accelerator, no borrowing (`accel_cash`) | 0.59 (0.52–0.65) | 0.52 / 0.55 | no | yes, down |
| Demand | growing 0.01 (`grow_01`) | 0.63 (0.56–0.69) | 0.53 / 0.53 | no | yes, down |
| | growing 0.03 (`grow_03`) | 0.39 (0.33–0.46) | 0.51 / 0.51 | no (leans to the profit-rate rule) | yes, down |
| | initially unmet (`unmet`) | 0.76 (0.69–0.81) | 0.43 / 0.45 | yes | no |
| | unmet and growing 0.02 | 0.46 (0.39–0.52) | 0.44 / 0.45 | no | yes, down |
| Selection intensity | CHI 0.25 / 0.5 / 2 / 4 | 0.71 / 0.79 / 0.75 / 0.79 | 0.40–0.51 | yes, all | **no level** |
| Demand form | logit, η = 1 | 0.805, identical to `base` | | | no: with η = 1 the logit form equals the replicator with χ = 1 to rounding (differences below 1e-12) |
| Technical change | categories q = 0 (`cat_q0`) | 0.62 (0.55–0.68) | 0.46 / 0.47 | yes | yes, down |
| | innovation set marx 1.5 (`is_marx_15`) | **0.94** (0.90–0.97) | 0.53 / 0.48 | yes | yes, up |
| (vs `is_marx_15`) | marx 0.5 | 0.80 (0.73–0.85) | 0.55 / 0.52 | yes | yes, down |
| | marx 3 | 0.97 (0.93–0.98) | 0.48 / 0.47 | yes | no |
| | neutral | 0.78 (0.71–0.83) | 0.38 / 0.54 | yes | yes, down |
| | no draws (`no_tech`, fixed menu) | **0.51** (0.44–0.58) | 0.45 / 0.45 | no | yes, down |
| Diffusion and timing (vs `is_marx_15`) | private | 0.87 (0.82–0.91) | 0.52 / 0.52 | yes | no |
| | draws per investment | **0.995** (0.97–1.00) | 0.46 / 0.42 | yes | yes, up (barely: 0.97 against 0.97) |
| | reference frontier | 0.93 (0.88–0.95) | 0.55 / 0.52 | yes | no |
| Entry | θ = 1 | 0.79 (0.72–0.84) | 0.46 / 0.51 | yes | no |
| | rbar 0.16 | 0.64 (0.57–0.70) | 0.49 / 0.49 | yes | yes, down |
| Scrapping | idle and obsolescence 4 / 4 | 0.78 | 0.49 / 0.54 | yes | no |
| Depreciation | by use | 0.75 | 0.46 / 0.45 | yes | no |
| Plant size | 40 | 0.79 | 0.48 / 0.43 | yes | no |
| Capital advanced | τ = 0.25 | 0.78 | 0.48 / 0.49 | yes | no |
| Hurdle floor | `HURDLE_FLOOR_AT_ZERO = False` | 0.805, identical to `base` | | | no: inert, the best profit rate on offer never falls below 0 under the defaults |

Reading. (i) **Without technical change there is no contest**: on the fixed menu C, D1, D2
the mixed population is at drift (0.51). Every advantage of the unit-cost rule comes from
how the two rules treat new designs. (ii) **The innovation set sharpens it**: from 0.81
(categories) to 0.94 (marx 1.5) and 0.97 (marx 3); a neutral set or a weak bias (0.5) brings
it back to about 0.8, and removing the conflict zone (q = 0) to 0.62, still beyond drift.
(iii) **Everything that slows or redistributes accumulation weakens it without reversing
it**: the accelerator (with or without debt), demand growth, rbar 0.16; at 0.03 growth and
at unmet-and-growing demand the outcome is no longer distinguishable from drift. (iv) **The
pricing rule matters, but only the version 1 anchor rule at rbar 0.16 reverses the
outcome** (the profit-rate rule wins 74 % of decided seeds, beyond drift). At rbar 0.05 the
anchor rule is indistinguishable from drift, so that reversal belongs to the anchor-and-high-
rbar combination. (v) Selection intensity, the demand form, the floor of the default rule,
the excess-demand signal, entry speed, scrapping, depreciation, plant size and τ move
nothing. Three switches are inert at the defaults (logit with η = 1, the hurdle floor, the
leader-follow shortage branch). (vi) **One cell has more than 10 % undecided seeds**:
leader-follow with the operating-cost floor (81 of 200 seeds end with no producing capacity:
prices fall to the operating cost and the whole industry is scrapped), so its share won is
not a result.

## 3. Stage 2: the factorial (figure 2)

Over the 120 factorial cells the unit-cost rule wins on average 0.82 of seeds; 86 cells are
beyond drift, **all of them in its favour; no cell of stage 2 has the profit-rate rule
beyond drift**, and no cell has more than 10 % undecided seeds. Main effects (mean share won
over the other factors):

| Factor | Levels: share won (cells beyond drift) |
|---|---|
| Pricing | real competition 0.79 (37 of 60); leader-follow 0.84 (49 of 60) |
| Finance | retained earnings 0.86 (49 of 60); accelerator + borrowing 0.77 (37 of 60) |
| Demand | static 0.79; growing 0.01 0.81; initially unmet 0.86 |
| Technical change | categories 0.67 (10 of 24); marx 1.5 0.88; marx 1.5 per investment 0.88; marx 3 0.91; neutral 0.76 |
| rbar | 0.05: 0.83; 0.16: 0.80 |

The interactions that matter:

- **Pricing × finance.** Under real competition the accelerator with borrowing costs the
  unit-cost rule about 0.3 (static demand 0.59 against 0.89 with retained earnings; growing
  0.63 against 0.88) except when demand is initially unmet (0.86 against 0.91). Under
  leader-follow the finance rule hardly matters (0.82–0.87 in every demand condition). The
  price channel and the accumulation channel interact: under real competition prices fall
  only through cost-backed cuts, so a firm that accumulates fast on borrowed money can hold
  share without the lowest cost.
- **Technical change × entry.** The categories rule is where rbar 0.16 hurts: 0.59 (real
  competition) and 0.64 (leader-follow) against 0.70 and 0.74 at rbar 0.05. Under the
  innovation set rbar barely matters (0.82–0.94).
- **The weakest cells** are categories, retained earnings, growing demand and rbar 0.16:
  `lf-re-g01-cat-r16` 0.29 (0.21–0.39) and `rc-re-g01-cat-r16` 0.32 (0.24–0.42), with
  controls at 0.41–0.55: the profit-rate rule leads, but not beyond drift at 100 seeds. The
  first went to stage 3 as the smallest share won, and at 500 seeds it is beyond drift
  (section 4).

**The phase diagram** (figure 2; the plane at rbar 0.05 and draws per period; mean share won
over the phase block 0.72 at CHI 0.25, 0.75 at 1, 0.78 at 4). Selection intensity does not
decide the winner on its own, as stage 1 said, but it interacts with finance. With retained
earnings a higher CHI helps the unit-cost rule under the innovation set (real competition,
marx 0.5: 0.53 → 0.81 → 0.98 from CHI 0.25 to 4; neutral: 0.65 → 0.77 → 0.97): fast
selection rewards the lower price that cheaper techniques allow. With the accelerator and
borrowing the slope turns over under real competition (marx 0.5: 0.88 → 0.59 → 0.54; marx
1.5: 0.88 → 0.61 → 0.56): when share moves fast, the firm that expands on credit gains as
much from it as the cheaper one. The categories rule with q = 0 stays near drift (0.47–0.62)
almost everywhere under retained earnings. Nowhere in the plane does the profit-rate rule
win beyond drift. The realised conflict share under the innovation set is small (0.04 for
the neutral set, 0.14–0.19 for the marx sets, against the 0.5 of the categories rule), yet
the innovation set gives the larger advantage: the conflict zone is not where the advantage
comes from (see section 5).

## 4. Stage 3: the cells that decide (500 seeds)

Chosen by the plan's rule (`outputs/sensitivity/stage3_cells.json`, `choose3`): `base`,
`lf`, the largest gap under each pricing rule, the largest and the smallest share won, the
finance arm where it changes the share won most, and one 3 % growth cell.

| Cell | Why | Share won (95 %) | Controls (uc / pr) | Beyond drift |
|---|---|---|---|---|
| `base` | version 2 defaults | **0.81** (0.77–0.84) | 0.48 / 0.50 | yes |
| `lf` | leader-follow defaults | **0.71** (0.67–0.75) | 0.50 / 0.49 | yes |
| `rc-re-static-is15-r16` | largest gap, real competition | 0.99 (0.97–0.99) | 0.49 / 0.49 | yes |
| `lf-re-g01-is15-r16` | largest gap, leader-follow | 0.98 (0.97–0.99) | 0.48 / 0.47 | yes |
| `rc-re-static-is3-r16` | largest share won | 0.99 (0.98–1.00) | 0.53 / 0.50 | yes |
| `lf-re-g01-cat-r16` | smallest share won | **0.32** (0.28–0.36) | 0.49 / 0.49 | **yes, for the profit-rate rule** |
| `lf-acd-g01-cat-r16` | finance arm (the previous cell with the accelerator and borrowing) | **0.85** (0.82–0.88) | 0.51 / 0.49 | yes |
| `grow_03` | 3 % growth | 0.43 (0.39–0.47) | 0.51 / 0.49 | no (touches the controls' intervals) |

No undecided seed in any stage 3 cell, no error, no failed check.

Reading. The two default cells are confirmed at 500 seeds (0.81 and 0.71, a 10-point gap
between the pricing rules that is itself beyond the intervals). **Stage 3 finds a second
reversal**: leader-follow pricing, retained earnings, demand growing at 1 %, the categories
rule and rbar 0.16. There the profit-rate rule wins 68 % of seeds, beyond drift, with almost
no entry (0.24 entries in the window), the profit-rate firms earning more (6.3 % against
3.3 %) and both channels against the unit-cost label (price −0.18, accumulation −0.18).
Profit-rate firms seldom choose a dearer technique there (`okishio_dearer` 0.06 against
0.51 in the base cell), so the mechanism that makes the unit-cost rule win elsewhere is
absent. **The same cell with the accelerator and borrowing flips to 0.85 for the unit-cost
rule**: the finance rule decides the contest in this corner, which is the second half of the
research question. The innovation set gives the unit-cost rule 0.98–0.99 in its best cells
whatever the pricing rule. At 3 % growth the profit-rate rule leads (0.57 of seeds) but not
beyond drift even at 500 seeds.


## 5. Which observables move with the winner

Across the 212 mixed cells of stages 1 and 2 (correlation of the cell's share won with the
cell mean) and across the 17 600 decided mixed seeds of stage 2 (seeds won by the unit-cost
rule against seeds won by the profit-rate rule):

- **The channel is prices, then exits** (figure 3). The whole-run price-driven term of
  Shaikh's sales share correlates 0.80 with the share won, the accumulation term 0.60. In
  93 % of cells the price term is larger in absolute value than the accumulation term. In
  the base cell the unit-cost label gains +0.25 of sales share through prices and +0.28 of
  capacity share through the exits of profit-rate firms, while accumulation nets to zero.
  The accumulation channel dominates only in a few cells: leader-follow with the unit-cost
  or operating-cost floor (+0.23, +0.32), the anchor rule at rbar 0.05 (+0.20), and the
  real-competition operating-cost floor (+0.21).
- **The mechanism is the profit-rate rule's switch to dearer techniques.** The share of
  profit-rate orders that are not the cheapest known technique (`okishio_dearer`)
  correlates 0.77 with the share won, the strongest of all observables: 0.49 in seeds the
  unit-cost rule wins against 0.17 in seeds it loses; 0.51 in the base cell, 0.79–0.85 under
  the marx innovation sets, 0.10 on the fixed menu (where the contest is at drift). The
  realised conflict share of draws does not (−0.12).
- **Prices.** Seeds won by the unit-cost rule have higher, not lower, mean prices (74.5
  against 62.3) and a price at t = 199 at the price of production of the cheapest technique
  in use (`price_to_pp` 1.01 against 0.90). The leader is the lowest-cost firm in 94 % of
  periods at the defaults (the third row of Shaikh's Table 7.3 holds as an outcome) and
  prices vary more than costs (`price_cv_over_uc_cv` 1.8 in the base cell; it falls below 1
  under leader-follow, 0.85, which matches all prices to the leader).
- **Profit rates.** The unit-cost firms earn the higher realised profit rate: in the base
  cell 8.4 % against 4.5 % for the profit-rate firms (both controls 7.3–7.5 %); across stage 2
  seeds 11.1 % against 8.8 % where the unit-cost rule wins. The rule that maximises the
  profit rate at the current price does not realise the higher profit rate.
- **Demand met.** Unmet demand is small everywhere (below 3 % of demand on average, except
  under the anchor rule and the leader-follow operating-cost floor, where the industry
  collapses) and does not move with the winner (correlation 0.06). It is highest under
  retained earnings with growing demand (figure 4); the accelerator meets demand.
- **Turnover.** More entry and more firms where the unit-cost rule wins (19.9 entries in the
  window against 13.3; 19 firms at t = 199 against 13; HHI 0.24 against 0.34). Bankruptcies
  occur only with borrowing and go with the profit-rate rule (0.6 against 0.3 per seed).
  Under the accelerator and borrowing about two firms go bankrupt per run.
- **Marx bias as an outcome** (figure 6). Realised technical change is Marx-biased (γ > 0,
  χ > 0) for the unit-cost label in 84 % of base seeds against 30 % for the profit-rate
  label; under the neutral innovation set it is not biased for either (χ < 0: the
  capital-saving designs dominate). Within stage 2, the profit-rate label's change is
  Marx-biased more often in the seeds it wins (0.71 against 0.49).
- **The price signature** (figure 5). Under real competition the price at t = 199 exceeds the
  price at t = 100 in 17 % (marx 0.5) to 31 % (marx 3) of seeds and ends about 10–20 % above
  the price of production; under leader-follow it rises in at most 6 % of seeds and ends
  below the price of production (0.85–0.93). A rise of the long-run price after
  capital-using adoptions (Okishio's theorem fails) happens only under real competition, and
  more often the more capital-using the innovation set.

## 6. The cells the group should argue about

1. **`anchor_r16`**: one of the two configurations where the profit-rate rule wins beyond
   drift (0.26 for the unit-cost rule). It is version 1 pricing with version 1 rbar; the same rule
   at rbar 0.05 is at drift. Is the anchor rule (target-return pricing with rbar 0.16)
   a legitimate treatment of "rare price wars", or an artefact of an anchor that builds
   rbar into the price?
2. **`no_tech`**: without technical change the two rules are indistinguishable. The research
   question is about technical change; the categories rule and the innovation set are not
   details, they are the model.
3. **Categories against the innovation set**: the innovation set gives the unit-cost rule
   0.88–0.94 where categories give 0.67–0.81. The group must choose which one is the model
   and which the robustness check.
4. **Real competition with the accelerator and borrowing** (`rc-acd-static-*`, 0.51–0.64):
   the finance arm of the research question; the unit-cost advantage halves.
5. **Leader-follow, retained earnings, growing demand, categories, rbar 0.16**
   (`lf-re-g01-cat-r16`): the other reversal beyond drift (0.32 at 500 seeds), and its
   finance twin `lf-acd-g01-cat-r16` at 0.85. The cleanest illustration of the research
   question in the whole design: the winner depends on how investment is financed. Its real
   competition twin `rc-re-g01-cat-r16` (0.32 at 100 seeds) was not run at 500 seeds.
6. **`lf_floor_ucs`**: 40 % of seeds end with no capacity; a configuration that destroys the
   industry should not be a treatment arm.

## 7. Recommendations: fixed choices and treatments

By the decision rule of `choices.md` (a factor whose levels do not move the share won
beyond the controls' interval is fixed at its default; one that does becomes a treatment
or is fixed at the level the group argues for from theory):

**Fix at the default** (no level moved the outcome): selection intensity CHI = 1 (but see
the interaction with finance: keep CHI ∈ {0.25, 4} as a robustness check of the finance
result); demand form replicator (the logit level at η = 1 is the same model; if the logit
form is wanted, it needs an η that differs from χ); `PRICE_FLOOR = "unit_cost"`;
`EXCESS_DEMAND = "normal_capacity"`; `ENTRY_SPEED` = 5; scrapping 2 / 2; depreciation by
time; `PLANT_SIZE` = 20; τ = 0; `HURDLE_FLOOR_AT_ZERO` (inert); `SHORTAGE_RULE` (inert under
leader-follow); `TECH_DIFFUSION` and `TECH_REFERENCE` (no move against marx 1.5).

**Treatments** (they move the outcome and carry the research question):
- **Pricing rule**: real competition and leader-follow, both kept, as planned. Leader-follow
  with the unit-cost floor (0.83) is the natural leader-follow arm: the markup floor (0.66)
  never lets the Okishio hurdle reach zero, and the operating-cost floor destroys the
  industry in 40 % of seeds. Recommendation: switch `LEADER_FOLLOW_FLOOR` to `unit_cost` for
  the leader-follow arm, or keep `markup` and say why. The anchor rule stays a version 1
  switch, outside the main design, reported as one of the two reversals.
- **Finance**: retained earnings and accelerator with borrowing, both kept; it is the
  strongest interaction with the pricing rule. The accelerator without borrowing adds little
  (it sits between the two) and can be dropped.
- **Technical change**: the decision of the group. Recommendation: the innovation set (marx,
  TECH_BIAS 1.5) as the main specification, since its zones are outcomes rather than coin
  flips, with TECH_BIAS {0.5, 3} and the neutral set as treatments; the categories rule as
  the version 1 robustness check; `TECH_DRAWS = False` reported as the null (no contest).
  `TECH_DRAW_TIMING = "investment"` pushes the unit-cost share to 1 by compounding a lead;
  keep `"period"` as the default for that reason.
- **Demand**: static and growing 0.01 as treatments; 0.03 growth and unmet-and-growing push
  the outcome to drift and cost 4–20 times more per run; report them, do not cross them.
- **rbar**: 0.05 as the default; 0.16 as a treatment only with the categories rule, where
  it matters.

## 8. Open questions

1. Why does the anchor rule at rbar 0.16 reverse the outcome? The decomposition says
   through both channels (price −0.18, accumulation −0.21), with almost no entry (0.05
   entries in the window) and 2 firms at the end: a duopoly in which the target-return
   anchor sets the price. Worth a closer look with `debug.report` before the group decides.
2. Unit-cost firms realise the higher profit rate and the higher prices where they win.
   Is that because the profit-rate firms' dearer techniques lower their realised rate once
   prices fall (the Shaikh argument), or because the winners are price leaders in a less
   competitive market? The seed-level data in `runs.csv` (`profit_rate_*`, `price_to_pp`,
   `hhi_mean`) allow a regression; not done here.
3. The decomposition's window (t = 100–199) misses most takeovers (mean `takeover_t`
   around 118 in the base cell): use the `_all` columns for attribution.
4. `uc_end_{label}` in `macro` is 0, not missing, when a label has no capacity (handled in
   `summarise`; the collector could write None).
5. Docs detail from the plan: with `PLANT_SIZE = 20` initial capacity is 760 and demand
   674.7, not the 680 of the overview and `choices.md`.
6. The controls depart from 0.5 by up to 0.12 (e.g. `is_neutral`: 0.38 for the unit-cost
   control): the single random stream consumed in firm order. Per-mechanism random streams
   would remove that label effect.

## 9. Files

- `outputs/sensitivity/runs.csv` and `runs.parquet` (86 400 rows; committed as
  `runs.csv.gz`, see `choices.md`), `cells.csv` (one row per stage, cell and population),
  `stage3_cells.json` (the stage 3 choice), `progress.log`.
- Figures, `outputs/sensitivity/figures/`: `1_tornado_stage1.png`, `2_phase_stage2.png`
  (technical-change rule as the vertical axis) and `2b_phase_stage2_conflict_share.png`
  (the realised conflict share instead), `3_channels.png`, `4_demand_turnover.png`,
  `5_price_signature.png`, `6_marx_bias.png`. Regenerate with
  `python -m experiments.sensitivity figures`.
- `debug.report` PDFs (not committed; regenerate with `python -m experiments.sensitivity
  rerun RUN_ID` and the `debug.report` command it prints): `outputs/sensitivity/reruns/
  1_base_mixed_s1/debug/report.pdf` (seed 1 of the base cell, a seed the profit-rate rule
  wins) and `1_base_mixed_s4` (a typical seed, the unit-cost rule takes over at t = 93),
  `1_lf_mixed_s1` (leader-follow defaults), `2_rc-re-static-is15-r16_mixed_s1` (the largest
  gap of stage 2, 0.56; 0.49 at 500 seeds in stage 3).
