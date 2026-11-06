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

Version 1 rule (`PRICING_RULE = "anchor"`):

| Choice | Status | Alternatives |
|---|---|---|
| Anchor = target return uc_i + rbar κ_i, with uc_i and κ_i the capacity-weighted averages of the firm's plants | Fixed by Ugo | `PRICING_ANCHOR = "markup"`: (1 + μ) uc_i, μ = 0.282; `PRICING_ANCHOR = "leader"`: one anchor for every firm, the target-return price of last period's price leader (tied leaders averaged) |
| Leader = lowest price posted in the previous period (entrants' entry prices excluded) | Fixed by Ugo | |
| Floor = ucs of the most expensive plant needed to produce last period's sales in merit order; the cheapest plant's ucs when last sales were zero | Fixed by Ugo (rule); default (zero sales) | Floor including the overtime premium |
| u_war = 0.95, `WAR_PERIODS` = 2, c = 0.02, b = 0.025, λ = 0.25 | Default (brief's ranges where given) | |
| No war before a firm has `WAR_PERIODS` periods of history (entrants start at peace) | Default | |
| War rule: every firm at war cuts its own price by c a period | Default | (`PRICE_WAR = "cost_gated"` removed in version 2: the real-competition rule replaces it) |

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
| Depreciation accounting only (straight line), no physical decay | Fixed by Ugo | Capacity or cost rising with age |
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

## Pricing switches compared (seeds 1–10), for the record

Everything else at its default. Final share of Shaikh firms at t = 199 (mean, with range over
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

## Fixed plants, scrapping and retained-earnings investment (seeds 1–10), for the record

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

## Technical change by draws (seeds 1–100), for the record

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
