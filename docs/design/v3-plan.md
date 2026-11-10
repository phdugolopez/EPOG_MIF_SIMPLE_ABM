# Version 3 plan: files, interfaces, tests and build order

Plan of 10 November 2026. It replaces the plan of 9 November (commit `e01733d`): the specification
was revised after the v2 pilot, and Ugo answered the first plan's questions. Written from
`final-model-proposal.md` (sections "The simplified model", "What to drop", "Model analysis",
"Sensitivity analysis", "Decisions"), the addendum A1–A13 of `v3-planning-prompt.md`,
`v3-choices.md` and the v2 files the prompt lists. It contains no model code.

**Order of authority.** A row of `v3-choices.md` wins over the addendum, and the addendum over the
proposal. Two rows change the addendum: the entrant chooses on the public menu only (A9 said every
technique in use), and initial cash is the depreciation already accumulated on the initial plants
(A2 said 0).

**What changed since 9 November.**

- **Replacement condition (A7, A13 j).** The depreciation reserve of a plant that leaves joins the
  investible funds only if r_new ≥ r̄ in that period; otherwise the firm pays it to the rest of the
  economy. r_new is therefore computed before scrapping, once a period, and step 4 gains one
  equation and two output columns.
- **Ties (A11).** An exact tie at one half is counted apart: the run row has an `outcome`, and the
  share won is wins over wins plus losses.
- **Initial cash (A13 k).** Each initial firm starts with the depreciation accumulated on its
  plants, so the reserves these plants release are backed by cash.
- **Line count (Q1).** Lines are counted without blank lines, with a tolerance of 10 %. The budgets
  were redone on that count: 693 against a target of 700 and a limit of 770.
- **Pilot.** Its numbers are the reference for E1 and for eight cells of E4 (section 7).

**Status.** Every question of section 10 has Ugo's answer, recorded in `v3-choices.md` on 10
November; the group still confirms them. The five points explained a second time (Q2, Q9, Q12,
Q13, A13 d) were confirmed as proposed, and so were the three new ones: the reserve condition
also holds under the accelerator (Q17), the operating-cost test is kept although the idle test
implies it in v3 (Q18, A13 l), and the pilot numbers are a reference, not a gate (Q19).

## Conventions used below

| Symbol in the proposal or addendum | Name in the code | Note (A13 h) |
| --- | --- | --- |
| R, lowest price posted last period (A5) | `low_price`, `low_rival` | never `R` |
| R, regulating technique (A8) | `industry.reg`, `industry.reg_price` | `reg_price` = uc_reg + r̄κ_reg |
| k, firms per (technique, rule) pair (A2) | `firms_per_pair` | |
| k, plant index (A3) | `i` | |
| k = β e^{σz}, the bias drawn (proposal) | `bias_draw` | |
| a, A | `cut_share`, `design_step` | the operating-cost cut drawn and its maximum |
| c | `price_cut` | |
| λ, r̄, δ, T, S | `lam`, `rbar`, `delta`, `plant_life`, `plant_size` | `delta` = 1 / `plant_life` |
| χ, d, θ, μ, π, β, σ, L, u*, g | `chi`, `payout`, `entry_speed`, `mutation`, `draw_prob`, `bias`, `bias_spread`, `public_lag`, `u_target`, `growth` | |

- **Labels and rules.** A firm has a label, `"shaikh"` or `"okishio"` (v2's names), and a rule,
  `"unit_cost"` or `"profit_rate"`. The rule is looked up from the label once, when the firm is
  created (`rule_shaikh`, `rule_okishio` in `parameters.py`). "The unit-cost label" of the
  proposal is `"shaikh"` in every population, the controls included.
- **Sums.** Every sum over firms or plants uses `math.fsum`, which is exactly rounded, so that no
  total depends on the order of a list. The permutation test of section 8 relies on it.
- **Random numbers.** Industry stream: `default_rng(SeedSequence(seed, spawn_key=(0,)))`. Firm
  stream: `default_rng(SeedSequence(seed, spawn_key=(1, firm.id)))`, keyed by the firm's serial
  number and not by its place in the list. Each firm takes four uniforms and one normal from its
  stream in every period, and the industry three uniforms, used or not (Q9).
- **Lines.** Counted without blank lines; comments and docstrings count (Q1). Target 700, limit
  770.

## 1. File tree

Model code: 693 lines without blank lines, as point estimates, against a target of 700 and a limit
of 770. `tests/test_budget.py` enforces the limit and prints the count.

```text
parameters.py                           60  every parameter, constant and switch (section 5)
run.py                                  14  one run at the defaults -> outputs/periods.csv, outputs/run.csv

equations/                             172  26 files, pure functions: no state, no random draw
  common_unit_cost.py                    3  uc = ucs + delta kappa
  common_profit_rate.py                  3  profit rate of a technique at a price
  common_hurdle.py                      10  evaluation price p^e and hurdle h: the one rule that differs
  common_technique_choice.py             7  cost of a technique at h, and the argmin j*
  common_regulating_price.py             8  regulating technique and price of production
  setup_initial_plants.py                5  number of plants and staggered ages of an initial firm (A2, A3)
  pricing_rule.py                       20  shortage step, undercut, follow (A5)
  pricing_floor.py                       3  unit cost of the firm's best plant in operation
  demand_replicator.py                  10  competitiveness E = 1/p and replicator shares
  accounts_merit_order.py                7  plants run cheapest first, then youngest
  accounts_depreciation.py               3  straight-line by time
  accounts_dividends.py                  3  d x max(0, profit)
  scrapping_below_cost.py                6  scrap cost and periods with the price below it
  scrapping_idle_plants.py               3  periods without output
  scrapping_retirement.py                9  age T, below cost, idle
  scrapping_reserve.py                   3  is the depreciation reserve released: r_new >= rbar (A7)
  investment_draw_marx.py                7  Marx-biased design (the model)
  investment_draw_neutral.py             7  neutral set (control)
  investment_draw_categories.py         12  categories rule (robustness)
  investment_retained_earnings.py        5  plants that the funds pay for
  investment_accelerator.py              5  plants missing to reach desired capacity
  entry_probability.py                   5  Pr(entry)
  entry_new_plant_rate.py                6  r_new
  entry_inherited_rule.py                8  label copied by share, flipped with probability mu
  entry_size.py                          4  entrant's number of plants
  entry_exit_rule.py                    10  who leaves, with the floor of 2 firms

markets/                                80  the transactions: they move cash, plants and firms
  payments.py                            5  pay(): the only place cash moves
  goods_market.py                       12  allocate(): sales, one re-allocation, lost demand (A6)
  plant_market.py                       25  buy_plant(), remove_plant(): order, reserve released or withdrawn
  entry_exit.py                         38  create_entrant(), remove_firm() (A10)

model/                                 367
  entities.py                           80  Technique, Plant, Firm, Account, Industry (section 2); new_firm()
  model.py                              40  build(): initial population and cash; run()
  scheduler.py                         185  period(), start_period(), the six step functions, check()
  outputs.py                            62  the period table: count(), record_production(), record_end()

tests/                               ~ 700  unittest, one file per step (section 8)
  helpers.py  test_common.py  test_setup.py  test_pricing.py  test_demand.py  test_accounts.py
  test_scrapping.py  test_investment.py  test_entry.py  test_neutrality.py  test_model.py
  test_budget.py  test_experiments.py

experiments/                         ~ 515  (section 7)
  cells.py                             100  E0-E6 and the robustness checks as {cell: overrides}
  populations.py                        25  start lists: homogeneous, invasion
  summary.py                            90  the run row: outcome, takeover, decomposition, mechanism, Marx bias
  stats.py                              30  wilson(), beyond_drift()
  harness.py                           160  tasks, pool, runs.csv, cells.csv, resume, command line
  morris.py                             70  SALib design, runs through the harness, mu* and sigma
  e5_channels.py                        40  within-cell regression of the profit-rate gap
  diagnosis.py                         150  throwaway: variants patched from outside (section 9)

figures/                             ~ 330  one script per report exhibit
  style.py  fig1_conflict_zone.py  fig2_typical_run.py  fig3_bias_lambda.py  fig4_heatmaps.py
  fig5_decomposition.py  fig6_morris.py  tab3_robustness.py

CLAUDE.md  README.md  requirements.txt  .github/workflows/build.yml      rewritten in stage 1
```

`equations/`, `markets/`, `model/`, `experiments/` and `figures/` each get an empty
`__init__.py`. The step functions live in `model/scheduler.py` and are named after their step
(`set_prices`, `allocate_demand`, `produce_and_account`, `scrap_plants`, `invest`,
`enter_and_exit`); `markets/` holds what they call to move cash, plants or firms, as in v2.

Two remarks on the count:

- The run row is a function of the period table alone and lives in `experiments/summary.py`,
  which `run.py` calls. In `model/outputs.py` it would bring the model code to about 780.
- The first plan's budgets were tight even by `wc -l`. These are redone file by file on the new
  count and include the reserve rule; real code can land 10 % either side.
- **After stage 3** the whole model is written and counts 762 lines: above the target, inside
  the limit, after its docstrings were shortened (it stood at 784). The budgets of this section
  were about 10 % too low, mostly in `scheduler.py` (203 against 185), `outputs.py` and
  `markets/entry_exit.py`. **After stage 4** it counts 769 lines, with the speed remedy of
  section 9 in: any further line has to replace one.

## 2. Data structures

`model/entities.py`. State keeps v2's names (`price`, `share`, `sales`, `capacity`, `util`,
`kappa`, `hurdle`, `cash`, `pending_plants`, `book_value`, `write_offs`, `known`, `roe`, `born`).
All five are `@dataclass(eq=False)`: an object is compared by identity.

```python
class Technique:
    name: str                  # "C", "D1", "D2"; a design gets a serial name, never read by a rule
    ucs: float                 # operating cost per unit of normal output (wage = 1)
    kappa: float               # capital per unit of normal output (capital goods priced 1)
    first_run: int | None      # period its first plant produced; public from first_run + public_lag

class Plant:
    technique: Technique
    capacity: float            # normal output a period: plant_size
    cost: float                # purchase cost, kappa x plant_size, paid when ordered
    book_value: float          # cost less straight-line depreciation; 0 at age T
    age: int = 0               # periods in operation
    output: float = 0.0        # this period
    profit: float = 0.0        # this period, after depreciation (read by r_new)
    below_cost: int = 0        # consecutive periods with the owner's price below the scrap cost
    idle: int = 0              # consecutive periods without output

class Firm:
    id: int                    # serial number: keys the random stream, never breaks a tie
    label: str                 # "shaikh" | "okishio"
    rule: str                  # "unit_cost" | "profit_rate", from the label, at creation
    rng: numpy.random.Generator
    born: int
    price: float               # posted this period (last period's until step 1)
    share: float               # notional replicator share f (A6)
    sales: float = 0.0
    notional: float = 0.0      # share x D_t
    util: float = 1.0          # sales / capacity of the last period it produced
    hurdle: float = 0.0        # h of its last investment step
    cash: float = 0.0          # money; moves only through pay()
    funds: float = 0.0         # investible funds F (A7)
    profit: float = 0.0        # after depreciation
    write_offs: float = 0.0
    cut: bool = False          # undercut at step 1
    active: bool = False       # had a plant in operation at step 3 of this period (Q9)
    plants: list[Plant]        # in operation
    pending_plants: list[Plant]   # ordered, produce from next period
    known: list[Technique]     # its own designs that are not public
    capacity                   # property: fsum of plant.capacity over `plants`

class Account:
    cash: float = 0.0          # the rest of the economy

class Industry:
    params: Parameters
    seed: int
    rng: numpy.random.Generator   # entry and inheritance
    time: int = 0
    firms: list[Firm]          # in order of creation
    roe: Account
    public: list[Technique]    # the public menu
    waiting: list[Technique]   # built, not yet public
    demand_0: float
    demand: float              # D_t
    lost: float                # demand left unserved this period
    excess: float              # (D - K) / D if positive: next period's shortage signal
    reg: Technique | None      # regulating technique (A8)
    reg_price: float           # uc_reg + rbar kappa_reg
    r_new: float | None        # set in step 3, read in steps 4 and 6
    next_id: int
    tally: dict                # this period's flows by label, for the output table only
    rows: list[dict]           # the period table
```

A technique is "known" to a firm if it is in `industry.public` or in `firm.known`.

`new_firm(industry, label, price, share)` creates a firm with the rule of its label and its own
stream, and adds it to the industry. It is in `entities.py` and not in `model.py`, which imports
the scheduler: `markets/entry_exit.py` can then create an entrant without a circular import.

**Three accounts, one identity.** `cash` is money. `profit` is sales less operating cost less
depreciation. `funds` is what the retained-earnings rule may spend: it rises by retained profit
and by a released reserve, and falls by purchases. Depreciation is no payment, so it leaves cash
and lowers profit and funds: for every firm and period

```text
cash - funds  >=  depreciation accumulated on its plants in operation
```

with equality as long as no withdrawal was cut short by a lack of cash. It follows that funds
never exceed cash. `test_accounts.py` asserts it on full runs.

## 3. The period loop

`model/scheduler.py`, `period(industry)`. Every step first reads what it needs from all firms,
then writes: moves are simultaneous and the order of `industry.firms` never matters.

```text
period t

0  start_period
     D_t = D_0 (1 + g)^t
     pending_plants -> plants                        construction lag (A4): ordered in t-1, produce from t
     a technique whose first plant starts now: first_run = t, joins `waiting`
     techniques in `waiting` with first_run + public_lag <= t join `public`              (A9)
     tally reset

1  set_prices                                        pricing (Jake)
     reads   price(t-1) and util(t-1) of every firm, excess(t-1),
             unit cost of every firm's best plant in operation
     rules   price_floor, posted_price
     writes  price, cut

2  allocate_demand                                   demand (Pierre-Loup)
     reads   price(t), share after last period's entry and exit, D_t, plants
     rules   competitiveness, replicator_shares, allocate
     writes  share (notional), notional = share x D_t, sales, industry.lost,
             industry.excess = max(0, D_t - K_t) / D_t, with K_t total normal capacity

3  produce_and_account                               accounts (Vincent)
     reads   sales, plants, price
     rules   dispatch, depreciation, dividends
     writes  plant.output, plant.profit, plant.age + 1, plant.book_value,
             pay: sales (rest of economy -> firm), operating costs and dividends (firm -> rest of economy),
             profit, funds += profit - dividends, util = sales / capacity
     then    industry.reg and reg_price, from the plants in operation in t                 (A8)
             industry.r_new = new_plant_rate() over the plants aged entry_window or less   (A7, A10)
             record_production(): the two rows of t, before any plant or firm leaves

4  scrap_plants                                      scrapping (Vincent)
     reads   price(t), plant.output, plant.age, r_new, cash
     rules   scrap_cost, periods_below_cost, periods_idle, retirement_reason, reserve_released
     writes  plant.below_cost, plant.idle; remove_plant() for each plant that leaves:
             reserve = cost - book_value
             r_new >= rbar, or no plant in its window:  funds += reserve                   (A7)
             r_new <  rbar:  pay min(reserve, cash) (firm -> rest of economy)              (A13 j)
             write_offs += book_value

5  invest                                            investment, technical change included (Ugo)
     reads   price(t), reg_price, public, known, funds, cash, notional, capacity; the firm's stream
     for every firm:
       four uniforms and one normal from its stream                                        (Q9)
       menu = public + known
       p_e  = (1 - lam) price + lam reg_price                                              (A8)
       h    = hurdle(rule, p_e, menu)
       if it had a plant in operation in t, tech_change is not "none" and u < draw_prob:
           o = choose_technique(menu, h);  n = a design drawn from o
           if technique_cost(n, h) < technique_cost(o, h):  n joins known and menu        ties keep o
       firm.hurdle = hurdle(rule, p_e, menu);  j* = choose_technique(menu, firm.hurdle)
       plants:  retained      floor(min(funds, cash) / (kappa* S))
                accelerator   min(ceil((notional / u* - capacity - on order) / S), floor(cash / (kappa* S)))
       buy_plant() for each: pay kappa* S (firm -> rest of economy), funds -= kappa* S,
                             the plant joins pending_plants

6  enter_and_exit                                    entry and exit (Pierre-Loup)
     reads   share, capacity and plants on order, r_new (of step 3), prices, public, reg_price;
             the industry's stream: three uniforms                                         (Q9)
     exit    leaving(); remove_firm(): cash -> rest of economy, plants written off,
             the survivors' shares rescaled to sum to 1
     entry   with probability entry_probability(r_new): create_entrant() among the survivors:
             label = inherited_label(), rule from the label; price = lowest posted price;
             h at that price (A8); j* on the public menu (A13 a); plants = entrant_plants(),
             paid by equity from the rest of the economy, arriving in t+1;
             share = its capacity / (survivors' next-period capacity + its capacity),
             survivors' shares x (1 - share)

7  record_end(); check(); time + 1
     check asserts: |sum of all cash| < 1e-6 + 1e-9 x |rest-of-economy cash| (money
     conservation, up to rounding), every firm's cash > -1e-6,
     shares sum to 1, K(t+1) = K(t) - retired + ordered - exit + entry
```

When the four timed objects act:

- **Hurdle.** Computed in step 5 from the price the firm posted in step 1 of the same period, and
  for an entrant in step 6 at its entry price. Nowhere else.
- **Regulating price.** Computed once a period, after production and before scrapping, the same
  for every firm. It enters p^e in steps 5 and 6 when λ > 0, and the outputs. If no plant is in
  operation, last period's value is kept.
- **r_new.** Computed once a period, with the regulating price, from the plants in operation aged
  `entry_window` or less. Step 4 reads it for the reserve, step 6 for entry: one number for every
  firm and both uses. Without a plant in the window it is `None`: the reserve is released (A7)
  and the entry probability is 0.
- **Construction lag.** A plant ordered in t (step 5, or step 6 for an entrant) has no output in
  t and is delivered in step 0 of t + 1. Entry shares and the exit test count plants on order; in
  step 5 nothing is on order yet, so the term is zero there and is kept only for the formula.

The initial state is read as period −1: price 100, `share` = capacity share, `sales` = share ×
D_0, `util` = sales / capacity (0.888), `excess` = 0, funds 0. Each firm's cash is the
depreciation accumulated on its plants, Σ cost × age / T: 6,325.00 for a firm on C, 6,546.26 on
D1, 8,526.06 on D2. The rest-of-economy account starts at minus their sum (−42,794.64 for six
firms), so all cash sums to zero. Firms with spare capacity and a cost edge already cut in
period 0.

## 4. Equations

Arguments are floats, or lists of floats in firm or plant order. "v2" names the function ported.

| File | Function | Docstring | Ports |
| --- | --- | --- | --- |
| `common_unit_cost.py` | `unit_cost(ucs, kappa, delta)` | uc = ucs + δκ, the cost per unit of normal output. | v2 `unit_cost`, as called in `hurdle.py` |
| `common_profit_rate.py` | `profit_rate_at_price(price, ucs, kappa, delta)` | (p − uc) / κ at normal output. | v2 `profit_rate_at_price`, as called in `hurdle.py` |
| `common_hurdle.py` | `evaluation_price(price, reg_price, lam)` | p^e = (1 − λ) p + λ p_reg. | new (v2 had the two ends as `HURDLE_PRICE`) |
| | `hurdle(rule, eval_price, menu, delta)` | h = 0 under the unit-cost rule; the best rate on the menu at p^e, never below 0, under the profit-rate rule. | v2 `hurdle.hurdle` and `best_profit_rate`, floor hard-coded |
| `common_technique_choice.py` | `technique_cost(ucs, kappa, hurdle, delta)` | ucs + (δ + h) κ. | v2 `technique_cost`, without τ |
| | `choose_technique(menu, hurdle, delta)` | The technique with the lowest cost at h; exact ties go to the lower κ, then the lower ucs. | v2 `choose_technique`; tie rule of `frontier_technique` |
| | `frontier(menu, delta)` | The techniques no other beats on both unit cost and κ: at any h ≥ 0 neither rule chooses a beaten one and none sets the hurdle. `start_period` keeps the public menu on it, for speed only. | new (stage 4) |
| `common_regulating_price.py` | `regulating_technique(techniques, delta)` | The technique in operation with the lowest unit cost; exact ties go to the lower κ. | v2 `regulating_price`, first half |
| | `price_of_production(ucs, kappa, delta, rbar)` | uc + r̄κ. | v2 `regulating_price`, second half |
| `setup_initial_plants.py` | `initial_ages(output, size, life)` | n = normal output / S rounded half up (at least 1) plants, of ages floor(i T / n). | new (A2, A3) |
| `pricing_floor.py` | `price_floor(unit_costs)` | The unit cost of the firm's lowest-unit-cost plant in operation; 0 without a plant. | new (A5) |
| `pricing_rule.py` | `posted_price(previous, rival_prices, rival_costs, own_cost, spare, excess, cost_edge, cut, shortage_step)` → (price, cut) | After a shortage, the next higher rival price, or previous × (1 + step × excess) with no rival above; else (1 − c) × the lowest rival price if entitled to cut; else the lowest price posted, its own included; never below `own_cost`, the unit cost of its best plant, which is both the edge criterion and the floor. | v2 `real_competition_price`; the systematic regime is new |
| `demand_replicator.py` | `competitiveness(price)` | E = 1 / p. | v2 `competitiveness` |
| | `replicator_shares(previous_shares, competitiveness, chi)` | f_i = f_i,−1 (1 + χ (E_i − Ē) / Ē), negatives set to 0, renormalised. | v2 `replicator_shares` |
| `accounts_merit_order.py` | `dispatch(ucs, ages, capacity, quantity)` → outputs | Plants run lowest operating cost first, then youngest, each up to its normal capacity. | v2 `merit_order.dispatch`, without overtime; ties by age (A13 b) |
| `accounts_depreciation.py` | `depreciation(cost, book_value, delta)` | δ × purchase cost a period, at most the remaining book value. | new (v2's by-time rule) |
| `accounts_dividends.py` | `dividends(profit, payout)` | d × max(0, profit). | new (v2's rule) |
| `scrapping_below_cost.py` | `scrap_cost(ucs, kappa, delta, rule)` | The cost the price must cover: ucs, or ucs + δκ under `"unit_cost"`. | v2 `retirement.scrap_cost` |
| | `periods_below_cost(previous, price, cost)` | Consecutive periods with the price below the scrap cost. | v2 `retirement.periods_below_cost` |
| `scrapping_idle_plants.py` | `periods_idle(previous, output)` | Consecutive periods without output. | v2 `idle_plants`: the same plants, given the running order |
| `scrapping_retirement.py` | `retirement_reason(age, life, below_cost, idle, periods)` → `"age"`, `"cost"`, `"idle"` or `None` | A plant leaves at age T, or after N periods below its scrap cost, or after N periods idle; the first reason that holds, in that order. | v2 `retirement.retirement_reason` |
| `scrapping_reserve.py` | `reserve_released(r_new, rbar)` → bool | True when new plants earn the general rate, r_new ≥ r̄, and when no plant is in the window of r_new: the reserve of a plant that leaves then joins the funds. | new (A7; arm 4 of the pilot) |
| `investment_draw_marx.py` | `draw_marx(ucs_o, kappa_o, u, z, step, bias, spread)` → (ucs, κ) | ucs_n = (1 − a) ucs_o, κ_n = (1 + k a) κ_o, a = u × step, k = bias × e^{spread z}. | v2 `innovation_set.draw_marx` |
| `investment_draw_neutral.py` | `draw_neutral(ucs_o, kappa_o, u, v, step)` → (ucs, κ) | Direction uniform on the circle in (Δucs/ucs, Δκ/κ), size u × step. | v2 `innovation_set.draw_neutral` |
| `investment_draw_categories.py` | `draw_categories(ucs_o, kappa_o, delta, price, u_cat, u_a, u_b, step, conflict_share)` → (ucs, κ) | A cost-reducing, capital-using design that both rules adopt at `price`, or with probability q only the unit-cost rule. | v2 `new_technique.design_category` and `draw_design` |
| `investment_retained_earnings.py` | `plants_affordable(funds, plant_cost)` → int | floor(funds / plant cost), 0 if funds are negative. | new (A7) |
| `investment_accelerator.py` | `plants_wanted(notional, u_target, capacity, on_order, size)` → int | ceil((notional / u* − capacity − on order) / S), at least 0. | new (A7) |
| `entry_probability.py` | `entry_probability(r_new, rbar, theta)` | min{1, θ max(0, r_new − r̄) / r̄}; 0 when r_new is None. | v2 `entry_probability` |
| `entry_new_plant_rate.py` | `new_plant_rate(rates, capacities)` | Capacity-weighted realised profit rate (plant profit / purchase cost) of the plants built in the window; None without one. | v2 `new_plant_rate` |
| `entry_inherited_rule.py` | `inherited_label(labels, shares, mutation, u_parent, u_flip)` | The label of an incumbent drawn by share, flipped with probability μ. | v2 `inherit`, with two uniforms in place of the generator |
| `entry_size.py` | `entrant_plants(capacities, entry_size, size)` → int | entry_size × the average incumbent capacity, in plants of size S, rounded half up, at least 1. | new (A10) |
| `entry_exit_rule.py` | `leaving(shares, capacities, exit_share, min_firms)` → list of bool | Firms below the exit share or without capacity leave; if fewer than min_firms would remain, the candidates with the largest share stay, tied ones together. | new (A10, A13 e) |

Transactions in `markets/` (they change state, so they are not equations):

| File | Function | Docstring | Ports |
| --- | --- | --- | --- |
| `payments.py` | `pay(payer, payee, amount)` | The only place cash moves: payer.cash − amount, payee.cash + amount; a negative amount is refused. | v2 `payments.pay`, as called in `entry_exit.py`, without the flow matrix |
| `goods_market.py` | `allocate(demand, shares, offered)` → (sales, lost) | Each firm sells min(share × D, offered capacity); the overflow is shared once, pro rata to spare offered capacity; the rest is lost. | v2 `goods_market.allocate`, one round, no priority to the cheapest |
| `plant_market.py` | `buy_plant(industry, firm, technique, cause)` | The firm pays κS now, its funds fall by κS, and the plant joins `pending_plants`. | v2 `buy_plant`, as called in `create_entrant` |
| | `remove_plant(industry, firm, plant, reason)` | The plant leaves. Its reserve, cost − book value, joins the funds if `reserve_released`; else the firm pays it to the rest of the economy, as far as its cash allows. The book value is written off. | new (A7, A13 j) |
| `entry_exit.py` | `create_entrant(industry, u_parent, u_flip)` | Label inherited, price = lowest posted, technique by its own rule on the public menu, plants paid by equity, share by capacity. | v2 `create_entrant` |
| | `remove_firm(industry, firm)` | Cash goes to the rest of the economy, plants are written off, the others' shares are rescaled. | v2 `remove_firm`, without debt |

Three remarks on the ports:

- `posted_price`: "entitled to cut" = spare capacity, and under cost-edge cutting a unit cost
  below that of at least one rival posting the lowest rival price (strict inequality, so equal
  costs give no edge). v2's second condition, own cost below the cut price, is replaced by the
  floor: price = max(min(previous, target), floor) (Q2). The returned `cut` is true when the
  firm was entitled and its price fell below both its previous price and the lowest rival price:
  a firm that stays below rivals held at their floors is not counted as cutting again. Rivals
  are the other firms with a plant in operation. Two prices are "equal" by `math.isclose`.
- `plants_affordable` adds 1e-9 to the funds before the floor: after T charges of δ × cost a
  book value can be 1e-13 off zero, and funds / cost would otherwise be 0.9999999999999999.
- The realised conflict share and v2's `adoption_zone` are not ported: no listed observable needs
  them.

## 5. `parameters.py`

```python
"""Parameters of version 3: the proposal's table and the addendum A1-A13.
Experiments change fields with dataclasses.replace; no other file holds a constant."""
from dataclasses import dataclass

LABELS = ("shaikh", "okishio")
EPS = 1e-9                               # numerical tolerance
MENU = (("C", 64.25, 137.50), ("D1", 61.77, 142.31), ("D2", 59.21, 157.89))   # name, ucs, kappa (A1)
START = tuple((name, label, output)      # one firm per (technique, label) pair (A2)
              for name, output in (("C", 120.0), ("D1", 120.0), ("D2", 140.0)) for label in LABELS)


@dataclass(frozen=True)
class Parameters:
    periods: int = 200
    # population and demand (A1, A2)
    rule_shaikh: str = "unit_cost"       # unit_cost | profit_rate: the hurdle mapping, label -> rule
    rule_okishio: str = "profit_rate"    # unit_cost | profit_rate
    menu: tuple = MENU
    start: tuple = START                 # (technique, label, normal output) of each initial firm
    firms_per_pair: int = 1              # robustness: 2 and 5
    plant_size: float = 20.0             # S; Morris 10-40
    initial_price: float = 100.0
    demand_ratio: float = 340 / 383      # D_0 / initial capacity: D_0 = 674.7 at the defaults
    growth: float = 0.0                  # g; E4: 0.01
    rbar: float = 0.05                   # general rate: entry gate, replacement condition,
                                         # price of production; E3, E4: 0.16
    plant_life: int = 10                 # T, with delta = 1 / T (A3); Morris 7-19
    # pricing (A5)
    pricing: str = "cost_edge"           # cost_edge | systematic
    price_cut: float = 0.02              # c; Morris 0.01-0.05
    u_full: float = 1.0                  # spare capacity = last utilisation below this
    shortage_step: float = 0.5           # price rise per unit of excess-demand share, no rival above
    # demand (A6)
    chi: float = 1.0                     # Morris 0.25-4
    # accounts
    payout: float = 0.5                  # d; Morris 0.25-0.75
    # scrapping
    scrap_cost: str = "operating_cost"   # operating_cost | unit_cost (robustness)
    scrap_periods: int = 2               # periods below cost, or idle, before a plant leaves
    # technical change (A9)
    tech_change: str = "marx"            # marx | neutral | categories | none
    bias: float = 1.5                    # beta; E2: 0, 0.5, 1.5, 3; Morris 0.5-3
    bias_spread: float = 0.8             # sigma
    design_step: float = 0.05            # A; Morris 0.02-0.10
    draw_prob: float = 0.2               # pi; Morris 0.1-0.4
    public_lag: int | None = 2           # L; None: a design never becomes public (robustness)
    conflict_share: float = 0.5          # q, categories rule only
    # hurdle and investment (A7, A8)
    lam: float = 0.0                     # lambda; E3: 0, 0.25, 0.5, 0.75, 1
    investment: str = "retained"         # retained | accelerator
    u_target: float = 0.9                # accelerator only; robustness: 0.8, 0.95
    # entry and exit (A10)
    entry_speed: float = 5.0             # theta; Morris 1-10
    mutation: float = 0.02               # mu; Morris 0-0.05; 0 in E6
    entry_window: int = 5                # r_new: plants aged this many periods or less
    entry_size: float = 0.5              # entrant's capacity / average incumbent capacity
    exit_share: float = 0.01
    min_firms: int = 2

    @property
    def delta(self) -> float:
        return 1.0 / self.plant_life
```

Five switches, each listed by the proposal: the population (`rule_shaikh`, `rule_okishio`),
`pricing`, `investment`, `tech_change` and `scrap_cost`. There is no entry switch and no switch
for the reserve: both are governed by `rbar`. The three populations are overrides held in
`experiments/cells.py`: mixed = the defaults, `all_unit_cost` = `rule_okishio="unit_cost"`,
`all_profit_rate` = `rule_shaikh="profit_rate"`. The initial firms are built from `start`,
repeated `firms_per_pair` times, with `initial_ages(output, plant_size, plant_life)` plants each
(6, 6 and 7 at the defaults: capacity 760), D_0 = `demand_ratio` × initial capacity, and cash as
in section 3. Initial cash is derived from the plants, so it is no parameter.

## 6. Output tables

### Period table: one row per period and label

`model/outputs.py`, kept in `industry.rows`. It observes and never decides: it draws no random
number and writes nothing a rule reads. `g` is a label, "its firms" the firms of g present in
steps 1–5 of t. Sums are over its firms or their plants in operation in t.

| Column | Formula |
| --- | --- |
| `t`, `label`, `rule` | period, label, the rule the label follows in this population |
| `firms` | number of its firms |
| `capacity` | K_g,t: normal capacity in operation in t (after deliveries, before scrapping) |
| `cap_retired`, `cap_retired_age`, `cap_retired_cost`, `cap_retired_idle` | capacity leaving in step 4, in total and by reason (A13 l) |
| `cap_released` | capacity leaving in step 4 whose reserve joined the funds |
| `withdrawn` | reserves paid to the rest of the economy in step 4, in money |
| `cap_ordered` | capacity ordered in step 5 |
| `cap_exit` | capacity, in operation and on order, of its firms that leave in step 6 |
| `cap_entry` | capacity ordered by an entrant of g |
| `capacity_next` | K_g,t+1 = capacity − cap_retired + cap_ordered − cap_exit + cap_entry |
| `share` | f_g,t: sum of the notional replicator shares after step 2 |
| `share_end` | f_g,t^end: sum of the shares after step 6 |
| `notional`, `sales` | f_g,t × D_t; units sold |
| `sales_share` | σ_g,t = sales / industry sales |
| `util` | sales / capacity |
| `price` | sales-weighted mean posted price (capacity-weighted when sales are zero) |
| `ucs`, `kappa`, `unit_cost` | capacity-weighted means over its plants in operation |
| `cuts` | its firms that undercut in step 1 |
| `profit`, `dividends` | after depreciation; d × max(0, profit) |
| `capital` | purchase cost of its plants in operation |
| `profit_rate` | profit / capital: the realised rate (Q12) |
| `cash`, `funds`, `write_offs` | sums over the label's firms at the end of the period, after step 6 |
| `hurdle` | mean h of its firms in step 5 |
| `orders`, `orders_dearer` | plants ordered (steps 5 and 6); those whose technique is not the lowest-unit-cost technique known to the buyer |
| `drawn`, `kept` | designs drawn; designs kept |
| `entries`, `exits` | firms of g entering; leaving |
| `demand`, `lost` | D_t; demand left unserved (industry, same on both rows) |
| `low_price` | lowest posted price (industry) |
| `reg_price` | uc_reg + r̄ κ_reg (industry) |
| `price_over_reg` | sales-weighted industry price / `reg_price` |
| `r_new` | the signal of entry and of the reserve (industry) |
| `war` | 1 if any firm undercut in t (industry) |
| `leader_cheapest` | 1 if a firm posting the lowest price has the lowest best-plant unit cost (industry; E0) |
| `rate_low`, `rate_high` | lowest and highest realised profit rate among firms with capacity (industry; E0) |

The flow columns come from `count(industry, firm, key, amount)`, called by `buy_plant`,
`remove_plant`, `create_entrant`, `remove_firm`, `produce_and_account` and `invest`; it is the
only function outside entry that reads a label. The tally keeps every amount and sums them
with `fsum`, and a value that is not defined (a label without firms, capacity or sales) is
`None`, so two runs of one seed give equal tables.

### Run table: one row per run

`experiments/summary.py`, `run_row(rows, params, seed)`: a function of the period table alone, as
v2's `analysis/indicators.py` was. U is the label `"shaikh"`, O the label `"okishio"`; "end"
means t = 200, that is `capacity_next` and `share_end` of the row t = 199 (A11).

| Column | Formula |
| --- | --- |
| `cap_share_end` | K_U,200 / K_200, with K_200 = Σ_g `capacity_next` at t = 199 |
| `outcome` | `"undecided"` if K_200 = 0; else `"win"` if `cap_share_end` > 0.5, `"loss"` if below, `"tie"` at one half (by `math.isclose`) (A11) |
| `sales_share_end` | σ_U at t = 199 |
| `takeover_t`, `takeover_label` | first period after which one label holds more than 0.9 of capacity in every remaining period (v2 `takeover`) |
| `dk_ordered`, `dk_retired`, `dk_entry`, `dk_exit` | Σ_t term_c for U, with term_c = sign_c (flow_c,g − s_g,t Σ_g flow_c) / K_t+1, s_g,t = K_g,t / K_t and signs +, −, +, − (v2 `capacity_share_terms`, without "cancelled": orders of a leaving firm are in `cap_exit`) |
| `dk_accumulation` | `dk_ordered` + `dk_retired`: the accumulation term of the proposal |
| `dk_resid` | (`cap_share_end` − s_U,0) − the four terms; zero up to rounding |
| `ds_price` | Σ_{t≥1} (f_U,t − f_U,t−1^end): the price term (v2 `sales_share_terms`) |
| `ds_entry_exit` | Σ_{t≥1} (f_U,t−1^end − f_U,t−1) |
| `ds_rationing` | Σ_{t≥1} [(σ_U,t − f_U,t) − (σ_U,t−1 − f_U,t−1)] |
| `ds_resid` | (σ_U,199 − σ_U,0) − the three terms; zero up to rounding |
| `hurdle_shaikh`, `hurdle_okishio` | mean of `hurdle` over the periods in which the label has firms |
| `shaikh_dearer`, `okishio_dearer` | Σ_t `orders_dearer` / Σ_t `orders` |
| `rate_shaikh`, `rate_okishio`, `rate_industry` | Σ_t `profit` / Σ_t `capital`, by label and for both |
| `price_over_reg` | mean over t |
| `war_freq` | mean of `war`: the price-war frequency |
| `leader_cheapest`, `rate_spread` | means over t of `leader_cheapest` and of `rate_high` − `rate_low` |
| `entries`, `exits`, and each by label | sums |
| `open_share` | share of periods with `r_new` ≥ r̄, or without a plant in its window: reserve released |
| `released_shaikh`, `released_okishio` | Σ_t `cap_released` / Σ_t `cap_retired`: the share of leaving plants whose reserve was released |
| `retired_age`, `retired_cost`, `retired_idle` | shares of Σ_t `cap_retired` by reason, both labels together (A13 l) |
| `g_ucs_shaikh`, `g_kappa_shaikh`, `g_ucs_okishio`, `g_kappa_okishio` | ln(x_last / x_first) / (t_last − t_first) for x = `ucs`, `kappa`, over the periods in which the label has capacity: the Marx-bias measures |
| `g_ucs`, `g_kappa`, `marx_biased` | the same for the industry's capacity-weighted means; `g_ucs` < 0 and `g_kappa` > 0 |
| `firms_end`, `capacity_end`, `capacity_over_demand` | at t = 200; K_200 / D_199 |
| `util_mean`, `lost_share` | Σ sales / Σ capacity; Σ `lost` / Σ `demand` |

The price, accumulation, exit and entry terms of the proposal are `ds_price`, `dk_accumulation`,
`dk_exit` and `dk_entry`, all over the whole run. The harness adds `experiment`, `cell`,
`population`, `seed`, `overrides` (JSON), `commit`, `wall_s` and `error`.

## 7. Experiment harness

**One run.** A task is (experiment, cell, population, overrides, seed). `run_one(task)` builds
`replace(Parameters(), **overrides, **population)`, runs one industry, and returns its run row; an
exception becomes a row with `error` set, which counts in no share.

**Parallel runs.** `multiprocessing.get_context("spawn").Pool(jobs)` and `imap` (ordered) over
the tasks sorted by cell, population and seed, in chunks of 8: one industry at a time in each
process, results back in seed order whatever the number of workers. Seeds are 0 … N − 1, the same
for the three populations and for every cell.

**Files.** `outputs/<experiment>/runs.csv` is the log: the rows of a (cell, population) are
appended when its last seed returns. `cells.csv` is rebuilt from `runs.csv` after each append and
written through a temporary file. `--resume` reads `runs.csv`, drops any (cell, population) with
fewer rows than seeds, and runs only what is missing. `--keep-periods S1,S2` also writes the
period table of the seeds named, for the typical-run figures.

**`cells.csv`**, one row per (cell, population): `n_seeds`, `n_error`, `n_undecided`, `won`,
`lost`, `tied`, `share_won` = won / (won + lost), `won_low`, `won_high` (95 % Wilson interval on
won out of won + lost, v2 `wilson`), and for each numeric column of the run table its mean and
the 95 % interval of the mean; the mean of `cap_share_end` is the one reported beside the share
won (A11). Mixed rows also get `ctrl_uc_share_won`, `ctrl_pr_share_won`, `gap` = share won − the
mean of the two controls, and `beyond_drift` = the mixed interval is disjoint from both controls'
intervals (v2 `_disjoint` and `summarise`).

**Command line.** `python -m experiments.harness E1 --seeds 500 --jobs 10 [--resume]`.

| Priority | Experiment | Cells | Populations | Seeds | Runs |
| --- | --- | --- | --- | --- | --- |
| 1 | E0 real competition without technical change | `tech_change="none"` | the two controls | 50 | 100 |
| 1 | E1 defaults | 1 | mixed, two controls | 500 | 1,500 |
| 1 | E2 bias | β = 0, 0.5, 1.5, 3; neutral; none | 3 | 200 | 3,600 |
| 1 | E3 evaluation price | λ (5) × `pricing` (2) × r̄ (0.05, 0.16) = 20 | 3 | 200 | 12,000 |
| 2 | E4 conditions | `pricing` × `investment` × r̄ × g (0, 0.01) = 16, under marx and under categories = 32 | 3 | 200 | 19,200 |
| 2 | E5 channels | no run: decomposition columns of E4; `e5_channels.py` regresses `rate_shaikh` − `rate_okishio` on `okishio_dearer` with cell fixed effects | | | 0 |
| 2 | Morris | 110 points (below) | 3 | 100 | 33,000 |
| 3 | E6 invasion | 2 directions (A12) | mixed, one control | 500 | 2,000 |
| 3 | Scrapping on unit cost | E1 and the 16 marx cells of E4 | 3 | 200 | 10,200 |
| 3 | Private diffusion (`public_lag=None`) | E1 | 3 | 200 | 600 |
| 3 | Homogeneous start | the 6 cells of E2 | 3 | 200 | 3,600 |
| 3 | 12 and 30 firms | E1 and the 4 cells of E4 with r̄ = 0.16 and g = 0.01 | 3 | 200 | 6,000 |
| 3 | u* = 0.8 and 0.95 | the 8 accelerator marx cells of E4 | 3 | 200 | 9,600 |

E0 to E6 are 38,400 runs, the proposal's count. At 0.11 s a run and 10 workers, priority 1 takes
about 3 minutes, priority 2 about 10, priority 3 about 6. The categories check is the second half
of E4.

**What E0 must show before E1–E6 are read** (thresholds proposed here, to be agreed before the
run): the price leader has the lowest unit cost in at least 0.9 of periods (v2: 0.94); capacity
at t = 200 is between 0.9 and 1.2 times demand in at least 0.9 of seeds (pilot: 0.99–1.09); the
mean `price_over_reg` is between 0.9 and 1.2 (pilot: 0.93–1.11); `rate_industry` is between 0.03
and 0.10 at r̄ = 0.05 (pilot: 0.06); profit rates stay unequal (`rate_spread` > 0); no seed ends
without capacity.

**Reference numbers from the pilot** (arm 4, 200 seeds; proposal, section "Pilot in v2"). Stage 5
sets E1 beside the first row, stage 6 the eight E4 cells with the innovation set and retained
earnings beside the others. A reference, not a gate (Q19).

| Measure | Pilot, arm 4 | v3 column |
| --- | --- | --- |
| Share won by the unit-cost rule, cost-edge cutting (4 cells) | 0.94–0.97 | `share_won` |
| Its mean final capacity share, same cells | 0.72–0.79 | `cap_share_end` |
| Share won, systematic cutting, r̄ = 0.05 | drift | `share_won`, `beyond_drift` |
| Share won, systematic cutting, r̄ = 0.16 | 0.10–0.19 | `share_won` |
| Industry profit rate | 0.06 at r̄ = 0.05; 0.14–0.15 at 0.16 | `rate_industry` |
| Price over the price of production | 0.93–1.11 | `price_over_reg` |
| Capacity over demand | 0.99–1.09 | `capacity_over_demand` |
| Hurdle of the profit-rate label, r̄ = 0.05 | 0.06–0.08 | `hurdle_okishio` |
| Its orders that are not the cheapest technique, r̄ = 0.05 | 0.46–0.65 | `okishio_dearer` |
| Entries a run | 47–140 | `entries` |
| Plants whose reserve is released, by label | 0.74 and 0.76 at r̄ = 0.05; 0.38 and 0.40 at 0.16 | `released_shaikh`, `released_okishio` |

**E6** (A13 d). `populations.invasion(resident)` gives ten firms on D1 with 6 plants
(120 of capacity) each, nine with the resident label and one with the other; D_0 = (340/383) ×
1,200 = 1,065.3 and μ = 0. Direction 1: residents `"shaikh"` on the unit-cost rule, mutant
`"okishio"` on the profit-rate rule; its control sets `rule_okishio="unit_cost"`. Direction 2 is
the mirror image. The E6 cells name the mutant label, and `run_row` adds `mutant_share_end` and
`invaded` (its final capacity share above 0.1, ties apart). Read: the mean `mutant_share_end`
against 0.1 and the invasion rate, each against the control.

**Morris** (`experiments/morris.py`, SALib `sample.morris.sample` and `analyze.morris.analyze`;
check their signatures against the installed version in stage 6). Ten parameters, 10 trajectories
on a 4-level grid, so 110 points, each a cell run through the harness: `bias` 0.5–3,
`design_step` 0.02–0.10, `draw_prob` 0.1–0.4, `price_cut` 0.01–0.05, log₂ `chi` −2 to 2,
`payout` 0.25–0.75, `plant_life` 7–19, `plant_size` 10–40, `entry_speed` 1–10, `mutation` 0–0.05.
Outcomes: `gap` and the mean `cap_share_end` of the mixed population. Output:
`outputs/morris/morris.csv` with μ*, σ and the interval of μ* per parameter and outcome. Each
parameter with μ* above 0.10 then gets a one-at-a-time sweep at 200 seeds.

**Figures**, each a script that reads `cells.csv` or `runs.csv` and writes one PDF:

| Exhibit | Script | Data |
| --- | --- | --- |
| Figure 1, the conflict zone on Shaikh's menu | `fig1_conflict_zone.py` | none: the three techniques, rates against the price |
| Figure 2, typical run, with the E0 panel | `fig2_typical_run.py` | period tables kept from E0 and E1 |
| Figure 3, share won against β and against λ | `fig3_bias_lambda.py` | E2, E3 |
| Figure 4, the two heat maps | `fig4_heatmaps.py` | E4 |
| Figure 5, decomposition bars in four cells | `fig5_decomposition.py` | E4 |
| Figure 6, μ* against σ | `fig6_morris.py` | Morris |
| Table 3, robustness | `tab3_robustness.py` | the priority-3 cells |

## 8. Tests

`python -m unittest discover -s tests`. A mechanism test builds a small industry by hand with
`tests/helpers.py` and calls one step function, so no step's test depends on another step.

| File | Asserts |
| --- | --- |
| `test_common.py` | On Shaikh's menu D2 has the lowest unit cost (75.0) and at p = 100 D1 the highest rate (16.86 % against 16.00 % and 15.83 %). h = 0 under the unit-cost rule at any price. Under the profit-rate rule h is the best rate on the menu, and 0 when p^e is below every unit cost. With that h, `choose_technique` returns the highest-rate technique: D1 at 100, D2 below 85.15. p^e at λ = 0, 0.5, 1. At λ = 1, p^e = 82.89 and h = 5.00 % for r̄ = 0.05; p^e = 100.26 and h = 17.05 % for r̄ = 0.16, never below r̄. Ties go to the lower κ. |
| `test_setup.py` | Six firms, 6, 6 and 7 plants, capacity 760, D_0 = 674.67, ages 0, 1, 3, 5, 6, 8 and 0, 1, 2, 4, 5, 7, 8, book value κS(1 − a/T), shares = capacity shares. Cash 6,325.00, 6,546.26 and 8,526.06, funds 0, and all cash sums to 0. `firms_per_pair=2` doubles firms and demand. |
| `test_pricing.py` | Shortage: a firm moves to the next higher rival price, and with none above rises by 0.5 × the excess share. No shortage: no price rises, except to the floor (Q2). Cost-edge: a firm cuts only with spare capacity and a strictly lower unit cost than a rival posting the lowest rival price; equal costs, no cut. Systematic: spare capacity is enough. The price is never below the unit cost of the firm's best plant in operation. Reversing the firm list gives the same prices. |
| `test_demand.py` | Shares sum to 1; equal prices leave them unchanged; the cheaper firm gains; χ = 0 changes nothing. Sales never exceed offered capacity; a plant with ucs above the price is not offered; sales + lost = D_t; the overflow goes pro rata to spare offered capacity, once; `share` is unchanged by rationing. |
| `test_accounts.py` | Plants run cheapest first, then youngest; output = sales; no plant above its capacity. Profit = revenue − operating cost − depreciation, and a plant without output still depreciates. Dividends are 0.5 × profit when positive, 0 otherwise. Book value is 0 after T periods. Cash never falls below 0. **Money conservation**: over 50 periods, in the three populations, under both investment rules and at r̄ = 0.05 and 0.16, the sum of all cash stays 0 every period. **Accounts identity**: cash − funds is never below the depreciation accumulated on the firm's plants in operation, and equals it for a firm that never lacked cash at a withdrawal. |
| `test_scrapping.py` | A plant leaves at age T; after 2 consecutive periods with the price below its ucs, and one period above resets the count; after 2 consecutive periods without output. Under `scrap_cost="unit_cost"` the price is compared with ucs + δκ. **Reserve released**: with r_new ≥ r̄, and with no plant in the window, funds rise by cost − book value and cash does not move. **Reserve withdrawn**: with r_new < r̄, funds do not move, the firm's cash falls by cost − book value and the rest of the economy gains as much; a firm with less cash pays what it has. In both cases write-offs rise by the book value. In a run without draws the initial plants retire on the dates the staggered ages give. |
| `test_investment.py` | The three draws: at β = 0 κ is unchanged; a categories "both" design is adopted by both rules and a "conflict" design only by the unit-cost rule; a design that ties is not kept. Retained earnings buy floor(min(F, cash) / (κS)) plants. **Depreciation reserve**: a firm sells its capacity at a price equal to its unit cost, so with zero profit for T periods. With r_new ≥ r̄ it buys one plant in the period its plant retires at age T. With r_new < r̄ the reserve is paid out and it buys none. **Funds never exceed cash**: in a full run no firm spends more than min(F, cash), and under the accelerator more than its cash. Accelerator: the ceil formula, capped by cash. Lag: a plant ordered in t has no output in t and can produce in t + 1. Diffusion: a rival's menu holds a design from first_run + L and not before; never when `public_lag=None`. Streams: a firm's stream is at the same position after t periods whatever it drew (Q9). |
| `test_entry.py` | The entry probability at r_new below, just above and far above r̄, and 0 without a plant in the window. r_new weights by capacity and ignores plants older than the window. Inheritance: μ = 0 gives the parent's label, μ = 1 the other. An entrant chooses on the public menu only, not among an incumbent's private designs; it is paid for by equity, so all cash still sums to 0; its plants arrive next period; its share and the incumbents' follow A10; its price is the lowest posted. Exit below 1 % or without capacity, cash to the rest of the economy, survivors' shares sum to 1; never fewer than 2 firms; tied candidates stay or leave together. |
| `test_neutrality.py` | **Label swap**: in each of the three populations, swapping the labels of all initial firms and the two fields `rule_shaikh`, `rule_okishio` leaves every firm on its rule; every firm's trajectory is then identical and the period table is the same with the two labels exchanged (Q4). **Symmetric controls**: in a control, swapping the labels alone gives the mirror image, and reversing `industry.firms` at the start changes nothing in any population, so a firm's draws do not depend on its place. **Label reads**: the attribute `label` is read only in `entities.py`, `model.py`, `markets/entry_exit.py`, `equations/entry_inherited_rule.py` and `outputs.py`; a rule is read only to look up the hurdle, and a serial number only to draw a parent and to name a design (a search of the source). |
| `test_model.py` | **Reproducibility**: the same seed gives the same period table, another seed a different one. A 200-period run at the defaults ends with capacity, and `check` holds every period. The capacity terms sum to the change in the capacity share and the sales terms to the change in the sales share (residuals below 1e-9). Every switch runs 120 periods through `check`. Without `frontier` the period table is the same. |
| `test_budget.py` | `parameters.py`, `run.py`, `equations/`, `markets/` and `model/` hold at most 770 lines that are not blank; the count is printed. |
| `test_experiments.py` | `wilson(81, 100)` = (0.722, 0.875), and NaN for n = 0. `beyond_drift` on overlapping and disjoint intervals. `takeover` on three hand-made series. **Ties**: capacity shares of 0.6, 0.4 and 0.5 give win, loss and tie, and 3 wins, 1 loss and 2 ties give a share won of 0.75. Two cells × three populations × four seeds give the same `runs.csv` with 1 and 2 workers, in seed order; a run stopped after the first cell and resumed gives the same file. |

Two statistical checks are read from `cells.csv` in stage 5 and are not unit tests: the two
controls of E1 at 500 seeds have intervals that contain 0.5, and in each control
`released_shaikh` and `released_okishio` are close, since the reserve condition is the same for
every firm.

## 9. Stages

Each stage ends with the tests passing and one commit on `v3`. Times are for one working session
with its review. 3a to 3d are parallel: each starts from the stage 2 commit on its own branch and
touches only its own files and the body of its own step functions in `scheduler.py` (Q14).

| Stage | Content | Owner | Time | Dates |
| --- | --- | --- | --- | --- |
| 1 Scaffold | New `CLAUDE.md` (the rules of the prompt's section 3, the order of authority and the line count of this plan), new `README.md`, `requirements.txt` (numpy, pandas, matplotlib, SALib), the workflow file on Python 3.12 with the unit tests and `run.py` only, empty packages, `parameters.py`, `entities.py`, the five `common_` files, `setup_initial_plants.py`. Tests: `test_common`, `test_budget`. | Ugo | 1.5 h | 12 Nov |
| 2 Skeleton | `model.py` (initial population, cash and streams), `payments.py`, `plant_market.py` in full with `scrapping_reserve.py`, `scheduler.py` with `period`, `start_period`, `check`, the end of step 3 (regulating price, r_new, with `entry_new_plant_rate.py`) and the six step functions as stubs with their final signatures and docstrings (prices and shares unchanged, sales = min(share × D, capacity), nothing else), `outputs.py` with `count` and its keys, `run.py`, `tests/helpers.py`. Tests: `test_setup`, reproducibility and money conservation on the stub loop. | Ugo | 3 h | 12 Nov |
| 3a Pricing ∥ | `pricing_rule.py`, `pricing_floor.py`, `set_prices`. Test: `test_pricing`. | Jake | 2 h | 13–14 Nov |
| 3b Demand, entry and exit ∥ | `demand_replicator.py`, `goods_market.py`, `allocate_demand`; the other four `entry_` files, `markets/entry_exit.py`, `enter_and_exit`. Tests: `test_demand`, `test_entry`. | Pierre-Loup | 3.5 h | 13–14 Nov |
| 3c Accounts, scrapping, outputs ∥ | The three `accounts_` files and the other three `scrapping_` files, `produce_and_account`, `scrap_plants`, `outputs.py` in full, `experiments/summary.py`, and `run.py` also writes `run.csv`. Tests: `test_accounts`, `test_scrapping`. | Vincent | 3.5 h | 13–14 Nov |
| 3d Technical change and investment ∥ | The three `investment_draw_` files, `investment_retained_earnings.py`, `investment_accelerator.py`, `invest`. Test: `test_investment`. | Ugo | 3 h | 13–14 Nov |
| 4 Integration | The four parts together; `test_neutrality`, `test_model`; profile 20 seeds against 0.11 s a run; line count; a first read of E0 on 20 seeds and of the plants leaving by reason (Q18). | Ugo, all four review | 3 h | 15 Nov |
| 5 Harness, E0–E3 | `stats.py`, `cells.py` (E0–E3), `harness.py`, `test_experiments`; runs; E1 beside the pilot; `fig1` to `fig3`. | Ugo (harness, E2, E3), Vincent (E0), Pierre-Loup (E1) | 4 h and 3 min of runs | 16 Nov, runs 17–19 Nov |
| 6 E4, E5, Morris | E4 cells, read beside the pilot; `e5_channels.py`, `morris.py`; `fig4` to `fig6`. | Jake (E4), Ugo (Morris) | 4 h | 21–23 Nov |
| 7 E6, robustness | `populations.py`, the E6 and robustness cells, `tab3_robustness.py`. | Pierre-Loup (E6), Vincent (robustness) | 3 h | 24–25 Nov |

**Built so far:** stages 1 to 5. The four parts of stage 3 were written in one tree, so
stage 4 had no merge to do. Stage 5 built the harness, the cells of E0 to E3 and the first
three figures; its runs are at the end of this section and are provisional, since E0 is not
met. Next are stage 6 (E4, E5, Morris) and the group's decision on the rules.

**First read after stage 3** (20 seeds a cell, 10 November; a look, not a result):

| Cell | Unit-cost label wins | Capacity / demand at the end | Price / price of production | Industry rate | Firms at the end | Time a run |
| --- | --- | --- | --- | --- | --- | --- |
| Mixed, defaults | 20 of 20 | 1.49 | 1.44 | 0.090 | 30 | 0.12 s |
| Control, all unit-cost | 8 of 20 | 1.44 | 1.43 | 0.081 | 33 | 0.11 s |
| Control, all profit-rate | 11 of 19, 1 tie | 1.18 | 1.32 | 0.087 | 26 | 0.14 s |
| Mixed, no technical change | 20 of 20 | 1.44 | 1.25 | 0.086 | 31 | 0.05 s |
| Mixed, r̄ = 0.16 | 19 of 20 | 1.24 | 1.16 | 0.149 | 15 | 0.08 s |
| Mixed, systematic cutting | 15 of 20 | 1.32 | 1.46 | 0.093 | 30 | 0.15 s |

- **The industry cycles.** In seed 0 the price falls from 100 to 77 in 13 periods, r_new drops
  below r̄, the reserves of the plants that retire are withdrawn and none is replaced: capacity
  falls from 1.48 to 0.65 times demand in seven periods. The shortage then lifts the price to
  145 in six periods, entry occurs every period and capacity overshoots to 2.08 times demand;
  the price needs 33 periods of cuts to come back. Nearly half of the plants leave idle.
- **Against the pilot** (arm 4): price over the price of production 1.25–1.46 against
  0.93–1.11, capacity over demand 1.2–1.5 against 0.99–1.09, about 30 firms against 6 to 8, the
  profit-rate hurdle 0.23 against 0.06–0.08. The industry rate at r̄ = 0.16 matches (0.149).
  The pilot kept overtime, which absorbs a shortage, and left the withdrawn reserve in cash.
- **Consequences.** The E0 thresholds of section 7 are not met at the defaults. Without
  technical change the unit-cost label still wins 20 of 20, where v2 found drift: the price
  stays above 85, where the profit-rate rule prefers D1. No plant left through the
  operating-cost test (Q18). The rules are those of the specification; whether to change one
  is for the group, before E1 is read.
- **Speed.** 0.12 s a run at the defaults against the target of 0.11: the public menu holds
  about 140 techniques at the end.

**Stage 4** (10 November).

- **Neutrality.** With the labels swapped and every firm on its rule, trajectories are identical
  and the period table is its mirror image, over 200 periods in the three populations and over
  80 periods in a second cell (systematic cutting, accelerator, categories, r̄ = 0.16, growth).
  Reversing the list of firms changes nothing. The source reads a label only at entry and in
  the outputs, a rule only to look up the hurdle, and a serial number only to draw a parent and
  to name a design.
- **Speed.** With `frontier`, a run at the defaults takes 0.087 s, the controls 0.09–0.10 s and
  the categories rule 0.11 s; 30 initial firms take 0.22 s. Under the Marx-biased set most
  designs are on the frontier, so the public menu still holds 50 to 90 techniques at the end.
- **E0 on 20 seeds** (no technical change, single-rule populations), against the thresholds of
  section 7:

| Measure | Threshold | All unit-cost | All profit-rate |
| --- | --- | --- | --- |
| Periods in which the price leader has the lowest unit cost | at least 0.9 | 1.00 | 1.00 |
| Seeds with capacity at the end within 0.9–1.2 of demand | at least 18 of 20 | 0 (mean 1.58) | 0 (mean 2.52) |
| Price over the price of production | 0.9–1.2 | 1.16 | 1.41 |
| Industry profit rate | 0.03–0.10 | 0.044 | 0.077 |
| Spread of profit rates across firms | above 0 | 0.12 | 0.19 |
| Seeds ending without capacity | 0 | 0 | 0 |
| Firms at the end; entries; utilisation; periods with a cut | for information | 43; 136; 0.62; 0.01 | 70; 180; 0.47; 0.09 |

- **E0 is not met**: on capacity in both populations, and on the price in one. Without
  technical change every firm ends on the same technique, so no firm has a cost edge and almost
  no period has a cut. Entry, not the price, absorbs the profit above r̄, and it does so through
  idle capacity.
- **Plants leaving by reason (Q18).** At the defaults 54 % leave by age and 46 % idle; none
  leaves through the cost test. Under `scrap_cost="unit_cost"` the 20 runs are identical to the
  defaults: that test never binds either, so the robustness check on scrapping would show no
  difference as things stand.

**Diagnosis** (10 November; `python -m experiments.diagnosis`, 19 variants, four cells each, 20
seeds). Each variant changes one parameter or patches one rule from the script; no file of the
model is changed. Two different things are at work.

*1. Without technical change, cost-edge cutting stops after two periods.* In E0 the firms on D1
and D2 cut in periods 0 and 1. From period 2 every firm owns a plant on D2, so every best-plant
unit cost is 75.0, no firm has an edge, and the price stays at 96.04 to the end: 1.16 times the
price of production (82.89). Nothing in the rule lowers a price when capacity is idle. The
profit above r̄ is then absorbed by quantity: entry and reinvestment add capacity until idle
plants bring r_new down to r̄. No parameter moves this: with an entry speed of 0.2 capacity is
still 1.65 times demand. Under systematic cutting the price does fall, and E0 then cycles like
the other cells. So E0 cannot meet a capacity or price threshold under cost-edge cutting.

*2. With technical change, or under systematic cutting, the industry cycles.* Mixed population,
measures from period 20, means over 20 seeds (minimum and maximum are those of each run):

| Variant | Capacity / demand, mean (min–max) | Price / price of production, mean (max) | Periods with lost demand | Industry rate | Unit-cost label wins, of 20 |
| --- | --- | --- | --- | --- | --- |
| Defaults | 1.42 (0.55–2.27) | 1.46 (2.98) | 0.17 | 0.09 | 20 |
| Shortage step 0.1 | 1.09 (0.37–1.77) | 1.18 (1.70) | 0.39 | 0.07 | 16 |
| Entry speed 1 | 1.35 (0.60–2.00) | 1.33 (2.33) | 0.18 | 0.08 | 20 |
| Accelerator | 1.32 (0.54–1.81) | 1.59 (3.58) | 0.16 | 0.12 | 11 |
| Reserve always released | 1.04 (0.88–1.25) | 0.88 (1.17) | 0.34 | 0.01 | 16, and 3 ties |
| Reserve never released | 1.34 (0.65–2.05) | 1.83 (3.01) | 0.21 | 0.21 | 8 |
| Withdrawn reserve left in cash | the same runs as the defaults | | | | |
| Overtime to 1.2 | 1.21 (0.64–1.96) | 1.20 (2.00) | 0.05 | 0.07 | 17 |
| Overtime, shortage step 0.25 | 1.09 (0.61–1.65) | 1.10 (1.56) | 0.09 | 0.06 | 18 |
| Overtime, step 0.25, entry speed 1 | 1.06 (0.68–1.47) | 1.06 (1.34) | 0.08 | 0.06 | 16 |
| Pilot, arm 4 (v2, 200 seeds) | 0.99–1.09 | 0.93–1.11 | | 0.06 | 0.94–0.97 of seeds |

- **The reserve condition makes the cycle.** When r_new falls below r̄ no plant that retires is
  replaced, and capacity falls by about a tenth a period until demand is lost. With the reserve
  always released there is no cycle, but the rate falls to 0.01 and the price below the price of
  production, as in arm 2 of the pilot.
- **The absence of overtime and the shortage step amplify it.** With output up to 1.2 times
  normal capacity, periods with lost demand fall from 0.17 to 0.05 and the highest price from
  2.98 to 2.00 times the price of production. A smaller shortage step alone lowers the price
  but lengthens the shortages (0.39 of periods).
- **Overtime with a shortage step of 0.25 comes close to the pilot**: capacity at 1.06 to 1.09
  times demand, the price at 1.06 to 1.10 times the price of production, a rate of 0.06.
- **Not drivers.** Leaving the withdrawn reserve in cash gives the same runs (the funds never
  held it). A smaller entrant, idle scrapping after 4 periods, a price cut of 0.05 and a
  shortage counted only above 1.2 times capacity do not help, or make it worse.
- **The headline moves with these choices.** The unit-cost label wins 20 of 20 at the defaults,
  16 to 18 with overtime, 11 under the accelerator and 8 with the reserve never released. On 20
  seeds a share has an interval of about ± 0.2, so only the last two differ clearly from 20.
- **For the group.** Three questions: whether to restore overtime and lower the shortage step
  (about 8 lines, with the model at 769 of 770, and a reversal of the decision of 9 November);
  what E0 should check, since under cost-edge cutting the price cannot reach the price of
  production; and whether a cycle of this size is acceptable if no rule changes.

**Stage 5** (10 November).

- **Harness.** `experiments/harness.py` uses the standard library only (`csv`, not pandas), so
  it runs wherever the model does. `runs.csv` and `cells.csv` are as section 7 describes; the
  number of workers does not change a row, and a run stopped and resumed gives the same file.
  A run that raises is reported in its row and counts in no share.
- **Figures.** `figures/style.py` and the scripts of figures 1 to 3 write a PDF and a PNG to
  `outputs/figures/`. They need matplotlib. Blue is the unit-cost label in every figure and
  orange the profit-rate label; two levels of r̄ take two steps of one blue.
- **Runs of E0 to E3** (17,200 runs in 4 min 36 s on 10 workers, commit `ab52ab5` plus the
  harness). Share of seeds won by the unit-cost label, with its 95 % Wilson interval:

| Experiment | Cell | Mixed | Control, all unit-cost | Control, all profit-rate | Beyond drift |
| --- | --- | --- | --- | --- | --- |
| E0, 50 seeds | no technical change | | 0.52 (0.39–0.65) | 0.42 (0.29–0.56) | |
| E1, 500 seeds | defaults | 0.98 (0.97–0.99) | 0.52 (0.47–0.56) | 0.50 (0.46–0.54) | yes |
| E2, 200 seeds | β = 0 | 0.58 (0.51–0.64) | 0.45 | 0.49 | no |
| | β = 0.5 | 0.92 (0.88–0.95) | 0.49 | 0.50 | yes |
| | β = 1.5 | 0.98 (0.95–0.99) | 0.52 | 0.49 | yes |
| | β = 3 | 0.98 (0.96–0.99) | 0.47 | 0.47 | yes |
| | neutral set | 0.82 (0.76–0.87) | 0.47 | 0.52 | yes |
| | no draws | 1.00 (0.98–1.00) | 0.46 | 0.49 | yes |

| E3, 200 seeds, mixed | λ = 0 | 0.25 | 0.5 | 0.75 | 1 |
| --- | --- | --- | --- | --- | --- |
| Cost-edge cutting, r̄ = 0.05 | 0.98 | 0.98 | 0.93 | 0.84 | 0.68 |
| Mean hurdle of the profit-rate label, same cells | 0.204 | 0.157 | 0.121 | 0.084 | 0.050 |
| Systematic cutting, r̄ = 0.05 | 0.61 | 0.52 | 0.54 | 0.41 | 0.48 |
| Cost-edge cutting, r̄ = 0.16 | 0.88 | 0.94 | 0.95 | 0.96 | 0.97 |
| Systematic cutting, r̄ = 0.16 | 0.04 | 0.03 | 0.03 | 0.06 | 0.12 |

- **The two statistical checks of section 8 hold.** Both controls of E1 have an interval that
  contains one half. In each control the reserve is released for the same share of plants
  under the two labels (0.80 and 0.80, then 0.82 and 0.82).
- **What stands out, for the group.** The mixed population is beyond drift at the defaults,
  with a mean final capacity share of 0.89 (pilot: 0.94–0.97 and 0.72–0.79). Without draws
  the unit-cost label wins every seed, where v2 found drift (0.51): the price stays above 85,
  where the profit-rate rule prefers D1. The share won falls with λ at r̄ = 0.05 and rises
  with it at 0.16. Under systematic cutting at r̄ = 0.16 the profit-rate label wins (pilot:
  0.10–0.19). None of this is a result before the group has decided on the rules.

**E0 to E3 under leader-follow pricing** (10 November; an analysis variant, registered in
`v3-choices.md`. No file of the model is changed and none of this is a result).

- **The rule.** `python -m experiments.price_rules leader_follow` runs the cells of E0 to E3 on
  their seeds with v2's leader-follow rule in place of step 1, its floor at the unit cost of
  the firm's best plant. L is the lowest price posted last period by a firm with a plant in
  operation. After excess demand every firm posts 1.03 L; otherwise every firm posts 0.98 L,
  or its floor if that is higher, whatever its utilisation; a firm alone raises its price by
  3 % a period up to 3 times its floor. It is not v3's systematic cutting, which cuts only
  with spare capacity, keeps a firm's own price when it is lower and uses the common shortage
  step. The same script runs systematic cutting in every cell of E0 to E2 (E3 holds it
  already). The label-swap and firm-order tests pass under the rule, and it returns what v2's
  function returns.
- **Runs.** 11,200 under leader-follow in 2 min 15 s and 5,200 under systematic cutting in
  1 min 27 s, on 10 workers, commit `0c7fa09`, no error. Files in `outputs/leader_follow/` and
  `outputs/systematic/`; figures `fig2_typical_run_leader_follow` and
  `fig3_bias_lambda_leader_follow`.
- **E0** (50 seeds; each cell gives all unit-cost / all profit-rate):

| Measure | Threshold | Cost-edge (stage 5) | Systematic | Leader-follow |
| --- | --- | --- | --- | --- |
| Periods in which the price leader has the lowest unit cost | at least 0.9 | 1.00 / 1.00 | 1.00 / 0.98 | 1.00 / 1.00 |
| Seeds with capacity at the end within 0.9–1.2 of demand | at least 45 of 50 | 0 / 1 | 7 / 2 | 10 / 13 |
| Capacity over demand at the end, mean (range over seeds) | | 1.57 (1.36–1.75) / 2.35 (1.16–2.85) | 1.95 (0.62–2.70) / 1.91 (0.74–2.82) | 1.06 (0.15–1.90) / 1.12 (0.30–1.81) |
| Price over the price of production | 0.9–1.2 | 1.16 / 1.37 | 1.57 / 1.54 | 1.15 / 1.13 |
| Industry profit rate | 0.03–0.10 | 0.044 / 0.072 | 0.143 / 0.155 | 0.078 / 0.077 |
| Spread of profit rates across firms | above 0 | 0.12 / 0.18 | 0.21 / 0.22 | 0.065 / 0.063 |
| Seeds ending without capacity | 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Share of demand lost over the run | for information | 0.000 / 0.006 | 0.042 / 0.041 | 0.140 / 0.128 |
| Utilisation; periods with a cut; firms at the end | for information | 0.62; 0.01; 43 / 0.51; 0.09; 65 | 0.54; 0.86; 36 / 0.54; 0.85; 35 | 0.77; 0.60; 24 / 0.79; 0.60; 24 |

- **The cycle**, in the measures of the diagnosis (20 seeds, from period 20; minimum and maximum
  are those of each run; the demand lost is over the whole run):

| Rule | Cell | Capacity / demand, mean (min–max) | Price / price of production, mean (max) | Periods with lost demand | Demand lost | Industry rate |
| --- | --- | --- | --- | --- | --- | --- |
| Cost-edge | E0, all unit-cost | 1.62 (1.28–1.93) | 1.16 (1.16) | 0.00 | 0.000 | 0.044 |
| | mixed, defaults | 1.42 (0.55–2.27) | 1.46 (2.98) | 0.17 | 0.034 | 0.090 |
| Systematic | E0, all unit-cost | 1.85 (0.46–2.71) | 1.59 (2.91) | 0.12 | 0.042 | 0.139 |
| | mixed, defaults | 1.50 (0.54–2.32) | 1.49 (3.04) | 0.16 | 0.035 | 0.093 |
| Leader-follow | E0, all unit-cost | 1.12 (0.27–1.94) | 1.16 (1.54) | 0.40 | 0.140 | 0.078 |
| | mixed, defaults | 1.07 (0.34–1.69) | 1.15 (1.58) | 0.38 | 0.088 | 0.063 |

- **E1 and E2.** Share of seeds won by the unit-cost label in the mixed population, with its
  95 % Wilson interval; the last two columns are for leader-follow:

| Experiment | Cell | Cost-edge (stage 5) | Systematic | Leader-follow | Its two controls | Beyond drift |
| --- | --- | --- | --- | --- | --- | --- |
| E1, 500 seeds | defaults | 0.98 (0.97–0.99) | 0.56 (0.52–0.61) | 0.49 (0.45–0.53) | 0.49 and 0.52 | no |
| E2, 200 seeds | β = 0 | 0.58 (0.51–0.64) | 0.52 (0.45–0.59) | 0.49 (0.42–0.56) | 0.48 and 0.47 | no |
| | β = 0.5 | 0.92 (0.88–0.95) | 0.56 (0.49–0.62) | 0.47 (0.40–0.54) | 0.57 and 0.52 | no |
| | β = 1.5 | 0.98 (0.95–0.99) | 0.61 (0.54–0.67) | 0.53 (0.46–0.59) | 0.50 and 0.51 | no |
| | β = 3 | 0.98 (0.96–0.99) | 0.58 (0.51–0.65) | 0.57 (0.49–0.63) | 0.46 and 0.47 | no |
| | neutral set | 0.82 (0.76–0.87) | 0.67 (0.61–0.73) | 0.51 (0.44–0.58) | 0.51 and 0.53 | no |
| | no draws | 1.00 (0.98–1.00) | 0.79 (0.73–0.84) | 0.73 (0.67–0.79) | 0.48 and 0.43 | yes |

  Under systematic cutting only the neutral set and "no draws" are beyond drift; E1 is not
  (controls 0.48 and 0.52). Under leader-follow the mean final capacity share of the
  unit-cost label in E1 is 0.50.
- **E3** (200 seeds, mixed population):

| Share won by the unit-cost label | λ = 0 | 0.25 | 0.5 | 0.75 | 1 |
| --- | --- | --- | --- | --- | --- |
| Leader-follow, r̄ = 0.05 | 0.53 | 0.47 | 0.46 | 0.50 | 0.51 |
| Mean hurdle of the profit-rate label, same cells | 0.096 | 0.084 | 0.072 | 0.061 | 0.050 |
| Leader-follow, r̄ = 0.16 | 0.08 | 0.13 | 0.10 | 0.11 | 0.15 |
| Mean hurdle of the profit-rate label, same cells | 0.193 | 0.191 | 0.188 | 0.184 | 0.181 |
| Systematic, r̄ = 0.05 (stage 5) | 0.61 | 0.52 | 0.54 | 0.41 | 0.48 |
| Systematic, r̄ = 0.16 (stage 5) | 0.04 | 0.03 | 0.03 | 0.06 | 0.12 |
| Cost-edge, r̄ = 0.05 (stage 5) | 0.98 | 0.98 | 0.93 | 0.84 | 0.68 |
| Cost-edge, r̄ = 0.16 (stage 5) | 0.88 | 0.94 | 0.95 | 0.96 | 0.97 |

  Under leader-follow no cell is beyond drift at r̄ = 0.05 and all five are at r̄ = 0.16, on
  the side of the profit-rate label.
- **Against the pilot** (arm 4, whose systematic cells are this rule in v2):

| Measure | Pilot, arm 4 | v3 under leader-follow |
| --- | --- | --- |
| Share won, r̄ = 0.05 | drift | 0.46–0.53, no cell beyond drift |
| Share won, r̄ = 0.16 | 0.10–0.19 | 0.08–0.15 |
| Industry profit rate | 0.06 at r̄ = 0.05; 0.14–0.15 at 0.16 | 0.06; 0.14 |
| Price over the price of production | 0.93–1.11 | 1.13–1.15 at r̄ = 0.05; 1.02 at 0.16 |
| Capacity over demand | 0.99–1.09 | at the end, 1.01–1.05 at r̄ = 0.05; 1.01–1.09 at 0.16 |
| Hurdle of the profit-rate label, r̄ = 0.05 | 0.06–0.08 | 0.096 |
| Its orders that are not the cheapest technique, r̄ = 0.05 | 0.46–0.65 | 0.64 |
| Entries a run | 47–140 | 126–127; 63–66 at r̄ = 0.16 |
| Plants whose reserve is released, by label | 0.74 and 0.76 at r̄ = 0.05; 0.38 and 0.40 at 0.16 | 0.68 and 0.68; 0.35 and 0.37 |

- **E0 is met on the price and the profit rate, not on capacity.** The price is within 0.9–1.2
  of the price of production in 49 and 50 of the 50 seeds and the rate is 0.08. Capacity is
  right on average (1.06 and 1.12 at the end) but ends within the band in 10 and 13 seeds of
  50: the industry still cycles, between 0.27 and 1.94 times demand in an average run.
- **The cycle changes shape: less overcapacity, long shortages.** Demand is lost in 0.40 of
  periods and 13 to 14 % of it over a run (none under cost-edge cutting in E0, 3 % at the
  defaults). In the run kept (E0, seed 0) the price falls 2 % a period from 98; at period 6
  new plants earn less than r̄, the reserves are withdrawn and entry stops, and capacity
  falls from 1.63 to 0.30 times demand in nine periods. In the shortage the price rises by
  only 3 % a period, from 77 to 120 over fifteen periods, with up to 70 % of demand lost,
  while capacity is rebuilt and then overshoots to 1.87.
- **The headline disappears.** At the defaults the unit-cost label wins 0.49 of seeds, as in
  the controls, and no E2 cell with draws is beyond drift (0.47 to 0.57). Every firm posts the
  same price unless its floor binds (in the mixed run kept the two labels' prices are equal in
  every period), so a cost advantage no longer moves market shares through the price. The
  price is also lower, so the hurdle of the profit-rate label is 0.096 against 0.205 and 64 %
  of its orders are not the cheapest technique, against 88 %. Only "no draws" is beyond drift
  (0.73).
- **At r̄ = 0.16 the profit-rate label wins** (the unit-cost label wins 0.08 to 0.15 of seeds),
  as under v3's systematic cutting (0.03 to 0.12) and in the pilot (0.10 to 0.19).
- **λ moves nothing under this rule.** The share won is flat at both levels of r̄, although
  the hurdle falls from 0.096 to 0.050 at r̄ = 0.05.
- **Checks.** Both E1 controls have an interval that contains one half (0.45–0.54 and
  0.48–0.57), and in each control the reserve is released for the same share of plants under
  the two labels (0.68 and 0.68).
- **For the group.** The price rule decides the headline: 0.98 under cost-edge cutting, drift
  under both versions of systematic cutting at r̄ = 0.05, and a win of the profit-rate label
  at r̄ = 0.16. Leader-follow brings E0 and the pilot's reference numbers closest, at the cost
  of long shortages. Adopting it is a departure from the specification (its own shortage
  rule, a cut without spare capacity, the monopoly cap) and about ten lines in a model that
  stands at 769 of 770.

**Why the unit-cost label stops winning under leader-follow** (10 November; read from the run
files of E1 to E3 and from 50 seeds of the mixed population; no new rule).

| Mixed population at the defaults | Cost-edge | Systematic | Leader-follow |
| --- | --- | --- | --- |
| Share of seeds won by the unit-cost label | 0.98 | 0.56 | 0.49 |
| Its final capacity share | 0.89 | 0.56 | 0.50 |
| Change in its sales share through the price (the replicator) | +0.27 | +0.02 | 0.00 |
| Change in its sales share through entry and exit | +0.14 | +0.05 | 0.00 |
| Change in its capacity share through orders and retirements | +0.24 | +0.03 | 0.00 |
| Realised profit rate, unit-cost / profit-rate label | 0.079 / 0.099 | 0.083 / 0.104 | 0.061 / 0.064 |
| Hurdle of the profit-rate label; its orders that are not the cheapest | 0.205; 0.88 | 0.222; 0.90 | 0.096; 0.64 |
| Periods in which the two labels post different prices (50 seeds) | 0.81 | | 0.00 |
| Mean unit cost, unit-cost / profit-rate label (50 seeds) | 57.6 / 63.4 | | 57.6 / 58.7 |
| Mean κ, unit-cost / profit-rate label (50 seeds) | 246 / 178 | | 231 / 209 |

- **A lower unit cost is not a higher profit rate.** The designs the unit-cost rule adopts
  lower the unit cost and raise κ. Above the price of production they earn a lower rate than
  the techniques the profit-rate rule keeps: under cost-edge cutting the unit-cost label
  earns 0.079 against 0.099, and 0.087 against 0.112 in the 95 % of periods with the price
  above the price of production. It wins 0.98 of seeds all the same.
- **Under cost-edge cutting it wins through the price.** Only a firm with a cost edge cuts,
  and a rival at its floor cannot follow, so the two labels post different prices in 0.81 of
  periods. The replicator then moves 0.27 of the market to the unit-cost label, and entrants,
  who inherit a label in proportion to market shares, add 0.14.
- **Leader-follow closes that channel.** Every firm posts 0.98 L, or 1.03 L after a shortage,
  whatever its cost, so the two labels post the same price in every period and the replicator
  term is exactly 0. The price level follows the capacity cycle, not the lowest unit cost.
- **Nothing else can carry a cost advantage.** In this model a market share moves only through
  a price difference or through entry and exit. Sales are rationed by share, so capacity
  beyond a firm's share stays idle and is scrapped; and entrants draw their label from the
  market shares, which is a random walk. Hence drift.
- **The two rules also differ less.** The price is lower (1.13 against 1.37 times the price of
  production), so the hurdle of the profit-rate label is 0.096 against 0.205 and it adopts
  more of the cost-reducing designs: the gap in unit cost between the labels is 2 % against
  9 %.
- **At r̄ = 0.16 the profit-rate label wins by accumulation.** The price never comes within 13 %
  of a unit cost, so the industry stays in the conflict zone: the profit-rate label earns
  more below the price of production (0.127 against 0.114) and above it (0.160 against
  0.152), and its plants cost less per unit of capacity (κ of 178 against 218). It orders
  more capacity (0.36 of the capacity share), sells the overflow in shortages and gains by
  entry (0.07 of sales share).
- **"No draws" is the exception, and not explained.** The unit-cost label wins 0.73 there, by
  entry and exit (+0.15 of sales share) and by retirements of the other label's plants
  (+0.27 of capacity share), not by the price (0.00). The reason has not been isolated.

**Leader-follow with the operating-cost floor** (10 November; the same analysis variant,
`python -m experiments.price_rules leader_follow_ucs`; E0 on commit `5d31fec`, 100 runs, no
error).

- **The floor.** v2's `LEADER_FOLLOW_FLOOR = "operating_cost"`, as its documents define it: the
  operating cost ucs of the dearest plant the firm ran last period, or of its cheapest plant
  if none ran. On the initial menu it is 59.21 to 64.25, against a unit-cost floor of 75.0 to
  78.0. The label-swap and firm-order tests pass under it.
- **E0** (50 seeds; each cell gives all unit-cost / all profit-rate):

| Measure | Threshold | Unit-cost floor | Operating-cost floor |
| --- | --- | --- | --- |
| Periods in which the price leader has the lowest unit cost | at least 0.9 | 1.00 / 1.00 | 1.00 / 1.00 |
| Seeds with capacity at the end within 0.9–1.2 of demand | at least 45 of 50 | 10 / 13 | 13 / 13 |
| Capacity over demand at the end, mean (range over seeds) | | 1.06 (0.15–1.90) / 1.12 (0.30–1.81) | 1.06 (0.27–1.90) / 1.12 (0.30–1.87) |
| Price over the price of production | 0.9–1.2 | 1.15 / 1.13 | 1.15 / 1.13 |
| Industry profit rate | 0.03–0.10 | 0.078 / 0.077 | 0.078 / 0.077 |
| Spread of profit rates across firms | above 0 | 0.065 / 0.063 | 0.064 / 0.063 |
| Seeds ending without capacity | 0 | 0 / 0 | 0 / 0 |
| Share of demand lost over the run | for information | 0.140 / 0.128 | 0.141 / 0.127 |
| Periods with lost demand, from period 20 (20 seeds) | for information | 0.40 / 0.40 | 0.40 / 0.40 |
| Utilisation; periods with a cut; firms at the end | for information | 0.77; 0.60; 24 / 0.79; 0.60; 24 | 0.78; 0.60; 23 / 0.79; 0.60; 24 |
| Plants leaving through the cost test | for information | none | none |

- **The floor does not matter in E0.** 39 and 30 of the 50 seeds give the same run under the
  two floors, and the others differ from period 73 and 23 at the earliest. The lowest price
  is at the unit-cost floor in 0.1 and 0.3 % of periods under the first, and below the lowest
  unit cost (75.0) in as many under the second, where it reaches 74.0 and 71.1 at the lowest.
- **The shortage stops the price before the floor does.** Once new plants earn less than r̄
  the reserves are withdrawn and capacity falls by about a tenth a period, so demand exceeds
  capacity about six periods later, when the price is near 77: the price then rises again.
  The lowest price of a run is 76.1 and 75.5 on average. The cycle, the lost demand and the
  thresholds met (price, profit rate) and not met (capacity) are those of the unit-cost floor.
- **v2's collapse does not occur.** There the operating-cost floor left 81 of 200 seeds
  without capacity; here no seed ends without capacity.
- **E1 to E3 under this floor** (11,100 runs in 2 min 19 s on 10 workers, commit `7453a9c`, no
  error). Share of seeds won by the unit-cost label in the mixed population; the last column
  counts the runs of the three populations that are the same under the two floors:

| Experiment | Cell | Unit-cost floor | Operating-cost floor | Identical runs |
| --- | --- | --- | --- | --- |
| E1, 500 seeds | defaults | 0.49 (0.45–0.53) | 0.49 (0.44–0.53) | 1,340 of 1,500 |
| E2, 200 seeds | β = 0 | 0.49 (0.42–0.56) | 0.49 (0.42–0.56) | 322 of 600 |
| | β = 0.5 | 0.47 (0.40–0.54) | 0.47 (0.40–0.54) | 437 of 600 |
| | β = 1.5 | 0.53 (0.46–0.59) | 0.52 (0.45–0.59) | 541 of 600 |
| | β = 3 | 0.57 (0.49–0.63) | 0.57 (0.50–0.64) | 562 of 600 |
| | neutral set | 0.51 (0.44–0.58) | 0.48 (0.41–0.55) | 403 of 600 |
| | no draws | 0.73 (0.67–0.79) | 0.72 (0.66–0.78) | 405 of 600 |
| E3, r̄ = 0.05 | λ = 0, 0.25, 0.5, 0.75, 1 | 0.53, 0.47, 0.46, 0.50, 0.51 | 0.52, 0.48, 0.45, 0.50, 0.49 | 2,786 of 3,000 |
| E3, r̄ = 0.16 | λ = 0, 0.25, 0.5, 0.75, 1 | 0.08, 0.13, 0.10, 0.11, 0.15 | 0.08, 0.13, 0.10, 0.11, 0.15 | 3,000 of 3,000 |

- **Nothing moves.** No share won changes by more than 0.03 and every verdict is the same:
  only "no draws" and the five cells at r̄ = 0.16 are beyond drift. In the mixed population
  the outcome of a seed changes in 2 of 500 runs of E1 and in at most 14 of 200 in a cell of
  E2. The price, capacity, profit rate and lost demand of E1 are those of the unit-cost floor
  (1.13 times the price of production, 1.03 times demand, 0.063, 0.086), and no plant leaves
  through the cost test.
- **The floor binds even less with technical change.** On 50 seeds of the mixed population
  under the operating-cost floor, a firm posts below its unit cost in 0.06 % of periods at
  the defaults, by 1.6 % at most, and in 0.25 % with the neutral set, by 4.1 % at most. At
  r̄ = 0.16 the price never comes within 13 % of a unit cost, so the runs are the same.
- **A property of v2's rule seen on the way.** Its floor applies to a cut only: after excess
  demand a firm posts 1.03 L even when that is below its floor. Under the unit-cost floor
  this happens in 0.01 % of periods with the neutral set, by 1.2 % at most.

**Leader-follow with overtime without a premium** (10 November; the same analysis variant,
`python -m experiments.price_rules leader_follow_overtime` and `leader_follow_ucs_overtime`).

- **The variant.** A firm sells up to 1.2 times the capacity it offers; its plants run to
  normal capacity cheapest first, then youngest, and what is left runs as overtime in the same
  order, at the same operating cost. Excess demand stays demand above normal capacity, so the
  price rises at the same signal as before. These are the functions of the diagnosis
  ("overtime to 1.2"), moved to `price_rules.py`. The label-swap and firm-order tests pass.
- **Runs.** 11,200 under each floor, in 2 min 23 s and 2 min 15 s on 10 workers, commit
  `0cb2e69`, no error. Figures `fig2_typical_run_leader_follow_overtime` and
  `fig3_bias_lambda_leader_follow_overtime`.
- **E0** (50 seeds; each cell gives all unit-cost / all profit-rate):

| Measure | Threshold | No overtime | Overtime | Overtime, operating-cost floor |
| --- | --- | --- | --- | --- |
| Periods in which the price leader has the lowest unit cost | at least 0.9 | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| Seeds with capacity at the end within 0.9–1.2 of demand | at least 45 of 50 | 10 / 13 | 20 / 20 | 20 / 22 |
| Capacity over demand at the end, mean (range over seeds) | | 1.06 (0.15–1.90) / 1.12 (0.30–1.81) | 1.02 (0.24–1.63) / 1.10 (0.24–1.81) | 1.02 (0.18–1.66) / 1.08 (0.18–1.84) |
| Price over the price of production | 0.9–1.2 | 1.15 / 1.13 | 1.06 / 1.07 | 1.06 / 1.07 |
| Industry profit rate | 0.03–0.10 | 0.078 / 0.077 | 0.067 / 0.069 | 0.067 / 0.071 |
| Spread of profit rates across firms | above 0 | 0.065 / 0.063 | 0.076 / 0.078 | 0.076 / 0.078 |
| Seeds ending without capacity | 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Share of demand lost over the run | for information | 0.140 / 0.128 | 0.041 / 0.053 | 0.040 / 0.060 |
| Utilisation; periods with a cut; firms at the end | for information | 0.77; 0.60; 24 / 0.79; 0.60; 24 | 0.91; 0.60; 23 / 0.90; 0.60; 23 | 0.91; 0.61; 23 / 0.90; 0.61; 22 |

- **The cycle** (unit-cost floor; 20 seeds, from period 20; minimum and maximum are those of
  each run; the demand lost is over the whole run):

| Rule | Cell | Capacity / demand, mean (min–max) | Price / price of production, mean (max) | Periods with lost demand | Demand lost | Industry rate | Periods with overtime |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No overtime | E0, all unit-cost | 1.12 (0.27–1.94) | 1.16 (1.54) | 0.40 | 0.140 | 0.078 | |
| | mixed, defaults | 1.07 (0.34–1.69) | 1.15 (1.58) | 0.38 | 0.088 | 0.063 | |
| Overtime | E0, all unit-cost | 1.05 (0.40–1.74) | 1.07 (1.35) | 0.21 | 0.038 | 0.067 | 0.40 |
| | mixed, defaults | 1.03 (0.60–1.41) | 1.05 (1.27) | 0.11 | 0.013 | 0.056 | 0.36 |

- **E1 to E3.** Share of seeds won by the unit-cost label, mixed population:

| Experiment | Cell | No overtime | Overtime | Overtime, operating-cost floor |
| --- | --- | --- | --- | --- |
| E1, 500 seeds | defaults | 0.49 (0.45–0.53) | 0.50 (0.45–0.54) | 0.49 (0.45–0.54) |
| E2, 200 seeds | β = 0 | 0.49 (0.42–0.56) | 0.48 (0.41–0.56) | 0.42 (0.35–0.49) |
| | β = 0.5 | 0.47 (0.40–0.54) | 0.43 (0.36–0.50) | 0.44 (0.37–0.51) |
| | β = 1.5 | 0.53 (0.46–0.59) | 0.47 (0.40–0.54) | 0.48 (0.41–0.55) |
| | β = 3 | 0.57 (0.49–0.63) | 0.47 (0.40–0.54) | 0.49 (0.42–0.56) |
| | neutral set | 0.51 (0.44–0.58) | 0.47 (0.40–0.54) | 0.53 (0.46–0.59) |
| | no draws | 0.73 (0.67–0.79) | 0.73 (0.66–0.79) | 0.71 (0.64–0.77) |
| E3, r̄ = 0.05 | λ = 0, 0.25, 0.5, 0.75, 1 | 0.53, 0.47, 0.46, 0.50, 0.51 | 0.47, 0.50, 0.42, 0.41, 0.48 | 0.48, 0.49, 0.43, 0.41, 0.48 |
| E3, r̄ = 0.16 | λ = 0, 0.25, 0.5, 0.75, 1 | 0.08, 0.13, 0.10, 0.11, 0.15 | 0.20, 0.16, 0.16, 0.18, 0.17 | 0.20, 0.16, 0.16, 0.18, 0.17 |

- **Against the pilot** (arm 4, which has leader-follow and overtime; unit-cost floor):

| Measure | Pilot, arm 4 | Leader-follow | With overtime |
| --- | --- | --- | --- |
| Share won, r̄ = 0.05 | drift | 0.46–0.53 | 0.41–0.50 |
| Share won, r̄ = 0.16 | 0.10–0.19 | 0.08–0.15 | 0.16–0.20 |
| Industry profit rate | 0.06 at r̄ = 0.05; 0.14–0.15 at 0.16 | 0.06; 0.14 | 0.055; 0.134 |
| Price over the price of production | 0.93–1.11 | 1.13–1.15; 1.02 | 1.05; 0.94–0.95 |
| Capacity over demand | 0.99–1.09 | 1.01–1.05; 1.01–1.09 | 1.01–1.03; 0.99–1.03 |
| Hurdle of the profit-rate label, r̄ = 0.05 | 0.06–0.08 | 0.096 | 0.068 |
| Its orders that are not the cheapest technique, r̄ = 0.05 | 0.46–0.65 | 0.64 | 0.47 |
| Entries a run | 47–140 | 126–127; 63–66 | 120; 45–47 |
| Plants whose reserve is released, by label | 0.74 and 0.76; 0.38 and 0.40 | 0.68 and 0.68; 0.35 and 0.37 | 0.68 and 0.68; 0.34 and 0.35 |

- **Overtime tames the cycle.** The demand lost falls from 14 to 4 % in E0 and from 8.6 to
  1.1 % at the defaults, the periods with lost demand from 0.40 to 0.21 and from 0.38 to
  0.11, and the highest price from 1.54 to 1.35 times the price of production. Firms work
  overtime in 0.4 of periods and utilisation is 0.91 to 0.95.
- **E0 comes closer and is still not met on capacity.** The price is at 1.06 to 1.07 times
  the price of production and the rate at 0.07, in the band in all 50 seeds. Capacity ends
  within the band in 20 seeds of 50, against 10 and 13: it still swings between 0.40 and 1.74
  times demand in an average run.
- **The headline does not change.** At r̄ = 0.05 no cell with draws is beyond drift (0.41 to
  0.50; E1: 0.50, with controls at 0.54 and 0.51, both intervals containing one half). Only
  "no draws" is (0.73). At r̄ = 0.16 the profit-rate label wins, a little less often (the
  unit-cost label wins 0.16 to 0.20). The two labels still post the same price, so the
  replicator term stays at 0.00.
- **The two rules differ even less.** The price is lower, so the hurdle of the profit-rate
  label is 0.068 against 0.096 and 47 % of its orders are not the cheapest technique,
  against 64 %.
- **The floor matters a little more, and still decides nothing.** With overtime the price
  falls lower before the shortage, so fewer runs are the same under the two floors (34 of
  100 in E0, 1,152 of 1,500 in E1, 1,895 of 3,600 in E2). No share won moves by more than
  0.06 and no verdict changes; at r̄ = 0.16 the cells are identical.
- **The pilot's reference numbers are met.** With overtime every measure is inside the
  pilot's range or at its edge, except the released reserves (0.68 against 0.74 to 0.76) and
  the rate at r̄ = 0.16 (0.134 against 0.14 to 0.15). At r̄ = 0.16 the price is below the
  price of production on average (0.94 to 0.95).

**Version 3's own pricing with overtime without a premium** (10 November; the same analysis
variant, `python -m experiments.price_rules overtime`).

- **The variant.** The cells of E0 to E3 as section 7 defines them, E3 with its two regimes,
  and the overtime of the block above: output up to 1.2 times normal capacity at the same
  operating cost, the shortage signal unchanged. The label-swap and firm-order tests pass
  under both regimes.
- **Runs.** 17,200 in 4 min 12 s on 10 workers, commit `080f0e2`, no error. Files in
  `outputs/overtime/`; figures `fig2_typical_run_overtime` and `fig3_bias_lambda_overtime`.
- **E0** (50 seeds; each cell gives all unit-cost / all profit-rate):

| Measure | Threshold | No overtime (stage 5) | Overtime |
| --- | --- | --- | --- |
| Periods in which the price leader has the lowest unit cost | at least 0.9 | 1.00 / 1.00 | 1.00 / 1.00 |
| Seeds with capacity at the end within 0.9–1.2 of demand | at least 45 of 50 | 0 / 1 | 0 / 3 |
| Capacity over demand at the end, mean (range over seeds) | | 1.57 (1.36–1.75) / 2.35 (1.16–2.85) | 1.56 (1.27–1.78) / 1.66 (1.04–2.73) |
| Price over the price of production | 0.9–1.2 | 1.16 / 1.37 | 1.16 / 1.12 |
| Industry profit rate | 0.03–0.10 | 0.044 / 0.072 | 0.043 / 0.047 |
| Spread of profit rates across firms | above 0 | 0.12 / 0.18 | 0.13 / 0.11 |
| Seeds ending without capacity | 0 | 0 / 0 | 0 / 0 |
| Share of demand lost over the run | for information | 0.000 / 0.006 | 0.000 / 0.000 |
| Utilisation; periods with a cut; firms at the end | for information | 0.62; 0.01; 43 / 0.51; 0.09; 65 | 0.61; 0.01; 42 / 0.68; 0.10; 44 |

- **The cycle** (20 seeds, from period 20; minimum and maximum are those of each run; the
  demand lost is over the whole run):

| Regime | Cell | Overtime | Capacity / demand, mean (min–max) | Price / price of production, mean (max) | Periods with lost demand | Demand lost | Industry rate | Periods with overtime |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cost-edge | E0, all unit-cost | no | 1.62 (1.28–1.93) | 1.16 (1.16) | 0.00 | 0.000 | 0.044 | |
| | | yes | 1.63 (1.25–1.93) | 1.16 (1.16) | 0.00 | 0.000 | 0.043 | 0.00 |
| | mixed, defaults | no | 1.42 (0.55–2.27) | 1.46 (2.98) | 0.17 | 0.034 | 0.090 | |
| | | yes | 1.21 (0.64–1.96) | 1.20 (2.00) | 0.05 | 0.006 | 0.069 | 0.23 |
| Systematic | mixed, defaults | no | 1.50 (0.54–2.32) | 1.49 (3.04) | 0.16 | 0.035 | 0.093 | |
| | | yes | 1.25 (0.60–1.99) | 1.23 (2.23) | 0.06 | 0.008 | 0.073 | 0.23 |

- **E1 and E2.** Share of seeds won by the unit-cost label in the mixed population, with its
  95 % Wilson interval; the last two columns are for the runs with overtime:

| Experiment | Cell | No overtime (stage 5) | Overtime | Its two controls | Beyond drift |
| --- | --- | --- | --- | --- | --- |
| E1, 500 seeds | defaults | 0.98 (0.97–0.99) | 0.92 (0.89–0.94) | 0.51 and 0.47 | yes |
| E2, 200 seeds | β = 0 | 0.58 (0.51–0.64) | 0.57 (0.50–0.64) | 0.48 and 0.43 | no |
| | β = 0.5 | 0.92 (0.88–0.95) | 0.75 (0.68–0.81) | 0.51 and 0.51 | yes |
| | β = 1.5 | 0.98 (0.95–0.99) | 0.89 (0.84–0.93) | 0.49 and 0.45 | yes |
| | β = 3 | 0.98 (0.96–0.99) | 0.96 (0.92–0.98) | 0.47 and 0.51 | yes |
| | neutral set | 0.82 (0.76–0.87) | 0.69 (0.62–0.75) | 0.46 and 0.51 | yes |
| | no draws | 1.00 (0.98–1.00) | 0.99 (0.97–1.00) | 0.44 and 0.54 | yes |

- **E3** (200 seeds, mixed population):

| Share won by the unit-cost label | λ = 0 | 0.25 | 0.5 | 0.75 | 1 |
| --- | --- | --- | --- | --- | --- |
| Cost-edge, r̄ = 0.05, no overtime | 0.98 | 0.98 | 0.93 | 0.84 | 0.68 |
| Cost-edge, r̄ = 0.05, overtime | 0.89 | 0.90 | 0.87 | 0.79 | 0.71 |
| Mean hurdle of the profit-rate label, overtime | 0.107 | 0.088 | 0.076 | 0.062 | 0.050 |
| Systematic, r̄ = 0.05, no overtime | 0.61 | 0.52 | 0.54 | 0.41 | 0.48 |
| Systematic, r̄ = 0.05, overtime | 0.57 | 0.53 | 0.54 | 0.48 | 0.40 |
| Cost-edge, r̄ = 0.16, no overtime | 0.88 | 0.94 | 0.95 | 0.96 | 0.97 |
| Cost-edge, r̄ = 0.16, overtime | 0.95 | 0.95 | 0.96 | 0.97 | 0.96 |
| Systematic, r̄ = 0.16, no overtime | 0.04 | 0.03 | 0.03 | 0.06 | 0.12 |
| Systematic, r̄ = 0.16, overtime | 0.05 | 0.05 | 0.04 | 0.05 | 0.07 |

  With overtime the ten cost-edge cells are beyond drift, no systematic cell is at r̄ = 0.05,
  and the five systematic cells at r̄ = 0.16 are, on the side of the profit-rate label.
- **The mixed population at the defaults** (E1):

| Measure | No overtime | Overtime |
| --- | --- | --- |
| Final capacity share of the unit-cost label | 0.89 | 0.78 |
| Price over the price of production | 1.37 | 1.14 |
| Capacity over demand at the end | 1.34 | 1.12 |
| Industry profit rate | 0.083 | 0.063 |
| Utilisation | 0.71 | 0.85 |
| Share of demand lost | 0.032 | 0.005 |
| Hurdle of the profit-rate label; its orders that are not the cheapest | 0.205; 0.88 | 0.105; 0.69 |
| Realised profit rate, unit-cost / profit-rate label | 0.079 / 0.099 | 0.063 / 0.065 |
| Change in its sales share through the price | +0.27 | +0.18 |
| Change in its sales share through entry and exit | +0.14 | +0.11 |

- **Against the pilot** (arm 4; the cells at λ = 0):

| Measure | Pilot, arm 4 | v3's pricing with overtime |
| --- | --- | --- |
| Share won, cost-edge cutting | 0.94–0.97 | 0.92 (E1); 0.95 at r̄ = 0.16 |
| Final capacity share, same cells | 0.72–0.79 | 0.78; 0.75 |
| Share won, systematic cutting, r̄ = 0.05 | drift | 0.57, not beyond drift |
| Share won, systematic cutting, r̄ = 0.16 | 0.10–0.19 | 0.05 |
| Industry profit rate | 0.06 at r̄ = 0.05; 0.14–0.15 at 0.16 | 0.064–0.066; 0.140–0.146 |
| Price over the price of production | 0.93–1.11 | 1.15–1.16; 1.02–1.06 |
| Capacity over demand | 0.99–1.09 | 1.14–1.17; 1.11–1.19 |
| Hurdle of the profit-rate label, r̄ = 0.05 | 0.06–0.08 | 0.107 |
| Its orders that are not the cheapest technique, r̄ = 0.05 | 0.46–0.65 | 0.68 |
| Entries a run | 47–140 | 124–125; 53–61 |
| Plants whose reserve is released, by label | 0.74 and 0.76; 0.38 and 0.40 | 0.71–0.72 and 0.73–0.74; 0.43–0.48 and 0.46–0.50 |

- **The headline holds, less strongly.** The unit-cost label wins 0.92 of seeds at the
  defaults against 0.98, with a final capacity share of 0.78 against 0.89: the pilot's
  numbers (0.94–0.97 and 0.72–0.79). It still wins through the price (+0.18 of sales share)
  and through entry (+0.11), with profit rates of 0.063 and 0.065.
- **The advantage now grows with the bias over the whole range.** 0.57, 0.75, 0.89 and 0.96
  for β = 0, 0.5, 1.5 and 3, where the runs without overtime are at the ceiling from
  β = 0.5 (0.92, 0.98, 0.98). β = 0 stays within drift.
- **The evaluation price still matters at r̄ = 0.05.** The share won falls from 0.89 to 0.71
  as λ goes to 1 and the hurdle from 0.107 to 0.050. At r̄ = 0.16 it is flat (0.95 to 0.97).
- **The cycle is milder.** At the defaults the demand lost falls from 3.2 to 0.5 %, the
  periods with lost demand from 0.17 to 0.05, the highest price from 2.98 to 2.00 times the
  price of production and capacity at the end from 1.34 to 1.12 times demand. Firms work
  overtime in 0.23 of periods.
- **E0 is not helped where it failed.** In the all-unit-cost population demand never exceeds
  capacity, so overtime is never used and the runs are those of stage 5: cutting stops after
  two periods, the price stays at 1.16 times the price of production and capacity at 1.56
  times demand. In the all-profit-rate population capacity falls from 2.35 to 1.66 and the
  price from 1.37 to 1.12. Capacity ends within the band in 0 and 3 seeds of 50.
- **Systematic cutting keeps its verdicts**: drift at r̄ = 0.05 and a win of the profit-rate
  label at r̄ = 0.16 (the unit-cost label wins 0.04 to 0.07).
- **Checks.** Both E1 controls have an interval that contains one half (0.46–0.55 and
  0.43–0.52), and in each control the reserve is released for the same share of plants under
  the two labels (0.73 and 0.73).
- **For the group.** Overtime on the pricing as specified keeps the headline, removes most of
  the lost demand and brings E1 to the pilot's numbers. It does not repair E0, whose failure
  under cost-edge cutting is the price that stops falling without technical change
  (diagnosis, point 1). Capacity, the price and the hurdle stay above the pilot's ranges.

What makes 3a–3d independent: `pay`, `buy_plant`, `remove_plant` with the reserve rule, r_new,
`count` and every dataclass field exist after stage 2, and `parameters.py` is frozen there (a new
constant is a departure to register in `v3-choices.md`). Stage 4 merges in the order 3c, 3a, 3b,
3d.

**Speed.** The target is 0.11 s for 200 periods on one core. Two costs grow during a run: the
menu, scanned by `hurdle` and `choose_technique` for every firm every period, and the number of
firms, since pricing compares each firm with every rival (the pilot had 47 to 140 entries a run).
The stage 4 profile was over the target (0.127 s, 58 % of it in the scan of the menu), so the
remedy is in: `frontier` drops from the public menu every technique that another one beats on
both unit cost and κ, since neither rule chooses it at any h ≥ 0 and it never sets the hurdle.
It costs 7 lines, and a test checks that the period table is the same without it.

## 10. Open questions

### Settled on 10 November

Ugo's answers to the first plan; each has a row in `v3-choices.md`, and the group still confirms
them. The decision is the first plan's default unless the row says otherwise.

| # | Point | Decision |
| --- | --- | --- |
| Q1 | The 700-line cap | Lines are counted without blank lines; target 700, tolerance 10 % (770 at most). |
| Q3 | Order inside step 6 | Exits, then entry among the survivors. r_new now comes earlier, at the end of step 3. |
| Q4 | Label-swap test | Every firm's label is swapped and every firm keeps its rule; trajectories must be identical. |
| Q5 | Private diffusion | No switch: `public_lag=None`. "What to drop" and the robustness table of the proposal are reworded. |
| Q6 | Morris on S | Each initial firm keeps a normal output of 120, 120 and 140 and gets output / S plants; D_0 = (340/383) × initial capacity. |
| Q7 | Homogeneous start | Six identical firms of 6 D1 plants: capacity 720, D_0 = 639.2. |
| Q8 | Entrant details | 0.5 × the survivors' mean capacity after scrapping, in plants of S, rounded half up, at least 1; first utilisation 1; r_new counts the initial plants aged 5 or less. |
| Q10 | Excess-demand share | (D − K) / D, with K the total normal capacity in operation. |
| Q11 | Hurdle at λ = 1 | r̄ or just above it: 5.00 % at r̄ = 0.05, 17.05 % at r̄ = 0.16 on the initial menu. The proposal and `v3-choices.md` are reworded. |
| Q14 | Sharing work in 3a–3d | One branch per part from the stage 2 commit, exchanged by the owners; build sessions never push. |
| Q15 | Leftovers of v2 | Stage 1 reduces the workflow to the tests and `run.py` on Python 3.12. Where the report lives is for the group. |
| Q16 | The pilot | Run and recorded on 10 November; the plan follows the revised specification. |
| a | Entrant's menu | The public menu only. |
| b | Scrapping | The owner's posted price is compared with ucs; the 2 periods are consecutive; idle = no output for 2 consecutive periods; equal-cost plants run youngest first. |
| c | Entrant's funding | Equity from the rest-of-economy account, added to its funds as well. |
| e | Ties | Technique costs: the lower κ, then the lower ucs; a design that ties is not kept. Prices: equal by `math.isclose`. Exits: candidates with the same share stay or leave together. The parent of an entrant is drawn over the firms in order of `id`, which maps one uniform to a firm and breaks no tie. |
| f | Morris on T | 7 to 19: the grid is 7, 11, 15, 19, and D2 keeps the lowest unit cost. |
| g | Scrapping on unit cost | With the maximum age T; only the cost compared with the price changes. |
| h | Names | The table under "Conventions". |
| i | Constants | All in `parameters.py` (section 5). |
| j | Withdrawn reserve | Paid to the rest-of-economy account, as far as the firm's cash allows. |
| k | Initial cash | The depreciation accumulated on the initial plants (section 3). |

### Confirmed on 10 November after a second explanation

Five points Ugo asked to have explained again, then confirmed as proposed; each has a row in
`v3-choices.md`. The explanations stay here for the group.

**Q2. The floor against "a price never rises".** A5 states two rules that can disagree: a price
never rises except after a shortage, and a price is never below the unit cost of the firm's best
plant in operation.

- **When they disagree.** A firm runs older plants with a unit cost of 75.0 and newer ones with a
  unit cost of 76.0, and posted 75.5. Its last 75.0 plant retires at age T: its floor is now
  76.0, above its price, and there is no shortage.
- **Who it happens to.** Only a firm that bought a dearer technique after a cheaper one. Under
  the Marx-biased set the unit-cost rule never does: it orders the lowest unit cost it knows, and
  what it knows only grows. The profit-rate rule does: at p = 100 the firm endowed with D2 (75.0)
  orders D1 (76.0), which has the higher rate there. So the choice bears on profit-rate firms.
- **Option A, the floor wins.** The firm posts 76.0. It is then dearer than its rivals and loses
  demand through the replicator: the price channel punishes the dearer plants at once. This is
  the one rise without a shortage. v2 does the same in its follow branch.
- **Option B, the price never rises.** The firm stays at 75.5 and sells every unit below its unit
  cost. It keeps its demand, books losses, and its funds shrink: the accumulation channel
  punishes it, slowly. Nothing brings the price back above cost before the next shortage.
- **Decided: A**, price = max(min(previous, target), floor). It is what the pilot's reference
  numbers were produced with, and "no price below the floor" can be asserted every period.

**Q9. Random numbers: five per firm and period.** Each firm has its own stream of random numbers.

- **What a firm needs.** One uniform to decide whether it draws a design this period (against π).
  If it does, the design needs two more numbers under the Marx set (the cut a, the bias z), two
  under the neutral set and three under the categories rule. Four uniforms and one normal cover
  all three rules.
- **The rule.** Every firm takes these five numbers at the start of step 5 in every period of its
  life, and throws away those it does not use. The industry does the same with three uniforms in
  step 6: is there an entrant, which incumbent it copies, is the label flipped.
- **Why.** Number n of a firm's stream then always belongs to the same period. On one seed a
  firm gets the same chance to draw, and the same cut a, in the mixed population, in both
  controls and in every cell (another β, λ or technical-change rule). A difference between two
  cells on the same seeds then comes from the treatment and not from different random numbers.
  If numbers were taken only when needed, the first design drawn would shift everything after it.
- **Cost.** About 6,000 numbers a run, most of them unused; no extra line.
- **Who draws.** A9 says "each firm with plants": read as a firm that had a plant in operation in
  the period, even if step 4 has just removed its last one. An entrant does not draw in the
  period it enters.
- **Decided: five per firm and period, three for the industry.** The alternative was to take a
  number only when it is used.

**Q12. Profit after depreciation, and the base of the realised rate.** The plant is paid once, in
cash, when it is ordered. Depreciation is not a second payment: no cash moves. It is how that one
payment is charged to the T periods in which the plant runs.

- **Two accounts.** A plant on C costs 2,750 (κ = 137.5, S = 20). At a price of 85 it brings in
  (85 − 64.25) × 20 = 415 a period. Cash: −2,750 at the order, then +415 a period. Profit: 0 at
  the order (cash became a plant of the same value), then 415 − 275 = 140 a period. Over the ten
  periods both come to the same 1,400.
- **Why split the 415.** 275 is the firm's own capital coming back; 140 is what the plant earned.
  The model uses the split three times:
  - Dividends are d × profit. On 415 the firm would pay out 207.5 a period and keep 2,075 in ten
    periods, less than the 2,750 a new plant costs: it would distribute part of its capital.
  - Financing (A7): the 275 a period builds the reserve that pays for replacement, if r_new ≥ r̄;
    the retained half of the 140 pays for net expansion.
  - Every rate in the model is after depreciation: the hurdle (p^e − uc) / κ, the price of
    production uc + r̄κ, r_new and r̄ itself. Here it is 140 / 2,750 = 5.1 %, to set against r̄ =
    5 %. Before depreciation it would be 15.1 % and comparable with none of them.
- **Where "the plant is paid" does apply.** In running and scrapping a plant that exists: capital
  is sunk, so the price is compared with the operating cost ucs alone (A6, step 4).
- **What Q12 asked** is only the denominator of the realised rate reported by label. **Decided:**
  profit after depreciation over the purchase cost of the plants in operation, the base of the
  hurdle and of r_new. Over the book value, the rate of an old plant would grow without bound as
  its book value goes to zero.

**Q13. The price that defines the categories.** The categories rule (robustness, the second half
of E4) builds each design in one of two categories: "both", which both rules adopt, or, with
probability q = 0.5, "conflict", which only the unit-cost rule adopts.

- **Why a price is needed.** A conflict design lowers the unit cost but raises capital per unit
  so much that the profit rate at the price falls. The boundary between the two categories is the
  capital increase at which the rate at price p is unchanged, b_O = a ucs / (δκ + p − uc): it
  depends on p.
- **The question.** v2 used the firm's own price. In v3 the profit-rate rule judges at p^e = (1 −
  λ) p + λ p_reg. With λ > 0 the two differ.
- **Option 1, the firm's own price (v2).** With λ > 0 a "conflict" design may then be one the
  profit-rate firm adopts at p^e, so q is no longer the share of designs on which the rules
  disagree.
- **Option 2, p^e.** "Conflict" always means "refused by the profit-rate rule as this firm
  applies it", whatever λ.
- **What depends on it.** Nothing planned: the categories rule runs only in E4, where λ = 0 and
  the two prices are the same. It matters only if categories are later crossed with λ.
- **Decided: p^e**, computed for every firm in the same way, whatever its rule.

**A13 d. E6: demand, mutation and measure.** E6 puts one mutant firm of one rule among nine
residents of the other, all ten on D1 with 6 plants each (capacity 1,200).

- **Demand.** The base has capacity 760 and demand 674.7, a ratio of 340/383: firms start at
  0.888 of capacity, with room to cut prices. **Decided:** the same ratio, D_0 = 1,065.3, so that
  E6 differs from E1 by its population only. With 674.7 firms would start at 0.56 and plants
  would be scrapped as idle within two periods; with 1,200 there would be no spare capacity and no
  price cutting at the start.
- **Mutation.** An entrant copies the rule of an incumbent drawn by market share, and with
  probability μ = 0.02 takes the other rule. With 47 to 140 entries a run, μ = 0.02 creates one
  to three mutants out of nothing, in the control as well. **Decided:** μ = 0 in E6, so the
  mutant label grows only through the mutant's own growth and through entrants that copy it.
- **Entry.** It stays as in the base, so a mutant with a larger share has more entrants copying
  it. That is selection, and the control has it too.
- **Measure.** The mutant label's mean capacity share at t = 200 against 0.1, and the invasion
  rate, the share of seeds in which it ends above 0.1 (exact ties apart, as in A11), each against
  the control, where the mutant follows the residents' rule and 0.1 is the expected share.

### New since the specification was revised, accepted on 10 November

| # | Question | Decision |
| --- | --- | --- |
| Q17 | **The reserve condition under the accelerator.** The proposal states it under retained earnings; A7 states it for the funds before it separates the two rules. The accelerator spends cash, not funds, so only the withdrawal matters there. | Step 4 is the same under both investment rules: when r_new < r̄ the reserve is paid out, also under the accelerator. The investment factor of E4 then changes one thing, the number of plants ordered. |
| Q18 | **The operating-cost test (A13 l).** In the pilot no plant left through it. In v3 it cannot bind alone: A6 does not offer a plant whose operating cost is above the price, so the plant has no output in exactly the periods the cost test counts, and the idle test removes it on the same date. The test changes the reason recorded, not the plant removed. It binds alone only under `scrap_cost="unit_cost"`. | Keep it: it is the group's rule, it costs 6 lines, and the robustness check needs it. `retirement_reason` reports "cost" before "idle"; the run row gives the shares of plants leaving by age, cost and idleness; stage 4 reads them. If "cost" stays at zero, the report says that plants leave by age or idleness at these parameters. |
| Q19 | **The pilot numbers.** The pilot is not a docking: v2 keeps overtime, its own shortage rule and leader-follow in place of systematic cutting, and leaves the withdrawn reserve in cash. | A reference, not a gate. Stages 5 and 6 set v3 beside the table of section 7; a number outside the pilot's range is explained in the stage note and does not stop the runs. The only gate is E0. |
