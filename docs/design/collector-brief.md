# ABM collector and plots brief

> Exported on 4 November 2026 from the Claude Doc "ABM collector and plots brief" (https://claude.ai/artifact/2pCkJLtfa4SysxWu5aeL3H), which remains the master copy.
>
> **Superseded on 4 November:** wherever this brief assumes one plant per firm in v1, read vintages instead. The model already gives each firm a list of plants (`Firm.plants`, `Firm.pending_plants`), so the plants table and every vintage indicator (age distribution, vintage spread, merit order) are v1.

Nov 3, 2026 · @Ugo

Each run stores six tidy tables (runs, industry, groups, firms, plants, events) plus one flow table for the stock-flow check. Everything else, including every figure, is computed after the run from those tables. Seven outputs are needed for the lab on 6 November and the seminar on 20 November; the rest can wait.

## 1. What the collector is for

The collector records what the research question needs and what proves the code is neutral. The question is whether market selection (sélection par le marché) favours firms that equip new plants at the lowest unit cost (coût unitaire; h = 0, Shaikh) or at the highest profit rate (taux de profit) at the current price (h = the best rate on offer, Okishio), and how the answer moves with the frequency of price wars and with finance. Every variable below serves either that question, one of the hypotheses H1–H5, a stylised fact, or a check.

**The outputs we cannot do without (all v1):**

1. Capacity and sales of each group of firms, every period: the fitness measure.
2. The four capacity flows of each group: plants ordered, plants retired, entrants' plants and exits. They decompose each rule's change in capacity share (part de capacité).
3. Each firm's price, unit cost and market share (part de marché): price wars, the law of correlated prices and the selection slope.
4. The technique of every new plant, and the technique the other rule would have chosen at the same moment: the share of decisions where the rules disagree.
5. The inputs of the three profit rates: profit, operating surplus, investment spending and the rate on the newest plant.
6. The residuals of the stock-flow (cohérence stock-flux), share and capacity checks, every period, as the course asks.
7. Run metadata: seed, every parameter, treatment, population and code version.

**Record at source.** Each mechanism writes its outputs into the period record at the step where it computes them; at step 7 the collector only assembles the rows and runs the checks. Two reasons. Capacity changes within the period (retirement at step 4), so a value read at step 7 is not the value used at step 3. And a firm that exits at step 6 must still have a row for the period it lived through.

**Groups, labels and rules.** A firm carries a label (`group`: S, O, or A and B in controls) separate from the rule it applies (`rule`) and the hurdle rate (taux de rendement exigé) it uses (`hurdle`). Neutrality checks need the three apart: in the neutral control two labels share one rule; in the swapped run the labels trade rules.

Names from the notation table of the mechanism briefs are used as they stand. Names marked † are proposals for the group to confirm. Units: money amounts in wage units (w.u., the money wage being the numéraire, w = 1), quantities in units of output per period, rates per period.

Data flow of one run: the six mechanisms (steps 1–6) write the seven tables at source; the collector checks them every period; indicators (§4) are computed after the run; figures and diagnostics (§6, §7) are drawn from the tables by `plot_outputs.py` and the `debug/` scripts.

Only the tables are written during the run; every indicator and figure is recomputed from them, so a new figure never needs a new run.

## 2. From questions to outputs

Every question, hypothesis, experiment and stylised fact maps onto stored variables, one figure and one set of runs. Populations and cells are defined in §5: MIX (50/50), HOM-S and HOM-O (one rule), INV (a 5 % invader, both ways), NEU (two labels, one rule), SWP (labels swapped); cells BASE, WAR+ (frequent price wars), CHI− (weak selection), CRED (capped credit). Figure IDs refer to §6.

| Item | Variables | Plot | Runs | Supports | Contradicts |
| --- | --- | --- | --- | --- | --- |
| Q1. Does selection favour the unit-cost rule? | groups: capacity, sales | F1, F2 | MIX, NEU · all cells · 50 seeds (20 Nov), 200 (1 Dec) | S's capacity share above 0.5 at the horizon, and S takes over in more seeds than the NEU benchmark | The reverse favours Okishio; inside the NEU band, selection decides nothing |
| Q2. Does it depend on how often price wars occur? | as Q1, plus war episodes (§4.9) | F3 | MIX · BASE vs WAR+ · 50 | S's share rises with war frequency | Flat or falling |
| Q3. Does it depend on finance? | as Q1, plus debt, borrow, exit causes | F3 | MIX · BASE vs CRED · 50 | O's share higher under internal finance; credit helps S | No difference, or the reverse |
| H1. Okishio benchmark | events (order): technique; price of production of each adopted technique, uc + rbar·kappa; industry: price\_avg | F5 | HOM-O · BASE, Shaikh's menu · 20 | Price of production never rises from one adoption to the next; long-run price relative to the wage at or below its start | Any rise: a coding error, since H1 is a theorem |
| H2. Shaikh benchmark | capacity-weighted kappa, price\_avg | F5 | HOM-S · neutral vs skewed draws (later) · 50 | kappa rises and the long-run price can rise with skewed draws; no rise with neutral draws | Price rises with neutral draws |
| H3. Selection by environment | groups: capacity; cell levels | F3 | MIX · 2×2×2 grid · 200 | S gains at strong selection and frequent wars; O at weak selection and internal finance | Opposite signs, or no gradient |
| H4. Price signature | price\_avg; capacity share of D2 | F6 | HOM-S, MIX · BASE, Shaikh's menu · 50 | Price dips during the war, then settles above its start, near 100.26 for a start at 100 (critique §1, from Shaikh 2016, p. 316) | Settles at or below its start |
| H5. Expectations | hurdle by firm (evolving h) | F14 | MIX with mutating h · war levels · later | Mean h falls as wars become more frequent | Rises or stays flat |
| E1. Selection experiment | groups: capacity, sales | F1, F2 | MIX, NEU | Fitness: capacity share at the horizon, share of seeds with a take-over, time to take-over; sales share reported apart | — |
| E2. Invasion | groups: capacity of the invader | F7 | INV both ways · all cells · 200 | The invader ends above its 5 % start in more seeds than a 5 % NEU group | Below the NEU rate: the resident rule resists |
| E3. Aggregate signature | price\_avg, kappa, r\_avg | F5, F11 | HOM-S, HOM-O · BASE · 50 | Capital per unit rises under S only, as in Park (2001) summarised in the critique §1; required before any mixed run is read | Rises under both, or under O |
| E4. Decomposition | groups: cap\_ordered, cap\_retired, cap\_entry, cap\_exit; firms: share, share\_end, sales | F4 | MIX · all cells | Says which channel moves shares: S's gains through the price-driven term, O's through net investment | — (a measurement, not a test) |
| SF1. Law of correlated prices (loi des prix corrélés), Table 7.3 row 2 (Shaikh 2016, p. 271) | firms: price, uc, sales, capacity | F8 | MIX, HOM · BASE | Price dispersion below unit-cost dispersion; lower-cost firms price lower | Prices as dispersed as costs |
| SF2. Regulating capital (capital régulateur) leads prices, row 3 | industry: leader\_id, lowest\_uc\_id | F12 | MIX · BASE | Leader is the lowest-cost firm in most periods | Leader unrelated to cost |
| SF3. Followers' margins are residuals, row 4 | firms: price, uc | F8 | MIX · BASE | Slope of margin on unit cost near −1 across firms | Slope near 0 |
| SF4. Lowest cost, highest sustainable rate under price cutting, row 5 | firms: r\_newest, tech; industry: war\_on | F12 | MIX · BASE, WAR+ | Ranking of techniques by profit rate flips toward D2 inside wars | No flip |
| SF5. Spread of costs, unequal margins and profit rates persist, rows 7–9 | plants: ucs; firms: price, uc, r\_avg | F13 | HOM, MIX · BASE with continuing draws (later) | Dispersion stays above zero | Collapses to one technique |
| SF6. Vintage spread: best to worst US cement plant about 3.5 in output per man-hour, 1935 (Salter 1966, p. 96) | plants: ucs, running | F13 | later (needs vintages) | Ratio of the same order | Ratio near 1 |
| SF7. Slow, bursty diffusion: US precalciner kilns 0 (1973), 24 (1983), 31 (1998), 66 (2013) (Macher, Miller & Osborne 2021, Table 1, p. 81); 74 % of capacity in 2013 (p. 82) | plants or firms: tech, capacity | F10 | HOM-S, HOM-O, MIX · later calibration | S-shaped curve with bursts and plateaus | Instant or linear diffusion |
| SF8. Shakeout with a flat real price: US plants 163 to 89, 1974–2019 (Miller et al. 2022, p. 8); price $102.16 per tonne in 1974, $104.83 in 2019 (p. 9) | industry: n\_firms, price\_avg | F15, F5 | MIX · later calibration | Firm count falls while capacity holds and the price is flat | — (shape target) |
| SF9. Entry follows profitability: the most profitable industries had “almost five times as many entrants” (Bryce & Dyer 2007, quoted in Shaikh 2016, p. 283) | events (entry); industry: r\_new | F15 | MIX · BASE | Entries concentrate in periods of high r\_new − rbar (a within-industry analogue) | No link |
| SF10. Incremental rates equalise turbulently (égalisation turbulente) around the general rate; average rates do not (Shaikh 2016, ch. 7; eq. 7.7, p. 300) | groups: gos, invest\_spend, profit; firms: r\_avg | F11 | MIX, HOM · BASE | r\_incr fluctuates around rbar; r\_avg stays apart across groups | r\_incr drifts away from rbar |
| SF11. Capital intensity rises and the profit rate falls with firm size: elasticities 0.272 and −0.263 (Shaikh 2016, Table 7.9, p. 295) | firms: kappa, r\_avg, capacity | — | later (needs scale economies, left out of v1 by the critique §5) | Same signs | Opposite signs |
| NC. Neutral control | as Q1 | F2 | NEU · all cells · 200 | A group takes over in a share of seeds equal to its starting share (dérive neutre) | Any deviation: a bias in the code (§7) |

## 3. Collector specification

Seven tables, one row per observation unit, each carrying `run_id`. "Step" is the step of the period at which the value is final: 0 run start, 1 Pricing, 2 Demand, 3 Production and accounts, 4 Scrapping, 5 Investment, 6 Entry and exit, 7 collector. "v1" means needed for 6 and 20 November.

### 3.1 Run metadata: `runs`, one row per run

| Python name | Meaning | Unit | Step | Mechanism | Phase |
| --- | --- | --- | --- | --- | --- |
| run\_id† | experiment, cell, population and seed in one string | text | 0 | run.py | v1 |
| seed | master seed (graine); one random stream per mechanism is spawned from it | integer | 0 | run.py | v1 |
| code\_version† | git commit hash, flagged if the tree had uncommitted changes | text | 0 | run.py | v1 |
| param\_hash† | hash of the full parameter set | text | 0 | parameters.py | v1 |
| experiment† | selection, invasion, aggregate, neutral\_control, swapped\_labels, identical | text | 0 | run.py | v1 |
| population† | starting mix: S50\_O50, S95\_O5, S100, A50\_B50 … | text | 0 | run.py | v1 |
| cell† | treatment cell: BASE, WAR+, CHI−, CRED, or a grid code | text | 0 | run.py | v1 |
| anchor† | normal price rule: target\_return or markup | text | 0 | Pricing | v1 |
| okishio\_price† | price at which Okishio firms evaluate techniques: average, leader or own | text | 0 | Investment | v1 |
| menu† | shaikh3, rule\_neutral, neutral\_draws, skewed\_draws | text | 0 | Investment | v1 for shaikh3 and rule\_neutral; draws later |
| delta, rbar, rho, … | every parameter, one column each, under its parameters.py name | as defined | 0 | parameters.py | v1 |
| horizon†, burn\_in† | periods run, periods discarded | periods | 0 | run.py | v1 |
| n\_check\_fail† | periods in which a check of §3.7 failed; must be 0 | count | 7 | collector | v1 |
| wall\_seconds† | run time, to budget the seeds | seconds | 7 | run.py | v1 |

### 3.2 Industry per period: `industry`, one row per t

| Python name | Meaning | Unit | Step | Mechanism | Phase |
| --- | --- | --- | --- | --- | --- |
| t | period | period | — | scheduler | v1 |
| demand | industry demand D\_t | units/period | 2 | Demand | v1 |
| sales\_total† | sum of sales | units/period | 2 | Demand | v1 |
| unmet\_total† | demand no firm could serve | units/period | 2 | Demand | v1 |
| capacity\_total† | capacity used in production | units/period | 3 | Production and accounts | v1 |
| n\_firms† | firms active at step 1 | count | 1 | — | v1 |
| price\_avg† | sales-weighted mean price | w.u./unit | 2 | Demand | v1 |
| price\_lead† | lowest posted price, p^lead\_t | w.u./unit | 1 | Pricing | v1 |
| leader\_id† | firm posting it (ties broken at random) | id | 1 | Pricing | v1 |
| lowest\_uc\_id† | firm with the lowest uc | id | 3 | Production and accounts | v1 |
| war\_on† | at least one firm in cut mode | bool | 1 | Pricing | v1 |
| n\_cutting† | firms in cut mode | count | 1 | Pricing | v1 |
| gos\_total† | operating surplus, sum of (price − ucs)·sales | w.u. | 3 | Production and accounts | v1 |
| invest\_total† | investment spending, entrants included | w.u. | 6 | Investment, Entry and exit | v1 |
| r\_new | profit rate at the current price on plants built in the last k periods | per period | 6 | Entry and exit | v1 |
| p\_entry† | entry probability given r\_new | 0–1 | 6 | Entry and exit | v1 |
| roe\_balance† | rest-of-economy account | w.u. | 6 | Production and accounts | v1 |

The check residuals of §3.7 are also columns of this table.

### 3.3 Groups per period: `groups`, one row per t and group

Everything here can be rebuilt from `firms` and `events`. It is stored anyway because it is small: the 200-seed runs keep it for every seed and drop the firm tables (§5).

| Python name | Meaning | Unit | Step | Mechanism | Phase |
| --- | --- | --- | --- | --- | --- |
| t, group† | period; label S, O, A or B | — | — | collector | v1 |
| n\_firms† | firms active at step 1 | count | 1 | — | v1 |
| capacity | capacity used at step 3 | units/period | 3 | Production and accounts | v1 |
| sales | units sold | units/period | 2 | Demand | v1 |
| share | sum of the group's f\_i from the replicator | 0–1 | 2 | Demand | v1 |
| share\_end† | the same after exits and entries are renormalised | 0–1 | 6 | Entry and exit | v1 |
| cap\_retired† | capacity retired by incumbents | units/period | 4 | Scrapping | v1 |
| cap\_ordered† | capacity ordered by incumbents, arriving at t + 1 | units/period | 5 | Investment | v1 |
| cap\_replace† | part of cap\_ordered that replaces retired plants | units/period | 5 | Investment, Scrapping | v1 |
| cap\_entry† | capacity of entrants' plants, arriving at t + 1 | units/period | 6 | Entry and exit | v1 |
| cap\_exit† | capacity of exiting firms, after step 4 | units/period | 6 | Entry and exit | v1 |
| n\_entry†, n\_exit† | entrants and leavers | count | 6 | Entry and exit | v1 |
| profit | profit after depreciation and interest | w.u. | 3 | Production and accounts | v1 |
| gos† | operating surplus | w.u. | 3 | Production and accounts | v1 |
| invest\_spend† | investment spending, entrants included | w.u. | 6 | Investment, Entry and exit | v1 |
| hurdle\_mean† | capacity-weighted mean h | per period | 5 | Investment | later (evolving h) |

### 3.4 Firm per period: `firms`, one row per t and firm, tagged with its rule

A firm that exits at step 6 keeps its row for period t, with `exited` true. An entrant's first row is t + 1, when its plant arrives.

| Python name | Meaning | Unit | Step | Mechanism | Phase |
| --- | --- | --- | --- | --- | --- |
| t, firm\_id† | period, firm | — | — | collector | v1 |
| group† | label used in the analysis | text | 0 or entry | run.py, Entry and exit | v1 |
| rule† | rule actually applied: shaikh or okishio | text | 0 or entry | run.py, Entry and exit | v1 |
| hurdle | h\_i used to choose the technique this period | per period | 5 | Investment | v1 |
| born† | period of entry (0 for initial firms) | period | 6 | Entry and exit | v1 |
| price | posted price p\_i | w.u./unit | 1 | Pricing | v1 |
| p\_normal† | anchor p^N\_i, own target-return price uc\_i + rbar·kappa\_i | w.u./unit | 1 | Pricing | v1 |
| p\_floor† | ucs of the most expensive plant the firm needs to run | w.u./unit | 1 | Pricing | v1 |
| cutting† | in cut mode this period | bool | 1 | Pricing | v1 |
| low\_util† | consecutive periods below the war threshold | periods | 1 | Pricing | v1 |
| share | f\_i from the replicator, before the capacity cap | 0–1 | 2 | Demand | v1 |
| sales | units sold x\_i | units/period | 2 | Demand | v1 |
| util | utilisation u\_i = x\_i / q̄\_i | ratio | 2 | Demand | v1 |
| unmet† | demand l\_i the firm could not serve | units/period | 2 | Demand | v1 |
| share\_end† | f\_i after exits and entries are renormalised | 0–1 | 6 | Entry and exit | v1 |
| capacity | normal output q̄\_i of the plants it runs this period | units/period | 3 | Production and accounts | v1 |
| output† | units produced (equal to sales in v1) | units/period | 3 | Production and accounts | v1 |
| ucs | output-weighted unit operating cost of running plants | w.u./unit | 3 | Production and accounts | v1 |
| kappa | capacity-weighted capital per unit of normal output | w.u. per unit/period | 3 | Production and accounts | v1 |
| uc | ucs + delta·kappa | w.u./unit | 3 | Production and accounts | v1 |
| revenue† | price·sales | w.u. | 3 | Production and accounts | v1 |
| op\_cost† | wages and materials, premium above q̄\_i included | w.u. | 3 | Production and accounts | v1 |
| depreciation† | delta·kappa·q̄ summed over plants | w.u. | 3 | Production and accounts | v1 |
| interest† | rho·B\_i,t−1 | w.u. | 3 | Production and accounts | v1 |
| profit | Π\_i, after depreciation and interest | w.u. | 3 | Production and accounts | v1 |
| dividends† | d·max(0, Π\_i) | w.u. | 3 | Production and accounts | v1 |
| r\_avg† | profit / k\_cost: the average rate over plants | per period | 3 | Production and accounts | v1 |
| r\_newest† | (price − uc\_v) / kappa\_v of the firm's newest plant | per period | 3 | Production and accounts | v1 |
| cap\_retired† | capacity retired | units/period | 4 | Scrapping | v1 |
| write\_off† | book value lost by early retirement (passage en perte) | w.u. | 4 | Scrapping | v1 |
| exp\_sales† | expected sales | units/period | 5 | Investment | v1 |
| cap\_desired† | desired capacity q̄^d\_i | units/period | 5 | Investment | v1 |
| cap\_ordered† | new capacity I\_i,t, replacements included | units/period | 5 | Investment | v1 |
| cap\_replace† | part of cap\_ordered replacing retired plants | units/period | 5 | Investment, Scrapping | v1 |
| tech\_new† | technique j\* of the plants ordered | id | 5 | Investment | v1 |
| tech\_other† | technique the other rule would pick at the same price | id | 5 | Investment | v1 |
| r\_best† | best profit rate on offer at the evaluation price (h of Okishio firms) | per period | 5 | Investment | v1 |
| invest\_spend† | kappa\_j\*·cap\_ordered | w.u. | 5 | Investment | v1 |
| borrow† | new debt ΔB\_i,t | w.u. | 5 | Investment | v1 |
| cash | M\_i at the end of the period | w.u. | 5 | Production and accounts, Investment | v1 |
| debt | B\_i at the end of the period | w.u. | 5 | Production and accounts, Investment | v1 |
| k\_book† | book value K^b\_i of plants, historical cost | w.u. | 4 | Production and accounts, Scrapping | v1 |
| k\_cost† | plants at purchase cost, sum of kappa\_v·q̄\_v | w.u. | 4 | Production and accounts | v1 |
| net\_worth | NW\_i = cash + k\_book − debt (valeur nette) | w.u. | 5 | Production and accounts | v1 |
| exited†, exit\_cause† | left at step 6, and why | bool, text | 6 | Entry and exit | v1 |
| r\_avg\_repl† | r\_avg with plants at replacement cost | per period | 3 | Production and accounts | later: equal to r\_avg while the price of capital goods in wage units is constant |

### 3.5 Plant per period: `plants`, one row per t and plant

With one plant per firm in v1 this is one row per firm, but it is kept: the floor, merit order and capacity checks read it, and vintages need no new code in the collector.

| Python name | Meaning | Unit | Step | Mechanism | Phase |
| --- | --- | --- | --- | --- | --- |
| t, plant\_id†, firm\_id† | period, plant, owner | — | — | collector | v1 |
| tech† | technique (C, D1, D2, or a draw id) | id | at order | Investment | v1 |
| vintage† | period the plant arrived (millésime) | period | at arrival | Investment | v1 |
| capacity | normal output q̄\_v | units/period | 3 | Production and accounts | v1 |
| ucs, kappa, uc | ucs\_v, kappa\_v, uc\_v | w.u./unit, w.u. per unit/period | 3 | plant | v1 |
| output† | output in merit order | units/period | 3 | Production and accounts | v1 |
| running† | ran this period | bool | 3 | Production and accounts | v1 |
| r\_plant† | (price − uc\_v) / kappa\_v at normal output | per period | 3 | Production and accounts | v1 |
| k\_book† | book value | w.u. | 4 | Production and accounts | v1 |
| below\_cost† | consecutive periods with price below ucs\_v | periods | 4 | Scrapping | v1 |
| retired†, retire\_cause† | left at step 4: age, obsolescence, replacement or exit | bool, text | 4 | Scrapping | v1 |
| age† | t − vintage | periods | — | computed | later (vintages) |

### 3.6 Event logs: `events`, one row per event

Columns: t, step, event, firm\_id, plant\_id, group, hurdle, tech, other\_tech, capacity, value, cause, other\_id. The table says what each event fills in.

| event | Step | Mechanism | Fields | Phase |
| --- | --- | --- | --- | --- |
| entry | 6 | Entry and exit | other\_id = incumbent whose h was copied; cause = inherited or mutated; tech, capacity; value = entry price | v1 |
| exit | 6 | Entry and exit | cause = bankruptcy (faillite), low\_share or non\_renewal; value = net worth; capacity left | v1 |
| default | 6 | Entry and exit | value = unpaid debt lost by the rest of the economy | v1 |
| order | 5 or 6 | Investment, Entry and exit | cause = expansion, replacement or entry; tech; other\_tech; capacity; value = cost | v1 |
| retire | 4 | Scrapping | cause = age, obsolescence, replacement or exit; value = book value written off | v1 |
| war\_start, war\_end | 1 | Pricing | industry episode; other\_id = episode number; value = price\_avg at t − 1 (start) or the minimum reached (end) | v1 |
| cut\_start, cut\_end | 1 | Pricing | one firm entering or leaving cut mode; value = price | v1 |
| draw | 5 | Investment | one innovation draw: tech id; value and capacity hold Δucs and Δkappa; cause = wedge 1, wedge 2 or none | later |
| mutate | 6 | Entry and exit | value = new h; other\_id = parent | later |

### 3.7 Flows and checks: `flows`, one row per t, flow and sector

The transaction-flow matrix each period: flows (sales revenue, wages and materials, interest, dividends, plant purchases, new borrowing, repayment, entrants' capital, default losses) by sector (firms of each group, rest of the economy). The checks run every period inside the collector and their residuals are stored in `industry`; any residual above tolerance raises an error in test runs and is counted in `n_check_fail` in production runs.

| Python name | Check | Tolerance | Phase |
| --- | --- | --- | --- |
| sfc\_resid† | for every firm, cash change = profit + depreciation − dividends − investment spending + new debt, and net-worth change = profit − dividends − write-offs | 1e-9 w.u. (design choice) | v1 |
| tfm\_resid† | every row and column of `flows` sums to zero (Caiani et al. 2016, p. 382, as cited in the briefs) | 1e-9 w.u. | v1 |
| money\_resid† | sum of cash plus roe\_balance minus its value at t = 0 | 1e-9 w.u. | v1 |
| share\_resid† | abs(sum of f\_i − 1) after steps 2 and 6; no f\_i below 0 | 1e-12 | v1 |
| cap\_resid† | capacity identity of §4.2 | 1e-9 units | v1 |
| sales\_resid† | sales\_total + unmet\_total − demand; no firm above u\_max·q̄\_i | 1e-9 units | v1 |
| floor\_viol† | firms with price below p\_floor | 0 | v1 |

## 4. Indicators computed after the run

Indicators are functions of the stored tables, written once in `analysis/indicators.py`† and tested like equations. Below, g is a group (S, O, A or B), i a firm, v a plant, j a technique, t a period, B the burn-in and H the last period. Thresholds and windows are design choices, marked as such.

**4.1 Shares and fitness.** Capacity share and sales share of group g:

```latex
S^{K}_{g,t} = \frac{\sum_{i \in g} \bar q_{i,t}}{\sum_i \bar q_{i,t}}, \qquad
S^{x}_{g,t} = \frac{\sum_{i \in g} x_{i,t}}{\sum_i x_{i,t}}, \qquad
\text{fitness}_g = \frac{1}{W} \sum_{t = H - W + 1}^{H} S^{K}_{g,t}
```

W = 20 periods (design choice). A take-over by g is S^K\_g,t ≥ 0.95 for 10 consecutive periods (design choice); its date is the first of those periods. Across seeds: the share of seeds with a take-over by g, with a Wilson 95 % interval.

**4.2 Decomposition of capacity-share changes.** Capacity moves between t and t + 1 through four flows: O (ordered by incumbents), R (retired), E (entrants) and X (exits). The identity is a check (cap\_resid):

```latex
K_{g,t+1} = K_{g,t} + O_{g,t} - R_{g,t} + E_{g,t} - X_{g,t}
```

The change in g's share splits exactly into four terms, one per flow c, each comparing g's flow with its share of the industry's flow:

```latex
S^{K}_{g,t+1} - S^{K}_{g,t} = \sum_{c \in \{O,\,-R,\,E,\,-X\}} \frac{\Delta^{c} K_{g,t} - S^{K}_{g,t}\, \Delta^{c} K_{t}}{K_{t+1}}
```

Incumbents' net investment is the O and −R terms together. Cumulate each term from B to H for one bar per seed. This is the evolutionary accounting Dosi (2007, p. 182) calls for, as cited in the entry brief.

**4.3 Decomposition of sales-share changes.** With σ the sales share, f the replicator share (step 2) and f^end the share after entry and exit (step 6), summed over the group:

```latex
\sigma_{g,t} - \sigma_{g,t-1} =
\underbrace{f_{g,t} - f^{end}_{g,t-1}}_{\text{price-driven}} +
\underbrace{f^{end}_{g,t-1} - f_{g,t-1}}_{\text{entry and exit}} +
\underbrace{(\sigma_{g,t} - f_{g,t}) - (\sigma_{g,t-1} - f_{g,t-1})}_{\text{capacity rationing}}
```

The price-driven term is Shaikh's channel: customers moving to cheaper firms. The rationing term grows when a cheap firm lacks capacity, which is where the two channels meet (“luring more customers to your door with lower prices is of little benefit unless you can increase your normal level of production”, Shaikh 2016, p. 268, as quoted in the critique).

**4.4 Price dispersion against unit-cost dispersion.** Coefficients of variation across firms, prices weighted by sales and costs by capacity:

```latex
CV^{p}_{t} = \frac{\operatorname{sd}_{x}(p_{i,t})}{\operatorname{mean}_{x}(p_{i,t})}, \qquad
CV^{uc}_{t} = \frac{\operatorname{sd}_{\bar q}(uc_{i,t})}{\operatorname{mean}_{\bar q}(uc_{i,t})}, \qquad
\text{lcp\_ratio}_t = \frac{CV^{p}_{t}}{CV^{uc}_{t}}
```

The law of correlated prices predicts lcp\_ratio below 1 and a positive correlation between p\_i and uc\_i. Undefined when all firms share one technique.

**4.5 Margins.** Margin m\_i = p\_i − uc\_i. Each period, the cross-firm OLS slope of m\_i on uc\_i: near −1 if followers' margins are residuals (row 4). The markup p\_i / ucs\_i is kept for §8 question 5 of the critique (later). Leverage is debt / (cash + k\_book), by firm and group, read beside exit causes for the critique's §8 question 6.

**4.6 Three profit rates.** The average rate r\_avg and the newest-plant rate r\_newest are stored. The incremental profit rate (taux de profit incrémental) follows Shaikh (2016, eq. 7.7, p. 300), gross operating surplus over last period's gross investment, by group and for the industry:

```latex
r^{I}_{g,t} = \frac{GOS_{g,t} - GOS_{g,t-1}}{I_{g,t-1}}, \qquad GOS_{g,t} = \sum_{i \in g} (p_{i,t} - ucs_{i,t})\, x_{i,t}, \qquad I_{g,t} = \text{invest\_spend}_{g,t}
```

A net variant replaces GOS with profit. Report 10-period moving averages (design choice): the ratio is noisy when investment is small. Comparing r^I with the capacity-weighted r\_newest answers the critique's §8 question 12 as a by-product.

**4.7 Price relative to the wage.** With w = 1, price\_avg is already the product price in wage units. Report P\_t = price\_avg\_t / price\_avg\_B and the long run as its mean over the last W periods. For H1, the exact test is on adoptions: the price of production uc\_j + rbar·kappa\_j of each technique adopted never rises from one adoption to the next in HOM-O.

**4.8 Concentration.** Herfindahl index (indice de Herfindahl) on sales shares, HHI\_t = sum of σ\_i,t squared, and its numbers equivalent 1 / HHI\_t, beside n\_firms.

**4.9 Price wars (guerres des prix).** An episode is a maximal run of periods with war\_on true (design choice: one firm cutting is enough). Per run: episodes per 100 periods; length L in periods; depth and recovery:

```latex
\text{depth} = \frac{p_{s-1} - \min_{s \le t \le e} p_t}{p_{s-1}}, \qquad \text{recovery} = \min\{\tau \ge 0 : p_{e+\tau} \ge 0.99\, p_{s-1}\}
```

with p = price\_avg, s and e the first and last period of the episode, and 0.99 a design choice. An episode still running at H is censored and flagged.

**4.10 Diffusion curves (courbes de diffusion).** Capacity share of technique j, S^K\_j,t, from `plants`. Dates at which it first reaches 10, 50 and 90 % (design choice), and the 10–90 duration.

**4.11 Vintage spread.** V\_t = max over running plants of ucs\_v / min over running plants of ucs\_v. If ucs is wages only, V\_t is the ratio of best to worst labour productivity, comparable with Salter's 3.5 (SF6). With it, the age distribution of running plants, weighted by capacity. Later, with vintages.

**4.12 Distribution of h.** Capacity-weighted histogram and mean of hurdle at chosen dates; across cells, mean h at H against episodes per 100 periods (H5). Later.

**4.13 Leader and ranking.** Share of periods with leader\_id equal to lowest\_uc\_id (row 3). Mean r\_newest by technique, separately for periods with war\_on true and false (row 5).

**4.14 Demography.** Entries and exits per period and their correlation; share of entrants that exit within T periods (infant mortality, T the plant life); exit causes by group; entries regressed on r\_new − rbar (SF9).

**4.15 Conflict share.** Share of order events with tech different from other\_tech: how often the two rules actually disagreed. With random menus, the share of draws in each wedge (critique §2), from the draw events.

**4.16 Selection slope.** Pooled OLS of share growth on relative price, which should recover χ (demand brief, test 3):

```latex
\frac{f_{i,t} - f^{end}_{i,t-1}}{f^{end}_{i,t-1}} = a + b\, \frac{E_{i,t} - \bar E_{t}}{\bar E_{t}} + \varepsilon_{i,t}, \qquad E_{i,t} = 1 / p_{i,t}
```

**4.17 Later.** Cross-section of firm profit rates (tent shape), firm-size and growth-rate distributions across seeds, and the period of endogenous price cycles from the autocorrelation of price\_avg.

## 5. Run design

Three stages: a debugging run for 6 November, 800 runs for 20 November, and the full grid with 200 seeds for 1 December. All values below are design choices unless a source is named.

| Item | 6 Nov lab | 20 Nov seminar | 1 Dec report |
| --- | --- | --- | --- |
| Period | one year, so that delta = 10 % gives a plant life of T = 10 | same | same |
| Burn-in B (période de chauffe) | 20 | 50 (five plant lives) | 50 |
| Horizon after burn-in | 80 | 300 (30 plant lives; about 8 share doublings at χ = 1, from the demand brief's 35 periods) | 300 |
| Seeds per cell | 5 | 50: detects a 20-point take-over gap (critique §6) | 200: detects 10 points at 5 % and 80 % power (critique §6) |
| Cells | BASE | BASE, WAR+, CHI−, CRED: one treatment at a time | 2×2×2 factorial of war frequency, selection intensity χ and finance |
| Populations | MIX, HOM-S, HOM-O, NEU on Shaikh's three plants | MIX, HOM-S, HOM-O, NEU | all seven: MIX, HOM-S, HOM-O, INV-O→S, INV-S→O, NEU, SWP |
| Runs | 20 | 4 × 4 × 50 = 800 | 8 × 7 × 200 = 11,200 |
| Tables kept | all, every seed | all, every seed | runs, industry, groups, events, flows for every seed; firms and plants for seeds 0–9 |

**Burn-in.** During burn-in every firm uses the rule-neutral menu (techniques lowering both unit cost and capital per unit, so both rules agree: critique §5) and labels are assigned at t = B. The spread of vintages then forms before the contest starts, and no rule profits from the initial conditions. Indicators start at B; tables start at 0.

**Treatment levels.** Three treatments at most before 20 November (critique §6): war frequency (the utilisation trigger u\_war, or demand volatility sigma), χ, and finance (internal only, or credit capped relative to sales). Each has two levels, to be fixed after the lab from the 6 November runs: WAR+ is the level at which wars occur several times as often as in BASE, CHI− a χ at which shares respond slowly. No value is proposed here, so none is invented. The innovation set (Shaikh's menu, then neutral and skewed draws) comes after 1 December, with the headline phase diagram.

**Seeds.** Seeds 0 to 199 in every cell and population (common random numbers, nombres aléatoires communs). Each mechanism draws from its own stream, spawned from the seed with `numpy.random.SeedSequence(seed).spawn(n)`, plus one stream for the initial assignment of labels. A change in one mechanism then leaves the other mechanisms' draws unchanged, which is the point of fixed seeds in the course (Funalot, session 2, slide 24).

**Storage.** One tidy long table per level and run, under `outputs/<experiment>/<cell>/<run_id>/`: runs, industry, groups, firms, plants, events and flows, each with run\_id as its first column, so that concatenating runs is one `pandas.concat`. CSV as in the course template for the lab; Parquet (pyarrow) for the grid. Floats stored as float32, except cash, debt, net worth and the check residuals, kept in float64.

**Data size.** Rows times columns times 8 bytes, assuming 20 firms alive on average over 350 periods (design assumption: the test industry starts with 3 firms, the cement market of the critique has 15 to 30 kilns):

| Table | Rows per run | Columns | Per run, uncompressed |
| --- | --- | --- | --- |
| firms | 7,000 | 45 | 2.5 MB |
| plants, one plant per firm | 7,000 | 16 | 0.9 MB |
| plants, 10 vintages per firm (later) | 70,000 | 16 | 9.0 MB |
| industry, groups, events, flows | about 5,000 | 12–30 | 0.4 MB |

About 4 MB per run in v1, so 3 GB for the 800 runs of 20 November. Keeping firm and plant tables for every seed of the 1 December grid would take about 130 GB with vintages; keeping them for 10 seeds per cell brings the total to about 10 GB. Parquet compression shrinks these further; by how much is to be measured on the lab runs.

## 6. Plot catalogue

Sixteen result figures and six diagnostics, all drawn by `plot_outputs.py` from the stored tables, never from model objects. Bands are across seeds; the burn-in is shaded grey on every time axis.

| ID | Answers | Type | Axes | Grouping | Aggregation | Runs | Phase |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F1 | Q1, E1 | line with band | period; capacity share of S | panel per cell; MIX and NEU overlaid | median, 10–90 % band | MIX, NEU, all cells | v1 |
| F2 | Q1, NC | dot with 95 % interval | cell; share of seeds where S takes over | MIX against the NEU line at the starting share | share of seeds (Wilson interval) | MIX, NEU | v1 |
| F3 | Q2, Q3, H3 | heatmap | war frequency level; χ level; colour = median fitness of S | panel per finance level | median over seeds | MIX, grid | 1 Dec |
| F4 | E4 | signed bars about zero | cell; cumulated change in S's share, one bar per term of §4.2, then of §4.3 | term | mean over seeds, 95 % interval | MIX | v1 |
| F5 | H1, H2, E3, SF8 | line with band | period; price relative to its value at B | HOM-S, HOM-O | median, 10–90 % band | HOM, BASE | v1 |
| F6 | H4 | event-study line with band | periods since D2 first holds 10 % of capacity; price\_avg relative to the period before | reference lines at 1 and 1.0026 | median, 10–90 % band | HOM-S, MIX, BASE | v1 |
| F7 | E2 | line with band | period; invader's capacity share | direction; 5 % NEU group as reference | median, 10–90 % band | INV, NEU | 1 Dec |
| F8 | SF1, SF3 | scatter | CV of unit costs; CV of prices; 45° line | population | one point per run and period after B | MIX, HOM, BASE | v1 |
| F9 | Q2 | histograms | length and depth of episodes; episodes per 100 periods | cell | pooled over seeds | MIX, BASE and WAR+ | v1 |
| F10 | SF7 | line | period; capacity share of each technique | technique; panel per population | median | HOM-S, HOM-O, MIX | v1 |
| F11 | SF10 | line | period; r\_avg, r\_newest and r^I (10-period average); rbar as a line | rate; group | one seed, then median band | MIX, HOM | v1 |
| F12 | SF2, SF4 | dot plot | technique; mean r\_newest inside and outside wars | war\_on | mean over seeds | MIX, BASE and WAR+ | v1 |
| F13 | SF5, SF6 | line with band | period; vintage spread V\_t, CV of margins and of r\_avg | Salter's 3.5 as reference | median, 10–90 % band | HOM, MIX with draws | later |
| F14 | H5 | ridgeline of histograms; scatter | date; h. Then mean h against episodes per 100 periods | cell | capacity-weighted | MIX with mutating h | later |
| F15 | SF8, SF9 | lines and bars | period; n\_firms and 1/HHI; entries and exits per period | — | median band; sums | MIX | v1 |
| F16 | §4.15 | histogram | conflict share per run; share of draws in each wedge | menu | per run | random menus | later |
| D1 | stock-flow consistency | strip plot, log scale | run; max over periods of sfc\_resid, tfm\_resid, money\_resid; tolerance line | check | max per run | all | v1 |
| D2 | shares sum to one | strip plot, log scale | run; max share\_resid | step 2, step 6 | max per run | all | v1 |
| D3 | no price below the floor | line | period; min over firms of price − p\_floor; floor\_viol count | run | min per period | all | v1 |
| D4 | capacity accounting | strip plot | run; max abs cap\_resid | — | max per run | all | v1 |
| D5 | demand accounting | strip plot | run; max abs sales\_resid; max util against u\_max | — | max per run | all | v1 |
| D6 | computing budget | histogram | wall\_seconds per run | population | — | all | v1 |

### Key figures: what the reader should see

**F1, capacity share of S over time.** The answer to the question at a glance. In each cell the MIX band either leaves the NEU band, upward (unit-cost rule selected) or downward (profit-rate rule), or stays inside it. Look at when it leaves, not only where it ends: a split after a few price wars points to the price channel.

**F2, take-over frequency against neutral drift.** The test in numbers. NEU sits on its starting share; a MIX dot whose interval clears that line is a result, one that overlaps it is not.

**F3, the selection map.** H3 in one picture: the share of S should rise toward the corner of strong selection and frequent wars, and fall toward weak selection and internal finance. A uniform map means the environment does not matter.

**F4, the decomposition.** Why S gains or loses. If S's gains come from the price-driven and rationing terms and O's from net investment, the two selection channels of the critique §3 are both at work and pull opposite ways.

**F5, the price path relative to the wage.** The aggregate signature. HOM-O must never drift up (H1 is a theorem, so a rise is a bug). HOM-S may drift up only with capital-using draws (H2).

**F6, the price signature of D2.** A dip during the war, then a level just above the start, near 100.26 for 100. A return to 100 or lower contradicts H4; a level near 100.26 matches the critique's arithmetic on Shaikh's numbers.

**F8, prices against costs.** Points below the 45° line: prices less dispersed than costs, the law of correlated prices. Points on the line would mean each firm prices off its own cost, with no competition between them.

**F11, three profit rates.** r^I should wander around rbar while r\_avg of the two groups stays apart: turbulent equalisation on new capital, not on the average. If r\_newest and r^I diverge, Shaikh's empirical proxy misleads in this model.

## 7. Neutrality checks

The only legitimate difference between the two groups is the hurdle used at step 5 (technique, replacement, entrant's plant). Each check below would expose a bias built in elsewhere, and all of them must pass before a mixed run is read.

| Check | Runs | Output | Passes if | Phase |
| --- | --- | --- | --- | --- |
| Swapped labels | SWP: firms labelled S apply the Okishio rule and the reverse, same seeds as MIX | all tables, by rule and by label | Results by rule are identical to MIX, row for row; results by label are mirrored. Any difference means the code reads the label somewhere | v1 |
| Neutral control | NEU: two labels, one rule (each rule in turn), 50/50 and 95/5 | take-over share, capacity share | Take-over share equals the starting share within its Wilson interval, in every cell | v1 |
| Identical firms | all firms identical in technique, size and cash; demand at normal capacity | price, share | Prices stay at the anchor and shares do not move (pricing brief test 2, demand brief test 2) | v1 |
| Rule-neutral menu | MIX with the rule\_neutral menu only | tech\_new, tech\_other, capacity share | tech\_new equals tech\_other in every order, and MIX behaves like NEU | v1 |
| Firm order | MIX with firm ids and loop order shuffled, same seed otherwise | capacity share | Same distribution across seeds: no advantage from being processed first or winning ties | v1 |
| Same rules elsewhere | MIX | firm-period regressions of price, share change, cap\_desired and borrow on their inputs plus a group dummy | Dummy coefficients indistinguishable from zero; with equal sales, equal investment (investment brief test 5) | v1 |
| Entry inherits by share | MIX | events (entry) against groups.share\_end | Entrants' rules match incumbents' shares, up to the mutation rate (entry brief test 3) | v1 |
| Start values | MIX at t = B | groups: capacity, cash, debt, net worth | Equal across groups at the start of the contest | v1 |
| Price anchor | MIX under target\_return and markup anchors | fitness | The verdict is reported for both anchors; if it flips, the anchor decides it (pricing brief) | 1 Dec |

Weak selection deserves its own report (demand brief): a verdict that holds only at high χ is a result about χ, not about the rules.

## 8. Open questions for the group

Each question states the assumption this brief makes until the group decides.

1. **One plant per firm, or vintages?** Assumed: one plant per firm in v1 (critique §4), with the plants table written anyway. Vintages make SF5, SF6 and F13 measurable.
2. **Who owns the collector and the analysis code?** Not assumed. It touches every mechanism, so whoever takes production and accounts is a natural owner.
3. **Which names?** Every name marked † is a proposal; the notation table should absorb the ones the group keeps, so that the code, the LaTeX document and this brief agree.
4. **What counts as an industry price war?** Assumed: at least one firm in cut mode. The alternative is a sales-weighted share of firms cutting above a threshold, which ignores a small firm's private war.
5. **Take-over and windows.** Assumed: 95 % of capacity for 10 periods; fitness averaged over the last 20 periods; diffusion dates at 10, 50 and 90 %; recovery at 99 % of the pre-war price.
6. **Burn-in.** Assumed: a rule-neutral menu during burn-in, labels assigned at t = B. Alternative: rules active from t = 0, with the first B periods discarded.
7. **At which price do Okishio firms evaluate?** The investment brief leaves it open; the collector stores the choice (okishio\_price) and r\_best, but F12 and the conflict share depend on it. So does H1's exact test: a technique that earns more at the current price lowers the price of production only if that price is the one at which the incumbent earns rbar; at another price two rankings can cross (critique §2).
8. **Pending orders of a firm that exits.** Are its plants cancelled, sold to the rest of the economy, or delivered to nobody? The capacity and money identities need one answer.
9. **Incremental rate, gross or net?** Assumed: gross operating surplus over gross investment as in Shaikh's eq. 7.7, with the net variant beside it.
10. **Replacement cost.** Assumed: identical to historical cost while the price of capital goods in wage units is constant, so r\_avg\_repl waits. If that price gets a path (critique §3), it becomes v1.
11. **Treatment levels.** No values proposed: the two levels of war frequency, χ and credit should come from the 6 November runs.
12. **Computing budget.** 11,200 runs of 350 periods: wall\_seconds from the lab tells us whether 200 seeds per cell fit before 1 December, or whether the grid must shrink.

## Sources

Every data target was read in the PDF on 3 November, at the page given; all four sources are in Ugo's own Zotero library (perso). Other citations come from the two design docs, whose references were checked in Zotero when they were written.

Read in the PDF for this brief:

- Shaikh, A. (2016). *Capitalism: Competition, Conflict, Crises*. Oxford University Press. Table 7.3, p. 271; the entry quotation, p. 283; Table 7.9, p. 295; eq. 7.7, p. 300.
- Salter, W. E. G. (1966). *Productivity and Technical Change*, 2nd ed. Cambridge University Press. Highest to lowest output per man-hour, cement 3.5, p. 96, from the table of 60 US plants in 1935, p. 95.
- Macher, J. T., Miller, N. H. & Osborne, M. (2021). “Finding Mr. Schumpeter: technology adoption in the cement industry.” *RAND Journal of Economics*, 52(1). [doi:10.1111/1756-2171.12362](https://doi.org/10.1111/1756-2171.12362). Table 1, p. 81; 74 % of capacity, p. 82.
- Miller, N., Osborne, M., Sheu, G. & Sileo, G. (2022). “Technology and market power: the United States cement industry, 1974–2019.” Working paper. [doi:10.2139/ssrn.4041168](https://doi.org/10.2139/ssrn.4041168). Plants 163 to 89, p. 8; real price, p. 9.

Cited through the design docs: Caiani et al. (2016), Dosi (2007), Park (2001) and Shaikh (2016, pp. 268 and 316), all in perso.

Not in Zotero perso:

- Bryce, D. J. & Dyer, J. H. (2007), quoted second-hand through Shaikh (2016, p. 283). To add in perso if cited directly; no DOI was looked up.
- Funalot, P. (2026), slides of session 2 (slide 24, fixed seeds): in the Inbox only (N7P9IPK2), not yet in perso.

Design documents: [ABM mechanism briefs](https://claude.ai/artifact/78MNTrWH1CACVixxqWBcRx) (16 October); [Real competition ABM — critique of the proposal](https://claude.ai/artifact/KVZ6AmcvynpoUMJw2rpgBm) (17 October); course template [pierrefunalot/EPOG\_MIF\_SIMPLE\_ABM](https://github.com/pierrefunalot/EPOG_MIF_SIMPLE_ABM) (`model/collector.py`, `model/scheduler.py`, `parameters.py`, `plot_outputs.py`); Ugo's notes on session 2 (2 October).
