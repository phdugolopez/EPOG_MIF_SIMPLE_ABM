# Real competition ABM: Shaikh against Okishio

Group project, M2 EPOG, MIP1 (Pierre Funalot and Federico Bassi). Built on the course
template `pierrefunalot/EPOG_MIF_SIMPLE_ABM` (remote `upstream`).

## Research question

In an industry where cheaper techniques often need more capital per unit of output, does
market selection favour firms that equip new plants at the lowest unit cost (Shaikh,
hurdle h = 0) or at the highest profit rate at the current price (Okishio, h = best profit
rate on offer)? How does the answer depend on how often price wars occur and on how
investment is financed? One industry inside a given economy: money wage = numéraire,
exogenous demand, general rate of profit rbar set outside.

## The neutrality rule (do not break it)

Shaikh and Okishio firms differ **only** in the hurdle h used to choose techniques, in
investment, replacement and entry. Pricing, demand, production and accounts, retirement and
exit treat both types identically.

- `firm.type` is read only by `equations/hurdle.py`, through `parameters.HURDLE_RULES`.
  Never branch on `firm.type` anywhere else (the collector may group outputs by type).
- Never break ties by firm order or id: the initial firms come in identical pairs. Share
  ties pro rata (see `equations/merit_order.py`, `markets/goods_market.py`).
- The label-swap tests (`tests/test_model.py` and one per mechanism) run the model with the
  labels swapped everywhere except the hurdle mapping and require identical trajectories.
  They must keep passing.

## Design reference

**docs/design/ is the design reference; propose changes there rather than diverging
silently.** `docs/design/mechanism-briefs.md` is the specification (notation, order of
events, test industry, the six mechanisms with their starting rule and tests).
`docs/design/choices.md` lists every choice the briefs leave open: when you change one,
update its row.

## Coding convention (from the course template)

- One equation or behavioural rule per file in `equations/` (pure functions, no model
  state); one interaction protocol per module in `markets/`.
- All parameters in `parameters.py` (upper case), passed explicitly to equations under the
  brief's Python names (`DELTA` -> `delta`, `RBAR` -> `rbar`, ...). Use the notation table's
  names for state: `price`, `share`, `sales`, `capacity`, `util`, `ucs`, `kappa`, `hurdle`,
  `cash`, `debt`, `profit`, `net_worth`, `r_new`.
- `model/entities.py` (Technique, Plant, Firm, RestOfEconomy), `model/model.py` (Industry:
  initialisation), `model/scheduler.py` (order of events, one function per step),
  `model/collector.py` (outputs and the stock-flow check).
- Each step reads only parameters and the state earlier steps produced.
- Every money flow goes through `markets/payments.pay`; the scheduler asserts stock-flow
  consistency every period (`check_stock_flow`). Never move `cash` directly.
- unittest tests in `tests/`, one file per mechanism; `tests/helpers.py` builds modified
  configurations (`make_config(**overrides)`, `swapped_config()`).
- Lines `# {name}` ... `# {endname}` in `model/scheduler.py` mark what the LaTeX sections
  include; keep them around the step functions.

## Who owns what

| Mechanism (step) | Owner | Files |
|---|---|---|
| Pricing (1) | Jake | `equations/anchor_price.py`, `price_floor.py`, `price_war.py`, `posted_price.py`; `set_prices` |
| Demand (2) | Pierre-Loup | `equations/competitiveness.py`, `market_shares.py`, `offered_capacity.py`; `markets/goods_market.py`; `allocate_demand` |
| Production and accounts (3) | unassigned | `equations/merit_order.py`, `operating_cost.py`, `depreciation.py`, `interest_payment.py`, `firm_profit.py`, `profit_rate.py`, `plant_profit.py`, `dividends.py`, `debt_repayment.py`; `markets/payments.py`, `credit_market.py`; `produce_and_account`; `model/collector.py` |
| Scrapping (4) | Vincent | `equations/retirement.py`, `replacement.py`, `lifetime_profit_rate.py`; `scrap_plants` |
| Investment (5) | Ugo | `equations/hurdle.py`, `technique_choice.py`, `desired_capacity.py`, `investment.py`, `borrowing_capacity.py`; `markets/plant_market.py`; `invest` |
| Entry and exit (6) | unassigned | `equations/new_plant_rate.py`, `entry_probability.py`, `inherited_rule.py`, `entrant_price.py`, `exit_conditions.py`; `markets/entry_exit.py`; `enter_and_exit` |

Shared: `parameters.py`, `model/entities.py`, `model/model.py`, `run_period`. Change shared
files only after agreeing with the group.

## How to run

```bash
python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests   # all tests
.venv/bin/python run.py                          # baseline -> outputs/*.csv
.venv/bin/python plot_outputs.py                 # figures -> outputs/*.png
cd docs && latexmk -pdf main.tex                 # report (needs outputs/ first)
```

CI (`.github/workflows/build.yml`) runs the same steps on Python 3.11 and uploads
`docs/main.pdf` as an artifact.

## Adding an alternative rule behind a switch

1. Write the alternative as a new function, in the mechanism's equation file or a new file
   in `equations/` (one rule per file).
2. Add a switch to `parameters.py`, with the version 1 rule as default (examples:
   `PRICING_ANCHOR`, `DEMAND_FORM`, `HURDLE_FLOOR_AT_ZERO`, `REPLACEMENT`,
   `INVESTMENT_SALES_LAG`).
3. Branch on the switch in the scheduler step that calls the rule.
4. Add tests for the new rule, including the label swap, and add the switch to
   `test_switches_run` in `tests/test_model.py`.
5. Record it in `docs/design/choices.md` and describe it in the mechanism's section of
   `docs/sections/`.
6. Check the neutrality rule: does the new rule hand one type an advantage by construction?
