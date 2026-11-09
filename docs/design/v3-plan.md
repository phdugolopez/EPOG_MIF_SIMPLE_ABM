# Version 3 plan: files, interfaces, tests and build order

Plan of 9 November 2026, written from `final-model-proposal.md` (sections "The simplified model",
"What to drop", "Model analysis", "Sensitivity analysis", "Decisions"), the addendum A1–A13 of
`v3-planning-prompt.md`, `v3-choices.md` and the v2 files the prompt lists. It contains no model
code. Where the proposal and the addendum differ, the addendum is followed.

**Status.** `v3-choices.md` still lists the v2 pilot as open and four decisions as "to confirm",
and the prompt says the plan comes after the pilot is read. The plan takes the specification as
written on 9 November. If the pilot changes scrapping or the financing of replacement, the parts
marked † change (step 4, `remove_plant`, the funds F); the rest stands.

**Five points the group must settle before stage 1** (all in section 10, with a default each):

1. The 700-line cap leaves no margin: the budgets below add up to 698 (Q1).
2. Which wins when the price floor is above last period's price: the floor or "a price never
   rises except after a shortage" (Q2).
3. Equal-cost plants run youngest first, so that "idle" can mean "no output" (A13 b).
4. Exit is applied before entry inside step 6 (Q3).
5. How the label-swap test is read (Q4).

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
  number and not by its place in the list. Each firm takes the same five variates every period
  and the industry the same three, used or not, so a stream's position depends only on the
  period: a mixed population and its controls share their random numbers on a seed.
- **Lines.** Counted with `wc -l`, blank lines and docstrings included, as the 5,100 of v2 was
  (5,167 for its `equations/`, `markets/`, `model/`, `parameters.py`, `run.py`, `analysis/` and
  `debug/`).

## 1. File tree

Model code: 698 lines, as point estimates (± 5 %), against a cap of 700. `tests/test_budget.py`
enforces the cap.

```text
parameters.py                           56  every parameter, constant and switch (section 5)
run.py                                  18  one run at the defaults -> outputs/periods.csv, outputs/run.csv

equations/                             190  25 files, pure functions: no state, no random draw
  common_unit_cost.py                    3  uc = ucs + delta kappa
  common_profit_rate.py                  3  profit rate of a technique at a price
  common_hurdle.py                      13  evaluation price p^e and hurdle h: the one rule that differs
  common_technique_choice.py            10  cost of a technique at h, and the argmin j*
  common_regulating_price.py            11  regulating technique and price of production
  setup_initial_plants.py                5  number of plants and staggered ages of an initial firm (A2, A3)
  pricing_rule.py                       22  shortage step, undercut, follow (A5)
  pricing_floor.py                       3  unit cost of the firm's best plant in operation
  demand_replicator.py                  12  competitiveness E = 1/p and replicator shares
  accounts_merit_order.py               10  plants run cheapest first, then youngest
  accounts_depreciation.py               3  straight-line by time
  accounts_dividends.py                  3  d x max(0, profit)
  scrapping_below_cost.py                8  scrap cost and periods with the price below it
  scrapping_idle_plants.py               3  periods without output
  scrapping_retirement.py                9  age T, below cost, idle
  investment_draw_marx.py                8  Marx-biased design (the model)
  investment_draw_neutral.py             8  neutral set (control)
  investment_draw_categories.py         12  categories rule (robustness)
  investment_retained_earnings.py        6  plants that the funds pay for
  investment_accelerator.py              6  plants missing to reach desired capacity
  entry_probability.py                   5  Pr(entry)
  entry_new_plant_rate.py                6  r_new
  entry_inherited_rule.py                8  label copied by share, flipped with probability mu
  entry_size.py                          4  entrant's number of plants
  entry_exit_rule.py                     9  who leaves, with the floor of 2 firms

markets/                                86  the transactions: they move cash, plants and firms
  payments.py                            6  pay(): the only place cash moves
  goods_market.py                       15  allocate(): sales, one re-allocation, lost demand (A6)
  plant_market.py                       24  buy_plant(), remove_plant(): order, reserve released, write-off
  entry_exit.py                         41  create_entrant(), remove_firm() (A10)

model/                                 348
  entities.py                           72  Technique, Plant, Firm, Account, Industry (section 2)
  model.py                              46  build(): initial population and streams; new_firm(); run()
  scheduler.py                         180  period(), start_period(), the six step functions, check()
  outputs.py                            50  the period table: count(), record_production(), record_end()

tests/                               ~ 640  unittest, one file per step (section 8)
  helpers.py  test_common.py  test_setup.py  test_pricing.py  test_demand.py  test_accounts.py
  test_scrapping.py  test_investment.py  test_entry.py  test_neutrality.py  test_model.py
  test_budget.py  test_experiments.py

experiments/                         ~ 500  (section 7)
  cells.py                             100  E0-E6 and the robustness checks as {cell: overrides}
  populations.py                        25  start lists: homogeneous, invasion
  summary.py                            80  the run row: winner, takeover, decomposition, mechanism, Marx bias
  stats.py                              30  wilson(), beyond_drift()
  harness.py                           150  tasks, pool, runs.csv, cells.csv, resume, command line
  morris.py                             70  SALib design, runs through the harness, mu* and sigma
  e5_channels.py                        40  within-cell regression of the profit-rate gap

figures/                             ~ 330  one script per report exhibit
  style.py  fig1_conflict_zone.py  fig2_typical_run.py  fig3_bias_lambda.py  fig4_heatmaps.py
  fig5_decomposition.py  fig6_morris.py  tab3_robustness.py

CLAUDE.md  README.md  requirements.txt  .github/workflows/build.yml      rewritten in stage 1
```

`equations/`, `markets/`, `model/`, `experiments/` and `figures/` each get an empty
`__init__.py`. The step functions live in `model/scheduler.py` and are named after their step
(`set_prices`, `allocate_demand`, `produce_and_account`, `scrap_plants`, `invest`,
`enter_and_exit`); `markets/` holds what they call to move cash, plants or firms, as in v2.

## 2. Data structures

`model/entities.py`. State keeps v2's names (`price`, `share`, `sales`, `capacity`, `util`,
`kappa`, `hurdle`, `cash`, `pending_plants`, `book_value`, `write_offs`, `known`, `roe`, `born`).
All four are `@dataclass(eq=False)`: an object is compared by identity.

```python
class Technique:
    name: str                  # "C", "D1", "D2"; a design gets a serial name, never read by a rule
    ucs: float                 # operating cost per unit of normal output (wage = 1)
    kappa: float               # capital per unit of normal output (capital goods priced 1)
    first_run: int | None      # period its first plant produced; public from first_run + public_lag

class Plant:
    technique: Technique
    capacity: float            # normal output a period: plant_size
    cost: float                # purchase cost, kappa x plant_size
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
    cash: float = 0.0
    funds: float = 0.0         # investible funds F (A7)
    profit: float = 0.0        # after depreciation
    write_offs: float = 0.0
    cut: bool = False          # undercut at step 1
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
    r_new: float | None
    next_id: int
    tally: dict                # this period's flows by label, for the output table only
    rows: list[dict]           # the period table
```

A technique is "known" to a firm if it is in `industry.public` or in `firm.known`.

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
             record_production(): the two rows of t, before any plant or firm leaves

4  scrap_plants                                      scrapping (Vincent) †
     reads   price(t), plant.output, plant.age
     rules   scrap_cost, periods_below_cost, periods_idle, retirement_reason
     writes  plant.below_cost, plant.idle; remove_plant() for each plant that leaves:
             funds += cost - book_value (reserve released), write_offs += book_value       (A7)

5  invest                                            investment, technical change included (Ugo)
     reads   price(t), reg_price, public, known, funds, cash, notional, capacity; the firm's stream
     for every firm:
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
     reads   share, capacity and plants on order, profit and cost of the plants aged 5 or less,
             prices, public, reg_price; the industry's stream
     r_new = new_plant_rate()                                    before anyone leaves
     exit    leaving(); remove_firm(): cash -> rest of economy, plants written off,
             the survivors' shares rescaled to sum to 1
     entry   with probability entry_probability(r_new): create_entrant() among the survivors:
             label = inherited_label(), rule from the label; price = lowest posted price;
             h at that price (A8); j* on the public menu; plants = entrant_plants(), paid by
             equity from the rest of the economy, arriving in t+1;
             share = its capacity / (survivors' next-period capacity + its capacity),
             survivors' shares x (1 - share)

7  record_end(); check(); time + 1
     check asserts: |sum of all cash| < 1e-6 (money conservation), every cash >= -1e-9,
     shares sum to 1, K(t+1) = K(t) - retired + ordered - exit + entry
```

When the three timed objects act:

- **Hurdle.** Computed in step 5 from the price the firm posted in step 1 of the same period, and
  for an entrant in step 6 at its entry price. Nowhere else.
- **Regulating price.** Computed once a period, after production and before scrapping, the same
  for every firm. It enters p^e in steps 5 and 6 when λ > 0, and the outputs. If no plant is in
  operation, last period's value is kept.
- **Construction lag.** A plant ordered in t (step 5, or step 6 for an entrant) has no output in
  t and is delivered in step 0 of t + 1. Entry shares and the exit test count plants on order; in
  step 5 nothing is on order yet, so the term is zero there and is kept only for the formula.

The initial state is read as period −1: price 100, `share` = capacity share, `sales` = share ×
D_0, `util` = sales / capacity (0.888), `excess` = 0, cash and funds 0. So firms with spare
capacity and a cost edge already cut in period 0.

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
| `common_regulating_price.py` | `regulating_technique(techniques, delta)` | The technique in operation with the lowest unit cost; exact ties go to the lower κ. | v2 `regulating_price`, first half |
| | `price_of_production(ucs, kappa, delta, rbar)` | uc + r̄κ. | v2 `regulating_price`, second half |
| `setup_initial_plants.py` | `initial_ages(output, size, life)` | n = normal output / S rounded half up (at least 1) plants, of ages floor(i T / n). | new (A2, A3) |
| `pricing_floor.py` | `price_floor(unit_costs)` | The unit cost of the firm's lowest-unit-cost plant in operation; 0 without a plant. | new (A5) |
| `pricing_rule.py` | `posted_price(previous, rival_prices, rival_costs, own_cost, floor, spare, excess, cost_edge, cut, shortage_step)` → (price, cut) | After a shortage, the next higher rival price, or previous × (1 + step × excess) with no rival above; else (1 − c) × the lowest rival price if entitled to cut; else the lowest price posted, its own included; never below the floor. | v2 `real_competition_price`; the systematic regime is new |
| `demand_replicator.py` | `competitiveness(price)` | E = 1 / p. | v2 `competitiveness` |
| | `replicator_shares(previous_shares, competitiveness, chi)` | f_i = f_i,−1 (1 + χ (E_i − Ē) / Ē), negatives set to 0, renormalised. | v2 `replicator_shares` |
| `accounts_merit_order.py` | `dispatch(ucs, ages, capacity, quantity)` → outputs | Plants run lowest operating cost first, then youngest, each up to its normal capacity. | v2 `merit_order.dispatch`, without overtime; ties by age (A13 b) |
| `accounts_depreciation.py` | `depreciation(cost, book_value, delta)` | δ × purchase cost a period, at most the remaining book value. | new (v2's by-time rule) |
| `accounts_dividends.py` | `dividends(profit, payout)` | d × max(0, profit). | new (v2's rule) |
| `scrapping_below_cost.py` † | `scrap_cost(ucs, kappa, delta, rule)` | The cost the price must cover: ucs, or ucs + δκ under `"unit_cost"`. | v2 `retirement.scrap_cost` |
| | `periods_below_cost(previous, price, cost)` | Consecutive periods with the price below the scrap cost. | v2 `retirement.periods_below_cost` |
| `scrapping_idle_plants.py` † | `periods_idle(previous, output)` | Consecutive periods without output. | v2 `idle_plants`: the same plants, given the running order |
| `scrapping_retirement.py` † | `retirement_reason(age, life, below_cost, idle, periods)` → `"age"`, `"cost"`, `"idle"` or `None` | A plant leaves at age T, or after N periods below its scrap cost, or after N periods idle. | v2 `retirement.retirement_reason` |
| `investment_draw_marx.py` | `draw_marx(ucs_o, kappa_o, u, z, step, bias, spread)` → (ucs, κ) | ucs_n = (1 − a) ucs_o, κ_n = (1 + k a) κ_o, a = u × step, k = bias × e^{spread z}. | v2 `innovation_set.draw_marx` |
| `investment_draw_neutral.py` | `draw_neutral(ucs_o, kappa_o, u, v, step)` → (ucs, κ) | Direction uniform on the circle in (Δucs/ucs, Δκ/κ), size u × step. | v2 `innovation_set.draw_neutral` |
| `investment_draw_categories.py` | `draw_categories(ucs_o, kappa_o, delta, price, u_cat, u_a, u_b, step, conflict_share)` → (ucs, κ) | A cost-reducing, capital-using design that both rules adopt at `price`, or with probability q only the unit-cost rule. | v2 `new_technique.design_category` and `draw_design` |
| `investment_retained_earnings.py` | `plants_affordable(funds, plant_cost)` → int | floor(funds / plant cost), 0 if funds are negative. | new (A7) |
| `investment_accelerator.py` | `plants_wanted(notional, u_target, capacity, on_order, size)` → int | ceil((notional / u* − capacity − on order) / S), at least 0. | new (A7) |
| `entry_probability.py` | `entry_probability(r_new, rbar, theta)` | min{1, θ max(0, r_new − r̄) / r̄}; 0 when r_new is None. | v2 `entry_probability` |
| `entry_new_plant_rate.py` | `new_plant_rate(rates, capacities)` | Capacity-weighted realised profit rate of the plants built in the window; None without one. | v2 `new_plant_rate` |
| `entry_inherited_rule.py` | `inherited_label(labels, shares, mutation, u_parent, u_flip)` | The label of an incumbent drawn by share, flipped with probability μ. | v2 `inherit`, with two uniforms in place of the generator |
| `entry_size.py` | `entrant_plants(capacities, entry_size, size)` → int | entry_size × the average incumbent capacity, in plants of size S, rounded half up, at least 1. | new (A10) |
| `entry_exit_rule.py` | `leaving(shares, capacities, exit_share, min_firms)` → list of bool | Firms below the exit share or without capacity leave; if fewer than min_firms would remain, the candidates with the largest share stay, tied ones together. | new (A10, A13 e) |

Transactions in `markets/` (they change state, so they are not equations):

| File | Function | Docstring | Ports |
| --- | --- | --- | --- |
| `payments.py` | `pay(industry, payer, payee, amount)` | The only place cash moves: payer.cash − amount, payee.cash + amount. | v2 `payments.pay`, as called in `entry_exit.py` |
| `goods_market.py` | `allocate(demand, shares, offered)` → (sales, lost) | Each firm sells min(share × D, offered capacity); the overflow is shared once, pro rata to spare offered capacity; the rest is lost. | v2 `goods_market.allocate`, one round, no priority to the cheapest |
| `plant_market.py` | `buy_plant(industry, firm, technique, cause)` | The firm pays κS now, its funds fall by κS, and the plant joins `pending_plants`. | v2 `buy_plant`, as called in `create_entrant` |
| | `remove_plant(industry, firm, plant, reason)` † | The plant leaves: cost − book value joins the funds, the book value is written off. | new (A7) |
| `entry_exit.py` | `create_entrant(industry, u_parent, u_flip)` | Label inherited, price = lowest posted, technique by its own rule, plants paid by equity, share by capacity. | v2 `create_entrant` |
| | `remove_firm(industry, firm)` | Cash goes to the rest of the economy, plants are written off, the others' shares are rescaled. | v2 `remove_firm`, without debt |

Three remarks on the ports:

- `posted_price`: "entitled to cut" = spare capacity, and under cost-edge cutting a unit cost
  below that of at least one rival posting the lowest rival price (strict inequality, so equal
  costs give no edge). v2's second condition, own cost below the cut price, is replaced by the
  floor. The returned `cut` is true when the firm was entitled and its price is below the lowest
  rival price. Two prices are "equal" by `math.isclose`.
- `plants_affordable` adds 1e-9 before the floor: after T charges of δ × cost a book value can be
  1e-13 off zero, and funds / cost would otherwise be 0.9999999999999999.
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
    rbar: float = 0.05                   # entry gate, price of production; E3, E4: 0.16
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
`pricing`, `investment`, `tech_change` and `scrap_cost`. There is no entry switch: entry is open
or closed through `rbar`. The three populations are overrides held in `experiments/cells.py`:
mixed = the defaults, `all_unit_cost` = `rule_okishio="unit_cost"`, `all_profit_rate` =
`rule_shaikh="profit_rate"`. The initial firms are built from `start`, repeated `firms_per_pair`
times, with `initial_ages(output, plant_size, plant_life)` plants each (6, 6 and 7 at the
defaults: capacity 760), and D_0 = `demand_ratio` × initial capacity.

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
| `cap_retired`, `cap_retired_age`, `cap_retired_cost`, `cap_retired_idle` | capacity leaving in step 4, in total and by reason |
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
| `profit_rate` | profit / capital: the realised rate |
| `cash`, `funds`, `write_offs` | sums at the end of step 5 |
| `hurdle` | mean h of its firms in step 5 |
| `orders`, `orders_dearer` | plants ordered (steps 5 and 6); those whose technique is not the lowest-unit-cost technique known to the buyer |
| `drawn`, `kept` | designs drawn; designs kept |
| `entries`, `exits` | firms of g entering; leaving |
| `demand`, `lost` | D_t; demand left unserved (industry, same on both rows) |
| `low_price` | lowest posted price (industry) |
| `reg_price` | uc_reg + r̄ κ_reg (industry) |
| `price_over_reg` | sales-weighted industry price / `reg_price` |
| `r_new` | the entry signal (industry) |
| `war` | 1 if any firm undercut in t (industry) |
| `leader_cheapest` | 1 if a firm posting the lowest price has the lowest best-plant unit cost (industry; E0) |
| `rate_low`, `rate_high` | lowest and highest realised profit rate among firms with capacity (industry; E0) |

The flow columns come from `count(industry, firm, key, amount)`, called by `buy_plant`,
`remove_plant`, `create_entrant`, `remove_firm` and `invest`; it is the only function outside
entry that reads a label.

### Run table: one row per run

`experiments/summary.py`, `run_row(rows, params, seed)`: a function of the period table alone, as
v2's `analysis/indicators.py` was. U is the label `"shaikh"`, O the label `"okishio"`; "end"
means t = 200, that is `capacity_next` and `share_end` of the row t = 199 (A11).

| Column | Formula |
| --- | --- |
| `decided` | K_200 > 0, with K_200 = Σ_g `capacity_next` at t = 199 |
| `cap_share_end`, `uc_wins` | K_U,200 / K_200; `cap_share_end` > 0.5 |
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
| `rate_shaikh`, `rate_okishio` | Σ_t `profit` / Σ_t `capital` |
| `price_over_reg` | mean over t |
| `war_freq` | mean of `war`: the price-war frequency |
| `leader_cheapest`, `rate_spread` | means over t of `leader_cheapest` and of `rate_high` − `rate_low` |
| `entries`, `exits`, and each by label | sums |
| `open_share` | share of periods with `r_new` > r̄ |
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
`share_won` = won / decided, `won_low`, `won_high` (95 % Wilson interval, v2 `wilson`), and for
each numeric column of the run table its mean and the 95 % interval of the mean. Mixed rows also
get `ctrl_uc_share_won`, `ctrl_pr_share_won`, `gap` = share won − the mean of the two controls,
and `beyond_drift` = the mixed interval is disjoint from both controls' intervals (v2 `_disjoint`
and `summarise`).

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
| 3 | 12 and 30 firms | E1 and the 4 closed, growing cells of E4 | 3 | 200 | 6,000 |
| 3 | u* = 0.8 and 0.95 | the 8 accelerator marx cells of E4 | 3 | 200 | 9,600 |

E0 to E6 are 38,400 runs, the proposal's count. At 0.11 s a run and 10 workers, priority 1 takes
about 3 minutes, priority 2 about 10, priority 3 about 6. The categories check is the second half
of E4.

**What E0 must show before E1–E6 are read** (thresholds proposed here, to be agreed before the
run): the price leader has the lowest unit cost in at least 0.9 of periods (v2: 0.94); capacity
at t = 200 is between 0.9 and 1.5 times demand in at least 0.9 of seeds, which is the pilot's
question, whether the industry holds its capacity; profit rates stay unequal (`rate_spread` > 0);
the price stays above the regulating unit cost.

**E6.** `populations.invasion(resident)` gives ten firms on D1 with 120 of capacity each, nine
with the resident label and one with the other. Direction 1: residents `"shaikh"` on the
unit-cost rule, mutant `"okishio"` on the profit-rate rule; its control sets
`rule_okishio="unit_cost"`. Direction 2 is the mirror image. Read: the mutant label's mean
capacity share at t = 200 against 0.1, and the share of seeds in which it is above 0.5, each
against the control.

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
| `test_common.py` | On Shaikh's menu D2 has the lowest unit cost (75.0) and at p = 100 D1 the highest rate (16.86 % against 16.00 % and 15.83 %). h = 0 under the unit-cost rule at any price. Under the profit-rate rule h is the best rate on the menu, and 0 when p^e is below every unit cost. With that h, `choose_technique` returns the highest-rate technique: D1 at 100, D2 below 85.15. p^e at λ = 0, 0.5, 1. At λ = 1 and r̄ = 0.05, p^e = 82.89 and h = 0.05. Ties go to the lower κ. |
| `test_setup.py` | Six firms, 6, 6 and 7 plants, capacity 760, D_0 = 674.67, ages 0, 1, 3, 5, 6, 8 and 0, 1, 2, 4, 5, 7, 8, book value κS(1 − a/T), shares = capacity shares. `firms_per_pair=2` doubles firms and demand. |
| `test_pricing.py` | Shortage: a firm moves to the next higher rival price, and with none above rises by 0.5 × the excess share. No shortage: no price rises. Cost-edge: a firm cuts only with spare capacity and a strictly lower unit cost than a rival posting the lowest rival price; equal costs, no cut. Systematic: spare capacity is enough. The price is never below the unit cost of the firm's best plant in operation. Reversing the firm list gives the same prices. |
| `test_demand.py` | Shares sum to 1; equal prices leave them unchanged; the cheaper firm gains; χ = 0 changes nothing. Sales never exceed offered capacity; a plant with ucs above the price is not offered; sales + lost = D_t; the overflow goes pro rata to spare offered capacity, once; `share` is unchanged by rationing. |
| `test_accounts.py` | Plants run cheapest first, then youngest; output = sales; no plant above its capacity. Profit = revenue − operating cost − depreciation, and a plant without output still depreciates. Dividends are 0.5 × profit when positive, 0 otherwise. Book value is 0 after T periods. Cash never falls below 0. **Money conservation**: over 50 periods, in the three populations and under both investment rules, the sum of all cash stays 0 every period. |
| `test_scrapping.py` | A plant leaves at age T; after 2 consecutive periods with the price below its ucs, and one period above resets the count; after 2 consecutive periods without output. Under `scrap_cost="unit_cost"` the price is compared with ucs + δκ. On leaving, funds rise by cost − book value and write-offs by the book value. In a run without draws the initial plants retire on the dates the staggered ages give. |
| `test_investment.py` | The three draws: at β = 0 κ is unchanged; a categories "both" design is adopted by both rules and a "conflict" design only by the unit-cost rule; a design that ties is not kept. Retained earnings buy floor(min(F, cash) / (κS)) plants. **Depreciation reserve**: a firm that sells its capacity at a price equal to its unit cost, so with zero profit for T periods, buys one plant in the period its plant retires at age T. **Funds never exceed cash**: in a full run no firm spends more than min(F, cash), and under the accelerator more than its cash. Accelerator: the ceil formula, capped by cash. Lag: a plant ordered in t has no output in t and can produce in t + 1. Diffusion: a rival's menu holds a design from first_run + L and not before; never when `public_lag=None`. |
| `test_entry.py` | The entry probability at r_new below, just above and far above r̄. r_new weights by capacity and ignores plants older than the window. Inheritance: μ = 0 gives the parent's label, μ = 1 the other. An entrant is paid for by equity, so all cash still sums to 0; its plants arrive next period; its share and the incumbents' follow A10; its price is the lowest posted. Exit below 1 % or without capacity, cash to the rest of the economy, survivors' shares sum to 1; never fewer than 2 firms; tied candidates stay or leave together. |
| `test_neutrality.py` | **Label swap**: in each of the three populations, swapping the labels of all initial firms and the two fields `rule_shaikh`, `rule_okishio` leaves every firm on its rule; every firm's trajectory is then identical and the period table is the same with the two labels exchanged (Q4). **Symmetric controls**: in a control, swapping the labels alone gives the mirror image, and reversing `industry.firms` at the start changes nothing in any population, so a firm's draws do not depend on its place. **Label reads**: the attribute `label` is read only in `entities.py`, `model.py`, `markets/entry_exit.py`, `equations/entry_inherited_rule.py` and `outputs.py` (a search of the source). |
| `test_model.py` | **Reproducibility**: the same seed gives the same period table, another seed a different one. A 200-period run at the defaults ends with capacity, and `check` holds every period. The capacity terms sum to the change in the capacity share and the sales terms to the change in the sales share (residuals below 1e-9). |
| `test_budget.py` | `parameters.py`, `run.py`, `equations/`, `markets/` and `model/` hold at most 700 lines. |
| `test_experiments.py` | `wilson(81, 100)` = (0.722, 0.875), and NaN for n = 0. `beyond_drift` on overlapping and disjoint intervals. `takeover` on three hand-made series. Two cells × three populations × four seeds give the same `runs.csv` with 1 and 2 workers, in seed order; a run stopped after the first cell and resumed gives the same file. |

The statistical form of symmetric controls, the two controls of E1 at 500 seeds having intervals
that contain 0.5, is read from `cells.csv` in stage 5, not run as a unit test.

## 9. Stages

Each stage ends with the tests passing and one commit on `v3`. Times are for one working session
with its review. 3a to 3d are parallel: they start from the stage 2 commit and each touches only
its own files and the body of its own step functions in `scheduler.py`.

| Stage | Content | Owner | Time | Dates |
| --- | --- | --- | --- | --- |
| 1 Scaffold | New `CLAUDE.md` (the rules of the prompt's section 3), new `README.md`, `requirements.txt` (numpy, pandas, matplotlib, SALib), the workflow file on Python 3.12 with the unit tests and `run.py` only, empty packages, `parameters.py`, `entities.py`, the five `common_` files, `setup_initial_plants.py`. Tests: `test_common`, `test_budget`. | Ugo | 1.5 h | 12 Nov |
| 2 Skeleton | `model.py` (initial population, streams), `payments.py`, `plant_market.py`, `scheduler.py` with `period`, `start_period`, `check` and the six step functions as stubs with their final signatures and docstrings (prices and shares unchanged, sales = min(share × D, capacity), nothing else), `outputs.py` with `count` and its keys, `run.py`, `tests/helpers.py`. Tests: `test_setup`, reproducibility and money conservation on the stub loop. | Ugo | 2.5 h | 12 Nov |
| 3a Pricing ∥ | `pricing_rule.py`, `pricing_floor.py`, `set_prices`. Test: `test_pricing`. | Jake | 2 h | 13–14 Nov |
| 3b Demand, entry and exit ∥ | `demand_replicator.py`, `goods_market.py`, `allocate_demand`; the five `entry_` files, `markets/entry_exit.py`, `enter_and_exit`. Tests: `test_demand`, `test_entry`. | Pierre-Loup | 3.5 h | 13–14 Nov |
| 3c Accounts, scrapping, outputs ∥ | The three `accounts_` and three `scrapping_` files, `produce_and_account`, `scrap_plants`, the regulating price, `outputs.py` in full, `experiments/summary.py`. Tests: `test_accounts`, `test_scrapping`. | Vincent | 3.5 h | 13–14 Nov |
| 3d Technical change and investment ∥ | The three `investment_draw_` files, `investment_retained_earnings.py`, `investment_accelerator.py`, `invest`. Test: `test_investment`. | Ugo | 3 h | 13–14 Nov |
| 4 Integration | The four parts together; `test_neutrality`, `test_model`; profile 20 seeds against 0.11 s a run; line count; a first read of E0 on 20 seeds. | Ugo, all four review | 3 h | 15 Nov |
| 5 Harness, E0–E3 | `stats.py`, `cells.py` (E0–E3), `harness.py`, `test_experiments`; runs; `fig1` to `fig3`. | Ugo (harness, E2, E3), Vincent (E0), Pierre-Loup (E1) | 4 h and 3 min of runs | 16 Nov, runs 17–19 Nov |
| 6 E4, E5, Morris | E4 cells, `e5_channels.py`, `morris.py`; `fig4` to `fig6`. | Jake (E4), Ugo (Morris) | 4 h | 21–23 Nov |
| 7 E6, robustness | `populations.py`, the E6 and robustness cells, `tab3_robustness.py`. | Pierre-Loup (E6), Vincent (robustness) | 3 h | 24–25 Nov |

What makes 3a–3d independent: `pay`, `buy_plant`, `remove_plant`, `count` and every dataclass
field exist after stage 2, and `parameters.py` is frozen there (a new constant is a departure to
register in `v3-choices.md`). Stage 4 merges in the order 3c, 3a, 3b, 3d.

**Speed.** The target is 0.11 s for 200 periods on one core. Two costs grow during a run: the
menu, scanned by `hurdle` and `choose_technique` for every firm every period, and the number of
firms, since pricing compares each firm with every rival (entry is open in most periods at
r̄ = 0.05). If the stage 4 profile is over the target, the first remedy is exact: drop from the
public menu every technique that another one beats on both unit cost and κ, since neither rule
chooses it at any h ≥ 0. It costs about 12 lines, which Q1 then has to find.

## 10. Open questions

Each has the default this plan uses. None is decided until it has a row in `v3-choices.md`.

### New in this plan

| # | Question | Proposed default |
| --- | --- | --- |
| Q1 | **The 700-line cap.** Counted with `wc -l`, the budgets add up to 698 and are estimates (± 5 %). The plan gets there only by computing the run row in `experiments/summary.py` (v2 also kept `observables` and `takeover` in `experiments/`, but its decomposition was in `analysis/`, which the 5,100 counted) and by the running order of A13 (b). The speed remedy of section 9 does not fit. | Keep `wc -l`, enforce it in `test_budget.py`, and take any overrun out of the output columns first (`drawn`, `kept`, `rate_low`, `rate_high`, the retirement reasons). The alternative is for the group: count code lines only, without blank lines, comments and docstrings, which is about 510 for this plan, or move the cap to 750. |
| Q2 | **Floor against "a price never rises".** A firm's floor can move above its last price, for instance when its best plant retires. A5 states both rules. | The floor wins, as in v2's follow branch: price = max(min(previous, target), floor). It is then the only rise without a shortage. |
| Q3 | **Order inside step 6.** | r_new first, then exits, then entry among the survivors: the entrant's size and share are computed on firms that stay, and no entrant leaves in the period it enters. |
| Q4 | **Reading of the label-swap test.** "Labels swapped everywhere except the hurdle mapping" can mean that firms change rule, which changes trajectories by design. | Read as: swap every firm's label and keep every firm on its rule (so the two mapping fields are exchanged with the labels). Trajectories must be identical; only the label names move. |
| Q5 | **Private diffusion.** "What to drop" drops it; the sensitivity table lists it as a check on E1. | No switch: `public_lag=None`, one comparison in `start_period`. |
| Q6 | **Morris on S.** The initial number of plants and D_0 are stated for S = 20 only. | Each initial firm keeps a normal output of 120, 120 and 140 (the 6, 6 and 7 plants of A2 at S = 20; Shaikh's own outputs are not in the documents read, so check them) and gets output / S plants, rounded half up; D_0 = (340/383) × initial capacity, so utilisation starts at 0.888 whatever S. The initial price stays 100 when T moves. |
| Q7 | **Homogeneous start.** Six firms on D1 with their own plant counts (6, 6, 7), or six identical firms. | Six identical firms of 6 D1 plants: capacity 720, D_0 = 639.2. |
| Q8 | **Entrant details.** | Its plants: 0.5 × the survivors' mean capacity in operation after scrapping, divided by S, rounded half up, at least 1. Its first period: `util` = 1, so it follows and does not cut. r_new counts the initial plants aged 5 or less, so it is defined from t = 0. |
| Q9 | **Who draws a design.** A9 says "each firm with plants". | A firm that had a plant in operation in the period. Every firm takes its five variates anyway. |
| Q10 | **Excess-demand share.** | (D − K) / D, with K the total normal capacity in operation, offered or not. |
| Q11 | **The hurdle at λ = 1 is not always r̄.** It is r̄ only when the regulating technique has the best rate at its own price of production. On the initial menu h = 5.00 % at r̄ = 0.05, but at r̄ = 0.16 p^e = 100.26 and h = 17.05 %, D1's rate. | No change to the code; E3's text should say "about r̄". |
| Q12 | **Realised rate.** | Profit after depreciation over the purchase cost of the plants in operation, the same base as the rate at a price and as r_new. |
| Q13 | **Categories rule and λ.** v2 judged a categories design at the firm's own price. | At p^e, which is the firm's price in every E4 cell (λ = 0). |
| Q14 | **Sharing work in 3a–3d.** The rules say never push; four owners on four machines need the stage 2 commit and a way to return their part. | One branch per part from the stage 2 commit, exchanged by the owners themselves; build sessions still never push. |
| Q15 | **Leftovers of v2 in the tree.** The workflow file runs Python 3.11, `plot_outputs.py` and a LaTeX build of `docs/main.tex`, none of which exists here; the proposal puts `report.tex` "in the existing LaTeX project", which is not in this tree. | Stage 1 reduces the workflow to tests and `run.py` on Python 3.12. Where the report lives is for the group. |
| Q16 | **The pilot.** `v3-choices.md` has no result for it yet. | Build stages 1 and 2 regardless, since they do not depend on it; do not start 3c and 3d before the pilot is recorded. |

### The open points of A13

| # | Point | Proposed default |
| --- | --- | --- |
| a | Entrant's menu | The public menu only, as the proposal says: one rule for who knows what, and entry cannot bypass the lag L. With L = 2 the two readings differ by the designs first run in the last two periods. |
| b | Scrapping | The price compared with ucs is the owner's posted price of the period. The 2 periods are consecutive, for both tests. Idle = no output for 2 consecutive periods, made exact by the running order: lowest ucs first, then youngest. v2 shared output pro rata among equal-cost plants and used a second ordering to call the oldest idle; the same plants end up idle, and `idle_plants` and half of `dispatch` go (about 15 lines). The cost: among plants of one technique the young ones run full, so r_new is a little higher than in v2 when utilisation is below 1. |
| c | Entrant's funding | Equity from the rest-of-economy account, added to its funds as well, so that paying for the plants leaves cash and funds at 0. |
| d | E6 | D_0 = (340/383) × 1,200 = 1,065.3: the same initial utilisation as the base. μ = 0. Entry stays as in the base, so the mutant's label can also spread through inheritance. |
| e | Ties | Technique costs: the lower κ, then the lower ucs; a design that ties with the reference is not kept. Prices: equal by `math.isclose`; equal prices leave shares unchanged; equal unit costs give no edge. Exits: candidates leave from the smallest share up while at least 2 firms remain, and candidates with the same share stay or leave together. The parent of an entrant is drawn over the firms in order of `id`, which maps one uniform to a firm and breaks no tie. |
| f | Morris on T | 7 to 19, so that the 4-level grid is the integers 7, 11, 15, 19 and D2 keeps the lowest unit cost (D1 passes below it under T = 6.09). |
| g | Scrapping on unit cost | With the maximum age T: the rules forbid plants without one. Only the cost compared with the price changes. |
| h | Names | The table under "Conventions". |
| i | Constants | `shortage_step`, `exit_share`, `entry_window`, `scrap_periods`, `entry_size`, plus `min_firms`, `u_full`, `initial_price`, `demand_ratio`, `conflict_share` and `EPS`, all in `parameters.py` (section 5). |
