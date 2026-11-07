# Prompt: sensitivity analysis of the real-competition ABM (step 4 of the plan)

Paste everything below the line into a session (Cowork, Claude for science or Claude Code)
started at the root of a checkout of branch `v2-collector` of
`phdugolopez/EPOG_MIF_SIMPLE_ABM`. Written 7 November 2026.

---

You are working in the group's real-competition ABM (Shaikh against Okishio), a Python model
built on the course template `pierrefunalot/EPOG_MIF_SIMPLE_ABM`. Your task is the **first
full sensitivity analysis** of version 2: map, over the parameter space, which rule of
technique choice dominates, whether demand is met, how often firms enter and leave, and what
else moves, so that the group can decide which switches become fixed choices and which become
treatments. The model itself must not change.

## 0. Read first, then plan and stop

Read in this order before running anything:

1. `CLAUDE.md`: the neutrality rule, the conventions and who owns which file. It binds you.
2. `docs/design/review-v2.md`, section 5 (the decisions of 7 November and the plan; you are
   doing step 4), and section 4 (the innovation set).
3. `docs/design/choices.md`: every choice made, the section "Sensitivity analysis (planned)"
   with the factor table, and the two "Neutral control" records.
4. `docs/design/collector.md` (every output column), `debug/README.md`, `README.md`
   ("Outputs and the debugging report"), `experiments/neutral_control.py`.
5. `parameters.py` in full: every switch and its values are documented there.

Then run `python -m unittest discover -s tests` (217 tests must pass), `python run.py` and
`python -m debug.report outputs`, and note the wall time of `Industry.run()` printed by
`run.py` (about 0.11 s on a laptop). Budget the design from it.

**Write a plan and stop.** It should contain the cell list of section 2 with the number of
runs and the estimated time, the observables of section 3 as a column list, your open
questions, and anything in these instructions that conflicts with the code or with
`choices.md`. Wait for my answer before running the grid.

## Ground rules

- **No change in behaviour.** You may add an experiment script and a `--set NAME=value`
  option to `run.py` (several allowed; values parsed as Python literals, strings as is, as
  `experiments/neutral_control.parse_overrides` does), nothing else. Prove with
  `python -m debug.compare_runs` that `run.py` without `--set` writes the same tables as
  before your change. No default in `parameters.py` moves: the defaults are frozen since
  7 November pending this analysis.
- **Neutrality.** `firm.type` is a label. Every cell that reports a winner also runs its
  neutral control (both labels on the unit-cost rule, both on the profit-rate rule) over
  the same seeds; a result is reported as beyond drift only when the mixed population's
  interval does not overlap the controls'. Report the controls next to every result.
- **Seeds fixed across cells**: seeds 1..N everywhere, so that treatments face the same
  draws. Never resolve a tie by firm order.
- **Every number carries its configuration.** The results table (section 4) holds every
  parameter of each run; a number without its row is not a result.
- One commit per phase on a branch `feature/sensitivity`, tests run before each commit, no
  push without asking. Record every choice you make in `docs/design/choices.md`.

## 1. The question the analysis answers

In an industry where cheaper techniques often need more capital per unit of output, does
market selection favour firms that equip new plants at the lowest unit cost (Shaikh, hurdle
h = 0) or at the highest profit rate at the current price (Okishio)? How does the answer
depend on how often price wars occur and on how investment is financed? Two selection
channels run at once: the price channel (lower costs, lower prices, more customers) and the
accumulation channel (higher profits, more plants). The pricing rule and the investment rule
set their relative strength, which is why both are factors here and not fixed.

## 2. Factors and design

**Factors.** Levels in brackets; the first is the version 2 default unless stated.

| Factor | Parameter(s) | Levels | Why |
|---|---|---|---|
| Pricing rule | `PRICING_RULE` | `real_competition`, `leader_follow`, `anchor` (version 1, with `RBAR = 0.16`) | how often price wars occur |
| Floor of the price | `PRICE_FLOOR` (real competition), `LEADER_FOLLOW_FLOOR` (leader-follow) | `unit_cost`, `operating_cost`; leader-follow also `markup` | where cuts stop; the Okishio hurdle reaches 0 only if the floor lets the margin close |
| Shortage branch (leader-follow) | `SHORTAGE_RULE` | `leader`, `no_cut` | whether a shortage lowers high prices |
| Investment rule and finance | `INVESTMENT_RULE`, `BORROWING` | (`retained_earnings`, False), (`accelerator`, True), (`accelerator`, False) | the accumulation channel; "how investment is financed" |
| Demand condition | `DEMAND_GROWTH`, `DEMAND_TO_CAPACITY` | static (0, 340/383); growing (0.01, 340/383) and (0.03, 340/383); initially unmet (0, 1.2) and growing and unmet (0.02, 1.2) | whether capacity is short or in excess; growth gives the accumulation channel room |
| Selection intensity | `CHI` | 0.25, 0.5, 1, 2, 4 | how fast a price gap becomes share (the demand brief's key parameter) |
| Demand form | `DEMAND_FORM` | `replicator`, `logit` (`ETA` = 1) | robustness of the selection environment |
| Technical change | `TECH_CHANGE`, `TECH_SET`, `TECH_BIAS` | `categories` with `TECH_CONFLICT` ∈ {0, 0.5}; `innovation_set` marx with `TECH_BIAS` ∈ {0.5, 1.5, 3}; `innovation_set` neutral | the innovation set, Marx-biased or neutral |
| Diffusion and timing | `TECH_DIFFUSION`, `TECH_DRAW_TIMING` | (`public`, `period`), (`private`, `period`), (`public`, `investment`) | private knowledge against the choice itself; draws per investment compound a lead |
| Entry | `RBAR`, `ENTRY_SPEED` | (0.05, 5), (0.05, 1), (0.16, 5) | the churn at rbar = 0.05 |
| Scrapping | `IDLE_PERIODS`, `OBSOLESCENCE_PERIODS` | (2, 2), (4, 4) | how fast capacity adjusts |
| Depreciation | `DEPRECIATION` | `time`, `use` | accounts of idle capacity |
| Plant size | `PLANT_SIZE` | 20, 40 | lumpiness of investment |
| Capital advanced | `TAU` | 0, 0.25 | above about 0.12 D2 stops being a conflict case: τ decides whether the rules ever disagree |

**Design, in three stages.**

1. **One factor at a time around the version 2 defaults**: every level of every factor
   above with everything else at its default, about 40 cells, 50 seeds each, with the two
   neutral controls for every cell (about 6 000 runs, 12 minutes at 0.11 s). 50 seeds
   detect a 20-point gap in the share of seeds won at the 5 % level with 80 % power
   (critique, section 6). Add a `TECH_DRAWS = False` cell (fixed menu C, D1, D2): the
   contest without technical change.
2. **A factorial on the movers**: the factors whose levels moved the share of seeds won
   beyond the controls' intervals in stage 1, crossed with each other (expect pricing rule,
   investment rule, demand condition, selection intensity and technical change; cap the
   factorial at about 100 cells by keeping two or three levels per factor), 50 seeds each,
   controls for every cell.
3. **The cells that decide**: the version 2 defaults, the leader-follow defaults, and the
   four or five cells the group will argue about, 200 seeds each with controls, to size a
   10-point gap.

Hold the headline figure in mind: the phase diagram of the winning rule in the plane of
selection intensity and the conflict share of the innovation set (critique, section 6),
one panel per pricing rule and per investment rule.

## 3. Observables

Per run (one row per cell, population and seed), from the collector's tables, with the
window t = 100–199 for means unless stated (the first 100 periods are the burn-in of the
initial endowment; also report t = 50–199 for the price so that the opening war shows):

**Who dominates.**
- `cap_share_shaikh_end`, `sales_share_shaikh_end`: capacity and sales shares of the label
  "shaikh" at t = 199 (from `macro`: `capacity_shaikh / capacity_total`,
  `sales_shaikh / sales_total`); `shaikh_wins` = capacity share > 0.5; `takeover_t`: the
  first period after which one label holds more than 90 % of capacity for the rest of the
  run (NaN if never); `n_shaikh_end`, `n_okishio_end`.
- The decomposition, cumulated over the window: `d_share_price`, `d_share_accum`,
  `d_share_entry`, `d_share_exit` from `analysis/indicators.py` (sections 4.2 and 4.3 of
  the collector brief), so that each win is attributed to the price channel or the
  accumulation channel.
- `hurdle_mean` by label (constant per rule today; it will matter when h evolves).

**Is demand met.**
- `unmet_share`: mean of `unmet_total / demand`; `shortage_periods`: periods with
  `unmet_total > 0`; `util_mean`: mean capacity-weighted utilisation; `capacity_to_demand`:
  mean `capacity_total / demand`; `excess_capacity_periods`: periods with utilisation below
  0.9.

**Entry and exit.**
- `entries`, `exits`, `exits_share`, `exits_bankruptcy`, `exits_non_renewal` over the
  whole run and over the window; `n_firms_mean`, `n_firms_end`, `hhi_mean` (on sales);
  `entrant_survival`: share of entrants still present 20 periods after entry;
  `exit_age_median`.

**Price and profit (the research question's observables).**
- `price_mean`, `price_end`, `price_min`, `price_max`; `price_to_pp`: the price at t = 199
  over the price of production uc + rbar κ of the lowest-unit-cost technique in use
  (Shaikh: the price gravitates around the regulating capital's price of production;
  Okishio: the long-run price relative to the wage never rises after an adoption);
  `price_rise_after_adoption`: did the price at t = 199 exceed the price at t = 100?
- `cut_periods`: periods with at least one cut (`war_on`); `war_episodes`, `war_depth_mean`
  (from the `war_start` and `war_end` events); `cutting_share_mean`: mean
  `n_cutting / n_active`.
- `profit_rate_shaikh`, `profit_rate_okishio`, `profit_rate_total` (means), `r_new_mean`,
  `periods_above_rbar`: how turbulent the equalisation is.
- `leader_lowest_cost_share`: share of periods in which the leader is the lowest-cost firm
  (row 3 of Shaikh's Table 7.3 as an outcome); `price_cv_over_uc_cv`: mean of
  `price_cv_w / uc_cv_w` (the law of correlated prices: prices closer than costs).
- `margin_spread`: mean of max − min of `margin` over firms; `ucs_spread_mean`: the
  vintage spread (`ucs_spread` from `firms`, capacity-weighted).

**Technical change.**
- From the `design` and `adopt` events: `designs_offered`, `designs_adopted_shaikh`,
  `designs_adopted_okishio`, `zone_both`, `zone_conflict`, `zone_profit_rate`, `zone_none`
  (shares of draws, at the firm's price); `conflict_adopted_shaikh`: share of conflict
  designs offered to Shaikh firms that they adopted (should be 1); `okishio_dearer`: share
  of Okishio orders whose technique is not the firm's cheapest known (the switch-back of
  the choices record).
- `gamma_shaikh`, `gamma_okishio`: the fall of `ucs_mean` over the window as a rate per
  period; `chi_shaikh`, `chi_okishio`: the rise of `kappa_mean`; `marx_biased`: γ > 0 and
  χ > 0 for each label (Marx bias as an outcome); `uc_end_shaikh`, `uc_end_okishio`.
- `diffusion_lag_mean`: periods from a design's first plant to half of industry capacity
  (NaN if never); `replacements_shaikh`, `replacements_okishio` (`n_replace` in `groups`).

**Finance and soundness.**
- `debt_to_sales_mean`, `defaults`, `unpaid_bills_end`, `dividends_total`;
  `n_check_fail` (must be 0) and `floor_viol_periods`.

Other observables you judge relevant to the research question are welcome: say why in the
plan. Two that may be: the age of the capital stock by label (capacity-weighted age from
`plants`), since Shaikh firms are expected to hold younger capital, and the number of
distinct techniques in use (the diversity that Table 7.3's row 7 expects to persist).

## 4. The results table

Deliver `outputs/sensitivity/runs.csv` (and `.parquet`), one row per run, with:

- `run_id` (`{stage}_{cell}_{population}_s{seed}`), `stage`, `cell` (a short name),
  `population` (`mixed`, `all_unit_cost`, `all_profit_rate`), `seed`;
- **every upper-case parameter of `parameters.py`** as a column under its lower-case name,
  tuples and dicts as JSON, exactly as the `runs` table of `run.py` does, plus `overrides`:
  the overrides of the cell as JSON (`{"CHI": 2, "PRICING_RULE": "leader_follow"}`), so
  that a run is rerun from its row alone;
- `code_version`, `param_hash`, `wall_seconds`;
- every observable of section 3.

And `outputs/sensitivity/cells.csv`, one row per cell and population: the mean and the
95 % interval of each observable over seeds, the share of seeds won with its Wilson
interval, and `beyond_drift` (the mixed interval does not overlap either control's).

**Rerunning one run for a closer look.** Give the experiment script a `rerun` command:

    python -m experiments.sensitivity rerun RUN_ID [--out DIR]

which reads the row, rebuilds the configuration from its `overrides` and `seed`, runs
`run.py --set ...` into `DIR` (default `outputs/sensitivity/reruns/RUN_ID/`) and prints the
`debug.report` command for it. Check that a rerun reproduces its row's observables exactly
(same `param_hash`, same values) for three rows picked at random; the check is a test.

## 5. Figures

In `outputs/sensitivity/figures/`, with the colours of `style.py` (Shaikh blue, Okishio
orange) and every chart's question as its title:

1. **Tornado of stage 1**: for each factor, the share of seeds won by Shaikh firms at each
   level, the controls' band shaded, the default marked.
2. **Phase diagrams of stage 2**: the winning rule (share of seeds won) in the plane of
   selection intensity × technical change (conflict share or bias), one panel per pricing
   rule and per investment rule; the demand condition as marker shape.
3. **Channels**: for every cell, the price-driven and the accumulation terms of the share
   change against each other, coloured by pricing rule.
4. **Demand and turnover**: unmet share and entries per period across the demand
   conditions and the investment rules.
5. **Price signature**: the price at t = 199 over the price of production against the
   bias of the innovation set, by pricing rule (does the long-run price rise after
   capital-using adoptions?).
6. **Marx bias as an outcome**: realised γ against χ by label and technical-change rule.

## 6. What to deliver

- The scripts: `experiments/sensitivity.py` (`grid`, `summarise`, `rerun`, `figures`
  subcommands) and `run.py --set`; tests for the override parsing, the rerun reproduction,
  the summary intervals and a two-cell, two-seed smoke run.
- The tables and figures of sections 4 and 5, and the `debug.report` PDFs of the version 2
  default cell, the leader-follow default cell and the cell with the largest gap.
- A short report, `docs/design/sensitivity-results.md`: for each factor, did its levels move
  the share of seeds won beyond the controls (the decision rule of `choices.md`); the
  phase diagram in words; which observables moved with the winner (prices, profit rates,
  demand met, turnover, Marx bias); the cells the group should argue about; the
  configurations you recommend as fixed choices and as treatments, with your reasons; and
  the open questions. Fill the "Result" column of the factor table in `choices.md`.
- A summary for me: what changed in the code (it should be two files and the tests), the
  run time, and what you could not do.

If something in these instructions conflicts with the code or with `choices.md`, do not
decide silently: note it in the plan and ask me, or follow `choices.md` and record the
conflict.
