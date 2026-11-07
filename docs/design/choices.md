# Choices the brief leaves open (version 2 defaults; version 1 values kept for the record)

> **Defaults frozen on 7 November 2026 pending the sensitivity analysis** (section
> "Sensitivity analysis (planned)" below, plan in `review-v2.md`). Pricing and technical
> change are treatment arms until then.

The brief (`mechanism-briefs.md`) gives each mechanism a starting rule. This file records
every other choice made to get one runnable model, so that each owner knows what to revisit.
**Fixed by Ugo** = decided at the planning stage; **default** = the simplest neutral choice,
open for the owner to change. Parameter names are those of `parameters.py`.

Version 2 (6 November 2026) changes the defaults of pricing, accounts, scrapping,
investment and entry; each version 1 rule stays behind a switch. **Default (version 2)** in
the tables marks the current default. Records of runs say which version, which pricing rule
and which rbar they used; a number without its configuration is not a result.

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
| delta = 0.10, rbar = 0.05, u_max = 1.2, seed 42, 200 periods | rbar: default (version 2); the rest fixed by Ugo | rbar = 0.16 (version 1; the records below use it unless they say otherwise) | group |
| Initial price 100 for every firm (the price of Shaikh's table), initial cash 0, debt 0, shares in proportion to capacity | Default | Start at each firm's anchor; start at the regulating capital's price of production | Jake |
| Notation clashes renamed: plant life `PLANT_LIFE` (T = 10) vs war trigger `WAR_PERIODS` (T = 2); price band `PRICE_BAND` vs K+S payback b; entry window `ENTRY_WINDOW` (k) | Default | | group |
| Parameters are upper case in `parameters.py` and passed to equations under the brief's lower-case names (`DELTA` → `delta`) | Default | | group |
| Ties (equal costs, equal prices) are always shared pro rata, never broken by firm order: the paired firms start identical, so ordering would favour one type | Default | | group |
| Plants of any size (`PLANT_SIZE = None`): investment fills the capacity gap exactly | Version 1, now a switch | **Default (version 2), S = 20:** `PLANT_SIZE` = S: every plant has capacity S. Initial plants are split into the nearest number of plants of S (C: 120 → 6 × 20); an entrant's capacity is rounded to whole plants; under the accelerator a firm buys enough plants to cover the gap, as many as it can finance (`equations/plant_number.py`) | Vincent, Ugo |

## Pricing (Jake)

Version 2 rule (`PRICING_RULE = "real_competition"`, `equations/real_competition_price.py`).
No anchor and no war trigger: price cuts come only from cost differences.

| Choice | Status | Alternatives |
|---|---|---|
| Order: (1) excess demand last period → move up to the next higher rival price, the highest-priced firm raises by `SHORTAGE_RESPONSE` × excess share; (2) spare capacity and a cost edge → post (1 − c) R; (3) otherwise follow the lowest price, never below the floor | Default (Jake) | `PRICING_RULE = "anchor"`: version 1 below |
| R = lowest rival price last period, the firm itself excluded, so a lone leader does not undercut itself | Default | Lowest price including the firm's own |
| Cost edge: the firm's best-plant unit cost uc = ucs + δκ is below the cut price (1 − c) R and below the uc of at least one rival posting R. An identical twin at R does not block the cut; a rival that is not at R does not count | Default | Edge over every rival at R: identical pairs then never cut |
| A cut never raises the firm's own price: min{p_{t−1}, (1 − c) R} | Default | |
| Spare capacity: utilisation last period below `U_FULL` = 1 (tolerance 1e-9) | Default | A lower threshold, e.g. 0.95 |
| Excess demand: last period's demand above normal capacity (`EXCESS_DEMAND = "normal_capacity"`), Shaikh's signal that capacity is short | Default | `"unserved"`: demand above all output with overtime (u_max = 1.2); prices then almost never rise (see below) |
| Floor when following: the firm's own best-plant unit cost (`PRICE_FLOOR = "unit_cost"`) | Default (Jake) | `"operating_cost"`: the version 1 floor (ucs, Shaikh 2016, p. 316). Followers then match the leader all the way and a war ends on one price; same baseline |
| c = `PRICE_CUT` = 0.02, `SHORTAGE_RESPONSE` = 0.5 | Default | |
| **The other arm of the price-war treatment:** `PRICING_RULE = "leader_follow"`, the group notebook's rule (`equations/leader_follow_price.py`). L = lowest price last period. (1) A lone firm raises its price by `LEADER_RISE` up to `MONOPOLY_CAP` = 3 × floor; (2) after excess demand (same signal as the default, `EXCESS_DEMAND`), every firm posts (1 + `LEADER_RISE`) L; (3) otherwise every firm posts max{floor, (1 − c) L}, so prices fall each period until floors bind: a price war whenever capacity is not short. Floor = (1 + `FLOOR_MARKUP`) × capacity-weighted average uc. Differences from the notebook, for neutrality: ε, the floor markup m and the shortage rise z are common parameters (c = 0.02, m = 0.20, z = 0.03, the notebook's means) instead of random draws per firm, and shares come from the replicator, not a price queue. Seeds 1–10, current defaults otherwise: final Shaikh share 0.55 (real competition: 0.81), leader is the lowest-cost firm in 195 of 200 periods (58), mean price over t ≥ 50 69.0 (75.7), profit rate S/O 7.0 / 6.4 % (8.9 / 6.4 %), 6.4 firms at t = 199 (18.1) | Committed (cc1dd0c), a switch; fixed or treatment after the sensitivity analysis | Random ε, m, z per firm, as in the notebook |
| Leader-follow floor: (1 + 0.20) × the capacity-weighted average uc of all the firm's plants, idle ones included. No plant then sells below its unit cost unless it is more than 20 % dearer than the firm's average, so obsolescence scrapping almost never fires and the Okishio hurdle never reaches zero: price wars never close the conflict zone | Default of the rule, now a switch: `LEADER_FOLLOW_FLOOR = "markup"` (step 1 of the plan, done 7 November) | `"unit_cost"` (the best plant's uc, the default rule's floor), `"operating_cost"` (ucs of the marginal plant, version 1, Shaikh 2016, p. 316); all three in the sensitivity analysis |
| Leader-follow shortage branch: after excess demand every firm posts (1 + z) L, so a firm priced above that lowers its price in a shortage and the price distribution collapses to one level 3 % above the leader | Default of the rule, now a switch: `SHORTAGE_RULE = "leader"` (step 1, done 7 November) | `"no_cut"`: max{p_{t−1}, (1 + z) L}, a shortage never lowers a price |

Version 1 rule (`PRICING_RULE = "anchor"`):

| Choice | Status | Alternatives |
|---|---|---|
| Anchor = target return uc_i + rbar κ_i, with uc_i and κ_i the capacity-weighted averages of the firm's plants | Fixed by Ugo | `PRICING_ANCHOR = "markup"`: (1 + μ) uc_i, μ = 0.282; `PRICING_ANCHOR = "leader"`: one anchor for every firm, the target-return price of last period's price leader (tied leaders averaged) |
| Leader = lowest price posted in the previous period (entrants' entry prices excluded) | Fixed by Ugo | |
| Floor = ucs of the most expensive plant needed to produce last period's sales in merit order; the cheapest plant's ucs when last sales were zero | Fixed by Ugo (rule); default (zero sales) | Floor including the overtime premium |
| u_war = 0.95, `WAR_PERIODS` = 2, c = 0.02, b = 0.025, λ = 0.25 | Default (brief's ranges where given) | |
| No war before a firm has `WAR_PERIODS` periods of history (entrants start at peace) | Default | |
| War rule: every firm at war cuts its own price by c a period | Default | (`PRICE_WAR = "cost_gated"` removed in version 2: the real-competition rule replaces it; its file `equations/war_price.py` was deleted on 7 November) |

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
| Stock-flow check: tolerance 1e-9 relative to the period's flows and the cash and debt stocks (stocks added in version 2: over long runs rounding grows with them) | Default | |
| ρ = 0.05 (< rbar), payout d = 0.5 for both types | Fixed by Ugo (d); default (ρ) | |
| Repayment: 10 % of debt per period from cash (`REPAYMENT_RATE`) | Default (the brief has no rule) | Repay from all surplus cash |
| Overdraft: a negative cash balance is covered by a loan outside the debt cap; the cap binds only borrowing for plants | Version 1 (`CASH_SHORTFALL = "overdraft"`), resolves "debt never exceeds its cap" vs losses that must be financed | **Default (version 2):** `CASH_SHORTFALL = "bankruptcy"`: no overdraft. A negative balance stays as bills the firm could not pay; the firm goes bankrupt at the end of the period (exit row below) and the rest of the economy bears the unpaid bills (`unpaid_bills` in the outputs). A firm kept by the floor of two firms carries them into the next period. Cash can run out only when interest exceeds the operating margin: a firm sells only what plants whose ucs the price covers can make, and dividends come out of positive profit. With no borrowing (version 2) that needs initial debt, so in the version 2 baseline the rule never fires (0 bankruptcies over seeds 1–20, as with the overdraft) |
| Plants bought now and arriving next period count in book value at purchase cost (construction in progress) | Default | |
| One rest-of-economy account: buyers, workers, suppliers, lender and owners. Every money flow goes through `markets/payments.pay`, which builds the transaction-flow matrix | Fixed by Ugo | Separate households, banks |
| Stock-flow check every period (`model/collector.check_stock_flow`, raised by the scheduler): money conserved, debt = loans, ΔNW = Π − Div − write-offs (+ equity at entry), rows and columns of the flow matrix | Fixed by Ugo | |
| Profit rates at replacement cost equal those at historical cost while the menu is fixed, so only one is collected | Default | Add when menus change |

## Scrapping (Vincent)

| Choice | Status | Alternatives |
|---|---|---|
| Retire at age T = 1/δ = 10, or after N = 4 consecutive periods with the owner's price below the plant's ucs | Version 1, now a switch | **Default (version 2):** no maximum age, N = 2 periods below unit cost, idle plants scrapped (rows below); Idle for N periods |
| Replacement on (`REPLACEMENT = True`): ucs_v > ucs_n + (δ + h) κ_n, n = the firm's technique choice, same h as investment; carried out only if the firm can pay (cash, then debt up to the cap; cash only with `BORROWING = False`, the version 2 default). Its cost comes out of retained earnings, like investment | Fixed by Ugo (rule); default (finance) | Off |
| Scrap value 0; remaining book value written off by the firm | Fixed by Ugo | Second-hand price |
| Depreciation accounting only (straight line), no physical decay | Fixed by Ugo, now a switch | Capacity or cost rising with age. **Proposed:** `DEPRECIATION = "use"` (default stays `"time"`): depreciation δ κ_v x_v, overtime included, until book value is zero (`equations/depreciation.py`, `depreciation_by_use`). The purchase cost is spread over a lifetime output of q̄_v / δ, so at normal output the charge equals the straight-line one, the capital charge per unit of output is δκ in both rules, and uc = ucs + δκ, the hurdle, technique choice, replacement and scrap cost are unchanged. Idle plants do not depreciate, so low utilisation costs less in the accounts and a plant scrapped while idle leaves a larger write-off. Plants still run in merit order on ucs: depreciation is not paid in cash |
| With `DEPRECIATION = "use"`, `PLANT_LIFE` counts periods of normal output (`Plant.wear` = Σ x_v / q̄_v), not age: a plant leaves once it has produced `PLANT_LIFE` × q̄_v, i.e. when it is fully depreciated if `PLANT_LIFE` = 1/δ. With `PLANT_LIFE = None` (version 2) only the accounts change | Default (proposed) | Age limit kept alongside wear |
| Maximum age T = 10 | Version 1, now a switch | **Default (version 2):** `PLANT_LIFE = None`: no maximum age; a fully depreciated plant then costs only ucs in the accounts |
| Obsolescence compares the price with ucs | Version 1, now a switch | **Default (version 2), with N = 2:** `SCRAP_COST = "unit_cost"`: with ucs + δκ, so a plant leaves once the price has not covered its unit cost for N periods (`equations/retirement.py`, `scrap_cost`) |
| No scrapping of idle plants | Version 1, now a switch | **Default (version 2):** `IDLE_SCRAPPING = True`: a plant the firm did not need for `IDLE_PERIODS` = 2 periods leaves. Not needed = the firm could have left it off and still produced its sales at normal capacity, highest ucs first, then oldest (`equations/idle_plants.py`). Identical plants share output pro rata, so idleness is counted in whole plants, not plant by plant |

## Investment (Ugo)

| Choice | Status | Alternatives |
|---|---|---|
| Desired capacity = (1 + g) x_{t−1}, g = 0; I = max{0, desired − capacity after scrapping − capacity on order} | Version 1 (`INVESTMENT_RULE = "accelerator"`) | `INVESTMENT_SALES_LAG = 0`: this period's sales |
| Okishio h = best profit rate on the menu at the firm's own current price, **floored at 0** (`HURDLE_FLOOR_AT_ZERO`), in investment, replacement and entry alike. Without the floor, h < 0 in a deep war makes replacement easier for Okishio firms than for Shaikh firms | Fixed by Ugo | Unfloored (the profit-rate rule exactly) |
| τ = 0 (no capital advanced) | Fixed by Ugo | τ > 0: above ≈ 0.12 D2 stops being a conflict case |
| Menu C, D1, D2 (fixed by Ugo); in version 1 continuous plant size, one plant of any size per investment | Menu fixed by Ugo; size: version 1, now a switch | **Default (version 2):** plants of `PLANT_SIZE` = 20 (row "Plants of any size" above); lumpy plants of 120–133 |
| Finance: cash first, then debt up to `DEBT_CAP` = 2 × this period's sales revenue; investment scaled down when it cannot be financed | Version 1 (`BORROWING = True`) | **Default (version 2):** `BORROWING = False`: no borrowing for plants anywhere, investment and replacement alike, under either investment rule: plants are paid from cash only. Entrants' plants are paid by their owners' equity. With `CASH_SHORTFALL = "bankruptcy"` there is no overdraft either, so firms take no debt at all |
| Replacement (step 4) is financed before expansion (step 5) | Default (order of events) | K+S: expansion first |
| Ties between techniques go to the first one listed in `MENU` | Default | |
| No technical change: the menu C, D1, D2 is fixed and known to every firm | Version 1, now a switch | **Default (version 2), q = 0.5:** `TECH_DRAWS = True`: each time a firm invests it is offered one new design, drawn relative to the technique it would otherwise build and judged at its own price. Every design is Marx-biased: operating cost falls by a share a ≤ `TECH_STEP` = 5 % (labour-saving) and capital per unit rises by a share b (capital-using). Unit cost falls if b < b_S = a ucs / (δκ); the profit rate at p rises if b < b_O = a ucs / (δκ + p − uc). With probability `TECH_CONFLICT` the design lies in the conflict zone b_O ≤ b < b_S (only the unit-cost rule adopts it), otherwise 0 < b < b_O (both adopt it). With no margin there is no conflict zone. The firm adopts the design if its hurdle prefers it (the same comparison as `choose_technique`) and keeps knowing it; if not, it still invests, in its best known technique. Hurdle and replacement use the firm's known techniques; an entrant can build any technique in use (`equations/new_technique.py`). Shaikh's menu is itself Marx-biased: D1 against C is a design both rules adopt at p = 100, D2 against D1 a conflict design |
| **Innovation set** (`TECH_CHANGE = "innovation_set"`, to implement; `"categories"` = the rule above stays the default): a design is drawn relative to a reference technique with nothing read from the firm, ucs_n = (1 − a) ucs_o, κ_n = (1 + b) κ_o, a = u · `TECH_STEP`, b = k a, k log-normal around the median `TECH_BIAS` (the capital per unit given up per unit of operating cost saved, the treatment) with spread `TECH_BIAS_SPREAD`. The two rules filter the same draw: the unit-cost rule adopts if k < ucs_o/(δκ_o), the profit-rate rule at price p if k < ucs_o/(δκ_o + max{0, p − uc_o}); the zones (both adopt, conflict, both reject) are outcomes, and a price war closes the conflict zone. Options: `TECH_SET` `"marx"` / `"neutral"` (direction uniform on the circle: capital-saving designs and the second wedge appear, realised Marx bias becomes an outcome), `TECH_REFERENCE` `"own"` / `"frontier"`, `TECH_DRAW_TIMING` `"investment"` / `"period"` (a draw per firm per period with probability `TECH_DRAW_RATE`), `TECH_DIFFUSION` `"private"` / `"public"` (a technique known to every firm `IMITATION_LAG` periods after its first plant produces). Limits of the current rule it answers: the conflict share is a coin flip, no design is ever rejected by a unit-cost firm, no capital-saving designs, the draw reads the firm's price, more investment means more draws, designs are private to the adopter but public to entrants. Zone shares on the test industry and the full specification: `review-v2.md`, section 4 | Implemented as a switch on 7 November (step 3 of the plan), `TECH_CHANGE = "categories"` staying the default; the option defaults are `TECH_SET = "marx"`, `TECH_BIAS = 1.5`, `TECH_BIAS_SPREAD = 0.8`, `TECH_REFERENCE = "own"`, `TECH_DRAW_TIMING = "period"` with `TECH_DRAW_RATE = 0.2`, `TECH_DIFFUSION = "public"` with `IMITATION_LAG = 2`. Public diffusion counts the lag from the first period a plant of the design produced, whether or not that plant still runs. Every draw is logged with its zone (`both`, `unit_cost`, `profit_rate`, `none`) at the firm's price; `groups` gets `ucs_mean`, `kappa_mean`, `n_designs_offered`, `n_designs_adopted` for the realised direction of technical change. In the sensitivity analysis (Ugo) | Keep `"categories"` only |
| Investment volume: the accelerator above | Version 1, now a switch | **Default (version 2):** `INVESTMENT_RULE = "retained_earnings"`: whatever the demand, a firm buys as many plants as its retained earnings pay for (profit after depreciation and interest, less dividends, accumulated and not yet spent on plants, and held as cash); no borrowing (`equations/retained_earnings_investment.py`) |

## Entry and exit (unassigned)

| Choice | Status | Alternatives |
|---|---|---|
| r_new = realised profit rate this period (before interest, net of depreciation, at the owner's price and actual output) of plants that came into operation in the last k = 5 periods, capacity-weighted; no such plant ⇒ no entry. (The brief says "realised" in question 1 and "at the current price" in the starting rule) | Default | Rate at normal output and the current price |
| Pr(entry) = min{1, θ (r_new − rbar)/rbar}, θ = 5, at most one entrant per period | Fixed by Ugo | |
| Entrant's type: drawn from incumbents by market share; flips to the other type with m = 0.02 | Fixed by Ugo | Fixed share of invaders |
| Entrant price = the lowest price posted in its entry period, after which it prices by the same rule as every other firm (version 2, real-competition pricing); under the anchor rule 0.99 × leader (`ENTRANT_UNDERCUT`, version 1). h at that price, technique by its own h, capacity φ = 0.5 × average incumbent capacity, share = its capacity over total next-period capacity (incumbents rescaled) | Fixed by Ugo (φ, rule); default (1 %) | |
| Entrant's owners bring equity equal to the plant's cost, from the rest of the economy | Default | Random fraction of incumbents' cash |
| Exit if NW < 0, share < f_min = 0.01, or non-renewal; floor of two firms (the firms with the highest net worth stay) | Fixed by Ugo (channels); default (f_min) | Version 2 (`CASH_SHORTFALL = "bankruptcy"`, default): bankruptcy also when cash is negative after the period's payments, net worth whatever it is |
| **Non-renewal at firm level**: a firm exits when its last plant retires, its lifetime profit rate (before interest) was below rbar, and it has no plant on order; such a firm does not invest that period. A firm left with no plant at all also exits. Plants of the initial endowment are exempt, since their record starts at t = 0 | Fixed by Ugo (firm level, last plant); default (exemption) | Plant level (Harrod): a retiring plant below rbar is not rebuilt |
| A leaving firm repays what its cash allows, the rest of its debt is a loss of the rest of the economy, its remaining cash returns to its owners, its plants are written off; its share is shared out in proportion to the other shares | Default | |
| Entry churn: with rbar = 0.05 and θ = 5 the trigger fires almost every period (67 entries and 58 exits by share over 200 periods, seeds 1–20, version 2 defaults; 15 firms at t = 199, most of them entrants at 1 % of the market); ρ = 0.05 now equals rbar | Default, kept; a factor of the sensitivity analysis | θ = 1; rbar = 0.10 or 0.16; a smaller `ENTRANT_SIZE` |

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
| Debugging plots (`debug/`, one script per question) read only the tables of a run folder, never the model, and write to `RUN_DIR/debug/`; colours and rcParams are defined once in `style.py` at the root, imported by `plot_outputs.py` and `debug/_common.py`. A folder lacking a table stops a script with a message; `debug.report` skips the pages that need it | Default | Plots drawn from model objects in the tests |
| `plant_gantt` draws one lane per cohort (firm, arrival period, technique), thickness by capacity, with every plant's retirement cause as a marker; the figure's height follows the number of lanes (0.09 in per lane, 4 to 30 in) | Default | One lane per plant (unreadable past a few hundred plants) |
| Price-war periods shaded on the debugging plots are the collector's industry episodes (maximal runs of `war_on`), recomputed from `macro` | Default | Read `war_start` / `war_end` from `events` |
| In the plots, ties are never resolved by firm order: firm lanes are sorted by entry period then id, merit-order segments of equal cost by plant id (drawing only), and `capacity_bridge` decomposes the group whose rule is `unit_cost`, whatever its label | Default | |
| `debug.report` draws the merit order at three periods: the first period of the first price war, the first rebuild (first period with retirements at step 4 and orders) and the last period | Default | First period after the first war |
| `debug.compare_runs` matches rows on keys ((t); (t, group); (t, firm_id); (t, plant_id); (t, step, event, firm_id, plant_id, rank); (t, item)), compares text as well as numbers (NaN = NaN; text, NaN against a number and missing rows count as infinite), tolerance 1e-12 absolute; `--swap-labels` swaps the two labels in values and column names but not `rule`; tables with the names used before phase 2 are renamed first; its PNG is written next to RUN_B (the run under test), never into RUN_A (the reference) | Default | Numeric columns only; relative tolerance |

| **Merge into version 2 (7 November 2026, branch `v2-collector`).** The collector predates the version 2 rules; reconciled as follows, with no change to any trajectory (every macro column shared with `v2` identical over seeds 42, 1 and 7). Retirement cause `idle` in the plants table and the `retire` events. Exit cause `bankruptcy` also covers negative cash (`CASH_SHORTFALL`); an `unpaid_bills` event (value = the bills left unpaid) is logged beside `default`; the cumulated `unpaid_bills` of the rest of the economy is a macro column. Designs under `TECH_DRAWS`: a `design` event per draw (tech = the design, other_tech = the reference it was drawn from, cause = its zone `both` or `unit_cost`, value = its unit cost) and an `adopt` event when the hurdle prefers it; whether it is then built shows as an `order` with that technique in the same period, so "adopted" and "built" are told apart; `designs_offered`, `designs_adopted` and `capacity_designs` (plants built with techniques not on the menu) in `macro`, `capacity_designs` in `groups`. `tech_other` and `r_best` are evaluated on the techniques the firm knows (`firm.known`), as the hurdle is; an entrant's hurdle and known techniques are set before its order (`create_entrant`), so `log_order` reads them. Firm columns `retained_earnings` and `n_known`; plant columns `periods_idle` and `wear`. `p_normal` is None under the rules without an anchor; `p_floor` is the floor each rule used. The floor check counts `floor_viol` under every rule but fails only under `PRICING_RULE = "anchor"`, the only rule that enforces its floor in every branch (the version 2 rules undercut or rise relative to rivals, and a shortage under `leader_follow` posts (1 + z) L whatever the floor). The money tolerance keeps the version 2 scale (flows + money + cash and debt stocks). The collector's fixtures that need bankruptcies, defaults, cancelled orders, an age retirement or a borrowed replacement run on the version 1 plants, investment and anchor pricing (`tests/helpers.py`: `BANKRUPTCIES`, `three_plant_industry`), since under the version 2 defaults no firm ever borrows and no plant retires by age. Wall time of `Industry.run()` on the version 2 defaults: 0.11 s (`run.py` 0.5 s in all; `debug.report` 15 s) | Default (Ugo) | Fail the floor check under every rule (false failures under `leader_follow`) |

## Sensitivity analysis (planned, 7 November 2026)

The prompt for the session that runs it, with the full factor list, the observables, the
results table and the figures: `sensitivity-prompt.md`.

Decided on 7 November: the pricing rule and the technical-change rule are the model's two
sensitive parts; no default changes until a first full sensitivity analysis, run after the
collector merge (done) and the innovation-set switch (step 3 of the plan in `review-v2.md`),
decides for each factor whether it is fixed or becomes a treatment. Design: one factor at a
time around the version 2 defaults (about 20 cells, 50 seeds each, enough to detect a
20-point gap in the share of seeds won), then a factorial over the factors that moved the
outcome, 200 seeds for the cells that decide the fixed version; seeds fixed across cells;
every cell with its neutral control (two groups on the same hurdle rule under different
labels). Decision rule: a factor whose levels do not move the share of seeds won beyond the
neutral control's interval is fixed at its default; one that does becomes a treatment, or is
fixed at the level the group argues for from theory, with the sensitivity recorded here.

| Factor | Levels | Mechanism | Result |
|---|---|---|---|
| `PRICING_RULE` | `real_competition`, `leader_follow` | Pricing | |
| Floor: `PRICE_FLOOR` (default rule), `LEADER_FOLLOW_FLOOR` (leader-follow) | `operating_cost` (ucs), `unit_cost`; `markup` (leader-follow only) | Pricing | |
| `SHORTAGE_RULE` (leader-follow) | `leader`, `no_cut` | Pricing | |
| `CHI` (selection intensity) | 0.5, 1, 2 | Demand | |
| `TECH_CHANGE`, `TECH_SET`, `TECH_BIAS` | `categories` with q ∈ {0, 0.5}; `innovation_set` marx with m ∈ {0.5, 1.5, 3}; `innovation_set` neutral | Investment | |
| `TECH_DIFFUSION` | `private`, `public` | Investment | |
| `TECH_DRAW_TIMING` | `investment`, `period` | Investment | |
| Finance | `retained_earnings` + `BORROWING = False`; `accelerator` + `BORROWING = True` | Investment | |
| `RBAR`, `ENTRY_SPEED` | (0.05, 5), (0.05, 1), (0.16, 5) | Entry | |
| `DEPRECIATION` | `time`, `use` | Accounts | |

Outputs per cell, from the collector: share of seeds in which Shaikh firms hold more than
half the capacity at t = 199 with a 95 % interval; final capacity and sales shares; the
decomposition of each type's share change into price-driven, accumulation, entry and exit
terms (`collector-brief.md` §4.2–4.3, `analysis/indicators.py`); share of draws in each
adoption zone and the realised γ and χ by type; periods with a cut, mean price and profit
rates over t ≥ 50; entries, exits and firms at the end; hurdle replacements by type; the
neutral control's share of seeds won. Computing time: `Industry.run()` takes 0.11 s on the
version 2 defaults, so 20 cells × 50 seeds take about two minutes and a 200-seed cell
about half a minute.

### Choices made running it (7 November 2026, branch `feature/sensitivity`)

The decided plan is `sensitivity-plan.md` (section 7 binding); the results are in
`sensitivity-results.md`. Choices the plan left to the script:

| Choice | Status | Alternatives |
|---|---|---|
| `run.py --set NAME=value` (repeatable), parsed by `experiments.neutral_control.parse_overrides`, applied through `configure(seed, **overrides)`; an unknown name is an error. Without `--set` the six tables are identical to those of the commit before (`debug.compare_runs`: identical within 1e-12; `runs` differs only in `code_version` and `wall_seconds`) | Default (sensitivity) | |
| One row per run in `outputs/sensitivity/runs.csv`: `run.runs_row` as is (`experiment` = the stage), then `stage`, `overrides` (the cell's overrides as sorted JSON, without the population's `HURDLE_RULES`), `error` (a run that raises is kept as a row with the message and no observables; none did), then the observables | Default (sensitivity) | Overrides including `HURDLE_RULES`: the population column already says it |
| `code_version` is asked of git once per grid and handed to the workers (`runs_row` would call git at every run); it is the commit the grid ran on | Default (sensitivity) | |
| Results gathered with `Pool.imap` (task order) and written cell by cell in (cell, population, seed) order; `runs.parquet` rewritten from `runs.csv` at the end of each `grid` call | Default (sensitivity) | Parquet rewritten after every cell |
| Decomposition terms: `analysis.indicators` on the run's `groups` table, cumulated from t = 100 for the group "shaikh" (`d_share_price` = `term_price`; `d_share_accum` = `term_ordered` + `term_retired` + `term_cancelled`; `d_share_entry`, `d_share_exit` from the capacity decomposition; `d_share_entry_exit`, `d_share_rationing` from the sales decomposition) | Default (sensitivity) | |
| Counts of events (wars, designs, adoptions, orders, defaults, replacements, floor violations) over the whole run; `war_episodes_w` and the `_w` entry and exit counts over the window; `shortage_periods`, `excess_capacity_periods`, `cut_periods`, `periods_above_rbar` over the window t = 100–199 | Default (sensitivity) | Everything over the window |
| `price_min`, `price_max` of `price_avg` over the window; `price_to_pp` uses the running plant with the lowest uc at t = 199; `capital_age_{label}` over plants not retired at t = 199; `margin_spread` and `ucs_spread_mean` over firms with capacity; `conflict_adopted_shaikh` over design events with zone `unit_cost` offered to firms on the unit-cost rule (NaN in the all-profit-rate control); `diffusion_lag_mean` over drawn designs only (menu techniques excluded) | Default (sensitivity) | |
| `cells.csv`: per (stage, cell, population) the share of decided seeds won (`undecided` excluded) with the Wilson interval; for each observable the mean, the 2.5 % and 97.5 % quantiles over seeds (`_lo`, `_hi`) and a normal 95 % interval of the mean (`_ci_lo`, `_ci_hi`); booleans as shares. For the mixed rows: the controls' shares won, `gap` = mixed − mean of the two controls, `beyond_drift` (disjoint from both controls' intervals) and `beyond_base` (disjoint from the same stage's `base` mixed interval, stage 1's when the stage has no `base`) | Default (sensitivity) | |
| Decomposition terms over the whole run as well (suffix `_all`, cumulated from t = 0): the first stage 1 grid had the window terms only, which are near zero in the base cell because most takeovers happen before or around t = 100 (mean `takeover_t` 118). Stage 1 was rerun with the extra columns before stage 2 (same seeds, same results otherwise: the model is deterministic per seed); figure 3 uses the whole-run terms | Default (sensitivity) | Window terms only |
| **Stage 2 design, from the stage 1 decision rule** (a level moves the outcome when its mixed interval is disjoint from the base cell's, `beyond_base`; every stage 1 cell except four was already beyond drift, so beyond the controls does not discriminate). CHI moved at no level (0.25 to 4), so it leaves the factorial and is held at 1, as the plan's rule says; the entry factor (`RBAR` 0.16 moved, θ = 1 did not) and the per-investment draw timing (moved) join it. Factorial: pricing {real competition, leader-follow} × finance {retained earnings, accelerator + borrowing} × demand {static, growing 0.01, initially unmet} × technical change {categories q = 0.5, innovation set marx 1.5, marx 3, neutral, marx 1.5 with draws per investment} × rbar {0.05, 0.16} = 120 cells. Plus a phase block for the headline figure, which needs CHI: pricing × finance × CHI {0.25, 1, 4} × technical change {categories q = 0 and 0.5, innovation set marx 0.5, 1.5, 3, neutral}, static demand, rbar 0.05: 72 cells, 16 of which are factorial cells and not run twice. 176 cells, 100 seeds, both controls | Default (sensitivity), deviates from the plan's 144-cell cross (CHI kept only in the phase block) | CHI in the full cross, without entry and timing |
| The anchor rule (version 1) is not crossed in stage 2 although it moved (rbar 0.16: the profit-rate rule wins 74 % of decided seeds); at rbar 0.05 it does not differ from the base beyond drift. The treatment arms of the pricing factor are real competition and leader-follow, as the factor table says | Default (sensitivity) | Anchor as a third pricing level |
| `runs.csv` is committed for stage 1 only (41 MB). With stages 2 and 3 it grows to about 160 MB, above GitHub's 100 MB limit per file, which would make the branch impossible to push, so from stage 2 on the commit holds `outputs/sensitivity/runs.csv.gz` (the same table, gzip) and `runs.csv` leaves the index; `runs.csv` and `runs.parquet` stay in the working tree, as the deliverable | Default (sensitivity), deviates from "commit runs.csv" | Git LFS; one CSV per stage |
| `uc_end_{label}` is the macro column `unit_cost_{label}` at t = 199 as written, which is 0 when the label has no producing capacity; `summarise` treats those zeros as missing (capacity share 0 for "shaikh", 1 for "okishio", or undecided) so that the cell means are means over the seeds where the label still produces | Default (sensitivity) | NaN in the run rows (would make rows written before the fix differ from a rerun) |

## Neutral control (seeds 1–20, version 2 defaults), for the record

`python -m experiments.neutral_control --seeds 20` (7 November 2026): share of seeds in which
the label "shaikh" holds more than half of the producing capacity at t = 199, with the 95 %
Wilson interval, and its mean final capacity share.

| Population | Seeds won by "shaikh" | Interval | Mean capacity share |
|---|---|---|---|
| Mixed (shaikh = unit_cost, okishio = profit_rate) | 16 of 20 | 0.58–0.92 | 0.80 |
| Both labels on the unit-cost rule | 12 of 20 | 0.39–0.78 | 0.57 |
| Both labels on the profit-rate rule | 9 of 20 | 0.26–0.66 | 0.45 |

With the innovation set instead (`TECH_CHANGE = "innovation_set"`, m = 1.5, public diffusion,
draws per period; same seeds): mixed 19 of 20 (0.76–0.99), mean capacity share 0.88; both
labels on the unit-cost rule 10 of 20 (0.30–0.70); both on the profit-rate rule 10 of 20.
Here the mixed population lies outside both controls' intervals: the first configuration in
which the unit-cost rule's advantage is a result beyond drift at 20 seeds. Under the
categories rule:

Under neutral drift a label should win about half the seeds; the controls do, within their
intervals. The mixed population's 16 of 20 lies above both controls' point estimates, but
its interval overlaps theirs at 20 seeds: the "Shaikh firms win 16 of 20" of the baseline
record is not yet a result beyond drift, which is what the 50- and 200-seed cells of the
sensitivity analysis are for. The two controls differ (12 against 9) because the random
draws are consumed in firm order, so the label listed first in `INITIAL_FIRMS` gets
different designs and entry draws: a label effect of the single random stream, not of the
rules, and an argument for the per-mechanism streams proposed in the collector table.

## What the baseline shows (seed 42), for the record

Version 2 defaults, rbar = 0.05, entrants on the pricing rule:

- Entry starts at t = 0: with rbar = 5 % the profit rate on new plants is above rbar almost
  every period, so a firm enters most periods (43 entries over the run) and most of them
  leave again once their share falls below 1 % (42 exits, all by share).
- The opening war takes prices from 100 to 73 by t = 20; afterwards prices follow unit costs
  down (Shaikh firms' unit cost 46 at t = 199, price 49), with a cut in 126 of 200 periods and
  50 periods above normal capacity (peak price 122 at t = 30). Over t = 50–199 the mean price
  is 59.5 and the mean profit rate 7.1 %.
- Okishio firms fall below 1 % of the market at t = 75; entrants that switch rule bring them
  back to 7 % by t = 199. 7 firms remain.

Version 2 defaults with rbar = 0.16 and entrants undercutting the leader by 1 % (before the
change of 4 November 2026):

- t = 0–17: the D1 and D2 firms undercut C and prices fall from 100 to 74, below the unit
  costs of C (78) and D1 (76). Their plants are scrapped (360 units at t = 16–17) and
  capacity falls to 460 against demand of 680.
- t = 18–23: the shortage lifts the price to 116 and the profit rate to 30 %; firms enter
  from t = 20 and capacity is back to about 800 by t = 23.
- Afterwards firms adopt 293 of the 326 designs offered; the unit cost of Shaikh firms falls
  from 76 to 50 by t = 199. Prices follow costs down through price wars (a cut in 140 of 200
  periods), broken by shortages when plants are scrapped (56 periods above normal capacity,
  a peak of 188 at t = 97). Over t = 50–199 the mean price is 75.7 and the mean profit
  rate 10.8 %.
- Okishio firms hold under 1 % of the market from t = 88. Over the run 17 firms enter and
  19 leave; 4 firms remain at t = 199.

Real-competition pricing with version 1 plants and investment:

- At t = 0 the D1 and D2 firms have a cost edge over C and spare capacity (demand 680 against
  766): they cut, the others follow, and prices fall 1–2 % a period to 78.5, C's unit cost,
  at t = 19. No firm cuts because utilisation is low; they cut because they are cheaper.
- At t = 20 retirements and one exit leave capacity at 584 against demand 680. Excess demand
  raises prices to 89.9 by t = 22.
- Capacity is then rebuilt to last sales (desired capacity = x_{t−1}), every firm is at full
  utilisation, and nothing moves again: price 89.9 from t = 22 to t = 199, profit rate 9.5 %
  against rbar = 16 %, no entry, all capacity D2, Shaikh share 0.60 in every seed.
- The price is stuck below the regulating price of production (D2: 100.3) because nothing in
  the model shrinks capacity when the profit rate is below rbar, so excess demand never
  returns. See "Real-competition pricing needs profit-sensitive investment" below.

Version 1 (`PRICING_RULE = "anchor"`):

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

## Pricing switches compared (seeds 1–10; version 1 plants and accelerator, rbar = 0.16), for the record

Everything else at its version 1 default (continuous plants, accelerator with borrowing, rbar = 0.16). Final share of Shaikh firms at t = 199 (mean, with range over
seeds), periods (of 200) in which the price leader is the lowest-cost firm, and mean price and
profit rates (Shaikh / Okishio) over t ≥ 50.

| Pricing | Final Shaikh share | Leader is lowest-cost | Mean price | Profit rate % S / O |
|---|---|---|---|---|
| Real competition (default) | 0.60 (0.60–0.60) | 187 | 89.9 | 9.4 / 9.8 |
| Real competition, `EXCESS_DEMAND = "unserved"` | 0.60 (0.60–0.60) | 187 | 78.5 | 2.2 / 2.2 |
| Real competition, `PRICE_FLOOR = "operating_cost"` | 0.60 (0.60–0.60) | 187 | 89.9 | 9.4 / 9.8 |
| Anchor, own target return | 0.12 (0.07–0.19) | 24 | 98.8 | 14.8 / 16.0 |
| Anchor, `PRICING_ANCHOR = "markup"` | 0.82 (0.76–0.85) | 126 | 96.3 | 13.5 / 14.1 |
| Anchor, `PRICING_ANCHOR = "leader"` | 0.51 (0.26–0.75) | 117 | 99.0 | 15.1 / 16.1 |

Under the anchor rule each firm-specific anchor hands the contest to one type: under its own
target return the capital-intensive D2 always posts above D1 in normal times and the
replicator moves its customers away; under the markup D2 is always cheaper. With one anchor
for all firms (the leader's), neither type wins systematically. Under the real-competition
rule there is no anchor to hand out the contest: the lowest-cost firm leads in 187 of 200
periods, and both types end on D2, so the profit rates are almost equal.

## Real-competition pricing needs profit-sensitive investment (scratch test, not in the code)

In Shaikh (2016, ch. 7) the price gravitates around the regulating capital's price of
production through the supply side: when its profit rate is below rbar, regulating capitals
slow accumulation, demand outruns capacity and the price rises; an innovator expands ahead of
its sales and cuts to fill the new capacity. With desired capacity = last sales neither can
happen. A scratch run replaced it with desired capacity = x_{t−1} (1 + β (r_i − rbar)/rbar),
β = 0.25, the adjustment capped at ±20 % (seeds 1–10, t = 100–199; D3 = a new technique, ucs 55,
κ 150, uc 70, price of production 94, offered from t = 100):

| Investment | New technique | Mean price | Profit rate | Periods with a cut | Price falls / rises | Entries |
|---|---|---|---|---|---|---|
| Desired capacity = x_{t−1} (current) | none | 89.9 | 9.5 % | 0 | 0 / 0 | 0 |
| Desired capacity = x_{t−1} (current) | D3 | 89.9 | 12.9 % | 0 | 0 / 0 | 0 |
| Profit-sensitive | none | 99.3 | 15.7 % | 8.8 | 10.8 / 7.8 | 2.8 |
| Profit-sensitive | D3 | 95.2 | 16.1 % | 2.2 | 16.8 / 9.0 | 15.5 |
| Anchor rule, current investment | D3 | 93.6 | 15.5 % | 9.1 | 9.3 / 5.6 | 2.7 |

With profit-sensitive investment the rule gives what the theory expects: the price gravitates
around the price of production (≈ 100), the profit rate around rbar, prices move turbulently
around it, entry happens, and a cheaper technique lowers the price towards its own price of
production (94). With the current investment rule the cheaper technique diffuses but its
adopters keep the surplus profit, and the price never moves. This is a proposal for the
investment owner (Ugo), not a change to the code.

## Fixed plants, scrapping and retained-earnings investment (seeds 1–10, rbar = 0.16), for the record

`PLANT_SIZE` = S, `PLANT_LIFE = None`, `SCRAP_COST = "unit_cost"` with
`OBSOLESCENCE_PERIODS = 2`, `INVESTMENT_RULE = "retained_earnings"`, pricing at its default
(real competition). Means over t = 100–199; "with D3": a technique with ucs 55, κ 150
(unit cost 70, price of production 94) offered from t = 100. Demand is 680.

| Version | Capacity | Utilisation | Price | Profit rate | Price at t = 199 with D3 |
|---|---|---|---|---|---|
| Version 1 plants and investment | 680 | 1.00 | 89.9 | 9.5 % | 89.9: D3 adopted, no war |
| S = 20, no idle scrapping | 5 489, rising | 0.13 | 81.7 | 1.2 % | 80.1 |
| S = 20, `IDLE_SCRAPPING = True` | 784 | 0.86 | 81.7 | 8.2 % | 78.5: short war, D3 replaces all D2 |
| S = 40, `IDLE_SCRAPPING = True` | 776 | 0.83 | 80.1 | 7.3 % | 91.7: war below D2's unit cost, D2 scrapped, shortage, entry |
| S = 130, `IDLE_SCRAPPING = True` | 1 084 | 0.64 | 75.4 | 4.5 % | 73.9 |

- Without idle scrapping capacity grows without limit. Plants never retire, are fully
  depreciated after 10 periods and then cost only ucs, so profits stay positive however
  idle the plants are, and retained earnings keep buying plants. The price does not fall:
  idle capacity alone never starts a cut, and the price stays above every plant's unit cost.
  (Counting all cash as retained earnings: capacity 16 000, utilisation 0.04.)
- With idle scrapping, retained earnings work as continuous replacement: each new plant
  pushes out the firm's highest-cost, oldest plant two periods later, and a new technique
  spreads through the whole industry (D3: 800 of 808 units by t = 199).
- Wars from technical change depend on how fast firms adopt. With S = 40, D3 adopters cut
  the price below D2's unit cost; D2 plants are scrapped as unprofitable, capacity falls to
  520, the shortage lifts the price to about 90 and attracts an entrant: war, scrapping and
  recovery as in Shaikh. With S = 20 every firm buys D3 within a few periods, cost edges are
  short-lived and the war stops at 78.5, above D2's unit cost.
- Between shocks the price still does not move, and the profit rate stays below rbar:
  firms buy before they scrap, so capacity never falls short of demand and the price has
  no reason to rise. Nothing in investment compares the profit rate with rbar.
- Large plants (S = 130) leave a firm with one or two plants: it cannot scrap part of its
  idle capacity, and utilisation stays near 0.64.

## Technical change by draws (seeds 1–100, rbar = 0.16, before the entrant-pricing change of 4 November), for the record

`TECH_DRAWS = True` with fixed plants of 20, no lifespan, scrapping below unit cost or when
idle, and retained-earnings investment. To isolate the draws, all six firms start on C and
C is the only technique on the menu (`INITIAL_FIRMS` = 3 × (C, shaikh), (C, okishio),
`MENU = ("C",)`): the two types begin identical, and every later difference comes from the
designs they adopt. Seeds (of 100) in which Shaikh firms hold more than half the market at
t = 199, with a 95 % interval, and the mean share.

| Conflict share q | Real-competition pricing | Anchor pricing (version 1) |
|---|---|---|
| 0 | 66 (56–75), share 0.65 | 46 (37–56), share 0.46 |
| 0.05 | 70 (60–78), share 0.67 | 47 (38–57), share 0.49 |
| 0.25 | 74 (65–82), share 0.74 | 47 (38–57), share 0.49 |
| 0.5 | 71 (61–79), share 0.73 | 58 (48–67), share 0.59 |

With Shaikh's menu instead (C, D1, D2) and q = 0.5: 76 (67–83) under real-competition pricing.

- Under real-competition pricing, Shaikh firms win about two runs in three whatever q. The
  conflict share adds little: a conflict design lowers unit cost by less than a design both
  rules adopt (for the same fall in operating cost it uses more capital), so the firms that
  take it gain only a small cost edge.
- The advantage at q = 0 comes from prices moving, not from the draws. A design adopted at
  one price can be in the conflict zone, relative to an older design, at a higher price: when
  prices rise after a shortage, the profit-rate rule switches back to a less mechanised
  design it already knows. Okishio firms build a known technique dearer than their cheapest
  in 12.5 % of investments (3.9 % dearer on average), then get undercut in the next price war.
  Shaikh firms never do. Under anchor pricing this happens in 4.8 % of investments (0.8 %
  dearer), and the outcome is even.
- Outcomes are mostly winner-take-all: firms with lower costs gain share, earn more, invest
  more often, and so are offered more designs.
- Costs and prices fall a long way (price at t = 199: 41–69 from 100), cuts happen in 75–92
  of every 100 periods, and profit rates stay below rbar (8–15 %).
- An earlier draw (unit cost cut by a fixed share, capital per unit set from the profit-rate
  threshold) let capital per unit grow without bound and drove operating costs negative; its
  results are void.

## Entrant pricing and rbar (seeds 1–20), for the record

Version 2 defaults, Shaikh's menu. Price spread = highest minus lowest posted price, mean over
t ≥ 20 and the run's maximum; shortage periods = periods above normal capacity.

| Version | Mean spread | Largest spread | Shortage periods | Entries | Exits (by share) | Firms at t = 199 | Shaikh firms win |
|---|---|---|---|---|---|---|---|
| Entrants 1 % below the leader, rbar 0.16 | 16.7 | 117 | 45 | 12.6 | 15.0 (14.9) | 3.6 | 15 of 20 |
| Entrants on the pricing rule, rbar 0.16 | 6.0 | 61 | 27 | 18.9 | 19.4 (19.4) | 5.5 | 17 of 20 |
| Entrants on the pricing rule, rbar 0.05 (default) | 11.3 | 86 | 60 | 66.8 | 57.7 (57.5) | 15.1 | 16 of 20 |

- Entrants that undercut the lowest price in a shortage add a new bottom rung every period
  while incumbents climb one rung at a time: prices fan out (up to 64–224 at seed 42) and
  profitable incumbents at the top fall below 1 % of the market and exit. Pricing entrants
  by the same rule removes most of this.
- With rbar = 0.05 the entry trigger fires almost every period (θ = 5): entries triple, most
  entrants exit again by share, and shortages are more frequent. The interest rate ρ = 0.05
  now equals rbar.
