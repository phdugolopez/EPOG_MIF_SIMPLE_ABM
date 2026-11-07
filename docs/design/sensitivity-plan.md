# Plan for the sensitivity analysis (step 4 of the plan in `review-v2.md`)

Written 7 November 2026 on branch `feature/sensitivity` (from `v2-collector` at `8649eb1`),
in answer to `sensitivity-prompt.md`. Nothing has been run beyond the checks of section 0.
**Waiting for an answer to section 6 before the grid runs.**

## 0. Checks done

- 217 tests pass (`python -m unittest discover -s tests`, 21 s).
- `python run.py` (seed 42): `Industry.run()` 0.121 s; `python -m debug.report outputs`
  writes 57 pages in 15 s, all checks pass.
- Machine: Apple M5, 10 cores, Python 3.13, pyarrow installed.
- Per-run wall time of `Industry.run()` by factor level (seeds 1–3, mean), which sizes the
  budget: the cost scales with the number of firms and plants, so the demand conditions are
  the expensive cells.

| Level | s/run | Firms at t = 199 (seeds 1–3) |
|---|---|---|
| version 2 defaults | 0.146 | 35, 10, 10 |
| `PRICING_RULE = leader_follow` | 0.136 | 3, 18, 7 |
| leader-follow, floor `unit_cost` / `operating_cost` | 0.134 / 0.095 | 24–26 / 2–7 (seed 1: no capacity left at t = 199) |
| `anchor`, `RBAR = 0.16` | 0.062 | 2, 2, 2 |
| accelerator, with / without borrowing | 0.073 / 0.075 | 3–6 / 5–10 |
| `DEMAND_GROWTH = 0.01` / `0.03` | 0.226 / **3.05** | 4–7 / 38–48 |
| `DEMAND_TO_CAPACITY = 1.2`, growth 0 / 0.02 | 0.192 / 0.823 | 2–41 / 12–33 |
| `innovation_set` marx 1.5 / 3 / neutral | 0.266 / 0.218 / 0.304 | 24–29 |
| `innovation_set`, private / per investment | 0.139 / 0.288 | 13–38 / 27–29 |
| `CHI = 0.25` / `4` | 0.132 / 0.135 | 13–22 / 2–29 |
| `PLANT_SIZE = 40`, `TECH_DRAWS = False` | 0.068 / 0.085 | 10–19 / 12 |
| others (`logit`, `TAU`, scrapping 4/4, `ENTRY_SPEED = 1`) | 0.13–0.15 | |

Building the seven tables of a run (`run.tables`) adds 0.055 s; the observables of section 3
are computed from those frames in the worker process and only the one-row summary is kept, so
a run costs about 0.2 s all in (3 s for the 3 % growth cell).

## 1. Code changes (two files and the tests, no change in behaviour)

- `run.py`: a repeatable `--set NAME=value` option (values parsed as Python literals,
  strings as is, as `experiments.neutral_control.parse_overrides`), applied through
  `configure(seed, **overrides)` after `--seed`. Dict literals work for the controls:
  `--set 'HURDLE_RULES={"shaikh": "unit_cost", "okishio": "unit_cost"}'`. Proof that nothing
  moved: `run.py` without `--set` written before and after the change and compared with
  `python -m debug.compare_runs` (recorded in `choices.md`).
- `experiments/sensitivity.py` with four subcommands:
  - `grid --stage {1,2,3} [--seeds N] [--jobs J] [--resume] [--cells NAME ...]`: runs every
    cell × population × seed, seeds 1..N everywhere, one `Industry` per task in a
    `multiprocessing` pool (`--jobs`, default the number of cores), results gathered and
    written in (cell, population, seed) order so that the tables never depend on scheduling.
    Every finished cell is appended to `outputs/sensitivity/runs.csv` (and `.parquet`) and a
    line goes to `outputs/sensitivity/progress.log`; `--resume` skips finished cells.
  - `summarise`: `cells.csv` (mean and 95 % interval of every observable over seeds, share
    of seeds won with its Wilson interval, `beyond_drift`).
  - `rerun RUN_ID [--out DIR]`: rebuilds the configuration from the row's `overrides`,
    `population` and `seed`, runs `run.py --set ...` into `DIR` and prints the `debug.report`
    command.
  - `figures`: the six figures of section 5 into `outputs/sensitivity/figures/`.
- `tests/test_sensitivity.py`: override parsing (`--set`), the rerun reproduction (three
  random rows of a two-cell, two-seed smoke grid give the same `param_hash` and observables),
  the Wilson and mean intervals, the smoke grid itself; `--set` added to the `run.py` tests.

The `rerun` reproduction holds only if a run is deterministic across processes: the model has
a single `random.Random(SEED)` and no set iteration over strings in the mechanisms, and the
test checks it.

## 2. Cells and budget

Populations per cell: `mixed` (`HURDLE_RULES` of `parameters.py`), `all_unit_cost`,
`all_profit_rate`; 3 populations × N seeds = 3N runs per cell. Seeds 1..N in every cell.
`run_id = {stage}_{cell}_{population}_s{seed}` (`run.py --experiment {stage}`).

### Stage 1: one factor at a time around the version 2 defaults (N = 50)

Overrides relative to the version 2 defaults; `lf` = `PRICING_RULE = leader_follow`,
`is` = `TECH_CHANGE = innovation_set`. The base of the leader-follow sub-factors (floor,
shortage branch) is the leader-follow cell; the base of the diffusion and timing cells is the
innovation-set cell, since `TECH_DIFFUSION` and `TECH_DRAW_TIMING` are inert under
`categories` (conflict 1, section 6).

| # | Cell | Overrides | s/run | Runs |
|---|---|---|---|---|
| 1 | `base` | none | 0.15 | 150 |
| 2 | `lf` | `PRICING_RULE=leader_follow` | 0.14 | 150 |
| 3 | `anchor_r16` | `PRICING_RULE=anchor, RBAR=0.16` | 0.06 | 150 |
| 4 | `rc_floor_ucs` | `PRICE_FLOOR=operating_cost` | 0.15 | 150 |
| 5 | `lf_floor_uc` | lf, `LEADER_FOLLOW_FLOOR=unit_cost` | 0.13 | 150 |
| 6 | `lf_floor_ucs` | lf, `LEADER_FOLLOW_FLOOR=operating_cost` | 0.10 | 150 |
| 7 | `lf_no_cut` | lf, `SHORTAGE_RULE=no_cut` | 0.14 | 150 |
| 8 | `accel_debt` | `INVESTMENT_RULE=accelerator, BORROWING=True` | 0.07 | 150 |
| 9 | `accel_cash` | `INVESTMENT_RULE=accelerator, BORROWING=False` | 0.08 | 150 |
| 10 | `grow_01` | `DEMAND_GROWTH=0.01` | 0.23 | 150 |
| 11 | `grow_03` | `DEMAND_GROWTH=0.03` | 3.05 | 150 |
| 12 | `unmet` | `DEMAND_TO_CAPACITY=1.2` | 0.19 | 150 |
| 13 | `unmet_grow_02` | `DEMAND_TO_CAPACITY=1.2, DEMAND_GROWTH=0.02` | 0.82 | 150 |
| 14–17 | `chi_025`, `chi_05`, `chi_2`, `chi_4` | `CHI=0.25 / 0.5 / 2 / 4` | 0.13 | 600 |
| 18 | `logit` | `DEMAND_FORM=logit` (`ETA = 1`) | 0.15 | 150 |
| 19 | `cat_q0` | `TECH_CONFLICT=0` | 0.15 | 150 |
| 20–22 | `is_marx_05`, `is_marx_15`, `is_marx_3` | is, `TECH_BIAS=0.5 / 1.5 / 3` | 0.25 | 450 |
| 23 | `is_neutral` | is, `TECH_SET=neutral` | 0.30 | 150 |
| 24 | `is_private` | is, `TECH_DIFFUSION=private` | 0.14 | 150 |
| 25 | `is_per_invest` | is, `TECH_DRAW_TIMING=investment` | 0.29 | 150 |
| 26 | `entry_theta1` | `ENTRY_SPEED=1` | 0.15 | 150 |
| 27 | `rbar_16` | `RBAR=0.16` | 0.15 | 150 |
| 28 | `scrap_4` | `IDLE_PERIODS=4, OBSOLESCENCE_PERIODS=4` | 0.14 | 150 |
| 29 | `depr_use` | `DEPRECIATION=use` | 0.15 | 150 |
| 30 | `plant_40` | `PLANT_SIZE=40` | 0.07 | 150 |
| 31 | `tau_025` | `TAU=0.25` | 0.14 | 150 |
| 32 | `no_tech` | `TECH_DRAWS=False` (fixed menu C, D1, D2) | 0.09 | 150 |

Proposed additions (say no to drop them): 33 `anchor_r05` (`PRICING_RULE=anchor` at
rbar 0.05, so that the anchor level is not confounded with the entry level, conflict 2);
34 `is_frontier` (is, `TECH_REFERENCE=frontier`, "run both" in `review-v2.md` section 4.2,
missing from the factor table); 35 `hurdle_no_floor` (`HURDLE_FLOOR_AT_ZERO=False`, the
Okishio rule below the floor); 36 `excess_unserved` (`EXCESS_DEMAND=unserved`, the other
shortage definition of the default pricing rule).

Stage 1: 32 cells, 4 800 runs (36 cells, 5 400 runs with the additions). Estimated time at
0.2 s a run plus the slow demand cells: about 27 min on one core, **about 4 min on 8
workers** (the 3 % growth cell alone is 450 s of core time).

### Stage 2: factorial on the movers (N = 50)

Decided from stage 1 by the decision rule (a level moves the outcome when the mixed
population's Wilson interval leaves both controls' intervals, or when the share of seeds won
differs from the base cell's beyond their intervals). Expected, and proposed as the default
if stage 1 confirms them: pricing rule {`real_competition`, `leader_follow`} × investment
{`retained_earnings`, `accelerator + BORROWING`} × demand {static, initially unmet} ×
`CHI` {0.5, 1, 2} × technical change {`categories` q = 0.5, `innovation_set` marx 1.5,
marx 3, neutral} = 96 cells, 14 400 runs, about 1 h of core time (8 min on 8 workers). If
demand growth is a mover, the 0.01 level replaces "initially unmet" (the 0.03 level would
cost 20 × more per run and only enters stage 3). A factor that did not move in stage 1 is
held at its default.

### Stage 3: the cells that decide (N = 200)

`base`, `lf`, and the four or five cells the group will argue about (the largest gaps of
stage 2, the cell with the headline phase-diagram contrast, the finance arm): about 7 cells,
4 200 runs, about 15 min of core time.

Total: about 24 000 runs, about 2 h of core time, **20–25 min on 8 workers**. The upgrade of
the unattended header (200 / 100 / 500 seeds) would be about 4 × that: 1.5 h on 8 workers.

## 3. Observables (one row per run; window t = 100–199 unless stated)

Who dominates (from `macro`, `groups`, `analysis.indicators`):
`cap_share_shaikh_end`, `sales_share_shaikh_end`, `shaikh_wins` (capacity share > 0.5),
`undecided` (no producing capacity at t = 199: neither wins, see conflict 4), `takeover_t`
(first t after which one label holds > 90 % of capacity to the end; NaN if never),
`takeover_label`, `n_shaikh_end`, `n_okishio_end`, `d_share_price` (cumulated `term_price`
of the sales-share decomposition, `shaikh` group), `d_share_rationing`, `d_share_entry_exit`
(sales), `d_share_accum` (`term_ordered` + `term_retired` + `term_cancelled` of the capacity
decomposition), `d_share_entry`, `d_share_exit` (capacity), `hurdle_mean_shaikh`,
`hurdle_mean_okishio`.

Is demand met (`macro`): `unmet_share` (mean `unmet_total / demand`), `shortage_periods`
(`unmet_total > 0`), `util_mean`, `capacity_to_demand`, `excess_capacity_periods`
(`util < 0.9`).

Entry and exit (`macro`, `events`, `firms`): `entries`, `exits`, `exits_share`,
`exits_bankruptcy`, `exits_non_renewal` (whole run) and the same with suffix `_w` (window);
`n_firms_mean`, `n_firms_end`, `n_firms_min`, `hhi_mean` (`hhi_sales`), `entrant_survival`
(entrants born at t ≤ 179 still present at born + 20), `exit_age_median`.

Price and profit (`macro`, `firms`, `plants`, `events`): `price_mean`, `price_mean_50`
(t = 50–199), `price_end`, `price_min`, `price_max`, `price_to_pp` (price at t = 199 over
uc + rbar κ of the lowest-uc running technique at t = 199), `price_rise_after_adoption`
(price at 199 > price at 100), `cut_periods` (`war_on`), `war_episodes`, `war_depth_mean`
(1 − `war_end.value / war_start.value`; wars starting at t = 0 have no depth),
`cutting_share_mean` (`n_cutting / n_active`), `profit_rate_shaikh`, `profit_rate_okishio`,
`profit_rate_total`, `profit_rate_total_50`, `r_new_mean`, `periods_above_rbar` (industry
`profit_rate > RBAR`), `leader_lowest_cost_share`, `price_cv_over_uc_cv` (mean of
`price_cv_w / uc_cv_w`, periods with `uc_cv_w = 0` dropped), `margin_spread`,
`ucs_spread_mean` (capacity-weighted over firms).

Technical change (`events`, `groups`, `plants`): `designs_offered`,
`designs_adopted_shaikh`, `designs_adopted_okishio`, `designs_built` (orders with a design
technique), `zone_both`, `zone_conflict`, `zone_profit_rate`, `zone_none` (shares of design
events by `cause`), `conflict_adopted_shaikh` (design events with cause `unit_cost` offered
to unit-cost firms that have an adopt event), `okishio_dearer` (order events of profit-rate
firms with `tech != other_tech`, `other_tech` being the unit-cost pick, i.e. the cheapest
known), `gamma_shaikh`, `gamma_okishio` (−ln(`ucs_mean`₁₉₉ / `ucs_mean`₁₀₀) / 99),
`chi_shaikh`, `chi_okishio` (same on `kappa_mean`), `marx_biased_shaikh`,
`marx_biased_okishio` (γ > 0 and χ > 0), `uc_end_shaikh`, `uc_end_okishio`,
`diffusion_lag_mean` (per design: periods from its first producing plant to half of
industry capacity; mean over designs that reach it; NaN if none), `diffusion_reached_share`,
`replacements_shaikh`, `replacements_okishio` (`n_replace`).

Proposed additions: `capital_age_shaikh`, `capital_age_okishio` (capacity-weighted plant age
at t = 199: Shaikh firms are expected to hold younger capital), `n_techniques_in_use_mean`
(distinct techniques among running plants, Table 7.3 row 7), `n_active_mean`,
`capacity_designs_share_end` (share of capacity on drawn designs).

Finance and soundness: `debt_to_sales_mean` (`debt` / (`price_avg` × `sales_total`)),
`defaults` (default events), `unpaid_bills_end`, `dividends_total`, `n_check_fail`,
`floor_viol_periods`.

Plus, as the prompt asks: `run_id`, `stage`, `cell`, `population`, `seed`, every parameter of
`parameters.py` under its lower-case name exactly as `run.runs_row` writes it, `overrides`
(JSON), `code_version`, `param_hash`, `wall_seconds`.

`cells.csv`: one row per (stage, cell, population) with `n_seeds`, `n_undecided`, `won`,
`share_won`, `won_low`, `won_high`, and for every numeric observable its mean, 2.5 % and
97.5 % quantiles over seeds (`{name}_mean`, `{name}_lo`, `{name}_hi`); for the mixed rows
`beyond_drift` (the mixed Wilson interval overlaps neither control's) and
`beyond_base` (does not overlap the base cell's mixed interval).

## 4. Figures (section 5 of the prompt)

As listed there, with `style.py` colours. For the phase diagram the technical-change axis is
the design parameter (q under `categories`, `TECH_BIAS` under `innovation_set`), with the
realised conflict share `zone_conflict` as a second row of panels, since under the innovation
set the conflict share is an outcome (`review-v2.md` section 4.1).

## 5. Deliverables and commits (one per phase on `feature/sensitivity`, tests before each)

1. This plan. 2. `run.py --set`, `experiments/sensitivity.py`, tests, the `compare_runs`
proof. 3. Stage 1 tables. 4. Stage 2 tables. 5. Stage 3 tables. 6. Figures, the three
`debug.report` PDFs (`base`, `lf`, the largest gap), `docs/design/sensitivity-results.md`,
the "Result" column of the factor table and the rows of `choices.md`.

## 6. Conflicts with the code or `choices.md`, and open questions

1. **Diffusion and timing are inert under the default technical-change rule.**
   `TECH_DIFFUSION` and `TECH_DRAW_TIMING` act only when `TECH_CHANGE = innovation_set`
   (`model/scheduler.py`, the branches at `start_period` and `invest`). The prompt lists
   (`public`, `period`) as the default level "with everything else at its default", which
   under `categories` would be the base cell twice. Plan: run `is_private` and
   `is_per_invest` around the innovation-set cell (marx 1.5), and read them against it.
2. **The `anchor` level bundles `RBAR = 0.16`**, which is also a level of the entry factor:
   the pricing comparison is confounded with the entry churn. Proposed: an extra
   `anchor_r05` cell. (The anchor rule at rbar 0.05 runs; it is in `test_switches_run`.)
3. **The 3 % growth cell costs 3 s a run** (the industry reaches 47 firms): fine in stage 1
   (450 s of core time), too dear to cross in stage 2. If growth moves the outcome, stage 2
   uses 0.01 and stage 3 includes one 0.03 cell.
4. **Seeds with no producing capacity at t = 199** (leader-follow with the operating-cost
   floor, seed 1: 2 firms and `capacity_total = 0`) give a NaN capacity share.
   `experiments/neutral_control.py` counts `NaN > 0.5` as False, i.e. as an Okishio win.
   Plan: count them as `undecided`, excluded from the share won, and report `n_undecided` per
   cell. Alternative: decide them on the sales share or on the number of firms. Your call.
5. **Window.** `choices.md` pre-registers means of price and profit rates over t ≥ 50; the
   prompt asks for t = 100–199 with t = 50–199 for the price. Both are reported for the price
   and the profit rate (`_50` suffix); the window for everything else is 100–199.
6. **Definitions fixed by me** (section 3): `periods_above_rbar` on the industry profit rate
   (not `r_new`); `debt_to_sales` on revenue; `okishio_dearer` from order events; γ and χ as
   log rates between t = 100 and 199; `takeover_t` with 90 % of capacity; entrants born after
   t = 179 excluded from `entrant_survival`. Say if another definition is wanted.
7. **The critique is not in the repository** (only quoted in `collector-brief.md`): the power
   statement (50 seeds for a 20-point gap) and the phase-diagram design are taken from the
   prompt. With 50 seeds a Wilson interval is about ±14 points wide, so `beyond_drift` needs
   roughly 80 % of seeds won against controls near 50 %: a strict rule, by design.
8. **Stage 2 is decided after stage 1.** Do you want a second stop with the stage 1
   tornado before the factorial runs, or should the script go on with the factorial of
   section 2 (adjusted by the decision rule) without waiting?
9. **Seeds.** The prompt says 50 / 50 / 200; the unattended header of `sensitivity-prompt.md`
   says 200 / 100 / 500. Both fit the machine (25 min against 1.5 h on 8 workers). Which?
10. **Parallel runs and resume** (`--jobs`, `--resume`, `progress.log`) are in the script
    only, as the unattended header asks; they change no result. Confirm.
11. **Docs detail, not a conflict:** with `PLANT_SIZE = 20` the initial capacity is 760 and
    demand 674.7, not the 680 the overview and `choices.md` state (their 766 is the version 1
    capacity). Worth a one-line fix in step 5.
