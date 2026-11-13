# Version 4 plan: files, interfaces, tests and build order

Plan of 10 November 2026 for the second rebuild of the group's agent-based model. No code is
written here. The specification is `v4-final-model.md` as corrected after the coherence review
(`v4-review.md`); `v4-choices.md` is the register and wins over it. "Decision n" below is row n
of the register. Version 3 (`../ABM-v3`, branch `v3`) is the reference to port from and is not
changed.

Every number quoted is provisional and names its run. "The default runs" are those of v3's
code with the settings of version 4 (`python3 -m experiments.price_rules v4_cost_edge`):
cost-edge cutting, r̄ = 0.16, overtime, the undercutting entrant, a shortage step of 0.25.

## Conventions

- **Line count.** Lines of the model code that are not blank, not a comment line and not part
  of a docstring. v3 counts 651 that way (769 with comments and docstrings).
- **Steps.** `setup`, `pricing`, `demand`, `accounts`, `scrapping`, `investment`, `entry`,
  and `common` for a definition several steps use. Equation files, step functions and test
  files carry these names.
- **Labels and rules.** A label is `shaikh` or `okishio`; a rule is `unit_cost` or
  `profit_rate`. `rule_shaikh` and `rule_okishio` map one to the other (decision 26).
- **Python.** The model, the harness and the tests run on `python3` with numpy alone. The
  figures, the figure of the viewer and Morris need matplotlib and SALib, which are in
  `../ABM-sources/.venv/bin/python` only (open question 4).

## 1. Where version 4 is built

A clean tree `../ABM-v4`: a git worktree on a new branch `v4` cut from the head of `v3`
(decision 10, as changed by Ugo on 10 November). v3 stays read-only beside it, as v2 did
beside v3.

```bash
git worktree add ../ABM-v4 -b v4 v3
```

The first commit of `v4` then does three things, as the first commit of v3 did with v2
(`651c773`, "v3: clean tree"):

- **It empties the tree.** `equations/`, `markets/`, `model/`, `experiments/`, `figures/`,
  `tests/`, `parameters.py`, `run.py`, `README.md` and `CLAUDE.md` are removed.
  `.gitattributes`, `.gitignore`, `.github/` and `requirements.txt` stay.
- **It keeps the documents.** `docs/design/` comes whole, with its history. Five files are the
  specification of version 4: `v4-final-model.md`, `v4-choices.md`, `v4-plan.md`,
  `v4-review.md` and `v4-literature-check.md`. The others are the records of v2 and v3:
  no rule, default or file layout is taken from them.
- **It writes the rules of the build.** A new `CLAUDE.md` (authority, the rules of section 12,
  the commands) and a new `README.md`.

The review said `v3` was cut from `main`. It was cut from the head of `v2` and emptied in its
first commit; `v4` does the same with `v3`. Nothing is copied by hand, and a later change to
a document is made in one tree only: after the first commit of `v4` the five documents are
edited there, not in `v3`.

## 2. File tree

Counts are the lines of section "Conventions". Files outside the count have none.

```
ABM-v4/
  CLAUDE.md  README.md  requirements.txt  .gitignore  .github/workflows/build.yml
  parameters.py                        60  every parameter and option, one dataclass
  run.py                               18  one run at the defaults -> outputs/periods.csv, run.csv
  equations/
    common_unit_cost.py                 2  uc = ucs + delta kappa
    common_profit_rate.py               3  the rate of a technique at a price
    common_hurdle.py                    8  evaluation price; hurdle of a rule
    common_technique_choice.py         12  cost at a hurdle; choice; frontier of the menu
    common_regulating_price.py          6  regulating technique; price of production
    setup_menu.py                      10  Shaikh's menu scaled to the general rate
    setup_initial_plants.py             4  staggered ages of the initial plants
    pricing_floor.py                    8  unit-cost floor; operating-cost floor
    pricing_cutting.py                 16  the price of a firm under the three cutting rules
    pricing_entitlement.py             10  who may cut: cost edge, normal price, systematic
    pricing_universal.py                9  universal undercutting
    demand_replicator.py               10  E = 1/p; replicator shares
    accounts_merit_order.py            11  which plants run, overtime included
    accounts_depreciation.py            2  straight-line charge
    accounts_dividends.py               2  d max(0, profit)
    scrapping_below_cost.py             5  the cost a price must cover; periods below it
    scrapping_idle_plants.py            2  periods without output
    scrapping_retirement.py             8  age, cost or idle
    scrapping_reserve.py                6  the three rules of the depreciation reserve
    investment_draw_marx.py             5  a Marx-biased design
    investment_draw_neutral.py          5  a design of the neutral set
    investment_draw_categories.py      11  a design of the categories rule
    investment_retained_earnings.py     4  plants the funds pay for
    investment_accelerator.py           4  plants missing for the demand addressed
    entry_new_plant_rate.py             6  r_new
    entry_probability.py                4  probability of an entrant
    entry_inherited_rule.py            11  the entrant's label
    entry_price.py                      5  the entrant's price
    entry_size.py                       4  the entrant's plants
    entry_exit_rule.py                 12  who leaves
  markets/
    payments.py                         4  pay(): the only place cash moves
    goods_market.py                    12  sales, re-allocation once, demand lost
    plant_market.py                    28  a plant is bought; a plant leaves with its reserve
    entry_exit.py                      52  a firm leaves; an entrant is created
  model/
    entities.py                        80  Technique, Plant, Firm, Account, Industry
    model.py                           40  the industry at t = 0; one run
    outputs.py                         78  tally of flows by firm; the period table
    scheduler.py                      290  STEPS, the seven step functions, close_period, check
  experiments/                             outside the count
    harness.py      cells x populations x seeds in parallel; runs.csv, cells.csv, resume
    cells.py        E0 to E6, E0r, the reruns, the reserve and the robustness checks as cells
    populations.py  homogeneous start, invasion (E6), firms per pair
    summary.py      the run row, with the E0 measures
    stats.py        Wilson interval, beyond drift, mean and its interval
    e0_gate.py      reads cells.csv and says whether E0 holds, rule by rule
    show_run.py     the run viewer
    morris.py       Morris screening (SALib)
    e5_channels.py  the reads of E5
  figures/          style.py, fig1 to fig6, tab3_robustness.py
  tests/            helpers.py and one file per step (section 11)
  docs/design/      the documents of v3; five are the specification (section 1)
```

| Part | v3 | Version 4 | Margin |
| --- | --- | --- | --- |
| `parameters.py`, `run.py` | 65 | 78 | |
| `equations/` | 147 | 205 | |
| `markets/` | 83 | 96 | |
| `model/` | 356 | 488 | |
| **Total** | **651** | **867** | **133 under 1,000** |

- **Where the margin goes first.** `scheduler.py`: the rule "no statement does two things"
  costs most there: step 1 alone takes 72 lines (section 12) against 10 in v3. If the file
  passes 330 lines, `set_prices` and `invest` each take a helper
  module in `model/`; no rule is cut to save a line.
- **The first candidate to drop, if the group ever wants fewer lines,** is normal-price
  cutting: at 0.16 it gives the same industry as the default (open question 9).

## 3. What comes from v3

"As it is": the code is copied, then its comments and docstrings are rewritten to cite the
proposal. "Rewritten": same rule, written again for a reader. No file of version 4 is
replaced from outside: every patch of `experiments/price_rules.py` becomes an option.

| v3 file | In version 4 | Reason |
| --- | --- | --- |
| `parameters.py` | Rewritten | Options added (section 7); `u_target` and `menu` leave; `rbar`, `shortage_step` change |
| `run.py` | As it is | |
| `equations/common_*.py` (5 files) | As they are | The rule that differs does not change |
| `equations/setup_initial_plants.py` | As it is | |
| — | New: `setup_menu.py` | The scaled menu (decision 12) |
| `equations/pricing_rule.py` | Rewritten as `pricing_cutting.py` and `pricing_entitlement.py` | One function held two regimes behind a flag; the three cutting rules now differ in one named test. The floor and the unit cost of the cost edge become two arguments |
| `equations/pricing_floor.py` | Rewritten | Gains the operating-cost floor: `operating_cost_floor` of `price_rules.py` |
| `price_rules.leader_follow_price` | New: `pricing_universal.py`, as it is | Renamed (decision 9) |
| `price_rules.normal_price_cutting` | Into `pricing_entitlement.py` | |
| `price_rules.set_prices_*`, `install_*`, `RULES`, `experiments()` | Dropped | The step chooses the rule by `params.pricing`; the cells set parameters |
| `equations/demand_replicator.py` | As it is | |
| `equations/accounts_merit_order.py` | Rewritten | Overtime: `dispatch_with_overtime`, over the offered plants only (decision 18) |
| `equations/accounts_depreciation.py`, `accounts_dividends.py` | As they are | |
| `equations/scrapping_below_cost.py`, `scrapping_idle_plants.py`, `scrapping_retirement.py` | As they are | |
| `equations/scrapping_reserve.py` | Rewritten | Three levels |
| `equations/investment_draw_*.py` (3), `investment_retained_earnings.py` | As they are | |
| `equations/investment_accelerator.py` | Rewritten | No target utilisation |
| `equations/entry_new_plant_rate.py`, `entry_probability.py`, `entry_size.py`, `entry_exit_rule.py` | As they are | |
| `equations/entry_inherited_rule.py` | As it is; its `shares` argument becomes `weights` | The market passes shares, or one vote a firm (decision 11) |
| `price_rules.entrant_undercuts` | New: `entry_price.py` | The entrant's price as an equation, with its two levels |
| `markets/payments.py`, `goods_market.py` | As they are | The sales limit is passed in: `u_max` times the capacity offered |
| `markets/plant_market.py` | Rewritten | The reserve option; the tally by firm |
| `markets/entry_exit.py` | Rewritten | `create_entrant` did nine things in one block; the entrant's price and label options |
| `model/entities.py` | As it is, less `u_target` | `Firm.active`, `Firm.cut` and the rest stay |
| `model/model.py` | Rewritten | The menu is built from r̄; `build` in named stages |
| `model/outputs.py` | Rewritten | The tally by firm; one column added (`overtime`) |
| `model/scheduler.py` | Rewritten | Section 12; `STEPS` and `close_period` |
| `experiments/harness.py`, `stats.py` | As they are, less the `initializer` argument | Nothing is patched any more |
| `experiments/summary.py` | As it is, plus the E0 measures, the share of designs kept, the gap in rates, the E6 columns | Decision 8 |
| `experiments/cells.py` | Rewritten | Section 9 |
| `experiments/diagnosis.py`, `price_rules.py` | Dropped | Throwaway scripts; their variants are parameters now |
| `figures/style.py`, `fig1` to `fig3` | As they are; `PRICING` names the four rules | `fig2` reads a run of the viewer |
| `tests/*.py` (267 tests) | Ported file by file (section 11) | `test_price_rules.py` is split among `test_pricing`, `test_demand`, `test_accounts`, `test_entry` |
| `.github/workflows/build.yml`, `requirements.txt` | As they are | |

## 4. Data structures

As in v3 (`model/entities.py`), objects compared by identity. Changes are marked.

| Entity | Fields | Changed |
| --- | --- | --- |
| `Technique` | `name`, `ucs`, `kappa`, `first_run` | — |
| `Plant` | `technique`, `capacity`, `cost`, `book_value`, `age`, `output`, `profit`, `below_cost`, `idle` | — |
| `Firm` | `id`, `label`, `rule`, `rng`, `born`, `price`, `share`, `sales`, `notional`, `util`, `hurdle`, `cash`, `funds`, `profit`, `write_offs`, `cut`, `active`, `plants`, `pending_plants`, `known`; property `capacity` | `util` can exceed 1 |
| `Account` | `cash` | — |
| `Industry` | `params`, `seed`, `rng`, `demand_0`, `time`, `firms`, `roe`, `public`, `waiting`, `demand`, `lost`, `excess`, `reg`, `reg_price`, `r_new`, `next_id`, `tally`, `rows` | `tally` is a list of flows, one entry a flow: (firm id, label, key, amount) |
| `Quote` (in `scheduler.py`) | `firm`, `price`, `cost`, `normal_price`, `floor`, `spare` | New: what step 1 reads about a firm, taken at the start of the step |

- **Two stocks of money.** `cash` moves only through `pay`. `funds` is what the firm may
  invest: retained profit, released reserves and an entrant's equity, less plants bought.
  Retained earnings spend the smaller of the two; the accelerator spends cash.
- **The tally.** `count(industry, firm, key, amount)` appends one entry. The period table
  sums the entries of a label with `math.fsum`; the viewer sums those of a firm. A firm that
  left in step 6 is still in the tally of its last period.
- **Random streams.** `SeedSequence(seed, spawn_key=(0,))` for the industry and
  `(1, firm id)` for a firm, as in v3.

## 5. The period loop

```
STEPS = (start_period, set_prices, allocate_demand, produce_and_account,
         scrap_plants, invest, enter_and_exit)

period(industry):
    for step in STEPS: step(industry)
    close_period(industry)            # the rows of the period, the checks, time + 1
```

`model.build(params, seed)` runs once before period 0. **The scaled menu acts there**: the
public menu is `scaled_menu(...)`, so the cost of the initial plants, the initial cash and
every later price of a plant follow r̄.

| Step | Reads | Writes | Where an option acts |
| --- | --- | --- | --- |
| 0 `start_period` | `time`, `growth`, `pending_plants`, `waiting`, `public_lag` | `demand`; `plants` (deliveries, an entrant's included); `first_run`; `public`, `waiting`, `known`; an empty `tally` | — |
| 1 `set_prices` | Each firm's `price`, `util`, plants (unit cost, κ, last `output`); `excess` | `price`, `cut` | `pricing` chooses the rule; `price_floor` the floor |
| 2 `allocate_demand` | `share`, `price`, plants (operating cost, capacity), `demand` | `share`, `notional`, `sales`; `lost`, `excess` | **Overtime**: a firm sells up to `u_max` times the capacity it offers. The shortage signal stays demand above normal capacity |
| 3 `produce_and_account` | `sales`, `price`, the offered plants | `output`, `profit`, `book_value`, `age` of each plant; cash through `pay`; `profit`, `funds`, `util`, `active`; `reg`, `reg_price`, `r_new`; the rows of the period | **Overtime**: the offered plants run to normal capacity, then to `u_max` times it, in the same order |
| 4 `scrap_plants` | `age`, `output`, the owner's `price`, `r_new` | `below_cost`, `idle`; `plants`; `funds` or cash; `write_offs` | **The reserve**: `reserve` chooses whether a reserve joins the funds |
| 5 `invest` | The firm's stream; the public menu and its own designs; `price`, `reg_price`; `funds`, `cash`, `notional` | `hurdle`, `known`; `pending_plants`; cash and `funds` | `tech_change`, `investment` |
| 6 `enter_and_exit` | The industry's stream; shares and capacities; `r_new`; the lowest price of a firm with a plant in operation; the public menu | `firms`; shares; the entrant, its price and its plants on order; cash | **The entrant's price**: `entry_price`. Its label: `entry_label` |
| `close_period` | The tally; the firms | The flows of the rows, `capacity_next`, `share_end`, closing stocks; the checks; `time` | — |

Step by step, in the words of the proposal's schedule:

```
0  start_period
     D_t = D_0 (1 + g)^t
     each firm: plants += pending_plants; a technique that runs for the first time is dated
     a design dated public_lag periods ago joins the public menu and leaves its owner's list
     the public menu keeps its frontier

1  set_prices                                   (written out in section 12)
     quotes = one Quote a firm with a plant in operation, read before any price changes
     each such firm: rivals = the other quotes
        universal:  price = universal_price(own price, lowest price of all quotes, ...)
        otherwise:  entitled = the test of the rule (cost edge | normal price | systematic)
                    price = cutting_price(own price, rivals' prices, entitled, ...)
     a firm without a plant in operation keeps its price

2  allocate_demand
     shares = replicator(shares, 1 / price, chi)
     offered_i = capacity of the plants of i with ucs <= price_i
     sales, lost = allocate(D_t, shares, u_max x offered)        # re-allocation once
     excess = max(0, D_t - K) / D_t,  K = normal capacity in operation

3  produce_and_account
     each firm: outputs = dispatch(its offered plants, sales, u_max)
        each plant in operation: depreciation, profit, book value, age + 1
        pay: revenue in, operating cost out, dividends out; funds += retained profit
        util = sales / normal capacity
     regulating technique and its price of production
     r_new = capacity-weighted profit / cost of the plants aged entry_window or less
     the two rows of the period

4  scrap_plants
     each plant: count periods below cost and periods idle; reason = age | cost | idle
     a plant that leaves: reserve = cost - book value
        reserve_released(rule, r_new, rbar):  funds += reserve
        otherwise:                            pay min(reserve, cash) to the rest of the economy
        write off the book value

5  invest
     each firm: four uniforms and one normal, used or not
        p_e, hurdle, best technique on the public menu and its own designs
        with a plant in operation and u < pi: a design from the best technique;
           kept if its own rule prefers it; the hurdle is recomputed
        retained:     plants = floor(min(funds, cash) / plant cost)
        accelerator:  plants = min(ceil((notional - capacity - on order) / S), floor(cash / cost))
        buy the plants: pay now, delivered next period

6  enter_and_exit
     three uniforms, used or not
     exits: share < 1 % or no capacity in operation or on order, while 2 firms remain
     with probability min(1, theta max(0, r_new - rbar) / rbar): one entrant
        label: an incumbent drawn by market share (or one vote a firm), flipped with mu
        technique: its rule on the public menu, at p_e with the lowest price as its own
        price: entrant_price(lowest price, unit cost of its plants, c, entry_price)
        plants: 0.5 x mean capacity, paid by equity; share = its capacity / next capacity

   close_period
     record_end; check: all cash sums to 0, no negative cash, shares sum to 1,
     capacity next = capacity - retired - exits + ordered + entry; time += 1
```

## 6. Equations

Pure functions: no state, no random draw. Each file opens with its formula and the paragraph
of `v4-final-model.md` it comes from.

| File | Signature | Formula | Paragraph of the proposal |
| --- | --- | --- | --- |
| `common_unit_cost.py` | `unit_cost(ucs, kappa, delta) -> float` | ucs + δκ | "Setting" |
| `common_profit_rate.py` | `profit_rate_at_price(price, ucs, kappa, delta) -> float` | (p − uc) / κ | "The one rule that differs" |
| `common_hurdle.py` | `evaluation_price(price, reg_price, lam) -> float` | (1 − λ)p + λ p_R | Same |
| | `hurdle(rule, eval_price, menu, delta) -> float` | 0 under `unit_cost`; max(0, max_j rate_j(p^e)) under `profit_rate` | Same |
| `common_technique_choice.py` | `technique_cost(ucs, kappa, hurdle, delta) -> float` | ucs + (δ + h)κ | Same |
| | `choose_technique(menu, hurdle, delta) -> Technique` | argmin of that cost; a tie to the lower κ, then the lower ucs | Same |
| | `frontier(menu, delta) -> list` | The techniques no other beats on both unit cost and κ | Speed, as v3 |
| `common_regulating_price.py` | `regulating_technique(techniques, delta) -> Technique` | Lowest unit cost in operation; a tie to the lower κ | Same; step 3 |
| | `price_of_production(ucs, kappa, delta, rbar) -> float` | uc + r̄κ | "Setting" |
| `setup_menu.py` | `scaled_menu(shaikh_menu, shaikh_rate, rbar, delta, scaling) -> list[tuple]` | κ_j = κ^S_j × 0.16 / r̄; ucs_j = ucs^S_j − δ(κ_j − κ^S_j); the table itself under `fixed`; `ValueError` if a ucs_j is not positive | "Initial industry" |
| `setup_initial_plants.py` | `initial_ages(output, size, life) -> list[int]` | n = output / S rounded half up; ages floor(kT / n), k = 0 … n − 1 | Same |
| `pricing_floor.py` | `unit_cost_floor(unit_costs) -> float` | The lowest unit cost of the firm's plants | Step 1 |
| | `operating_cost_floor(ucs_ran, ucs_owned) -> float` | The highest ucs of the plants that ran last period; the lowest ucs owned if none ran | Step 1, option `price_floor` |
| `pricing_cutting.py` | `cutting_price(previous, rival_prices, entitled, excess, floor, cut, shortage_step) -> tuple[float, bool]` | After a shortage: the next higher rival price, or previous × (1 + step × excess); never below the floor. Without a rival: max(previous, floor). Else target = (1 − c)P if entitled, P if not; price = max(min(previous, target), floor). Returns the price and whether the firm cut | Step 1, the three cutting rules |
| `pricing_entitlement.py` | `entitled_cost_edge(spare, own_cost, costs_at_lowest) -> bool` | Spare capacity and a unit cost below that of a rival posting P | *Cost-edge cutting* |
| | `entitled_normal_price(spare, own_cost, costs_at_lowest, lowest_rival, own_normal_price) -> bool` | Spare capacity, and P above the firm's price of production or the cost edge | *Normal-price cutting* |
| | `entitled_systematic(spare) -> bool` | Spare capacity | *Systematic cutting* |
| `pricing_universal.py` | `universal_price(previous, lowest, floor, excess, alone, cut, rise, cap) -> tuple[float, bool]` | Alone: min((1 + z) previous, cap × floor). After a shortage: (1 + z)L. Else (1 − c)L, or the floor if higher | *Universal undercutting* |
| `demand_replicator.py` | `competitiveness(price) -> float` | 1 / p | Step 2 |
| | `replicator_shares(previous_shares, competitiveness, chi) -> list[float]` | f_i [1 + χ(E_i − Ē) / Ē], cut at 0 and renormalised | Step 2 |
| `accounts_merit_order.py` | `dispatch(ucs, ages, capacity, quantity, u_max) -> list[float]` | Lowest ucs first, then youngest, each to its capacity; what is left in the same order to u_max times capacity | Step 3; "Overtime, in one place" |
| `accounts_depreciation.py` | `depreciation(cost, book_value, delta) -> float` | min(δ × cost, book value) | Step 3 |
| `accounts_dividends.py` | `dividends(profit, payout) -> float` | d × max(0, profit) | Step 3 |
| `scrapping_below_cost.py` | `scrap_cost(ucs, kappa, delta, rule) -> float` | ucs; ucs + δκ under `unit_cost` | Step 4 |
| | `periods_below_cost(previous, price, cost) -> int` | previous + 1 if p < cost, else 0 | Step 4 |
| `scrapping_idle_plants.py` | `periods_idle(previous, output) -> int` | previous + 1 without output, else 0 | Step 4 |
| `scrapping_retirement.py` | `retirement_reason(age, life, below_cost, idle, periods) -> str or None` | `age`, then `cost`, then `idle` | Step 4 |
| `scrapping_reserve.py` | `reserve_released(rule, r_new, rbar) -> bool` | `conditional`: r_new is undefined or r_new ≥ r̄. `always`: true. `never`: false | Step 4, option `reserve` |
| `investment_draw_marx.py` | `draw_marx(ucs_o, kappa_o, u, z, step, bias, spread) -> tuple` | ucs_n = (1 − a)ucs_o, κ_n = (1 + ka)κ_o, a = uA, k = β e^(σz) | "Technical change" |
| `investment_draw_neutral.py` | `draw_neutral(ucs_o, kappa_o, u_step, u_direction, step) -> tuple` | As v3's file | Same, option |
| `investment_draw_categories.py` | `draw_categories(ucs_o, kappa_o, delta, eval_price, u_kind, u_step, u_size, step, conflict_share) -> tuple` | As v3's file; the categories at p^e | Same, option |
| `investment_retained_earnings.py` | `plants_affordable(funds, plant_cost) -> int` | floor(funds / cost), at least 0 | Step 5 |
| `investment_accelerator.py` | `plants_wanted(notional, capacity, on_order, size) -> int` | ceil((notional − capacity − on order) / S), at least 0 | Step 5 |
| `entry_new_plant_rate.py` | `new_plant_rate(rates, capacities) -> float or None` | Capacity-weighted mean; undefined without a plant | Step 3 |
| `entry_probability.py` | `entry_probability(r_new, rbar, theta) -> float` | min{1, θ max(0, r_new − r̄) / r̄}; 0 when r_new is undefined | Step 6 |
| `entry_inherited_rule.py` | `inherited_label(labels, weights, mutation, u_parent, u_flip) -> str` | The label of an incumbent drawn by weight, flipped if u_flip < μ | Step 6 |
| `entry_price.py` | `entrant_price(lowest, floor, cut, rule) -> float` | `undercut`: max((1 − c) lowest, floor). `lowest`: lowest | Step 6, option `entry_price` |
| `entry_size.py` | `entrant_plants(capacities, entry_size, size) -> int` | 0.5 × mean capacity / S, rounded half up, at least 1 | Step 6 |
| `entry_exit_rule.py` | `leaving(shares, capacities, exit_share, min_firms) -> list[bool]` | Share below 1 % or no capacity; the largest stay while fewer than 2 would remain, equal shares together | Step 6 |

## 7. `parameters.py` as it will be

It matches the parameter table and the table of options of the proposal, name for name.

```python
"""Parameters of version 4 (v4-final-model.md, parameter table and table of options).

Experiments change fields with dataclasses.replace. No other file holds a constant.
"""
from dataclasses import dataclass

LABELS = ("shaikh", "okishio")
EPS = 1e-9                                  # numerical tolerance
MONEY_EPS = 1e-6                            # tolerance on a sum of money or of capacity

# Shaikh 2016, Tables 7.10-7.11: name, operating cost, capital per unit of normal output.
SHAIKH_MENU = (("C", 64.25, 137.50), ("D1", 61.77, 142.31), ("D2", 59.21, 157.89))
SHAIKH_RATE = 0.16                          # the general rate of that table

# One firm for each pair (technique, label): technique, label, normal output.
START = tuple((name, label, output)
              for name, output in (("C", 120.0), ("D1", 120.0), ("D2", 140.0))
              for label in LABELS)

# The levels of every option that takes a name; model.build refuses any other level.
OPTIONS = {
    "rule_shaikh": ("unit_cost", "profit_rate"),
    "rule_okishio": ("unit_cost", "profit_rate"),
    "menu_scaling": ("scaled", "fixed"),
    "pricing": ("cost_edge", "normal_price", "systematic", "universal"),
    "price_floor": ("unit_cost", "operating_cost"),
    "scrap_cost": ("operating_cost", "unit_cost"),
    "reserve": ("conditional", "always", "never"),
    "tech_change": ("marx", "neutral", "categories", "none"),
    "investment": ("retained", "accelerator"),
    "entry_price": ("undercut", "lowest"),
    "entry_label": ("share", "even"),
}


@dataclass(frozen=True)
class Parameters:
    periods: int = 200

    # Population and demand
    rule_shaikh: str = "unit_cost"          # unit_cost | profit_rate
    rule_okishio: str = "profit_rate"       # unit_cost | profit_rate
    start: tuple = START
    firms_per_pair: int = 1                 # robustness: 2 and 5
    plant_size: float = 20.0                # S; Morris 10-40
    initial_price: float = 100.0
    demand_ratio: float = 340 / 383         # D_0 over initial capacity
    growth: float = 0.0                     # g; E4: 0.01

    # General rate and initial menu
    rbar: float = 0.16                      # E0r: 0.10, 0.05
    menu_scaling: str = "scaled"            # scaled | fixed (robustness)
    plant_life: int = 10                    # T, delta = 1 / T; Morris 7-19

    # Step 1, pricing
    pricing: str = "cost_edge"              # cost_edge | normal_price | systematic | universal
    price_floor: str = "unit_cost"          # unit_cost | operating_cost (robustness)
    price_cut: float = 0.02                 # c, also the entrant's; Morris 0.01-0.05
    u_full: float = 1.0                     # spare capacity: last utilisation below this
    shortage_step: float = 0.25             # cutting rules; robustness 0.5; Morris 0.1-0.5
    shortage_rise: float = 0.03             # z, universal undercutting
    monopoly_cap: float = 3.0               # a firm alone stops at this multiple of its floor

    # Steps 2 and 3, demand and production
    chi: float = 1.0                        # Morris 0.25-4
    u_max: float = 1.2                      # overtime limit; 1 gives none; Morris 1-1.4
    payout: float = 0.5                     # d; Morris 0.25-0.75

    # Step 4, scrapping
    scrap_cost: str = "operating_cost"      # operating_cost | unit_cost (robustness)
    scrap_periods: int = 2
    reserve: str = "conditional"            # conditional | always | never (sensitivity)

    # Step 5, technical change and investment
    tech_change: str = "marx"               # marx | neutral | categories | none
    bias: float = 1.5                       # beta; E2: 0, 0.5, 1.5, 3; Morris 0.5-3
    bias_spread: float = 0.8                # sigma
    design_step: float = 0.05               # A; Morris 0.02-0.10
    draw_prob: float = 0.2                  # pi; Morris 0.1-0.4
    public_lag: int | None = 2              # L; None: never public (robustness)
    conflict_share: float = 0.5             # q, categories rule
    lam: float = 0.0                        # lambda; E3: 0, 0.25, 0.5, 0.75, 1
    investment: str = "retained"            # retained | accelerator

    # Step 6, entry and exit
    entry_speed: float = 5.0                # theta; Morris 1-10
    mutation: float = 0.02                  # mu; Morris 0-0.05; 0 in E6
    entry_window: int = 5                   # r_new: plants aged this or less
    entry_size: float = 0.5                 # entrant's capacity over the mean capacity
    entry_price: str = "undercut"           # undercut | lowest (robustness)
    entry_label: str = "share"              # share | even (robustness)
    exit_share: float = 0.01
    min_firms: int = 2

    @property
    def delta(self) -> float:
        return 1.0 / self.plant_life
```

- **Against v3.** New: `menu_scaling`, `price_floor`, `shortage_rise`, `monopoly_cap`,
  `u_max`, `reserve`, `entry_price`, `entry_label`. Gone: `menu` (built from `SHAIKH_MENU`),
  `u_target`. Changed: `rbar` 0.16, `shortage_step` 0.25, `pricing` with four levels.
- **Frozen after stage 2.** A new constant is then a departure to register.
- **A wrong level raises.** `build` checks every option against its levels, so a misspelt
  cell fails at once instead of running the default. The levels are in `OPTIONS`, added in
  stage 1 with `MONEY_EPS`, the tolerance of `check`: both are constants, so they are here.
  The file then counts 69 lines, against 60 in section 2.

## 8. Output tables

**The period table**: one row per period and label, in `industry.rows`, as in v3. It observes
and never decides. Undefined values are `None`.

| Group | Columns |
| --- | --- |
| Identity | `t`, `label`, `rule` |
| Stocks at step 3 | `firms`, `capacity`, `share`, `notional`, `sales`, `sales_share`, `util`, `price`, `ucs`, `kappa`, `unit_cost`, `cuts`, `profit`, `capital`, `profit_rate` |
| New | `overtime`: output above normal capacity, summed over the firms of the label |
| Industry, the same on both rows | `demand`, `lost`, `low_price`, `reg_price`, `price_over_reg`, `r_new`, `war`, `leader_cheapest`, `rate_low`, `rate_high` |
| Flows of the period, from the tally | `dividends`, `cap_retired`, `cap_retired_age`, `cap_retired_cost`, `cap_retired_idle`, `cap_released`, `withdrawn`, `cap_ordered`, `cap_exit`, `cap_entry`, `orders`, `orders_dearer`, `drawn`, `kept`, `entries`, `exits` |
| After step 6 | `capacity_next`, `share_end`, `cash`, `funds`, `write_offs`, `hurdle` |

**The run row**: one row per run, a function of the period table alone
(`experiments/summary.py`). The columns of v3 stay: `outcome`, `cap_share_end`,
`sales_share_end`, the takeover, the two decompositions (`dk_*`, `ds_*`), `price_over_reg`,
`war_freq`, `leader_cheapest`, `rate_spread`, `rate_industry`, `entries`, `exits`,
`open_share`, the plants leaving by reason, `g_ucs`, `g_kappa`, `firms_end`, `capacity_end`,
`capacity_over_demand`, `util_mean`, `lost_share`, `marx_biased`, and by label the hurdle,
the dearer orders, the realised rate, entries, exits, the reserves released and the growth
of ucs and κ.

New columns. Those of E0 are read on periods 20 to 199 (`E0_START = 20` in `summary.py`):

| Column | Definition | E0 line |
| --- | --- | --- |
| `e0_leader` | Share of periods with `leader_cheapest` = 1 | at least 0.9 |
| `e0_price` | Mean of `price_over_reg` | 0.9 to 1.2 |
| `e0_crossings` | Times `price_over_reg` passes from one side of 1 to the other between two periods | at least 5 |
| `e0_capacity` | Mean of capacity over demand | 0.9 to 1.2 |
| `e0_r_new` | Mean of `r_new` where defined | 0.6 to 2 times r̄ |
| `e0_lost` | Sum of `lost` over the sum of `demand` | at most 0.10 |
| `e0_alive` | `capacity_end` above 0 | true |
| `e0_pass` | Every line above is true | — |
| `e0_lines` | Share of the seven lines that are true | Morris outcome |
| `e0_rate_industry`, `e0_rate_spread` | The industry rate and the mean spread of rates, same window | reported |
| `e0_capacity_min`, `e0_capacity_max`, `e0_price_max` | The range of capacity over demand and the highest price over the price of production within the run | reported |
| `overtime_share` | Output above normal capacity over output | — |
| `rate_gap` | `rate_shaikh` − `rate_okishio` | H6; Morris outcome |
| `kept_shaikh`, `kept_okishio` | Designs kept over designs drawn, by label | E0r |
| `mutant_share_end`, `invaded` | E6 only: the mutant label's final capacity share; whether it is above 0.1 | E6 |

`cells.csv` gives the mean of every column, so the mean of `e0_pass` is the share of seeds
that pass. `python -m experiments.e0_gate <folder>` reads it and prints, rule by rule, the
seeds that pass in each population, whether E0 holds (at least 0.9 in both), and the weakest
line.

## 9. Experiments

A cell is a dictionary of parameter overrides, run for every population of its experiment on
the same seeds. `python -m experiments.harness <name> [--seeds N] [--jobs N] [--resume]
[--keep-periods 0,1,2]` writes `outputs/<name>/runs.csv` and `cells.csv`. Populations: `mixed`
and the two controls `all_unit_cost`, `all_profit_rate`.

**E0 is the gate.** It is run and read first, with `e0_gate`. If it does not hold at the
default rule on the new code, nothing else is read and the difference from the reference
below is diagnosed (decision 7).

| Priority | Name | Cells | Populations | Seeds | Runs |
| --- | --- | --- | --- | --- | --- |
| 0 | `E0` | `tech_change="none"` × the 4 price rules | 2 controls | 50 | 400 |
| 1 | `E0r` | At the default rule, `rbar` = 0.10 and 0.05 on the scaled menu: a cell without draws and a cell at the defaults | 2 controls; 3 | 50; 500 | 3,200 |
| 1 | `reruns` | What the proposal marks "100 seeds", at the default rule: the accelerator; a shortage step of 0.5 (without draws, at the defaults, under the accelerator); `entry_price="lowest"` and `u_max=1` (each without draws and at the defaults); `reserve` = `always` and `never` (the same two); `growth=0.01` | 2 controls without draws; 3 otherwise | 50; 500 | 12,500 |
| 1 | `homogeneous` | The 6 cells of E2 with six firms on D1 (`populations.homogeneous`) | 3 | 200 | 3,600 |
| 2 | `E1` | The defaults × the 4 price rules | 3 | 500 | 6,000 |
| 2 | `E2` | β = 0, 0.5, 1.5, 3; the neutral set; no draws; × the 4 price rules | 3 | 200 | 14,400 |
| 2 | `E3` | λ = 0, 0.25, 0.5, 0.75, 1 × 3 price rules (default, systematic, universal) | 3 | 200 | 9,000 |
| 3 | `E4` | 3 price rules × 2 investment rules × g (0, 0.01), under `marx` and under `categories`; × 2 levels of r̄ if E0r keeps one | 3 | 200 | 14,400, or 28,800 |
| 3 | `E5` | No run: `e5_channels.py` reads E4 (the two decompositions; the regression of `rate_gap` on `okishio_dearer` with cell effects) and E3 at λ = 0 and 1 (`okishio_dearer`, the rates by label, the spread of hurdles) | | | 0 |
| 3 | `morris` | 12 parameters, 10 trajectories on a 4-level grid: 130 points | 3 | 100 | 39,000 |
| 4 | `E6` | 1 among 9, both ways, at the default and under universal undercutting (`populations.invasion`) | mixed, one control | 500 | 4,000 |
| 4 | `reserve` | `reserve` = `always` and `never` under universal undercutting: without draws and at the defaults | 2 controls; 3 | 50; 500 | 3,200 |
| 4 | `robustness` | No overtime under the 3 other rules (4,800); operating-cost floor at the default and under universal undercutting (3,000); `entry_label="even"`, the same two (3,000); scrapping on unit cost, E1 and the 12 `marx` cells of E4 (7,800); `public_lag=None` (600); 12 and 30 firms, E1 and 4 cells of E4 (6,000) | 3 | 500 or 200 | 25,200 |
| 4 | `fixed_menu` | Only if E0r keeps a level: E0 and E1 on the fixed menu at that level | 2 controls; 3 | 50; 500 | 1,600 |

- **Total.** 134,900 runs without the two conditional lines: about half an hour on 10
  workers at v3's speed (11,200 runs in 2 min 27 s). Priorities 0 and 1 are 19,700 runs,
  about 4 minutes.
- **What E0r decides.** r̄ enters E4 at 0.10 if E0 holds there at the default rule, else at
  0.05 if it holds there, else not at all (decision 1). It reports `kept_shaikh` and
  `kept_okishio` beside the share won, since β stays at 1.5 (decision 2).
- **E0 with draws.** `e0_gate` is also run on the two controls of E1 and reported beside
  E0, outside the gate (decision 6).
- **Morris.** `bias` 0.5–3, `design_step` 0.02–0.10, `draw_prob` 0.1–0.4, `price_cut`
  0.01–0.05, log₂ `chi` −2 to 2, `payout` 0.25–0.75, `plant_life` 7–19,
  `plant_size` 10–40,
  `entry_speed` 1–10, `mutation` 0–0.05, `u_max` 1–1.4, `shortage_step` 0.1–0.5. Outcomes:
  `gap`, the mean `cap_share_end`, `lost_share`, `e0_lines`, `rate_gap`. Output
  `outputs/morris/morris.csv`: μ*, σ and the interval of μ* by parameter and outcome.
- **E6.** Ten firms of 6 plants on D1, nine of the resident label and one of the other,
  D_0 = 1,065.3, μ = 0; the control puts the mutant on the resident's rule.

**Reference numbers** for the first reads, from v3's code with these settings. A reference,
not a gate: version 4 differs from that code by decisions 14 and 18.

| Measure | Reference | Run |
| --- | --- | --- |
| Seeds that pass E0, default | 50 and 49 of 50 | Cost-edge, r̄ = 0.16, 50 seeds, recomputed in the review |
| The same, normal-price; universal; systematic | 50 and 50; 46 and 43; 0 and 0 | Same |
| Mean r_new and industry rate in E0, default | 0.159 and 0.158; 0.132 and 0.130 | Same |
| Share won, default | 0.92 (0.90–0.94); controls 0.46 and 0.46 | Cost-edge, r̄ = 0.16, 500 seeds |
| Final capacity share; change in sales share through the price | 0.86; +0.21 | Same |
| Hurdle of the profit-rate label; its dearer orders | 0.170; 0.80 | Same |
| Realised rates, unit-cost and profit-rate label; demand lost | 0.148 and 0.151; 0.069 | Same |
| Share won, normal-price; systematic; universal | 0.92; 0.76; 0.23 | r̄ = 0.16, 500 seeds each |
| Share won for λ = 0 to 1, default | 0.93, 0.86, 0.83, 0.62, 0.61 | Cost-edge, r̄ = 0.16, 200 seeds each |

**Figures.** `fig1_conflict_zone` (the menu, no run), `fig2_typical_run` (a run of the
viewer), `fig3_bias_lambda` (E2 and E3, one curve a price rule), `fig4_heatmaps` and
`fig5_decomposition` (E4), `fig6_morris`, `tab3_robustness`.

## 10. The run viewer

`experiments/show_run.py`, outside the line count. It runs one industry and shows why it
behaved as it did.

```bash
python -m experiments.show_run --seed 7 pricing=universal rbar=0.05 population=all_unit_cost
```

- **Inputs.** `--seed` (default 0); any parameter as `name=value`, converted by the type of
  its field in `Parameters`; `population` = `mixed` (default), `all_unit_cost` or
  `all_profit_rate`; `--firms` for one line a firm; `--name` for the output folder
  (default: the overrides and the seed); `--no-figure` for the tables alone.
- **How it steps the model.** It calls `model.build`, then for each period the functions of
  `scheduler.STEPS` in order and `scheduler.close_period`. Between steps it reads the firms
  and writes its own rows. The model has no recorder for it and no branch that knows the
  viewer exists.

| Read after | What | Why then |
| --- | --- | --- |
| Step 3 | Each firm's price, floor, sales, capacity, utilisation, profit, share, unit cost and κ of its best plant | The values the period table reads |
| Step 5 | Each firm's hurdle; from the tally its orders, dearer orders, plants scrapped by reason and reserve withdrawn | Before a firm can leave |
| Step 6 | The firms that left and the entrant, by comparing the lists of firms; the share after entry | Entry and exit of the period |

- **Files**, in `outputs/runs/<name>/`: `periods.csv` (the period table), `firms.csv` (one
  row per firm and period), `prices.csv` (how the prices vary, one row a period: lowest,
  highest, mean, standard deviation and coefficient of variation of the posted prices of the
  firms in operation, their spread over the price of production, the log change of the
  industry price, `war`), `run.csv` (the run row), `run.txt` (outcome, final shares, the E0
  measures line by line, the two decompositions, the variability of prices from period 20),
  `run.pdf` and `run.png` (the figure).
- **A check in the viewer.** Its `periods.csv` is the period table of `model.run` for the
  same parameters and seed; a test asserts it.
- **The figure.** Twelve panels on one time axis, in two columns, following `figures/style.py`:
  blue for the unit-cost label and orange for the profit-rate label in every panel, no
  second axis, one question a panel as its title.

| Panel | Series | Source | Question |
| --- | --- | --- | --- |
| Prices | Posted price by label, or one line when they coincide; the price of production of the regulating technique; the lowest unit cost in operation | Period table; `firms.csv` | Does the price gravitate, and who is below whom? |
| Capacity and sales | Normal capacity over demand; sales over demand; the band between 1 and u_max | Period table | When is the industry short, and when does it work overtime? |
| Demand lost | `lost` over `demand` | Period table | How long and how deep are the shortages? |
| Entry gate | `r_new` against r̄; the industry rate; the periods with `withdrawn` above 0, shaded | Period table | When does capital enter and when does it leave? |
| Firms | Firms with a plant; entries and exits a period | Period table | Who enters and who leaves, and when? |
| Selection | Capacity share and market share of the unit-cost label | Period table | Which label gains, and through sales or capacity? |
| Choice of technique | Hurdle of the profit-rate label; `orders_dearer` over `orders` | Period table | How far apart are the two rules in this run? |
| Techniques | Unit cost by label; capital per unit by label | Period table | Is technical change Marx-biased, and for whom? |
| Profit rates | Realised rate by label | Period table | Does the rule that maximises the rate realise it? |
| Plants | Capacity ordered by label; capacity leaving by reason | Period table | Where does capacity come from and go? |
| Spread of prices | Lowest to highest posted price over the price of production, shaded; the industry price over it | `prices.csv` | How far apart are the firms' prices? |
| Volatility of prices | Log change of the industry price a period, in %; coefficient of variation across firms, in %; the periods with `war`, shaded | `prices.csv` | How much does the price move? |

  With `--firms` the price and selection panels draw one thin line a firm, coloured by label,
  from `firms.csv`.

## 11. Tests

`python -m unittest discover -s tests`. A mechanism test builds a small industry by hand with
`tests/helpers.py` and calls one step function, so no step's test depends on another step.
v3 has 267 tests; each file is ported and gains what is listed.

| File | Asserts |
| --- | --- |
| `test_common.py` | As v3: on Shaikh's menu D2 has the lowest unit cost and D1 the highest rate at 100; h = 0 under the unit-cost rule; the profit-rate rule picks D1 at 100 and D2 below 85.1; p^e at λ = 0, 0.5 and 1; ties to the lower κ |
| `test_setup.py` | As v3 at 0.16: six firms, 6, 6 and 7 plants, capacity 760, D_0 = 674.67, the ages, cash of 6,325.00, 6,546.26 and 8,526.06, all cash sums to 0. **New, the scaled menu**: at 0.16 it is Shaikh's table at T = 10 and at T = 7; at 0.10 and 0.05 it is the proposal's table; unit costs and prices of production are those of 0.16 at every rate; at a given price the two rules choose the same technique at 0.05 as at 0.16; r̄ = 0.03 is refused, and r̄ = 0.04 at T = 7; `menu_scaling="fixed"` gives Shaikh's table at any rate; at 0.05 the initial cash is 3.2 times that at 0.16. A misspelt option is refused |
| `test_pricing.py` | The three cutting rules: the shortage branch (next higher rival price; a rise of 0.25 × the excess share; never below the floor); no price rises without a shortage, except to the floor; a firm without a rival keeps its price or takes its floor. **Each rule's test**: cost edge (spare capacity and a strictly lower unit cost than a rival posting P; equal costs, no cut); normal price (above its price of production spare capacity is enough; a cut can end below it; at or below it the cost edge is needed); systematic (spare capacity alone). **Universal undercutting**: every firm posts (1 − c)L whatever its price and cost; the floor stops a cut; after a shortage every firm posts (1 + z)L, even below its floor; a firm alone rises by z up to 3 times its floor. **Floors**: the unit cost of the best plant; the operating cost of the dearest plant that ran, or of the cheapest without output; under the operating-cost floor the cost edge is still read on unit cost. **Decision 14**: a firm without a plant in operation keeps its price under each of the four rules and is no one's rival. An entrant of t − 1 is a rival at t. No price is below the floor under the cutting rules in a full run. Reversing the firms gives the same prices |
| `test_demand.py` | As v3: shares sum to 1; the cheaper firm gains; a plant with ucs above the price is not offered; sales + lost = D_t; one re-allocation. **Overtime**: a firm sells up to 1.2 times what it offers; `u_max=1` gives v3's sales; the shortage signal is demand above normal capacity |
| `test_accounts.py` | As v3: merit order, profit, dividends, book value 0 after T periods, money conservation over 50 periods in the three populations, the accounts identity. **Overtime**: plants run to normal capacity in merit order before any overtime; output stops at u_max times capacity; a plant that was not offered has no output (decision 18); utilisation can exceed 1; `u_max=1` gives the run without overtime, row for row. Money conservation under the four price rules, both investment rules and r̄ = 0.16, 0.10 and 0.05 |
| `test_scrapping.py` | As v3: age T; 2 consecutive periods below cost; 2 consecutive idle periods; scrapping on unit cost; reserve released and withdrawn. **The three levels of the reserve**: `always` adds the reserve to the funds whatever r_new; `never` pays it out whatever r_new, as far as cash allows; `conditional` is v3's rule |
| `test_investment.py` | As v3: the three draws; a design that ties is not kept; retained earnings buy floor(min(F, cash) / κS) plants; the delivery lag; diffusion and `public_lag=None`; the streams. **The accelerator without a target**: ceil((notional − capacity − on order) / S), capped by cash; a firm at its notional demand orders nothing |
| `test_entry.py` | As v3: the entry probability; r_new; inheritance; the public menu only; equity; shares; exits. **The entrant's price**: (1 − c) times the lowest price of a firm with a plant in operation; never below the unit cost of its plants; `entry_price="lowest"` posts that price. **The entrant's label**: `share` draws the parent by market share, `even` gives each incumbent one vote; μ = 0 and 1 |
| `test_neutrality.py` | **Label swap and firm order under every price rule and investment rule**: for each of the 4 × 2 pairs and each of the three populations, 60 periods; with the labels swapped and every firm on its rule the trajectories are identical; with the firms reversed the period table is the same. Also once each: the two other levels of the reserve, the operating-cost floor, `entry_label="even"`, `entry_price="lowest"`, r̄ = 0.05. The label is read only where v3's test allows it; a rule only to look up the hurdle; a serial number only to key a stream, to order the incumbents for the draw of a parent and to name a design |
| `test_model.py` | As v3: reproducibility; a run at the defaults ends with capacity and passes `check` every period; `check` catches money, shares and capacity that do not add up; the terms of the two decompositions sum to the change in the share; every option at every level runs 120 periods; the period table is the same without `frontier`. **New**: running `STEPS` and `close_period` by hand gives the table of `model.run` |
| `test_experiments.py` | As v3: Wilson, beyond drift, ties apart, the harness with 1 and 2 workers, resume, a failing run. **New**: the E0 measures on hand-made period tables (a crossing either way counts once; periods before 20 are not read; a seed passes only with every line; the line on the rate reads `r_new`); `e0_gate` on a hand-made `cells.csv`; the cells of section 9 have the counts of section 9; `rate_gap`, `kept_*`, `overtime_share` |
| `test_viewer.py` | A run of 30 periods: `periods.csv` is the table of `model.run`; `firms.csv` has one row per firm and period, a firm that left included in its last period; the flows of the firms sum to those of their label; `name=value` is converted by the field's type and a wrong name is refused. The figure is drawn where matplotlib is installed, skipped elsewhere |
| `test_budget.py` | At most 1,000 lines without blank lines, comment lines and docstrings, counted with `tokenize` and `ast`; the count is printed. Equation files are named after their step |
| `test_readability.py` | The automatic checks of section 12 |

Two statistical checks are read from `cells.csv` and are not unit tests: the two controls of
E1 at 500 seeds have intervals that contain one half, and in each control the reserve is
released for the same share of plants under the two labels.

## 12. Readability

The rules of "Rebuilding the code" and how each is checked.

| Rule | Checked by |
| --- | --- |
| At most 1,000 lines; no line saved at the cost of a name, a step or a comment | `test_budget`; review |
| A comprehension that filters, a sort key or a `lambda` has a comment line above its statement | `test_readability`, on the syntax tree: every such statement is preceded by a comment line |
| No statement does two things | `test_readability`: no assignment of a tuple of values to a tuple of names, no `;`, no conditional expression inside a call; review for the rest |
| A step function reads like its paragraph, one stage a block, each block opened by a comment | `test_readability`: in `scheduler.py` every block that follows a blank line starts with a comment; review against the schedule |
| Names in the model's words; single letters for the symbols of the proposal and loop indices | `test_readability`: a name of one letter is one of `p`, `c`, `z`, `t`, `u`, `i`, `j`, `k`, `n`; review |
| Each equation file opens with its formula and its source | `test_readability`: the module docstring names `v4-final-model.md` and a section |
| Lines of at most 100 characters | `test_readability` |

**The review of stage 4.** Each step function is read by a member who did not write it,
beside its paragraph of the schedule. The reader notes any line they had to read twice; the
writer adds a name or a comment until none is left.

**The example of the style**: step 1, written out. `p` is the parameters.

```python
class Quote(NamedTuple):
    """What step 1 reads about one firm, taken before any price changes."""
    firm: Firm
    price: float           # the price it posted last period
    cost: float            # the unit cost of its best plant
    normal_price: float    # the price of production of its best plant
    floor: float           # the lowest price it may cut to
    spare: bool            # whether it had spare capacity last period


def set_prices(industry) -> None:
    """Step 1, pricing (v4-final-model.md, "Schedule", step 1).

    Every firm with a plant in operation posts a price from last period's prices and last
    period's shortage. A firm without a plant in operation keeps its price.
    """
    p = industry.params

    # Read every firm before any price changes: the firms move at the same time.
    # Only the firms with a plant in operation set a price.
    quotes = [read_quote(firm, p) for firm in industry.firms if firm.plants]

    # No firm has cut yet this period.
    for firm in industry.firms:
        firm.cut = False

    # Each firm posts its price from what the others posted last period.
    for own in quotes:
        # A firm's rivals are the other firms with a plant in operation.
        rivals = [other for other in quotes if other.firm is not own.firm]
        if p.pricing == "universal":
            price, has_cut = universal_step(own, quotes, industry.excess, p)
        else:
            price, has_cut = cutting_step(own, rivals, industry.excess, p)
        own.firm.price = price
        own.firm.cut = has_cut


def read_quote(firm, p) -> Quote:
    """The quote of a firm with a plant in operation."""
    # The best plant has the lowest unit cost; a tie goes to the lower capital per unit.
    best = min(firm.plants, key=lambda plant: (plant_unit_cost(plant, p), plant.technique.kappa))
    cost = plant_unit_cost(best, p)

    if p.price_floor == "operating_cost":
        # The operating costs of the plants that ran last period, and of every plant it owns.
        ran = [plant.technique.ucs for plant in firm.plants if plant.output > EPS]
        owned = [plant.technique.ucs for plant in firm.plants]
        floor = operating_cost_floor(ran, owned)
    else:
        floor = cost

    return Quote(
        firm=firm,
        price=firm.price,
        cost=cost,
        normal_price=cost + p.rbar * best.technique.kappa,
        floor=floor,
        spare=firm.util < p.u_full,
    )


def cutting_step(own: Quote, rivals: list[Quote], excess: float, p) -> tuple[float, bool]:
    """The price of a firm under one of the three cutting rules, and whether it cut."""
    return cutting_price(
        previous=own.price,
        rival_prices=[rival.price for rival in rivals],
        entitled=is_entitled(own, rivals, p),
        excess=excess,
        floor=own.floor,
        cut=p.price_cut,
        shortage_step=p.shortage_step,
    )


def is_entitled(own: Quote, rivals: list[Quote], p) -> bool:
    """Whether the price rule lets the firm undercut the lowest price of its rivals."""
    if not rivals:
        return False
    lowest = min(rival.price for rival in rivals)
    # The unit costs of the rivals that posted that lowest price.
    costs_at_lowest = [rival.cost for rival in rivals if isclose(rival.price, lowest)]

    if p.pricing == "systematic":
        return entitled_systematic(own.spare)
    if p.pricing == "normal_price":
        return entitled_normal_price(own.spare, own.cost, costs_at_lowest, lowest,
                                     own.normal_price)
    return entitled_cost_edge(own.spare, own.cost, costs_at_lowest)


def universal_step(own: Quote, quotes: list[Quote], excess: float, p) -> tuple[float, bool]:
    """The price of a firm under universal undercutting, and whether it cut."""
    # L, the lowest price posted last period by a firm with a plant in operation.
    lowest = min(quote.price for quote in quotes)
    return universal_price(
        previous=own.price,
        lowest=lowest,
        floor=own.floor,
        excess=excess,
        alone=len(quotes) == 1,
        cut=p.price_cut,
        rise=p.shortage_rise,
        cap=p.monopoly_cap,
    )


def plant_unit_cost(plant, p) -> float:
    """The unit cost of a plant's technique."""
    return unit_cost(plant.technique.ucs, plant.technique.kappa, p.delta)
```

It is 72 lines as counted, against 10 for v3's `set_prices`, which chose between two regimes
with a flag. One argument a line costs lines and saves a reader from counting positions.

## 13. Stages

Each stage ends with its tests passing and one commit on `v4`; build sessions never push.
Times are for one working session with its review. The code is due on 16 November, the first
experiments run from 17 to 19 November, the seminar is on 20 November.

| Stage | Content | Owner | Time | Date |
| --- | --- | --- | --- | --- |
| 1 Scaffold | The tree of section 1; `CLAUDE.md`, `README.md`, `requirements.txt`, the workflow; `parameters.py`; `entities.py`; the five `common_` files; `setup_menu.py`, `setup_initial_plants.py`. Tests: `test_common`, the menu part of `test_setup`, `test_budget`, `test_readability` | Ugo | 2 h | 11 Nov |
| 2 Skeleton | `model.py` (menu from r̄, initial population, cash, streams, the check of the options); `payments.py`; `plant_market.py` with `scrapping_reserve.py`; `entry_new_plant_rate.py`; `scheduler.py` with `STEPS`, `period`, `start_period`, `close_period`, `check`, the end of step 3 (regulating price, r_new) and the six steps as stubs with their final signatures and docstrings; `outputs.py` with the tally by firm; `run.py`; `tests/helpers.py`. Tests: the rest of `test_setup`; reproducibility and money conservation on the stub loop. `parameters.py` is frozen here | Ugo | 3 h | 11 Nov |
| 3a Pricing ∥ | The four `pricing_` files, `set_prices` and its helpers as in section 12. Test: `test_pricing` | Jake | 3.5 h | 12–13 Nov |
| 3b Demand, entry and exit ∥ | `demand_replicator.py`, `goods_market.py`, `allocate_demand` with the sales limit; the five other `entry_` files, `markets/entry_exit.py`, `enter_and_exit`. Tests: `test_demand`, `test_entry` | Pierre-Loup | 4 h | 12–13 Nov |
| 3c Accounts, scrapping, outputs ∥ | The three `accounts_` files with overtime, the three other `scrapping_` files, `produce_and_account`, `scrap_plants`, `outputs.py` in full, `experiments/summary.py` with the E0 measures. Tests: `test_accounts`, `test_scrapping`, the E0 part of `test_experiments` | Vincent | 4 h | 12–13 Nov |
| 3d Technical change and investment ∥ | The five `investment_` files, `invest`. Test: `test_investment` | Ugo | 2.5 h | 12–13 Nov |
| 4 Integration | The four parts together, merged in the order 3c, 3a, 3b, 3d; `test_neutrality` under the 4 × 2 rules, `test_model`; the line count; the review for reading of section 12; a profile against 0.2 s a run | Ugo; all four read | 3.5 h | 14 Nov |
| 5 Harness and gate | `stats.py`, `harness.py`, `cells.py` (E0, E0r, the reruns, the homogeneous start, E1 to E3), `populations.py`, `e0_gate.py`, the rest of `test_experiments`. **Runs, in this order**: E0, read with the gate against the reference; then E0r, the scaled menu at 0.10 and at 0.05; then the reruns and the homogeneous start. Their read goes into this plan, and the level of r̄ for E4 into the register | Ugo (harness, E0r), Vincent (E0), Pierre-Loup (reruns) | 4 h and 5 min of runs | 15 Nov |
| 6 Viewer and figures ∥ | `show_run.py`, `test_viewer`; `figures/style.py`, `fig1` to `fig3`, with `fig2` on a run of the viewer | Jake (viewer), Vincent (figures) | 4 h | 15–16 Nov |
| 7 First experiments | E1, E2, E3; E0's lines on the controls of E1; the two statistical checks; the reads of H1, H2, H5 and H6 | All four, one experiment each | 3 h and 4 min of runs | 17–19 Nov |
| 8 E4, E5, Morris | The E4 cells, with r̄ if E0r kept a level; `e5_channels.py`; `morris.py`; `fig4` to `fig6` | Jake (E4), Ugo (Morris, E5) | 4 h and 7 min of runs | 21–23 Nov |
| 9 E6, reserve, robustness | The E6, reserve and robustness cells; `tab3_robustness.py` | Pierre-Loup (E6), Vincent (robustness) | 3 h and 5 min of runs | 24–25 Nov |

- **What makes 3a to 3d independent.** After stage 2 `pay`, `buy_plant`, `remove_plant`
  with the reserve, r_new, `count` and every field of the entities exist, and
  `parameters.py` is frozen. Each part starts from the stage 2 commit on its own branch and
  touches only its own files and the body of its own step functions in `scheduler.py`.
- **What the seminar of 20 November can show.** Stages 1 to 7: E0, the scaled menu, E1 to
  E3 on the new code, and runs of the viewer.
- **If a stage runs late.** The viewer's figure (stage 6) and stages 8 and 9 move after the
  seminar. Stages 1 to 5 and E1 do not.

**What stage 6 built** (10 November). 405 tests pass, five of them only with matplotlib.

- **No panel has a second axis**, so two panels of the viewer change their measure: the
  hurdle of the profit-rate label is drawn over the general rate, beside the share of its
  orders that are not the cheapest over the last 10 periods; unit cost and capital per unit
  are drawn relative to period 0. In the last panel capacity that leaves is below 0.
- **`firms.csv` holds every flow of the tally by firm**, read at the end of the period:
  a firm that left is still in the tally. Its state is read after steps 3, 5 and 6.
- **`fig2` calls the viewer's `trace`** on a seed, for the mixed population at the defaults
  and for the all-unit-cost control without draws.
- **`fig3` gives the price rules four steps of one hue**, from the rule under which only a
  cost leader cuts to the one under which every firm does: blue and orange stay the two
  labels. It is drawn on E2 and E3, which are stage 7: it has only been checked on 20 seeds.
- **The harness cannot be started from standard input**: its workers are spawned and import
  the calling module.

**What stages 3 to 5 built** (10 November). 383 tests pass; the model code counts 954 lines
of the 1,000, against 867 planned; a run at the defaults takes 0.05 s. What differs from the
sections above, none of it a rule of the model:

- **One builder, no branches.** Parts 3a to 3d were built one after the other on `v4`, in
  the merge order 3c, 3a, 3b, 3d, one commit each.
- **Where the 87 lines went.** `outputs.py` counts 113 lines against 78: the period table is
  written one column a line. `parameters.py` 69 against 60, `entry_exit.py` 59 against 52,
  the equations 236 against 205. `scheduler.py` is at 287, as planned. The margin is 46
  lines: stages 8 and 9 add no model code.
- **`read_quote` calls `unit_cost_floor`**, where section 12 writes `floor = cost`: the
  equation would have been unused.
- **Six columns more in the run row**, `e0_<line>_ok`: the verdict of each line of E0, so
  that `e0_gate` names the weakest line from `cells.csv` alone.
- **A cell carries its populations and its seeds** (`cells.py`): the cells of E0r and of the
  reruns differ in both within one experiment.
- **Speed with 30 firms.** A run with `firms_per_pair=5` takes 0.21 s: the limit of 0.2 s is
  on the defaults.

**What stages 1 and 2 built** (10 November). 130 tests pass; the model code counts 450 lines.
Four points differ from the sections above, none of them a rule of the model:

- **`parameters.py` holds `OPTIONS` and `MONEY_EPS`** (section 7): 69 lines against 60.
- **`entry_new_plant_rate.py` is written in stage 2**, not in 3b: the end of step 3 needs it.
- **`run.py` writes `periods.csv` only.** `run.csv` joins it with `experiments/summary.py`,
  in stage 3c.
- **The underscore is let through by the check on names of one letter**: it is not a letter
  and stands for a value that is not read (`for _ in range(plants)`).

What stages 3a to 3d start from: `start_period`, `close_period`, `check`,
`set_regulating_price` and `set_new_plant_rate` are final; `record_end` is final and
`record_production` writes the identity of a row and the stocks `check` reads, the rest being
3c's; the six steps are stubs. `tests/helpers.py` gives `industry`, `empty_industry`,
`add_firm`, `cash_total` and `tallied`, which reads the tally by label or by firm.

## 14. Open questions

Each has a proposed default, which the build follows until the question is answered.

1. **The base of branch `v4`.** *Settled by Ugo on 10 November: the head of `v3`, emptied
   in the first commit (section 1; decision 10).*
2. **`entry_label = "even"`.** The review said "even odds". A coin between the two labels
   would break the label swap: swapped, the same uniform gives the other rule. *Default: the
   parent is drawn evenly among the incumbents, one vote a firm, then flipped with μ. It
   removes the weight of market share and passes the swap. The proposal and decision 11 say
   so.*
3. **The level of r̄ in E4.** *Default: the rule of section 9, decided by E0r in stage 5.*
4. **matplotlib and SALib.** They are in `../ABM-sources/.venv` only. *Default: the figures,
   the figure of the viewer and Morris run with that interpreter; everything else, tests
   included, runs on `python3` with numpy.*
5. **The threshold of 5 crossings in E0.** Proposed in the proposal, not yet agreed.
   *Default: 5; the default runs give 24 and 23.*
6. **What "the lowest-cost firm sets the price" means with draws.** In the controls of E1
   the price leader is the cost leader in 0.67 and 0.73 of periods (cost-edge, r̄ = 0.16, 50
   seeds). *Default: no change to the model; stage 7 reads, in runs of the viewer, who posts
   the lowest price when it is not the cost leader (an entrant, a firm following down), and
   the report words H1 from that.*
7. **The mechanism of H5.** *Default: the reads of E5 in stage 8; no new cell before them.*
8. **The price leader measure under universal undercutting.** Every firm posts the same
   price, so the line holds by construction. *Default: reported as it is, with that remark.*
9. **Whether normal-price cutting earns its place.** At 0.16 it gives the same industry as
   the default (E0 in 50 and 50 seeds, 0.92 on 500 seeds). *Default: kept, as specified; the
   group looks again after E1.*
10. **Speed.** The limit is 0.2 s a run at the defaults; v3's code takes 0.085 s with these
    settings. *Default: profile in stage 4 only if the limit is passed.*
11. **The seeds of Figure 2.** *Default: seeds 0 to 2 of the default, one for each
    population; chosen for being typical on the E0 measures, not for their outcome.*

## 15. The runs of stage 5

Run on 10 November on commit `d58d9c0` with `python3 -m experiments.harness <name> --jobs 10`:
E0 (400 runs, 2 s), E0r (3,200 runs, 31 s), the reruns (12,500 runs, 2 min 41 s) and the
homogeneous start (3,600 runs, 33 s). No run failed. Each cell without draws gives the
all-unit-cost and the all-profit-rate population, 50 seeds each, measures on periods 20 to
199; a share won is on 500 seeds of the mixed population (200 for the homogeneous start),
with its Wilson interval.

**E0 holds at the default: the gate is open.** `python3 -m experiments.e0_gate outputs/E0`:

| Rule | Seeds of 50 that pass | Capacity over demand, mean (range within a run) | Price over the price of production | Crossings | r_new; industry rate | Demand lost | Weakest line |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Cost-edge (default) | 50 / 49 | 1.08 (0.70–1.39) / 1.09 (0.70–1.43) | 0.99 / 0.99 | 24.5 / 23.5 | 0.159 / 0.158; 0.132 / 0.130 | 0.003 / 0.003 | Capacity |
| Normal-price | 50 / 50 | 1.07 (0.71–1.34) / 1.07 (0.70–1.35) | 0.98 / 0.99 | 25.8 / 26.6 | 0.158 / 0.158; 0.133 / 0.133 | 0.003 / 0.003 | — |
| Systematic | 0 / 0 | 0.91 (0.10–2.13) / 0.90 (0.15–2.00) | 1.11 / 1.05 | 21.4 / 24.2 | 0.245 / 0.213; 0.191 / 0.177 | 0.160 / 0.130 | Demand lost |
| Universal undercutting | 46 / 43 | 0.93 (0.33–1.30) / 0.92 (0.29–1.31) | 0.95 / 0.96 | 21.7 / 23.1 | 0.151 / 0.152; 0.132 / 0.132 | 0.067 / 0.077 | Capacity |

- **The new code gives the reference.** Every count and every mean is that of section 9 and
  of annex D of the review. Decisions 14 and 18, on which version 4 differs from the code
  behind the reference, move nothing that these tables show.

**E0r: the scaled menu at 0.10 and at 0.05.**

| r̄ | Seeds of 50 that pass E0, no draws | Capacity over demand | r_new; industry rate | Demand lost | Share won, with draws | Controls | Final capacity share | Demand lost, mixed | Designs kept, unit-cost / profit-rate label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.16 (E0; 60 seeds for the share) | 50 / 49 | 1.08 / 1.09 | 0.159 / 0.158; 0.132 / 0.130 | 0.003 / 0.003 | 0.93, to rerun in E1 | — | 0.86 | 0.069 | — |
| 0.10 | 50 / 50 | 1.01 / 1.02 | 0.108 / 0.109; 0.093 / 0.093 | 0.007 / 0.008 | 0.80 (0.76–0.83), beyond drift | 0.49 and 0.53 | 0.75 | 0.084 | 0.29 / 0.20 |
| 0.05 | 48 / 50 | 0.96 / 0.96 | 0.065 / 0.062; 0.057 / 0.055 | 0.021 / 0.015 | 0.59 (0.55–0.63), within drift | 0.53 and 0.49 | 0.58 | 0.285 | 0.064 / 0.043 |

- **Without draws the scaled menu gives a working industry at both rates.** E0 holds at
  0.10 and at 0.05. By the rule of section 9, r̄ enters E4 at 0.10 (register, decision 29).
- **With draws 0.10 keeps the headline and 0.05 does not.** At 0.10 the unit-cost label
  wins 0.80. At 0.05 the contest is within drift and the mixed population loses 28 % of
  demand: its capacity averages 0.62 of demand and its price 1.43 times the price of
  production. The two controls lose 10 and 11 %.
- **Technical change slows as the proposal computed.** The unit-cost label keeps 0.29 of
  the designs it draws at 0.10 and 0.06 at 0.05.
- **E0's lines on the controls with draws** are read outside the gate: no seed of 500
  passes at 0.10, and 5 and 2 at 0.05. The line that fails is the price leader: the firm
  posting the lowest price has the lowest unit cost in 0.66 and 0.70 of periods at 0.10.

**The reruns**, at the default rule. E0 is the cell without draws; "—" where the plan has
none.

| Setting changed | Seeds of 50 that pass E0 | Share won | Controls | Final capacity share | Demand lost, mixed | Realised rates, unit-cost / profit-rate label | Highest price over the price of production |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Accelerator | — | 0.63 (0.58–0.67), beyond drift | 0.52 and 0.52 | 0.57 | 0.028 | 0.128 / 0.135 | 1.5 |
| Shortage step 0.5 | 50 / 50 | 0.94 (0.91–0.95) | 0.50 and 0.47 | 0.91 | 0.072 | 0.183 / 0.172 | 3.7 |
| Shortage step 0.5, accelerator | — | 0.78 (0.74–0.81) | 0.50 and 0.55 | 0.69 | 0.023 | 0.163 / 0.165 | 2.0 |
| Entrant at the lowest price | 0 / 0 | 0.93 (0.90–0.95) | 0.48 and 0.48 | 0.65 | 0.011 | 0.136 / 0.139 | 1.3 |
| No overtime | 26 / 27 | 0.77 (0.73–0.81) | 0.48 and 0.47 | 0.74 | 0.144 | 0.160 / 0.177 | 2.2 |
| Reserve always released | 0 / 0 | 0.80 (0.76–0.83) | 0.48 and 0.50 | 0.53 | 0.000 | 0.009 / 0.009 | 0.8 |
| Reserve never released | 50 / 33 | 0.39 (0.35–0.44), within drift | 0.52 and 0.45 | 0.41 | 0.118 | 0.241 / 0.228 | 2.4 |
| Growth of 1 % a period | — | 0.94 (0.92–0.96) | 0.50 and 0.47 | 0.77 | 0.046 | 0.146 / 0.156 | 1.6 |

- **What the proposal marked "100 seeds" stands on 500**, with one change: under the
  accelerator the unit-cost label wins 0.63, beyond drift by a narrow margin, where 100
  seeds gave 0.56 within drift. The lower end of its interval is 0.58 and the upper end of
  the controls' 0.56.
- **The sign of H6 turns with the shortage step**, as on v3: 0.148 and 0.151 at 0.25 (60
  seeds, to rerun in E1), 0.183 and 0.172 at 0.5.
- **Each piece is needed for E0**: the entrant at the lowest price fails it in every seed
  (the price crosses the price of production 0.1 and 0.3 times a run), no overtime gives 26
  and 27 seeds, the reserve always released none.

**The homogeneous start**: the six cells of E2 from six firms on D1, 200 seeds.

| Cell | Share won | Controls | Final capacity share | Orders of the profit-rate label that are not the cheapest |
| --- | --- | --- | --- | --- |
| β = 0 | 0.50 (0.43–0.57), within drift | 0.51 and 0.45 | 0.49 | 0.03 |
| β = 0.5 | 0.86 (0.80–0.90) | 0.46 and 0.54 | 0.79 | 0.59 |
| β = 1.5 | 0.92 (0.87–0.95) | 0.49 and 0.45 | 0.86 | 0.79 |
| β = 3 | 0.86 (0.80–0.90) | 0.50 and 0.51 | 0.79 | 0.89 |
| Neutral set | 0.72 (0.65–0.77), beyond drift | 0.53 and 0.46 | 0.66 | 0.38 |
| No draws | 0.99 (0.96–1.00) | 0.50 and 0.48 | 0.95 | 1.00 |

- **The homogeneous start does not remove the initial menu.** Every firm starts on D1, but
  the public menu still holds C, D1 and D2. Without draws the unit-cost label orders D2 and
  the profit-rate label D1 from the first period: every order of the profit-rate label is
  dearer, and the unit-cost label wins 0.99. The cell does not tell the bias from the menu.
- **With draws it gives the pattern of E2**: drift at β = 0, where the draws replace the
  menu with designs on which the rules agree (0.03 of dearer orders), and 0.86 to 0.92 with
  a bias. To separate the two, the start would also need a public menu of D1 alone: a
  question for the group, not built.

## 16. The runs of stage 7

Run on 10 November on commit `06e2fbb` (branch `v4-experiments`): E1 (6,000 runs, 61 s), E2
(14,400 runs) and E3 (9,000 runs). No run failed and no seed is undecided. Shares are of the
mixed population, with their 95 % Wilson interval; "beyond drift" is an interval disjoint
from those of the two controls.

**E1: which rule wins, by price rule** (500 seeds).

| Price rule | Share won | Controls | Final capacity share | Change in sales share: price; entry and exit | Hurdle of the profit-rate label; its dearer orders | Realised rates, unit-cost / profit-rate label | Demand lost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Cost-edge (default) | 0.92 (0.90–0.94) | 0.46 and 0.46 | 0.86 | +0.21; +0.16 | 0.170; 0.80 | 0.148 / 0.151 | 0.069 |
| Normal-price | 0.92 (0.89–0.94) | 0.47 and 0.48 | 0.86 | +0.21; +0.16 | 0.171; 0.80 | 0.149 / 0.152 | 0.073 |
| Systematic | 0.76 (0.72–0.80) | 0.47 and 0.51 | 0.75 | +0.05; +0.20 | 0.171; 0.79 | 0.164 / 0.156 | 0.111 |
| Universal undercutting | 0.23 (0.19–0.27) | 0.50 and 0.51 | 0.45 | 0.00; −0.03 | 0.142; 0.75 | 0.133 / 0.135 | 0.032 |

- **H1 is met, H1′ fails under the three cutting rules.** The unit-cost label wins beyond
  drift where a cost leader sets the price; under universal undercutting, where the price
  moves no market share, the profit-rate label wins. Every number is that of the reference.
- **H4 is met**: 0.92, 0.76 and 0.23 from cost-edge to systematic cutting to universal
  undercutting.
- **H6 is not met at the default, and the gap is small but not zero.** The unit-cost label
  realises 0.3 point less than the profit-rate label (−0.003, interval −0.004 to −0.002).
  Under systematic cutting the sign is the other one (+0.008).
- **E0's lines on the controls of E1** (`e0_gate outputs/E1`, outside the gate). Under the
  three cutting rules no seed of 500 passes: the firm posting the lowest price has the
  lowest unit cost in 0.68 and 0.73 of periods at the default. Demand lost passes in 0.80
  and 0.95 of seeds, capacity in 0.86 and 0.99. Under universal undercutting 448 and 500
  seeds pass: every firm posts the same price, so the leader line holds by construction.

**The two statistical checks**, on the controls of E1.

- **Every control's interval contains one half**, under the four price rules. The tightest
  is the all-profit-rate control at the default: 0.413 to 0.502.
- **The reserve is released for the same share of plants under the two labels** in each
  control: 0.274 and 0.276, then 0.299 and 0.300 at the default, with intervals that
  overlap, and the same under the three other rules.

**E2: the bias** (200 seeds). A share in brackets is within drift.

| Cell | Cost-edge | Normal-price | Systematic | Universal undercutting |
| --- | --- | --- | --- | --- |
| β = 0 | (0.52) | (0.55) | 0.39 | (0.50) |
| β = 0.5 | 0.89 | 0.91 | 0.77 | (0.36) |
| β = 1.5 | 0.93 | 0.94 | 0.78 | 0.21 |
| β = 3 | 0.82 | 0.88 | (0.59) | 0.17 |
| Neutral set | (0.66) | (0.66) | (0.59) | (0.52) |
| No draws | 0.98 | 0.97 | 0.72 | (0.39) |

- **H2 is met in part.** With draws the advantage needs the bias and does not grow with it:
  at the default it is at drift at β = 0, 0.89 at 0.5, 0.93 at 1.5 and 0.82 at 3. Without
  any draw the unit-cost label wins 0.98 on the initial menu.
- **Under universal undercutting the bias works for the profit-rate label**: 0.50, 0.36,
  0.21 and 0.17.

**E3: the evaluation price** (200 seeds).

| λ | Cost-edge: share won; hurdle; dearer orders | Systematic | Universal undercutting |
| --- | --- | --- | --- |
| 0 | 0.93; 0.170; 0.80 | 0.78; 0.171; 0.78 | 0.21; 0.142; 0.74 |
| 0.25 | 0.86; 0.174; 0.79 | (0.63); 0.174; 0.79 | 0.17; 0.152; 0.76 |
| 0.5 | 0.83; 0.178; 0.79 | (0.40); 0.176; 0.78 | 0.18; 0.162; 0.77 |
| 0.75 | (0.62); 0.181; 0.77 | 0.17; 0.176; 0.70 | 0.15; 0.172; 0.78 |
| 1 | (0.61); 0.183; 0.73 | 0.12; 0.174; 0.58 | 0.13; 0.183; 0.78 |

- **H5: the outcome is met, the mechanism is not.** At the default the advantage falls from
  0.93 to 0.61, within drift from λ = 0.75, while the hurdle rises from 0.170 to 0.183.
- **Under systematic cutting the result turns over.** The unit-cost label wins 0.78 at
  λ = 0 and 0.12 at λ = 1: judged at the price of production the profit-rate label wins
  beyond drift. This cell was not run before. The profit-rate label then realises 0.179
  against 0.158.
- **Under universal undercutting λ moves little**: 0.21 to 0.13, the profit-rate label
  winning throughout, while its hurdle rises from 0.142 to 0.183.

Figure 3 is drawn on these runs (`outputs/figures/fig3_bias_lambda`).

**Who posts the lowest price when it is not the cost leader** (open question 6). Read on 30
runs of the viewer in each control of E1 at the defaults, periods 20 to 199, among the
firms with a plant in operation.

| | All-unit-cost | All-profit-rate |
| --- | --- | --- |
| Periods in which a firm posting the lowest price has the lowest unit cost | 0.69 | 0.73 |
| Otherwise, the price leader entered the period before | 0.59 | 0.57 |
| Otherwise, it is 2 to 5 periods old | 0.06 | 0.07 |
| Otherwise, it is older | 0.35 | 0.36 |
| Its unit cost above the lowest unit cost | 0.9 % | 1.8 % |
| The cost leader's price above the lowest price | 27 % | 16 % |

- **It is the entrant, most of the time.** In three cases of five the firm posting the
  lowest price entered the period before: it posts one cut below the lowest price, as the
  rule says, and its plants are almost as cheap as the best.
- **The cost leader is then a firm whose price is still high**, 16 to 27 % above the
  lowest: a firm that holds the newest design does not post the lowest price at once.
- **For the wording of H1**: with draws, "the lowest-cost firm sets the price" holds in
  two periods of three; in the others the price is set by a firm whose cost is within 2 %
  of the lowest. The report can say that the price is set at the lowest costs, not by the
  one firm that has the lowest.

## 17. The runs of stage 8

Run on 10 November: E4 (28,800 runs, commit `06e2fbb`) and the Morris screening (39,000
runs, commit `2da30de`), side by side on 10 workers in 16 minutes. No run failed; one seed
of the screening is undecided. E5 has no run: `python3 -m experiments.e5_channels` reads E4
and E3 into `outputs/E5/`. Figures 4, 5 and 6 are drawn on these runs.

**E4: where each rule wins** (200 seeds; a share in brackets is within drift).

| Price rule, investment rule | r̄ = 0.16, g = 0 | r̄ = 0.16, g = 1 % | r̄ = 0.10, g = 0 | r̄ = 0.10, g = 1 % |
| --- | --- | --- | --- | --- |
| *Marx-biased set* | | | | |
| Cost-edge, retained earnings | 0.93 | 0.96 | 0.78 | 0.93 |
| Cost-edge, accelerator | (0.59) | 0.78 | (0.54) | (0.52) |
| Systematic, retained earnings | 0.78 | (0.55) | (0.58) | (0.56) |
| Systematic, accelerator | 0.11 | 0.12 | 0.29 | 0.33 |
| Universal, retained earnings | 0.21 | 0.23 | 0.34 | (0.37) |
| Universal, accelerator | 0.12 | 0.30 | (0.32) | (0.43) |
| *Categories rule* | | | | |
| Cost-edge, retained earnings | 0.79 | 0.77 | (0.68) | 0.77 |
| Cost-edge, accelerator | (0.63) | 0.77 | (0.48) | (0.55) |
| Systematic, retained earnings | (0.57) | 0.30 | (0.43) | (0.43) |
| Systematic, accelerator | 0.16 | 0.27 | 0.34 | (0.42) |
| Universal, retained earnings | (0.30) | 0.34 | (0.41) | (0.37) |
| Universal, accelerator | 0.18 | 0.35 | (0.35) | (0.48) |

- **The unit-cost rule wins where a cost leader sets the price and firms grow out of
  profits**: cost-edge cutting with retained earnings, 0.78 to 0.96 in seven cells of eight.
- **H3 is met.** The profit-rate label wins beyond drift under universal undercutting at
  0.16 and under systematic cutting with the accelerator (0.11 and 0.12). There the change
  in the unit-cost label's capacity share through accumulation is −0.30 and −0.17, against
  +0.32 at the default.
- **The accelerator takes the headline to drift at the default** on 200 seeds (0.59); on
  500 seeds it is 0.63, beyond drift by a narrow margin (section 15). With growth it is
  0.78.
- **At 0.10 most cells are within drift**: 15 of 24, against 5 of 24 at 0.16. The unit-cost
  label still wins under cost-edge cutting with retained earnings (0.78 and 0.93).
- **The categories rule gives the same map with smaller shares.**

**E5: the channels.**

- **The decompositions** (figure 5, the twelve Marx cells at 0.16). Under cost-edge cutting
  the unit-cost label gains through the price (+0.17 to +0.24) in the four cells; under
  universal undercutting the price moves nothing (0.00) and the label loses through
  accumulation. Rationing moves no share anywhere.
- **The regression of the gap in rates.** In the 9,600 mixed runs of E4, with an effect for
  each cell, the gap in realised rates (unit-cost less profit-rate label) falls by 0.024
  (standard error 0.003) per unit of the share of the profit-rate label's orders that are
  not the cheapest: −0.029 at 0.16, −0.021 at 0.10, −0.069 under the Marx-biased set and
  0.001 (0.004) under the categories rule. Where the profit-rate label orders more of the
  dearer techniques it realises more, not less: H6 is not met here either.
- **E3 at λ = 0 and 1** (`outputs/E5/lambda.csv`; the spread is read on 20 runs of the
  viewer in each cell).

| Cell | Share won | Dearer orders | Realised rates | Mean hurdle | Spread of hurdles across firms |
| --- | --- | --- | --- | --- | --- |
| Cost-edge, λ = 0 | 0.93 | 0.80 | 0.148 / 0.151 | 0.170 | 0.016 |
| Cost-edge, λ = 1 | 0.61 | 0.73 | 0.153 / 0.159 | 0.183 | 0.001 |
| Systematic, λ = 0 | 0.78 | 0.78 | 0.162 / 0.156 | 0.171 | 0.026 |
| Systematic, λ = 1 | 0.12 | 0.58 | 0.158 / 0.179 | 0.174 | 0.001 |
| Universal, λ = 0 | 0.21 | 0.74 | 0.133 / 0.135 | 0.142 | 0.001 |
| Universal, λ = 1 | 0.13 | 0.78 | 0.132 / 0.134 | 0.183 | 0.001 |

- **A candidate for the mechanism of H5: the spread of hurdles, not their mean.** At λ = 0
  under a cutting rule the firms of the profit-rate label judge at their own prices, which
  differ, and their hurdles differ with them (0.016 and 0.026); at λ = 1 they judge at one
  price and have one hurdle. Under universal undercutting every firm posts the same price,
  the hurdles do not differ at either λ, and λ moves the outcome little. This is a reading
  of three pairs of cells, not a test: no cell varies the spread alone.

**The Morris screening** (figure 6; `outputs/morris/morris.csv`). mu* is the mean absolute
effect of moving a parameter across its range, with its 95 % interval over the 10
trajectories; the mean of the outcome over the 130 points is in the header.

| Parameter | Share won less the controls' mean (0.17) | Final capacity share (0.61) | Demand lost (0.11) | E0's lines that hold (0.67) | Gap in realised rates (−0.007) |
| --- | --- | --- | --- | --- | --- |
| Selection intensity χ | 0.42 (0.23–0.60) | 0.26 | 0.19 | 0.13 | 0.010 |
| Payout d | 0.37 (0.15–0.59) | 0.21 | 0.06 | 0.11 | 0.013 |
| Price cut c | 0.35 (0.22–0.48) | 0.21 | 0.23 | 0.18 | 0.013 |
| Entry speed θ | 0.21 (0.11–0.31) | 0.14 | 0.08 | 0.09 | 0.009 |
| Plant life T | 0.21 (0.11–0.31) | 0.13 | 0.04 | 0.19 | 0.012 |
| Bias β | 0.19 (0.08–0.30) | 0.07 | 0.01 | 0.03 | 0.018 |
| Plant size S | 0.17 (0.09–0.25) | 0.06 | 0.03 | 0.05 | 0.007 |
| Shortage step | 0.14 (0.07–0.22) | 0.10 | 0.07 | 0.11 | 0.017 |
| Overtime limit | 0.12 (0.08–0.16) | 0.11 | 0.15 | 0.16 | 0.020 |
| Design step A | 0.11 (0.03–0.19) | 0.10 | 0.11 | 0.13 | 0.014 |
| Draw probability π | 0.08 (0.04–0.12) | 0.05 | 0.02 | 0.03 | 0.002 |
| Mutation μ | 0.04 (0.02–0.05) | 0.04 | 0.00 | 0.01 | 0.016 |

- **The headline depends most on how the market selects and on what firms retain**: the
  selection intensity, the payout ratio and the price cut. The advantage rises with χ and
  with the cut, and falls as firms pay out more.
- **The parameters of technical change matter less than those of competition**: the bias,
  the design step and the draw probability rank sixth, tenth and eleventh.
- **Over the grid the industry is often not that of E0**: on average 0.67 of E0's lines
  hold and 11 % of demand is lost, up to 73 % at one point. The screening moves parameters
  far from the defaults, and its effects are means over that grid.
- **The method.** The screening is written with numpy: SALib is not installed beside this
  tree, and no package was installed during the build. With 10 trajectories the intervals
  are wide: the ranking of the first three and of the last two is firm, the middle is not.

## 18. The runs of stage 9

Run on 10 November, after E4: E6 (4,000 runs), the reserve under universal undercutting
(3,200), the robustness checks (25,200) and the fixed menu (1,600), on commits `2da30de`
and `9ae5c26`, whose model code is that of `06e2fbb`. No run failed and none is undecided.
`python3 -m figures.tab3_robustness` writes the table of every check beside the cell it
varies, in `outputs/figures/tab3_robustness.md`.

**E6: can one firm of a rule invade the other?** Ten firms on D1, one of the mutant label;
its capacity share starts at 0.10. The control puts the mutant on the residents' rule.

| Price rule | Mutant | Final capacity share: mixed; control | Seeds in which it ends above 0.10: mixed; control |
| --- | --- | --- | --- |
| Cost-edge | Unit-cost firm among profit-rate firms | 0.33; 0.10 | 0.86; 0.39 |
| Cost-edge | Profit-rate firm among unit-cost firms | 0.003; 0.10 | 0.01; 0.38 |
| Universal undercutting | Unit-cost firm among profit-rate firms | 0.10; 0.10 | 0.37; 0.41 |
| Universal undercutting | Profit-rate firm among unit-cost firms | 0.17; 0.10 | 0.87; 0.38 |

- **Under cost-edge cutting the unit-cost rule invades and resists invasion.** One unit-cost
  firm triples its share among profit-rate firms; one profit-rate firm among unit-cost
  firms is driven out.
- **Under universal undercutting it is the profit-rate rule that invades**, and a unit-cost
  mutant does no better than a firm on the residents' rule.

**The reserve under universal undercutting** (the default is in section 15).

| Reserve | Seeds of 50 that pass E0 | Share won | Controls | Realised rates |
| --- | --- | --- | --- | --- |
| Released if r_new ≥ r̄ (E0 and E1) | 46 / 43 | 0.23 (0.19–0.27) | 0.50 and 0.51 | 0.133 / 0.135 |
| Always released | 0 / 0 | 0.56 (0.51–0.61), within drift | 0.48 and 0.49 | 0.010 / 0.010 |
| Never released | 0 / 0 | 0.15 (0.12–0.19) | 0.51 and 0.47 | 0.189 / 0.193 |

- **The reserve sets the profit rate under this rule too**: 1 % when always released, 19 %
  when never released. E0 fails in every seed at both levels: the price stays a quarter
  below the price of production in the first case, capacity at 0.8 of demand in the second.
- **The profit-rate label's advantage needs the condition or no reserve**: always released,
  the contest is at drift.

**The robustness checks.** "Base" is the cell the check varies; shares on 500 seeds for the
checks on E1, 200 for those on E4.

| Check | Cell | Share won | Base | Verdict |
| --- | --- | --- | --- | --- |
| No overtime | Cost-edge (reruns) | 0.77 | 0.92 | Smaller; E0 in 26 and 27 seeds |
| | Normal-price | 0.74 | 0.92 | Smaller; E0 in 50 and 50 |
| | Systematic | (0.47) | 0.76 | To drift; E0 in no seed |
| | Universal undercutting | 0.07 | 0.23 | The profit-rate label wins more; E0 in no seed |
| Entrant at the lowest price | Default | 0.93 | 0.92 | Same; E0 in no seed |
| Shortage step of 0.5 | Default | 0.94 | 0.92 | Same; E0 in 50 and 50 |
| | Accelerator | 0.78 | 0.63 | Larger |
| Entrant's parent drawn evenly | Default | 0.90 | 0.92 | Same |
| | Universal undercutting | 0.21 | 0.23 | Same |
| Operating-cost floor | Default | 0.93 | 0.92 | Same |
| | Universal undercutting | 0.23 | 0.23 | Same |
| Fixed menu at r̄ = 0.10 | Default | 0.83 | 0.80 on the scaled menu | Same; E0 in 50 and 49 |
| Private designs (L = none) | Default | (0.62) | 0.92 | To drift |
| Scrapping on unit cost | Default and the 12 Marx cells of E4 | within 0.03 of the base | | No verdict changes |
| 12 firms | Default | 0.97 | 0.92 | Larger |
| | Cost-edge, accelerator, g = 1 % | 0.89 | 0.78 | Larger |
| | Universal, retained and accelerator, g = 1 % | 0.25; 0.32 | 0.23; 0.30 | Same |
| 30 firms | Default | 0.98 | 0.92 | Larger |
| | Cost-edge, accelerator, g = 1 % | 0.95 | 0.78 | Larger |
| | Universal, retained and accelerator, g = 1 % | 0.22; (0.41) | 0.23; 0.30 | One cell to drift |

- **Three checks move a verdict.** Without diffusion of designs the headline falls to
  drift (0.62). Why is not established: no cell isolates it, and it is one cell on 200
  seeds. Without
  overtime the industry is no longer that of E0 under three rules of four. With 30 firms
  the cell under universal undercutting with the accelerator goes to drift.
- **Five checks move nothing**: the entrant at the lowest price (for the headline; it does
  fail E0), the shortage step, the entrant's parent drawn evenly, the operating-cost floor
  and scrapping on unit cost.
- **The entrant's label is not what carries the headline.** Drawn evenly instead of by
  market share, the unit-cost label still wins 0.90.
- **More firms strengthen the headline**: 0.97 with 12 firms and 0.98 with 30, and under
  the accelerator with growth 0.89 and 0.95 against 0.78.
- **Without overtime normal-price cutting still meets E0**, in 50 and 50 seeds, where the
  default meets it in 26 and 27: the one case in which the two rules part.

**Where the hypotheses stand on the new code.**

| # | Hypothesis | Verdict | Evidence |
| --- | --- | --- | --- |
| H1 | The unit-cost rule wins where the lowest-cost firm sets the price | Met | E1: 0.92, 0.92, 0.76 under the cutting rules, 0.23 under universal undercutting; E6: it invades and resists under cost-edge cutting |
| H1′ | The profit-rate rule cannot lose systematically | Fails under the cutting rules; holds under universal undercutting | E1, E6 |
| H2 | The advantage grows with the Marx bias | In part | E2: it needs the bias (drift at β = 0) and does not grow with it (0.89, 0.93, 0.82) |
| H3 | Where selection runs through accumulation it can favour the profit-rate rule | Met | E4: universal undercutting, and systematic cutting with the accelerator (0.11) |
| H4 | The more firms cut, the smaller the advantage | Met | E1: 0.92, 0.76, 0.23 |
| H5 | Judged at the price of production the advantage shrinks, because the hurdle falls | Outcome met; mechanism not | E3: 0.93 to 0.61 while the hurdle rises; E5: the spread of hurdles across firms falls from 0.016 to 0.001, a candidate not yet tested |
| H6 | The profit-rate adopter does not realise the rate it maximises | Not met | E1: 0.148 against 0.151; E5: the gap falls as its dearer orders rise |

**For the group**, beside the three points of section 15: whether private designs, which
take the headline to drift, belong in the report as a condition of the result; and whether
a cell should vary the spread of hurdles alone, to test the candidate mechanism of H5.
