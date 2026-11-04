# Collector and debugging plots: plan (phase 0)

Written 4 November 2026 from `docs/design/collector-brief.md` (the specification), after
reading `CLAUDE.md`, `mechanism-briefs.md`, `choices.md`, `model/`, `markets/`,
`equations/`, `run.py`, `plot_outputs.py` and `tests/`. Nothing below is implemented yet.

## 0. State of the tree, timings

- Branch `feat-collector-and-metrics` at `49f7974`, clean apart from the staged brief and
  the untracked `.idea/`. **`parameters.py` has no local changes**: `DEMAND_TO_CAPACITY`,
  `PRICING_ANCHOR` and `MARKUP` are at their committed values (340/383, `target_return`,
  0.282). See open question 1.
- Tests: 44 pass in 0.34 s (`python -m unittest discover -s tests`).
- Baseline: `run.py` 0.25 s wall in total, of which `Industry().run()` is 0.044 s (median of
  5); the rest is the pandas import and the CSV writes. The 50 % budget of phase 5 is read
  against the 0.044 s loop (see open question 9).
- A provisional reference run from `49f7974` (macro, firms, plants, flows) is saved in the
  session scratchpad; it is regenerated once the parameter values are confirmed, from a
  `git worktree` of the reference commit, so it never depends on the working tree.
- `pyarrow` is not installed in `.venv`; `pandas` 3.1, `matplotlib` 3.11, Python 3.13 (CI
  runs 3.11).

## 1. Design decisions proposed

**D1. Names: the brief's names are used (decided at open question 6, implemented in
phase 2).** The plan first proposed keeping every existing column name and recording the
brief's † names as aliases; Ugo chose the brief's names instead. Every row marked
"alias" in the mapping tables of §2 is therefore a **rename**: `time` → `t`,
`sales` → `sales_total`, `unserved` → `unmet_total`, `capacity` → `capacity_total`,
`mean_price` → `price_avg`, `leader_price` → `price_lead`, `n_at_war` → `n_cutting`,
`investment` → `invest_total`, `roe_cash` → `roe_balance` (macro); `time` → `t`,
`at_war` → `cutting`, `profit_rate` → `r_avg`, `write_offs` → `write_off`,
`investment` → `invest_spend`, `book_value` → `k_book`, `exit_reason` → `exit_cause`
(firms); `time` → `t`, `technique` → `tech`, `book_value` → `k_book`,
`periods_below_cost` → `below_cost` (plants); `time` → `t` (flows). `plot_outputs.py`,
`run.py` and the tests were updated with them; the LaTeX sections reference no column.
The reference comparison matches renamed columns by this map, value for value. `n_firms`
(end of period) and `share` (after step 6) keep their meaning, with `n_active` and
`share_demand` / `share_end` beside them.

**D2. Record at source through one hook.** `run_period` calls
`collector.after_step(industry, step)` after each of the six steps. The hook copies into
`industry.record` (one dict per period) what later steps overwrite: shares after step 2,
plant book values before write-offs (step 3), pending plants after step 4 and after step 5
(to split replacement from expansion orders), debt after steps 3 and 5 (overdraft versus
plant finance), net worth before exit (step 5), exits and entries (step 6). `collect`
builds all rows from the record and from the state at step 7. The hook never writes to
model state and never draws from `industry.rng`.

**D3. Values that only exist as locals.** Three cases need instrumentation (§3 below):
the anchor and the floor in `set_prices`, the retirement cause in `retire_plants`, and the
parent and mutation flag in `inherited_type`. Everything else is either already an
attribute (`revenue`, `operating_cost`, `depreciation`, `interest`, `hurdle`, `at_war`,
`util_history`) or exactly recomputable from state with the pure equation that produced
it: `p_entry = entry_probability(industry.r_new, RBAR, ENTRY_SPEED)`, `exp_sales` and
`cap_desired` from `previous_sales`/`sales` and `INVESTMENT_SALES_LAG`, `tech_other` and
`r_best` from `hurdle`/`choose_technique`/`best_profit_rate`, the order cause from the
step at which the pending plant appeared (4 replacement, 5 expansion, 6 entry).

**D4. Ties.** `leader_ids` and `lowest_uc_ids` are sorted id lists stored as JSON strings
(`"[2, 3]"`), with `n_leaders`, `n_lowest_uc`, and `leader_id` / `lowest_uc_id` set to the
id only when the set is a singleton (−1 otherwise). `leader_is_lowest_cost` = the two sets
intersect. Equality of prices and of unit costs uses `math.isclose` with the default
relative tolerance, as `goods_market.allocate` does for prices (the paired initial firms
are bit-identical, so exact equality would also work; `isclose` is the safer convention
and is recorded in `choices.md`). Note: the existing `leader_is_lowest_cost` picks by list
order; its values therefore change where ties exist. It is the one pre-existing column
whose values may differ from the reference, and the comparison report will list every
period where it does (expected: the first periods, when the paired firms tie).

**D5. Plants are vintages.** Firm aggregates: `ucs` output-weighted over running plants,
`kappa` and `uc` capacity-weighted over producing plants (as `firm_uc` does today),
`k_cost` = Σ κ_v q̄_v over producing plants (= `Firm.capital` at step 3, so that
`r_avg = profit / k_cost` holds exactly), `k_book` = Σ book values over plants in
operation and on order (= existing `book_value`, construction in progress included, as
`choices.md` fixes). `r_newest` on the producing plants of the highest vintage,
capacity-weighted, at normal output. `p_floor` and `p_normal` are the values pricing used.
`n_plants`, `oldest_vintage`, `newest_vintage`, `ucs_spread` (max/min ucs over running
plants; 1 when one plant runs, NaN when none).

**D6. The capacity identity.** With K the producing capacity at the start of the period,
`K_{t+1} = K_t − retired − exit + ordered + entry − cancelled` holds only if `ordered`
counts **every** order placed at steps 4 and 5, by exiters as well as survivors, and
`cancelled` is the exiters' part of it (written off by `remove_firm`). With `ordered`
restricted to survivors, as the task statement words it, the `cancelled` term is
subtracted twice. Proposed: `ordered` = all incumbents' orders (which is also what the
plant market knows at step 5, before exit is decided), `cancelled` = orders of firms that
exit the same period, so that `ordered − cancelled` is the survivors' capacity arriving at
t + 1. Open question 3.

**D7. Groups.** Labels are the keys of `HURDLE_RULES`; one row per period and label even
when the label has no firm (zeros). `hurdle_mean` is capacity-weighted over producers.

**D8. Flows by group.** The brief's flow matrix has one column per group of firms. The
only way to split `pay()`'s `firms` column by label without reading the label in a market
module is to record the flow per firm (one line in `markets/payments.pay`, a file of the
unassigned production-and-accounts role) and let the collector group it at step 7. The
existing columns `firms` and `roe` stay; `firms_<label>` columns are added. Open
question 4 (it is optional). **Decided: keep two sectors; nothing added.**

**D9. War episodes and cutting episodes.** `war_on` = at least one firm in cut mode
(`n_at_war > 0`, the brief's assumption). An episode is a maximal run of periods with
`war_on`; `war_start` is logged at its first period with value = `mean_price` of the
period before; `war_end` is logged with t = the last war period and value = the minimum
`mean_price` over the episode (so length = t_end − t_start + 1); `other_id` = episode
number. An episode still running at the last period gets a `war_end` with
cause = "censored". `cut_start` / `cut_end` per firm in the same way from `at_war`; a firm
that exits while cutting gets `cut_end` with cause "exit". All recorded in `choices.md`.

**D10. Entrants' first row.** The existing collector gives an entrant a row at its entry
period (mostly zeros, `born = t`); the brief says its first row is t + 1. Kept as it is
(no change in existing columns); `share_demand` is NaN and `share_end` is its starting
share on that row, so the §4.3 entry term picks it up at t + 1.

**D11. Rows of firms that exit.** Kept at period t with `exited` true, as today. Their
`cash`, `debt`, `net_worth` columns read 0 after `remove_firm` (already the case); the
`exit` event carries the net worth before exit (step 5 snapshot) and `default` the unpaid
debt.

## 2. Mapping table (every variable of §3 of the brief)

Action: **keep** = existing column, unchanged values; **add** = new column; **alias** =
existing column kept under its name, brief name recorded in the schema. "Source" says
where the value comes from under D2/D3.

### 2.1 `runs` (new table, one row per run) — all added, written by `run.py`

| brief name | existing | action | file touched | source |
|---|---|---|---|---|
| run_id | — | add | run.py | `{experiment}_{cell}_{population}_s{seed}` |
| seed | `SEED` | add | run.py | parameters |
| code_version | — | add | run.py | `git rev-parse HEAD` + `-dirty`; "unknown" if git fails |
| param_hash | — | add | run.py | sha256 of `json.dumps(sorted upper-case parameters)` |
| experiment, population, cell | — | add | run.py | CLI arguments, default "baseline" |
| anchor | `PRICING_ANCHOR` | add (as the parameter column) | run.py | parameters |
| okishio_price | — | add, constant "own" | run.py | fixed by `choices.md` (Okishio h at the firm's own price); no parameter exists |
| menu | `MENU` | add (JSON) | run.py | parameters |
| delta, rbar, rho, … | all of `parameters.py` | add, one column each, tuples/dicts as JSON | run.py | parameters |
| horizon | `PERIODS` | add (`periods`) | run.py | parameters |
| burn_in | — | add, 0 | run.py | no burn-in in the code; open question 10 |
| n_check_fail | — | add | run.py, collector | count of failing periods (phase 1) |
| wall_seconds | — | add | run.py | around `industry.run()` |
| python_version | — | add | run.py | `platform.python_version()` |

### 2.2 `industry` = `macro.csv` (existing table)

| brief name | existing column | action | file touched | notes |
|---|---|---|---|---|
| t | `time` | alias | — | |
| demand | `demand` | keep | — | |
| sales_total | `sales` | alias | — | |
| unmet_total | `unserved` | alias | — | existing `unmet` (= overflow before reallocation) also kept |
| capacity_total | `capacity` | alias | — | producing capacity, step 3 |
| n_firms | `n_firms` | keep; add `n_active` | collector | existing counts firms at the end of the period (plots, tests); `n_active` = firms at step 1 as the brief says |
| price_avg | `mean_price` | alias | — | sales-weighted |
| price_lead | `leader_price` | alias | — | = `min_price`; both kept |
| leader_id | — | add `leader_id`, `leader_ids`, `n_leaders` | collector | D4 |
| lowest_uc_id | — | add `lowest_uc_id`, `lowest_uc_ids`, `n_lowest_uc` | collector | D4 |
| (leader is lowest cost) | `leader_is_lowest_cost` | keep name, **values change on ties** | collector | D4 |
| war_on | — | add | collector | `n_at_war > 0` |
| n_cutting | `n_at_war` | alias | — | |
| gos_total | — | add | collector | Σ over plants of (price − ucs_v)·output_v, premium not deducted (brief) |
| invest_total | `investment` | alias | — | entrants included |
| r_new | `r_new` | keep | — | |
| p_entry | — | add | collector | `entry_probability(r_new, RBAR, ENTRY_SPEED)` |
| roe_balance | `roe_cash` | alias | — | `roe_loans`, `loan_losses` kept |
| price_cv_w, uc_cv_w | `price_cv`, `uc_cv` (unweighted) kept | add | collector | §4.4 weights |
| hhi_sales | `hhi` (end-of-period shares) kept | add | collector | on sales shares |
| incremental_rate_gross | `incremental_rate` (net) kept | add | collector | ΔGOS_t / invest_{t−1}; NaN when invest_{t−1} = 0 |
| sfc_resid | — | add `money_resid`, `debt_resid`, `nw_resid` | collector | phase 1; `nw_resid` = max abs over firms |
| tfm_resid | — | add `tfm_row_resid`, `tfm_col_resid` | collector | max abs over rows / columns |
| share_resid | — | add `share_resid_demand`, `share_resid_end`, `share_min` | collector | after steps 2 and 6 |
| cap_resid | — | add | collector | D6, industry level; by group in `groups` |
| sales_resid | — | add `sales_resid`, `util_max_viol` | collector | |
| floor_viol | — | add | collector | count of firms with price < p_floor − tol |
| (tolerance, failures) | — | add `check_tol`, `check_fail` | collector | the tolerance used that period; number of failing checks |
| by-group columns | `n_{type}`, `share_{type}`, `sales_{type}`, `capacity_{type}`, `profit_rate_{type}`, `capacity_{type}_{tech}`, `entries_{type}` | keep | — | duplicated in `groups`; kept for the plots and tests |

### 2.3 `groups` (new table, one row per period and label)

All added, built in `collect` from the record: `n_firms` (step 1), `capacity`, `sales`,
`share_demand`, `share_end`, `cap_retired`, `cap_replace`, `cap_ordered`, `cap_entry`,
`cap_exit`, `cap_cancelled`, `cap_resid`, `n_entry`, `n_exit`, `n_exit_{cause}`, `profit`,
`gos`, `invest_spend`, `cash`, `debt`, `net_worth`, `borrow`, `capacity_{tech}`,
`hurdle_mean`, `rule` (the rule the label maps to, so that swapped runs can be matched on
it). Note the brief's `share` is stored as `share_demand` to keep it apart from
`share_end` (the group's row has no legacy `share`).

### 2.4 `firms` = `firms.csv` (existing table)

| brief name | existing | action | file touched | source |
|---|---|---|---|---|
| t, firm_id | `time`, `firm_id` | alias / keep | — | |
| group | `type` kept | add `group` (= label) | collector | dropped by `history_without_labels` |
| rule | — | add | collector | `HURDLE_RULES[type]`; swap-invariant, so **kept** in the label-swap comparison |
| hurdle | `hurdle` | keep | — | set at step 4, used at 4 and 5 |
| born | `born` | keep | — | |
| price | `price` | keep | — | |
| p_normal | — | add | collector; **instr. `set_prices`, `Firm`** | `firm.p_normal = anchor` |
| p_floor | — | add | collector; **instr. `set_prices`, `Firm`** | `firm.p_floor = floor` |
| cutting | `at_war` | alias | — | |
| low_util | — | add | collector | trailing count of `util_history` below `U_WAR`, snapshot at step 1 |
| share | `share` | keep (value = share after step 6, as today) | — | existing `share` is read at step 7, after rescaling; hence the two columns below |
| share_demand | — | add | collector | step 2 snapshot (NaN for the entrant's row) |
| share_end | — | add | collector | after step 6; 0 for a firm that exited |
| sales, util, unmet | same | keep | — | |
| capacity | `capacity` | keep | — | producing capacity |
| (next capacity) | `capacity_next` | keep | — | |
| output | — | add | collector | Σ plant output (= sales) |
| ucs | — | add | collector | output-weighted over running plants |
| kappa | — | add | collector | capacity-weighted over producing plants |
| uc | `uc` | keep | — | capacity-weighted, as today |
| (margin) | `margin` | keep | — | |
| revenue, op_cost, depreciation, interest | attributes exist | add | collector | `firm.revenue`, `operating_cost`, `depreciation`, `interest` |
| profit, dividends | same | keep | — | |
| r_avg | `profit_rate` | alias | — | = profit / k_cost |
| r_newest | — | add | collector | D5 |
| cap_retired | — | add | collector | Σ capacity of this firm's plants in `industry.retired` (replacements included; `cap_retired_replace` not needed: it equals `cap_replace`) |
| write_off | `write_offs` | alias | — | |
| exp_sales | — | add | collector | `previous_sales` or `sales` per `INVESTMENT_SALES_LAG` |
| cap_desired | — | add | collector | `desired_capacity(exp_sales, EXPECTED_GROWTH)` |
| cap_ordered | — | add | collector | pending plants added at steps 4 and 5 (D6) |
| cap_replace | — | add | collector | pending plants added at step 4 |
| tech_new | `newest_technique` kept | add | collector | technique ordered this period ("" if none); `newest_technique` is the newest plant held, not the same thing |
| tech_other | — | add | collector | `choose_technique` under the other rule at `firm.price` |
| r_best | — | add | collector | `best_profit_rate(price, menu, DELTA)`, before the zero floor |
| invest_spend | `investment` | alias | — | |
| borrow | — | add `borrow`, `borrow_plants` | collector | ΔB over the period; the part borrowed at steps 4–5 (debt after 5 − debt after 3) |
| cash, debt | same | keep | — | |
| k_book | `book_value` | alias | — | plants in operation and on order |
| k_cost | — | add | collector | Σ κ_v q̄_v over producing plants (step 3) |
| net_worth | same | keep | — | |
| exited | — | add | collector | `exit_reason != ""` |
| exit_cause | `exit_reason` | alias | — | |
| r_avg_repl | — | — | — | later (brief) |
| (vintages) | `n_plants` kept | add `oldest_vintage`, `newest_vintage`, `ucs_spread` | collector | D5 |

### 2.5 `plants` = `plants.csv` (existing table; one row per plant in operation at the start of the period)

| brief name | existing | action | file touched | source |
|---|---|---|---|---|
| t, plant_id, firm_id | `time`, `plant_id`, `firm_id` | alias / keep | — | |
| (group) | `firm_type` | keep; add `group` | collector | both dropped in label-swap tests |
| tech | `technique` | alias | — | |
| vintage, capacity, ucs, kappa | same | keep | — | |
| uc | — | add | collector | ucs + δκ |
| output | `output` | keep | — | `overtime_output` kept |
| running | — | add | collector | output > 0 |
| r_plant | — | add | collector | (price − uc_v)/κ_v at normal output |
| (realised rate) | `profit_rate` | keep | — | profit / purchase cost |
| k_book | `book_value` | alias | — | as today: 0 after a write-off at step 4 or 6 |
| (write-off) | — | add `write_off` | collector | book value written off this period (step 3 snapshot − 0) |
| below_cost | `periods_below_cost` | alias | — | |
| retired | `retired` | keep | — | |
| retire_cause | — | add | collector; **instr. `remove_plant`** | "age", "obsolescence", "replacement" |
| exited_with_firm | — | add | collector | owner in `industry.exits` |
| age | `age` | keep | — | periods of operation completed, this one included |
| (other) | `initial`, `profit`, `lifetime_profit` | keep | — | |

### 2.6 `events` (new table)

Columns `t, step, event, firm_id, plant_id, group, rule, hurdle, tech, other_tech,
capacity, value, cause, other_id` (the brief's list plus `rule`, for the swap test).
Written by `collector.log_event`; sources per event as in the task statement:
`order` in `buy_plant` (cause kwarg), `retire` in `remove_plant` (cause kwarg), `exit` /
`default` / `cancel` in `remove_firm`, `entry` in `admit_entrant`, `war_*` and `cut_*` by
the collector. Events are sorted by (t, step, event, firm_id, plant_id) on output.

### 2.7 `flows` = `flows.csv`

`time, item, firms, roe` kept; no `firms_<label>` columns (open question 4: keep two sectors).

## 3. Instrumentation in files owned by others or shared

Each is one line or one attribute, no change in logic, listed for the owner's review.

| file (owner) | change | phase |
|---|---|---|
| `model/scheduler.run_period` (shared) | six calls `after_step(industry, k)`, one after each step | 2 |
| `model/entities.Firm` (shared) | two attributes `p_normal: float = 0.0`, `p_floor: float = 0.0` | 2 |
| `model/scheduler.set_prices` (Jake) | `firm.p_normal = anchor`; `firm.p_floor = floor` | 2 |
| `parameters.py` (shared) | `CHECKS_RAISE: bool = True` | 1 |
| `model/scheduler.remove_plant` (Vincent) | keyword `cause: str = ""` and one `log_event` call; `retire_plants` passes `reason`, `replace_plants` passes `"replacement"` | 3 |
| `markets/plant_market.buy_plant` (Ugo) | keyword `cause: str = "expansion"` and one `log_event`; `replace_plants` passes `"replacement"`, `create_entrant` passes `"entry"` | 3 |
| `markets/entry_exit.remove_firm` (unassigned) | `log_event` for exit, default and each cancelled pending plant | 3 |
| `equations/inherited_rule.py` (unassigned) | new `inherit(...) -> (type, parent, mutated)` with the two RNG calls in the same order; `inherited_type` becomes `inherit(...)[0]`; `admit_entrant` calls `inherit` and logs `entry` | 3 |
| `markets/payments.pay` (unassigned) | one line recording the flow per firm id for the group split | not done (Q4: keep two sectors) |
| `model/model.Industry.__init__` (shared) | `self.events = []`, `self.record = {}`, `self.group_history = []`, `self.n_check_fail = 0` | 1–4 |

Not instrumented, because exactly recomputable (D3): `p_entry`, `exp_sales`,
`cap_desired`, `tech_other`, `r_best`, the order cause by step, `low_util`.

## 4. Conflicts between the brief, the code and `choices.md`

1. **`n_firms`** (brief: firms active at step 1; code: firms at the end of the period).
   Resolved by keeping the column and adding `n_active` (D1).
2. **Capacity identity and `cancelled`** (D6): the task statement's definition of
   `ordered` double-counts cancelled orders. Proposed: `ordered` = all incumbents' orders.
3. **`k_cost` at step 4** (brief) versus `r_avg = profit / k_cost` (brief, same table):
   the two agree only if `k_cost` is the capital of the plants that produced (step 3), since
   `profit_rate` divides by `Firm.capital` before scrapping. Proposed: step 3.
4. **Entrant's first row** (brief: t + 1; code: t). Kept at t (D10) to leave the existing
   table unchanged; recorded in `choices.md`.
5. **`gos_total`**: the brief's "(price − ucs)·sales" ignores the overtime premium that
   `choices.md` adds to operating cost. Proposed: `gos` = revenue − operating cost
   (premium included), so that `gos − depreciation − interest = profit` holds exactly and
   the incremental rate is consistent with the accounts; the brief's formula differs only
   on overtime output. Open question 5.
6. **Flows by group** (brief §3.7) needs per-firm recording in `pay()` (D8).
7. **`okishio_price`**: the brief lists it as a run parameter; the code has no such
   parameter (h is always at the firm's own price). Stored as the constant "own".
8. **Seeds per mechanism** (brief §5): would change trajectories; kept as one
   `random.Random(SEED)`, a row proposing separate streams is added to `choices.md`
   (phase 5).
9. **`leader_is_lowest_cost`** changes values on ties (D4): the only pre-existing column
   whose values may move; reported period by period in the reference comparison.

## 5. Phases and files

| phase | files added / changed | commit |
|---|---|---|
| 0 | `docs/design/collector-brief.md`, `docs/design/collector-plan.md` | "Collector: brief and plan" |
| 1 | `model/collector.py` (`check_stock_flow` → residuals then raise; residual columns), `parameters.CHECKS_RAISE`, `model/model.py` (`n_check_fail`), `tests/test_collector.py` | checks |
| 2 | `model/collector.after_step`, `run_period` hook, `Firm.p_normal/p_floor`, `set_prices`, firms/plants/macro columns, `tests/helpers.history_without_labels` (+ `group`), `tests/test_collector.py` (three-plant firm, weights, `r_newest`, `p_floor`, ties) | record at source |
| 3 | `collector.log_event`, `industry.events`, `buy_plant`, `remove_plant`, `remove_firm`, `inherited_rule.inherit`, `admit_entrant`, episodes; `tests/test_events.py` (consistency, RNG proof against the reference) | events |
| 4 | groups table, `analysis/__init__.py`, `analysis/indicators.py` (§4.2, §4.3), `tests/test_indicators.py`, `payments.pay` per-firm record (Q4) | groups and decompositions |
| 5 | `run.py` (`--out`, `--format`, `--experiment`, `--population`, `--cell`, `--seed`, runs table, `run_id` first column), `model/schema.py`, `analysis/schema_doc.py` → `docs/design/collector.md`, `tests/test_schema.py`, `choices.md` seeds row, timing | metadata and schema |
| 6 | `debug/_common.py`, `checks.py`, `firm_panel.py`, `plant_gantt.py`, `merit_order.py`, `events_timeline.py`, `capacity_bridge.py`, `flow_matrix.py`, `compare_runs.py`, `report.py`; `tests/test_debug_plots.py` | debugging plots |
| 7 | `docs/design/collector.md`, `choices.md` rows, `docs/sections/accounts.tex` paragraph, `debug/README.md`, `README.md` layout block | documentation |

After every phase: full test suite, `run.py`, column-by-column exact comparison of
`macro`, `firms`, `plants`, `flows` with the reference (a scratch script until
`compare_runs.py` exists in phase 6).

## 6. Open questions

1. **Parameter values for the reference run.** The tree is clean, so the reference would
   use the committed values: `DEMAND_TO_CAPACITY = 340/383`, `PRICING_ANCHOR =
   "target_return"`, `MARKUP = 0.282`, seed 42, 200 periods. Confirm, or give other values
   (they would then have to be committed first, since the reference is built from a
   worktree of a commit). [Ugo's answer] Okay for the commited values as reference
2. **Branch.** The task says `feature/collector`; the work sits on
   `feat-collector-and-metrics`, where the brief is staged. Keep this branch, or create
   `feature/collector` from it? [Ugo's answer] use feat-collector-and-metrics branch
3. **Capacity identity** (D6): accept `ordered` = all incumbents' orders and `cancelled` =
   the exiters' subset? [Ugo's answer] ok
4. **Flows by group**: add the one-line per-firm record in `markets/payments.pay` so the
   flow matrix has a column per label, or keep two sectors (`firms`, `roe`)? [Ugo's answer] keep two sectors
5. **`gos`**: revenue − operating cost (premium included, consistent with `profit`), or the
   brief's (price − ucs)·output literally? [Ugo's answer] measure consistent with profit
6. **Names**: confirm D1 (keep every existing name, alias the brief's † names in the
   schema), or switch to the brief's names and let me update `plot_outputs.py` and the
   tests. [Ugo's answer]  switch to brief's names
7. **`--seed`** on `run.py`: add it alongside `--experiment/--population/--cell` (needed
   for the 50-seed runs; the default leaves the reference unchanged)? [Ugo's answer] all right
8. **`.idea/`**: add it to `.gitignore` in the phase 0 commit, or leave it untracked? [Ugo's answer] add to gitignore
9. **Run-time budget**: the 50 % limit of phase 5 read against the 0.044 s model loop
   (strict) or the 0.25 s of `run.py` (import and CSV writes included)? [Ugo's answer] consider worst case scenario
10. **`burn_in`**: the code has no burn-in; store 0 in `runs` and leave the rule-neutral
    menu during burn-in (brief §5) for later? [Ugo's answer] yes
11. **Parquet**: `pyarrow` is not installed; `--format parquet` will fail with a clear
    message unless it is. Install it in `.venv` only (not in `requirements.txt`)? [Ugo's answer] install in requirements.txt
