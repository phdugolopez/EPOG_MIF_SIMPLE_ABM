# Version 1: choices the brief leaves open

The brief (`mechanism-briefs.md`) gives each mechanism a starting rule. This file records
every other choice made to get one runnable model, so that each owner knows what to revisit.
**Fixed by Ugo** = decided at the planning stage; **default** = the simplest neutral choice,
open for the owner to change. Parameter names are those of `parameters.py`.

Each choice must respect the neutrality rule: only the technique choice (investment,
replacement, entry) may use the hurdle h. In the code, `firm.type` is used only to look up
the hurdle rule (`HURDLE_RULES`, `equations/hurdle.py`) and to pass it on to entrants, and
the label-swap tests check it.

## Shared

| Choice | Status | Alternatives | Owner |
|---|---|---|---|
| Six firms: each of C, D1, D2 given to one Shaikh and one Okishio firm, identical within each pair | Fixed by Ugo | Three firms (test industry), random draws | group |
| One plant of age 0 per initial firm. All initial plants retire together at t = 9 and the industry rebuilds at once, which leaves echo cycles every 10 periods | Fixed by Ugo | Each firm's capacity spread over T plants aged 0–9: smooth, but retirement absorbs the initial excess capacity in two periods and no early price war happens | Vincent, Ugo |
| Demand D = (340/383) × 766 = 680, constant (`DEMAND_GROWTH = 0`) | Fixed by Ugo | Growth path, shocks | Pierre-Loup |
| delta = 0.10, rbar = 0.16, u_max = 1.2, seed 42, 200 periods | Fixed by Ugo | | group |
| Initial price 100 for every firm (the price of Shaikh's table), initial cash 0, debt 0, shares in proportion to capacity | Default | Start at each firm's anchor; start at the regulating capital's price of production | Jake |
| Notation clashes renamed: plant life `PLANT_LIFE` (T = 10) vs war trigger `WAR_PERIODS` (T = 2); price band `PRICE_BAND` vs K+S payback b; entry window `ENTRY_WINDOW` (k) | Default | | group |
| Parameters are upper case in `parameters.py` and passed to equations under the brief's lower-case names (`DELTA` → `delta`) | Default | | group |
| Ties (equal costs, equal prices) are always shared pro rata, never broken by firm order: the paired firms start identical, so ordering would favour one type | Default | | group |

## Pricing (Jake)

| Choice | Status | Alternatives |
|---|---|---|
| Anchor = target return uc_i + rbar κ_i, with uc_i and κ_i the capacity-weighted averages of the firm's plants | Fixed by Ugo | `PRICING_ANCHOR = "markup"`: (1 + μ) uc_i, μ = 0.282 |
| Leader = lowest price posted in the previous period (entrants' entry prices excluded) | Fixed by Ugo | |
| Floor = ucs of the most expensive plant needed to produce last period's sales in merit order; the cheapest plant's ucs when last sales were zero | Fixed by Ugo (rule); default (zero sales) | Floor including the overtime premium |
| u_war = 0.95, `WAR_PERIODS` = 2, c = 0.02, b = 0.025, λ = 0.25 | Default (brief's ranges where given) | |
| No war before a firm has `WAR_PERIODS` periods of history (entrants start at peace) | Default | |

## Demand (Pierre-Loup)

| Choice | Status | Alternatives |
|---|---|---|
| Linear quasi-replicator on E = 1/p, χ = 1; negative shares set to 0 and the rest renormalised | Fixed by Ugo | `DEMAND_FORM = "logit"`: f_i ∝ f_i,t−1 p_i^(−η), η = 1 (same response as χ = 1 for small gaps) |
| The share f is the replicator's state; realised sales can differ from f·D after capping and overflow, and do not feed back into f | Default | Reset f to x/D each period |
| Sales capped at the output a firm offers at its price: the plant segments whose cost (ucs, or (1 + premium) ucs above normal output) is at most p | Default | Cap at u_max·q̄ regardless of price |
| Overflow goes to the cheapest firm(s) with spare capacity, tied firms sharing in proportion to spare capacity; demand nobody can serve is recorded (`unserved`) | Fixed by Ugo (rule); default (ties) | |
| Unmet demand l_i recorded per firm, not yet used in competitiveness | Default | Add l_i to E |

## Production and accounts (unassigned)

| Choice | Status | Alternatives |
|---|---|---|
| Produce to order; plants run in merit order, lowest operating cost first, all normal segments before any overtime segment of the same cost | Fixed by Ugo | Production to expected demand with inventories |
| Overtime premium of 10 % on ucs for output above normal capacity (`OVERTIME_PREMIUM`); it enters operating cost and profit (the brief's profit equation omits it) | Default | 0 (brief's equation literally) |
| Profit Π = p x − operating cost − Σ δ κ_v q̄_v − ρ B_{t−1}; profit rate on capital at purchase cost of plants in operation | Fixed by Ugo | |
| ρ = 0.05 (< rbar), payout d = 0.5 for both types | Fixed by Ugo (d); default (ρ) | |
| Repayment: 10 % of debt per period from cash (`REPAYMENT_RATE`) | Default (the brief has no rule) | Repay from all surplus cash |
| Overdraft: a negative cash balance is covered by a loan outside the debt cap; the cap binds only borrowing for plants | Default (resolves "debt never exceeds its cap" vs losses that must be financed) | Bankruptcy when cash runs out |
| Plants bought now and arriving next period count in book value at purchase cost (construction in progress) | Default | |
| One rest-of-economy account: buyers, workers, suppliers, lender and owners. Every money flow goes through `markets/payments.pay`, which builds the transaction-flow matrix | Fixed by Ugo | Separate households, banks |
| Stock-flow check every period (`model/collector.check_stock_flow`, raised by the scheduler): money conserved, debt = loans, ΔNW = Π − Div − write-offs (+ equity at entry), rows and columns of the flow matrix | Fixed by Ugo | |
| Profit rates at replacement cost equal those at historical cost while the menu is fixed, so only one is collected | Default | Add when menus change |

## Scrapping (Vincent)

| Choice | Status | Alternatives |
|---|---|---|
| Retire at age T = 1/δ = 10, or after N = 4 consecutive periods with the owner's price below the plant's ucs | Fixed by Ugo | Idle for N periods |
| Replacement on (`REPLACEMENT = True`): ucs_v > ucs_n + (δ + h) κ_n, n = the firm's technique choice, same h as investment; carried out only if the firm can pay (cash, then debt up to the cap) | Fixed by Ugo (rule); default (finance) | Off |
| Scrap value 0; remaining book value written off by the firm | Fixed by Ugo | Second-hand price |
| Depreciation accounting only (straight line), no physical decay | Fixed by Ugo | Capacity or cost rising with age |

## Investment (Ugo)

| Choice | Status | Alternatives |
|---|---|---|
| Desired capacity = (1 + g) x_{t−1}, g = 0; I = max{0, desired − capacity after scrapping − capacity on order} | Fixed by Ugo | `INVESTMENT_SALES_LAG = 0`: this period's sales |
| Okishio h = best profit rate on the menu at the firm's own current price, **floored at 0** (`HURDLE_FLOOR_AT_ZERO`), in investment, replacement and entry alike. Without the floor, h < 0 in a deep war makes replacement easier for Okishio firms than for Shaikh firms | Fixed by Ugo | Unfloored (the profit-rate rule exactly) |
| τ = 0 (no capital advanced) | Fixed by Ugo | τ > 0: above ≈ 0.12 D2 stops being a conflict case |
| Menu C, D1, D2; continuous plant size (one plant of any size per investment) | Fixed by Ugo (menu); default (size) | Lumpy plants of 120–133 |
| Finance: cash first, then debt up to `DEBT_CAP` = 2 × this period's sales revenue; investment scaled down when it cannot be financed | Fixed by Ugo (rule); default (cap value) | Internal finance only (treatment) |
| Replacement (step 4) is financed before expansion (step 5) | Default (order of events) | K+S: expansion first |
| Ties between techniques go to the first one listed in `MENU` | Default | |

## Entry and exit (unassigned)

| Choice | Status | Alternatives |
|---|---|---|
| r_new = realised profit rate this period (before interest, net of depreciation, at the owner's price and actual output) of plants that came into operation in the last k = 5 periods, capacity-weighted; no such plant ⇒ no entry. (The brief says "realised" in question 1 and "at the current price" in the starting rule) | Default | Rate at normal output and the current price |
| Pr(entry) = min{1, θ (r_new − rbar)/rbar}, θ = 5, at most one entrant per period | Fixed by Ugo | |
| Entrant's type: drawn from incumbents by market share; flips to the other type with m = 0.02 | Fixed by Ugo | Fixed share of invaders |
| Entrant price = 0.99 × leader (`ENTRANT_UNDERCUT`), h at that price, technique by its own h, capacity φ = 0.5 × average incumbent capacity, share = its capacity over total next-period capacity (incumbents rescaled) | Fixed by Ugo (φ, rule); default (1 %) | |
| Entrant's owners bring equity equal to the plant's cost, from the rest of the economy | Default | Random fraction of incumbents' cash |
| Exit if NW < 0, share < f_min = 0.01, or non-renewal; floor of two firms (the firms with the highest net worth stay) | Fixed by Ugo (channels); default (f_min) | |
| **Non-renewal at firm level**: a firm exits when its last plant retires, its lifetime profit rate (before interest) was below rbar, and it has no plant on order; such a firm does not invest that period. A firm left with no plant at all also exits. Plants of the initial endowment are exempt, since their record starts at t = 0 | Fixed by Ugo (firm level, last plant); default (exemption) | Plant level (Harrod): a retiring plant below rbar is not rebuilt |
| A leaving firm repays what its cash allows, the rest of its debt is a loss of the rest of the economy, its remaining cash returns to its owners, its plants are written off; its share is shared out in proportion to the other shares | Default | |

## Collector (unassigned; signed off by Ugo)

The collector observes and never decides (`model/collector.py`, `docs/design/collector-brief.md`,
plan in `collector-plan.md`). Choices made while implementing phases 1–6:

| Choice | Status | Alternatives |
|---|---|---|
| Column names follow the brief (`t`, `price_avg`, `sales_total`, `cutting`, `r_avg`, `k_book`, ...); `n_firms` keeps its end-of-period meaning with `n_active` (firms at step 1) beside it; `share` stays the share after step 6, with `share_demand` (step 2) and `share_end` beside it | Fixed by Ugo | Keep the template's names, alias the brief's in the schema |
| Ties among leaders and lowest-cost firms are kept as sets (`leader_ids`, `lowest_uc_ids`, with counts); equality by `math.isclose`; `leader_id` / `lowest_uc_id` = −1 when tied; `leader_is_lowest_cost` = the two sets intersect | Default | Break ties at random (brief) |
| Firm aggregates over plants: `ucs` output-weighted over running plants; `kappa`, `uc` capacity-weighted over plants in operation; `k_cost` = Σ κ_v q̄_v over the plants that produced (step 3, so that `r_avg = profit / k_cost`); `k_book` includes plants on order | Default | `k_cost` after scrapping (brief, step 4) |
| `r_newest` on the plants in operation with the highest vintage, capacity-weighted, at normal output; None for a firm with no plant in operation | Default | Newest plant held, orders included |
| `gos` = revenue − operating cost (overtime premium included), so that `gos − depreciation − interest = profit` | Fixed by Ugo | (price − ucs)·output (brief, premium ignored) |
| Capacity identity, plant level: K_{t+1} = K_t − retired − exit + ordered + entry − cancelled, with `ordered` = every incumbent's orders at steps 4 and 5 and `cancelled` = the leavers' part of it | Fixed by Ugo | `ordered` restricted to survivors (double-counts `cancelled`) |
| An industry price war is a maximal run of periods with at least one firm cutting (`war_on`); `war_start` at its first period, `war_end` at its last (value = lowest `price_avg`), censored at the horizon; cutting episodes per firm likewise from `cutting` | Default | Sales-weighted share of cutting firms above a threshold |
| Check tolerances: money 1e-9·max(1, scale), quantities 1e-9·max(1, demand), shares 1e-12 (brief §3.7); floor 1e-9·max(1, floor). `CHECKS_RAISE = True` stops at the first failure; False counts failing periods in `n_check_fail` | Fixed by Ugo | |
| `borrow` = debt after step 5 − debt at the start of the period (overdraft, repayment and plant finance), before any exit settlement; `borrow_plants` = the part taken at steps 4–5 | Default | Net change over the whole period (−debt for a defaulting leaver) |
| An entrant has a firm row at its entry period (`born = t`, `share_demand` None); `exp_sales` and `cap_desired` are None for entrants and for firms that `invest` skips on non-renewal | Default | First row at t + 1 (brief) |
| Events are logged at source through `Industry.log_event` / `log_order` / `log_exit`, so that no market module imports the collector; the default is logged by `log_exit` from the same arithmetic as `credit_market.default` | Default | Derive orders from pending-plant diffs in `after_step` |
| `groups`: one row per period and label (keys of `HURDLE_RULES`, sorted), empty groups included; members are the firms that produced this period plus its entrants; `share_end`, `cash`, `debt`, `net_worth` are after step 6 over the firms still in the industry; `hurdle_mean` weighted by producing capacity; `capacity_next` = K_{g,t+1} | Default | Rebuild from `firms` after the run |
| The capacity identity is also checked group by group (`cap_resid_group` = largest absolute group residual, in the macro row) | Default | Industry level only |
| Section 4.2 decomposition: five terms (ordered, −retired, entry, −exit, −cancelled), K_{t+1} = `capacity_next`; section 4.3: NaN in the first period. A table holding several runs is decomposed run by run (`run_id`) | Default | Four terms with cancelled netted from ordered |
| `flows` keeps two sectors (`firms`, `roe`); flows by group are read from `groups` and `firms` rather than from the flow matrix | Fixed by Ugo | `firms_<label>` columns, from one line in `markets/payments.pay` |
| `runs`: `run_id` = `{experiment}_{cell}_{population}_s{seed}` (defaults "baseline"); every parameter in its own column under its lower-case name, tuples and dicts as JSON, except `SEED`, `PRICING_ANCHOR`, `MENU` stored as the brief's `seed`, `anchor`, `menu`; `param_hash` = sha256 of the sorted parameters as JSON; `code_version` = HEAD with `-dirty` if tracked files changed; `okishio_price` = "own" (no parameter: h is evaluated at the firm's own price); `burn_in` = 0; `horizon` = periods actually run | Default | |
| One schema for every table (`model/schema.py`); `docs/design/collector.md` is generated from it (`python -m analysis.schema_doc`). Tests fail when the schema and the tables `run.py` writes differ, or when the schema part of the document is stale; the parameter table at its end (built from the comments of `parameters.py`) is not tested, so a comment edit by a mechanism's owner never breaks the suite | Fixed by Ugo | Hand-written schema; regenerate in CI |
| `run.py --format parquet` needs `pyarrow`, added to `requirements.txt`; writing a folder removes a stale copy of each table in the other format, so `plot_outputs.py` and `docs/main.tex` (CSV readers) never read an older run by mistake | Fixed by Ugo | CSV only |
| One random stream, `random.Random(SEED)`, shared by every mechanism (today: exit tie-breaks, entry draws, inherited rule). Separate streams per mechanism spawned from the master seed (brief §5) would keep one mechanism's draws fixed when another changes, but change every trajectory: proposed for later, with a new reference run | Default (proposal for later) | `numpy.random.SeedSequence(SEED).spawn(k)`, one stream per mechanism |
| Debugging plots (`debug/`, one script per question) read only the tables of a run folder, never the model, and write to `RUN_DIR/debug/`; colours and rcParams are defined once in `debug/_common.py` and imported by `plot_outputs.py` | Default | Plots drawn from model objects in the tests |
| Price-war periods shaded on the debugging plots are the collector's industry episodes (maximal runs of `war_on`), recomputed from `macro` | Default | Read `war_start` / `war_end` from `events` |
| In the plots, ties are never resolved by firm order: firm lanes are sorted by entry period then id, merit-order segments of equal cost by plant id (drawing only), and `capacity_bridge` decomposes the group whose rule is `unit_cost`, whatever its label | Default | |
| `debug.report` draws the merit order at three periods: the first period of the first price war, the first rebuild (first period with retirements at step 4 and orders) and the last period | Default | First period after the first war |
| `debug.compare_runs` matches rows on keys ((t); (t, group); (t, firm_id); (t, plant_id); (t, step, event, firm_id, plant_id, rank); (t, item)), compares text as well as numbers (NaN = NaN; text, NaN against a number and missing rows count as infinite), tolerance 1e-12 absolute; `--swap-labels` swaps the two labels in values and column names but not `rule`; tables with the names used before phase 2 are renamed first | Default | Numeric columns only; relative tolerance |

## What the baseline shows (seed 42), for the record

- A price war starts at t = 2 (utilisation 0.89), prices fall 2 % a period to about 83, and
  end once the initial plants retire at t = 9 and capacity is rebuilt to demand.
- The rebuild at t = 9 happens at prices near 85, where D2 overtakes D1 (below 85.1): all
  Shaikh firms and two of the three Okishio firms (h ≈ 6 %) build D2, and C disappears.
- At t = 19 the three firms whose capital is a single cohort built at t = 9 exit by
  non-renewal (the cohort earned below rbar during the war). Entrants refill the industry
  (4 entries and 4 exits over the run, all exits by non-renewal).
- Afterwards Okishio firms build D1, Shaikh firms D2, and under target-return pricing D1
  firms post the lowest price (98.77 against 100.26): Shaikh firms lose share steadily
  (from 0.5 to about 0.16 by t = 200). This is the anchor trap of the pricing brief at work,
  not a result about the two rules in general.
