# ABM version 4: final model, analysis plan and build constraints

Proposal of 10 November 2026, for the group to discuss before the code is rebuilt a second time.
It replaces `final-model-proposal.md`, the addendum of `v3-planning-prompt.md` and the rows of
`v3-choices.md` as the description of the model: the rules that do not change are restated here,
so the rebuild reads one document. The sections of the v3 proposal on the literature, the report,
the presentation and the division of work stand; the changes they need are in the last section
but one.

Every number comes from version 3's code, with the rules that differ put in place from
`experiments/price_rules.py` (`v3-plan.md`, section 9). The runs are provisional, and nothing
here is a decision until the group records it.

## At a glance

- **Three changes to the model.** Overtime comes back, without a premium. The accelerator loses
  its target utilisation. The default price rule becomes *normal-price cutting*: v3's two
  regimes joined by the price of production. The price rule is the first treatment, with four
  levels.
- **How the default was chosen.** By Ugo's criterion of 10 November: the rule that best fits
  both E0 (without technical change the industry behaves as under real competition) and the
  headline (the unit-cost rule wins beyond drift). Fifteen rules were scored on both.
- **No rule fits both.** Whatever lets firms without a cost advantage cut the price, which E0
  needs, also takes away the lead of the cost leader, which the headline needs. Leader-follow
  meets E0 and leaves the contest at drift (0.50). Cost-edge cutting gives the headline (0.92)
  and fails E0 in every seed.
- **The default is the best joint fit.** Under normal-price cutting the unit-cost rule wins
  0.67 of seeds (0.63–0.71, beyond drift), and E0 holds in 43 seeds of 50 in the all-unit-cost
  population and in 12 of 50 in the all-profit-rate population. E0 is therefore met as far as
  possible, not met.
- **What stays true under it.** The advantage grows with the Marx bias (0.50, 0.62, 0.67,
  0.84) and falls to drift when the profit-rate rule judges at the price of production.
- **Two constraints on the rebuild.** Readable code comes before the line count: at most 1,000
  lines of model code, comments excluded. And a run viewer, outside that count, runs one set of
  parameters on one seed and plots what explains the run.

## What changed from the v3 final model

| # | In v3 | In v4 | Why |
| --- | --- | --- | --- |
| 1 | No overtime: output stops at normal capacity | Output up to u_max = 1.2 times normal capacity, at the same operating cost (no premium) | Without it no rule comes near E0: at the default, capacity is 1.5 times demand and the price 1.3 times the price of production |
| 2 | Accelerator: desired capacity = the demand addressed to the firm over a target utilisation u* = 0.9 | Desired capacity = the demand addressed to the firm; no target | The target was the buffer of a model without overtime. Without it E0 holds in 50 and 48 seeds of 50 under the accelerator, against 47 and 21 with it |
| 3 | Default price rule: cost-edge cutting | Default: normal-price cutting. Above its price of production a firm cuts with spare capacity alone; at or below it, it also needs a cost edge | The best joint fit of E0 and the headline among fifteen rules |
| 4 | Two price regimes; systematic cutting stood for leader-follow | Four price rules: normal-price cutting, cost-edge cutting, leader-follow, systematic cutting | The headline depends on the rule, so the rule is a treatment. v3's systematic cutting is not leader-follow |
| 5 | Leader-follow's own shortage rule and monopoly cap dropped for the common shortage step | Restored, for the leader-follow option only: 3 % above the lowest price after a shortage; a firm alone stops at 3 times its floor | They are part of the rule that meets E0 |
| 6 | One floor: unit cost | The same by default; the operating-cost floor as a robustness option | Under leader-follow it moves no share won by more than 0.06 and no verdict |
| 7 | E0 read at the last period (capacity within a band in 9 seeds of 10) | E0 read on averages over the run, from period 20, with two new lines (the price crosses the price of production; at most 10 % of demand is lost) and the cycle reported beside | A cycle cannot meet a band at one date; gravitation is around a centre |
| 8 | H1: the unit-cost rule wins under price competition | H1 depends on the price rule; H4 becomes the central test | 0.92 under cost-edge cutting, 0.67 at the default, drift under leader-follow |
| 9 | E1 to E4 at the default rule; pricing varied in E3 and E4 only | The price rule crossed with E0 to E4 | The size of every effect depends on it |
| 10 | Robustness: u* = 0.8 and 0.95 | Dropped. Added: no overtime (u_max = 1), the operating-cost floor | u* no longer exists |
| 11 | Model code at most 770 lines, blank lines excluded | At most 1,000 lines, comments excluded; readability first | Section "Rebuilding the code" |
| 12 | Figure 2 from period tables kept by the harness | A run viewer for any parameters and seed | Every diagnosis of v3 needed a trace of one run |
| 13 | The depreciation reserve is released when r_new ≥ r̄; no other rule in the model | The same by default; an option with two other levels (always released, never released) for a sensitivity check | The reserve sets the profit rate and makes the cycle: 1 % and no cycle when always released, 21 % when never released |

Not changed: the one rule that differs between the types, the menu, the replicator, scrapping,
the default rule of the depreciation reserve, technical change, entry and exit, the winner, the
populations and controls, and the rules of neutrality.

## What the v3 experiments showed

All the runs of this section have overtime.

### E0 and the headline, rule by rule

E0: single-rule populations without technical change, 50 seeds, measures from period 20; each
cell gives the all-unit-cost and the all-profit-rate population. A seed passes when every line
of E0 (section "Experiments") is true in it. The headline is the share of seeds won by the
unit-cost label in the mixed population at the defaults, on 500 seeds (200 for systematic
cutting).

| Rule | Seeds of 50 that pass E0 | Capacity over demand, mean (range within a run) | Price over the price of production | Times it crosses 1 | Profit rate | Demand lost | Share won | Beyond drift |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Leader-follow | 50 / 49 | 1.05 (0.39–1.73) / 1.04 (0.30–1.72) | 1.07 / 1.07 | 22 / 22 | 0.067 / 0.069 | 0.041 / 0.053 | 0.50 (0.45–0.54) | no |
| Normal-price cutting (default) | 43 / 12 | 1.15 (0.71–1.79) / 1.29 (0.57–2.12) | 1.08 / 1.17 | 30 / 23 | 0.063 / 0.088 | 0.002 / 0.008 | 0.67 (0.63–0.71) | yes |
| Cost-edge cutting | 0 / 0 | 1.63 (1.26–1.93) / 1.52 (0.87–1.92) | 1.16 / 1.13 | 0 / 1 | 0.043 / 0.047 | 0.000 / 0.000 | 0.92 (0.89–0.94) | yes |
| Systematic cutting | 0 / 0 | 1.43 (0.51–2.43) / 1.44 (0.44–2.60) | 1.27 / 1.30 | 16 / 17 | 0.100 / 0.115 | 0.013 / 0.015 | 0.57 (0.50–0.64) | no |

- **At the default E0 fails on capacity.** In the all-unit-cost population the average of
  capacity over demand is outside 0.9–1.2 in 7 seeds of 50; every other line holds in all 50.
  In the all-profit-rate population capacity passes in 12 seeds, the price in 37 and the
  profit rate in 42: firms there hold different techniques, so cost-edge wars start and the
  cycle is wider.
- **Cost-edge cutting cannot meet E0.** Without technical change every firm ends on the same
  technique after two periods, no firm has a cost edge, and nothing lowers the price while
  capacity is idle: the price never crosses the price of production.
- **Leader-follow meets E0 and gives no headline.** Every firm posts the same price in every
  period, so the price moves no market share.

### No rule fits both, and why

- **The headline needs the cost leader to cut alone.** Under cost-edge cutting a follower is
  one step of 2 % behind the leader during every price war, and the replicator moves 0.18 of
  the market to the unit-cost label. A lower unit cost is not a higher profit rate: the
  unit-cost label earns 0.063 against 0.065.
- **E0 needs someone to cut when no firm has a cost edge.** Otherwise the price stays where
  the last war left it and entry fills the industry with idle capacity.
- **Each way of meeting the second weakens the first.** Share won on 100 seeds unless marked:

| What lets firms without a cost edge cut | Seeds of 50 that pass E0 | Share won |
| --- | --- | --- |
| Nothing (cost-edge cutting) | 0 / 0 | 0.92 (500 seeds) |
| A price above the firm's price of production; the cut stops above it | 0 / 12 | 0.69 (500 seeds) |
| The same; the cut may end up to 2 % below it (the default) | 43 / 12 | 0.67 (500 seeds) |
| A price above the regulating price of production | 43 / 8 | 0.63 (500 seeds) |
| The same, with a shortage step of 0.25 instead of 0.5 | 50 / 35 | 0.56 |
| Entrants post 2 % below the lowest price | 48 / 5 | 0.68; a quarter of demand is lost in the mixed population |
| The default with leader-follow's rise of 3 % after a shortage | 50 / 50 | 0.51 |
| The default with the accelerator | 50 / 48 | 0.52 |
| Every firm cuts (leader-follow) | 50 / 49 | 0.50 (500 seeds) |

- **The price level works the same way.** E0 asks for a price near the price of production.
  There the hurdle of the profit-rate rule is near r̄ and the two rules choose alike: 0.07
  under leader-follow against 0.10 at the default. The headline of v3 (0.98) came with a price
  at 1.37 times the price of production.

### What holds at the default

Mixed population, 500 seeds at the defaults and 200 in the other cells.

| Measure | Normal-price cutting | Cost-edge cutting | Leader-follow |
| --- | --- | --- | --- |
| Share won at the defaults | 0.67 (0.63–0.71) | 0.92 (0.89–0.94) | 0.50 (0.45–0.54) |
| Final capacity share of the unit-cost label | 0.60 | 0.78 | 0.49 |
| Share won for β = 0, 0.5, 1.5, 3 | 0.50, 0.62, 0.67, 0.84 | 0.57, 0.75, 0.89, 0.96 | 0.48, 0.43, 0.47, 0.47 |
| Share won with the neutral set; without draws | 0.59; 0.95 | 0.69; 0.99 | 0.47; 0.73 |
| Share won for λ = 0, 0.25, 0.5, 0.75, 1 at r̄ = 0.05 | 0.67, 0.61, 0.66, 0.59, 0.49 | 0.89, 0.90, 0.87, 0.79, 0.71 | 0.47, 0.50, 0.42, 0.41, 0.48 |
| Share won at r̄ = 0.16, λ = 0 | 0.44 | 0.95 | 0.20 |
| Change in sales share through the price | +0.06 | +0.18 | 0.00 |
| Hurdle of the profit-rate label; its orders that are not the cheapest | 0.101; 0.67 | 0.105; 0.69 | 0.068; 0.47 |
| Price over the price of production; demand lost | 1.14; 0.005 | 1.14; 0.005 | 1.05; 0.011 |

- **The bias of technical change matters.** At the default the share won is beyond drift from
  β = 1.5.
- **So does the evaluation price.** At r̄ = 0.05 the advantage is gone at λ = 1.
- **At r̄ = 0.16 the default is at drift** at every λ (0.44 to 0.61). The unit-cost label wins
  there under cost-edge cutting and loses under leader-follow and systematic cutting (0.05).
- **Not explained.** Under leader-follow without draws the unit-cost label wins 0.73, through
  entry, exit and retirements. The cause is not isolated.

### What does not matter

- **The floor.** Under leader-follow, with the operating-cost floor the runs are identical in
  34 to 96 % of cases, by experiment, and no verdict changes: the shortage turns the price up
  before either floor is reached. Not run under the default.
- **The pilot.** Leader-follow with overtime is the rule of the pilot's systematic cells, and
  cost-edge cutting with overtime that of its cost-edge cells. Both are close to its headline
  (drift and 0.16–0.20 against drift and 0.10–0.19; 0.92 against 0.94–0.97). The default has
  no counterpart in the pilot.

## Research questions and hypotheses

- **RQ1 (A).** In a mixed population of unit-cost firms (Shaikh, h = 0) and profit-rate firms
  (Okishio, h = the best rate at the evaluation price), which rule does market selection
  favour under Marx-biased technical change?
- **RQ2 (A).** How does the answer depend on the price rule, and then on the investment rule,
  the general rate and demand growth?
- **RQ3 (B).** Why does the winner win: through the price or through accumulation, and how
  much of the unit-cost rule's advantage comes from the price at which the profit-rate rule
  judges techniques?

| # | Hypothesis | Experiment | v3 evidence (provisional) |
| --- | --- | --- | --- |
| H1 | The unit-cost rule wins where the lowest-cost firm sets the price | E1 by price rule | Met in proportion: 0.92 when only the cost leader cuts, 0.67 at the default, 0.50 when every firm cuts |
| H1′ | The profit-rate rule cannot lose systematically | E1 | Fails at the default and under cost-edge cutting; holds under leader-follow and systematic cutting |
| H2 | The advantage grows with the Marx bias | E2 by price rule | Met at the default (0.50 to 0.84) and under cost-edge cutting (0.57 to 0.96); no effect under leader-follow |
| H3 | Where selection runs through accumulation it can favour the profit-rate rule | E3, E4, reserve | Met at r̄ = 0.16 under leader-follow (0.20) and systematic cutting (0.05), and when the reserve is never released (0.01 at the default); at the default r̄ = 0.16 gives drift |
| H4 | The more firms cut, the smaller the margin, the hurdle and the advantage | E1, E3 by price rule | Met: 0.92, 0.67, 0.50 as cutting spreads; under leader-follow prices are also equal across firms |
| H5 | Judged at the price of production, the hurdle falls to r̄ or just above it and the advantage shrinks | E3 | Met at r̄ = 0.05: 0.67 → 0.49 at the default, 0.89 → 0.71 under cost-edge cutting; not at r̄ = 0.16 |
| H6 | The profit-rate adopter does not realise the rate it maximises | E1, E5 | Not met in v3: the profit-rate label realises the higher rate under every rule (0.066 against 0.062 at the default) |

Not tested, as in v3: Okishio's theorem about the general rate, and the emergence of the bias
at a rising wage.

## The model

Six steps a period and one rule that differs between the types.

**Setting.** One industry in a given economy. The money wage is the numéraire and capital goods
are priced 1. Demand is exogenous, D_t = D_0(1 + g)^t, and so is the general rate r̄. A technique j
is a pair (ucs_j, κ_j): operating cost and capital per unit of normal output, with unit cost
uc_j = ucs_j + δκ_j and δ = 1/T. Its price of production is uc_j + r̄κ_j. Plants have one technique
and a normal capacity S = 20.

**Initial industry.** Shaikh's three techniques (2016, Tables 7.10–7.11): C (64.25, 137.50), D1
(61.77, 142.31), D2 (59.21, 157.89), each given to one unit-cost and one profit-rate firm. Six
firms, identical within pairs, with 6, 6 and 7 plants: capacity 760 against D_0 = 674.7. Every
price is 100 and every share is the capacity share. Plant k of a firm's n plants has age
floor(kT/n), so retirements spread over the first T periods. A firm's cash is the depreciation
already accumulated on its plants, which backs the reserves they release.

**The one rule that differs.** At every order, for investment or entry, a firm picks

```latex
j^{*}_{i} = \arg\min_{j \in M_t} \big[\, ucs_j + (\delta + h_i)\,\kappa_j \,\big]
```

```latex
h_i = \begin{cases} 0 & \text{unit-cost rule (Shaikh)} \\ \max\Big(0,\ \max_{j \in M_t} \dfrac{p^{e}_{i} - uc_j}{\kappa_j}\Big) & \text{profit-rate rule (Okishio)} \end{cases} \qquad p^{e}_{i} = (1-\lambda)\,p_{i,t} + \lambda\,\big(uc_R + \bar r\,\kappa_R\big)
```

R is the regulating technique, the lowest unit cost among plants in operation. λ = 0 judges at
the firm's own price; λ = 1 at the price of production of R.

**Schedule.**

1. **Pricing.** Every firm reads last period's prices and last period's excess demand. A
   shortage is last period's demand above total normal capacity. The floor is the unit cost
   of the firm's best plant in operation, the one with the lowest unit cost. A firm without a
   plant in operation keeps its price. One option, `pricing`, chooses among four rules. In the
   three cutting rules P is the lowest price of the firm's rivals; after a shortage the firm
   moves up to the next higher rival price, or, with no rival above, raises its price by 0.5
   times the excess-demand share; otherwise it undercuts to (1 − c)P, c = 0.02, when the rule
   entitles it to, and else follows P. Its price rises only after a shortage or to reach its
   floor.
   - *Normal-price cutting* (default). A firm with spare capacity (last utilisation below 1)
     is entitled to cut while P is above its own price of production, that of its best plant.
     At or below it, it also needs a unit-cost edge over a rival posting P. A cut can end up
     to c below the price of production.
   - *Cost-edge cutting.* Spare capacity and a unit-cost edge over a rival posting P, at any
     price.
   - *Systematic cutting.* Spare capacity alone, at any price.
   - *Leader-follow.* L is the lowest price posted last period by a firm with a plant in
     operation. After a shortage every firm posts (1 + z)L, z = 0.03. Otherwise every firm
     posts (1 − c)L, or its floor if that is higher, whatever its utilisation. A firm that is
     alone with a plant in operation raises its price by z a period, up to 3 times its floor.
2. **Demand.** Market shares follow the replicator below, with E = 1/p and χ = 1. A firm offers
   its plants whose operating cost is at most its price and can sell up to u_max = 1.2 times
   their normal capacity. Sales are the smaller of share × D and that limit; unserved demand
   is re-allocated once, pro rata to the room left; the rest is lost and recorded.
3. **Production and accounts.** Plants run cheapest first, then youngest, up to normal
   capacity; what is left runs as overtime in the same order, up to u_max times capacity, at
   the same operating cost. Every plant in operation ages and depreciates straight-line over
   T. Profit is after depreciation; dividends are d × max(0, profit), d = 0.5; the rest joins
   the investible funds. No debt, interest or bankruptcy. Then, once a period: the regulating
   technique and its price of production uc_R + r̄κ_R, and r_new, the capacity-weighted
   realised rate (profit over purchase cost) of the plants aged 5 periods or less.
4. **Scrapping.** A plant leaves at age T = 10, after 2 consecutive periods with its owner's
   price below its operating cost, or after 2 consecutive periods without output. Its
   depreciation reserve (purchase cost less book value) joins the firm's investible funds if
   r_new ≥ r̄ in that period, or if no plant is in the window of r_new. Otherwise the firm pays
   it to the rest of the economy, as far as its cash allows. The book value left is written
   off. A working plant is never replaced. One option, `reserve`, replaces this condition for
   the sensitivity check: the reserve always joins the funds, or is always paid out.
5. **Technical change and investment.** Draws as below. The firm computes its hurdle and
   picks j*. *Retained earnings* (default): it buys the whole plants of j* that its funds,
   still in cash, pay for. *Accelerator*: it buys the plants missing for its capacity, plants
   on order included, to reach the demand addressed to it, share × D_t, as far as its cash
   pays. There is no target utilisation: overtime is the buffer. The reserve condition of
   step 4 is the same under both rules. A plant ordered in t produces from t + 1.
6. **Entry and exit.** Exits first: a firm leaves with a share below 1 % or without capacity,
   in operation or on order, while 2 firms remain; its cash goes to the rest of the economy.
   Then at most one entrant, with the probability below. Its label is copied from an incumbent
   drawn by market share and flipped with probability μ = 0.02; its price is the lowest
   posted; its technique is chosen by its own rule on the public menu at that price; its
   capacity is 0.5 times the survivors' mean capacity, in whole plants, paid by equity from
   the rest of the economy and delivered next period; its share is its capacity over next
   period's capacity, and the incumbents' shares are scaled down.

```latex
f_{i,t} = f_{i,t-1}\Big[1 + \chi\,\frac{E_{i,t} - \bar E_t}{\bar E_t}\Big], \qquad \bar E_t = \sum_j f_{j,t-1}\,E_{j,t}, \qquad E_{i,t} = 1/p_{i,t}
```

```latex
ucs_n = (1-a)\,ucs_o, \quad \kappa_n = (1+k\,a)\,\kappa_o, \quad a \sim U(0, A], \quad k = \beta\, e^{\sigma z},\ z \sim N(0,1)
```

```latex
\Pr(\text{entry}_t) = \min\Big\{1,\ \theta\,\frac{\max(0,\ r^{new}_t - \bar r)}{\bar r}\Big\}
```

**The default price rule in one sentence.** Competition for sales brings the price down to the
price of production; below it only a cost leader cuts. It is v3's two regimes and no new
constant: systematic cutting above the firm's price of production, cost-edge cutting at or
below it.

**Technical change.** Each period a firm with a plant in operation draws, with probability
π = 0.2, one design from its best known technique o (A = 0.05, σ = 0.8, β = 1.5). It keeps the
design if its own rule prefers it to o. A design is public 2 periods after its first plant
produces. The neutral set, the categories rule (with its two categories defined at the
evaluation price) and "no draws" are options.

**Overtime, in one place.** Utilisation is sales over normal capacity and can exceed 1. The
shortage signal, the spare-capacity test of the cutting rules, the idle test and depreciation by
time are those of v3: only the sales limit of step 2 and the production order of step 3 change.
u_max = 1 gives v3 back.

**Randomness and neutrality.** One random stream per firm and one for the industry, from the
run seed. Every firm takes four uniforms and one normal a period, and the industry three
uniforms, used or not, so populations and cells are compared on the same numbers. Every step
computes all firms from the state at the start of the step. The label is read only to look up
the rule and in inheritance at entry; ties are never broken by a firm's place or serial number.
All cash, the rest of the economy included, sums to zero in every period.

**Winner.** A seed is decided if producing capacity is positive at t = 200. The unit-cost label
wins with more than half of it; an exact tie is counted apart. The share won is wins over wins
plus losses, with its 95 % Wilson interval, and it is beyond drift when that interval is
disjoint from those of the two controls (both labels on one rule, same seeds).

| Parameter | Symbol | Default | Varied in | Against v3 |
| --- | --- | --- | --- | --- |
| Price rule | — | normal-price cutting | E0 to E4: cost-edge, leader-follow; E0 and E1: systematic | New default; four levels |
| Overtime limit | u_max | 1.2 | Robustness: 1 (none); Morris 1–1.4 | New |
| Price cut | c | 0.02 | Morris 0.01–0.05 | — |
| Shortage step (the three cutting rules) | — | 0.5 | Morris 0.1–0.5 | Now screened: it trades E0 against the headline |
| Spare-capacity threshold (the three cutting rules) | u_full | 1 | Fixed | — |
| Rise after a shortage; cap of a firm alone (leader-follow) | z; — | 0.03; 3 × floor | Fixed | New, for that option |
| Price floor | — | unit cost | Robustness: operating cost | Option added |
| Bias of technical change | β | 1.5 | E2: 0, 0.5, 1.5, 3, neutral set, none; Morris 0.5–3 | — |
| Evaluation-price weight | λ | 0 | E3: 0, 0.25, 0.5, 0.75, 1 | — |
| Investment rule | — | retained earnings | E4: accelerator | Accelerator without u* |
| General rate | r̄ | 0.05 | E3 and E4: 0.16 | — |
| Demand growth | g | 0 | E4: 0.01 | — |
| Largest operating-cost cut per design | A | 0.05 | Morris 0.02–0.10 | — |
| Draw probability | π | 0.2 | Morris 0.1–0.4 | — |
| Selection intensity | χ | 1 | Morris 0.25–4 | — |
| Payout ratio | d | 0.5 | Morris 0.25–0.75 | — |
| Plant life | T | 10 | Morris 7–19 | — |
| Plant size | S | 20 | Morris 10–40 | — |
| Entry speed | θ | 5 | Morris 1–10 | — |
| Mutation at entry | μ | 0.02 | Morris 0–0.05; 0 in E6 | — |
| Spread of the bias; lag before a design is public | σ; L | 0.8; 2 | Fixed; robustness L = none | — |
| Entry window; entrant's size; exit share; least firms; scrap periods | — | 5; 0.5; 1 %; 2; 2 | Fixed | — |
| Depreciation reserve | — | released if r_new ≥ r̄ | Sensitivity: always released; never released | Option added |
| Scrap cost | — | operating cost | Robustness: unit cost | — |
| Initial firms per pair | — | 1 | Robustness: 2 and 5 | — |
| Target utilisation | u* | — | — | Removed |

## Experiments

Each cell is a mixed population run against its two controls on the same seeds.

**E0, the gate.** Single-rule populations, no draws, 50 seeds, under each price rule. Measures
over periods 20 to 199. E0 holds when each line below is true in at least 9 seeds of 10 in both
populations. Two lines are new. The threshold on the crossings is proposed here. The ceiling on
the demand lost was set at 0.10 by Ugo on 10 November, after the runs; 0.05 was proposed first.

| Fact | Measure | Threshold | Default, v3 runs: mean; seeds of 50 that pass |
| --- | --- | --- | --- |
| The lowest-cost firm leads the price | Periods in which a firm posting the lowest price has the lowest unit cost | at least 0.9 | 1.00 and 0.99; 50 and 50 |
| The price gravitates around the price of production | Mean of price over price of production | 0.9–1.2 | 1.08 and 1.17; 50 and 37 |
| | Times it crosses 1 | at least 5 | 30 and 23; 50 and 50 |
| Capacity follows demand | Mean of capacity over demand | 0.9–1.2 | 1.15 and 1.29; 43 and 12 |
| The profit rate gravitates around r̄ | Industry rate at r̄ = 0.05 | 0.03–0.10 | 0.063 and 0.088; 50 and 42 |
| Profit rates stay unequal | Mean spread of rates across firms | above 0 | 0.09 and 0.12; 50 and 50 |
| Demand is served | Share of demand lost | at most 0.10 | 0.002 and 0.008; 50 and 50 |
| The industry survives | Capacity at the last period | above 0 | 50 and 50 |

E0 is not met at the default: 43 and 12 seeds of 50 pass every line, where 45 are needed. It is
met under leader-follow (50 and 49), and at the default with the accelerator (50 and 48), in
both cases without the headline. Reported beside E0, and not part of it: capacity at the last
period within 0.9–1.2 of demand (27 and 22 seeds of 50 at the default), and the range of
capacity within a run (0.71 to 1.79 and 0.57 to 2.12).

| # | Question | Design | Seeds | Runs |
| --- | --- | --- | --- | --- |
| E0 | Does the industry behave as under real competition? | No draws, two controls, 4 price rules | 50 | 400 |
| E1 | Which rule wins, by price rule? | Defaults, 4 price rules | 500 | 6,000 |
| E2 | Does the advantage grow with the Marx bias? | β = 0, 0.5, 1.5, 3; neutral set; none; 3 price rules | 200 | 10,800 |
| E3 | How much comes from the evaluation price? | λ (5) × price rule (3) × r̄ (0.05, 0.16) | 200 | 18,000 |
| E4 | Where does each rule win? | Price rule (3) × investment rule (2) × r̄ (2) × g (0, 1 %), then under the categories rule | 200 | 28,800 |
| E5 | Through which channel? | Decomposition of E4; regression of the profit-rate gap on the dearer orders | — | 0 |
| E6 | Can one firm of a rule invade the other? | 1 among 9, both ways, with a one-rule control; the default and cost-edge cutting | 500 | 4,000 |

The three price rules of E2 to E4 are the default, cost-edge cutting and leader-follow. About
68,000 runs: 20 minutes on 10 workers at v3's speed with overtime (11,200 runs in 2 min 23 s
under leader-follow, 3 min 22 s at the default). E6 keeps v3's design: ten firms on D1,
D_0 = 1,065.3, μ = 0.

## Sensitivity analysis

- **Morris screening.** The ten parameters of v3 plus u_max and the shortage step: 10
  trajectories on a 4-level grid, 130 points × 3 populations × 100 seeds = 39,000 runs, at
  the default. Outcomes: the share won less the controls' mean, the mean final capacity
  share, and the share of E0's lines that hold.
- **Sensitivity over the reserve** (asked by Ugo, 10 November). The rule of the depreciation
  reserve gets three levels: released if r_new ≥ r̄ (default), always released, never
  released. These are arms 4, 2 and 1 of the v2 pilot. Cells: E0 and E1 at each of the two
  other levels, under the default, cost-edge cutting and leader-follow: 9,600 runs. A first
  look on v3's code (E0 at the default on 50 seeds, all-unit-cost population, from period
  20; share won on 100 seeds of the mixed population):

| Reserve | Capacity over demand, mean (range within a run) | Price over the price of production | Profit rate | Demand lost | Share won, default | Share won, cost-edge | Share won, leader-follow |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Released if r_new ≥ r̄ | 1.15 (0.71–1.79) | 1.08 | 0.063 | 0.002 | 0.69 | 0.86 | 0.45 |
| Always released | 1.29 (1.22–1.39) | 0.99 | 0.012 | 0.000 | 0.68 | 0.82 | 0.49 |
| Never released | 1.37 (0.64–2.03) | 1.53 | 0.212 | 0.011 | 0.01 | 0.80 | 0.05 |

  - **The reserve sets the profit rate.** Always released, the rate falls to 1 %; never
    released, it is 21 % and the price half as high again as the price of production. Only
    the condition puts the rate near r̄. E0 fails in every seed at both other levels.
  - **The condition makes the cycle.** With the reserve always released capacity stays between
    1.22 and 1.39 times demand and no demand is lost; the price settles just below the price
    of production and never crosses it.
  - **The headline does not need the condition, but it needs a reserve.** Always released,
    the unit-cost label still wins at the default (0.68) and under cost-edge cutting (0.82).
    Never released, the profit-rate label wins at the default (the unit-cost label takes
    0.01 of seeds) and under leader-follow (0.05): the price stays far above the price of
    production and accumulation selects. Under cost-edge cutting the unit-cost label still
    wins (0.80).

- **Robustness checks.**

| Check | Cells | Seeds | v3 result |
| --- | --- | --- | --- |
| No overtime (u_max = 1) | E0 and E1 under the 4 price rules | 500 | At the default, 100 seeds: 0.70, and E0 holds in no seed. Others: 0.98 (cost-edge), 0.49 (leader-follow), 0.56 (systematic) |
| Operating-cost floor | E1 at the default and under leader-follow | 500 | Under leader-follow 0.49 against 0.50; not run at the default |
| Scrapping on unit cost | E1 and the marx cells of E4 | 200 | Under v3's default, 20 seeds: the same runs under either cost, since no plant leaves through the cost test |
| Private diffusion (L = none) | E1 | 200 | Not run |
| Homogeneous start (six firms on D1) | The 6 cells of E2 | 200 | Not run |
| 12 and 30 firms | E1 and the 4 cells of E4 with r̄ = 0.16 and g = 0.01 | 200 | Not run |
| Categories rule | The cells of E4 (already in E4) | 200 | Not run |

## Rebuilding the code

Version 3 was built under a line budget (769 lines of 770) and its rules were then changed from
outside, by patching functions from a script. Version 4 is rebuilt for a reader.

**Readability before the line count.**

- The model code (`parameters.py`, `run.py`, `equations/`, `markets/`, `model/`) has at most
  1,000 lines, counted without blank lines, comment lines and docstrings. A test enforces it.
  No line is saved at the cost of a name, a step or a comment.
- A comprehension that filters, a sort key or a nested expression gets a comment line above
  it that says in plain words what it selects and why:

  ```python
  # The firms that can set a price: those with at least one plant in operation.
  active = [firm for firm in industry.firms if firm.plants]
  ```

- A step function reads top to bottom like its paragraph of the schedule, one stage a block,
  each block opened by a comment. No statement does two things.
- Names say what a thing is in the model's words (`lowest_price`, `floor`, `reserve`); single
  letters are kept for the symbols of this document (`p`, `c`, `z`) and loop indices.
- Each equation file opens with its formula and its source in this document.

**Rules as options, not patches.** The price rules are pure functions in
`equations/pricing_*.py`, chosen in one place by `params.pricing`; the floor by
`params.price_floor`; overtime by `params.u_max`; the reserve by `params.reserve`. No
experiment replaces a function of the model.

**Kept from v3.** Equations as pure functions, named `equations/<step>_<equation>.py`;
transactions in `markets/`; one payment function and money conservation asserted every period;
simultaneous moves and `math.fsum`; the random streams; undefined values as `None`; the
label-swap and firm-order tests, run under every price rule and investment rule; the harness
with ordered parallel runs, `runs.csv`, `cells.csv` and resume; the run row with the share
decompositions. The run row gains the E0 measures above. Speed comes second: a run at the
defaults in at most 0.2 s, profiled only if it is slower.

**The run viewer** (`experiments/show_run.py`, outside the line count). It runs one industry
and shows why it behaved as it did.

```bash
python -m experiments.show_run --seed 7 pricing=cost_edge rbar=0.16 population=all_unit_cost
```

- **Input.** Any parameter as `name=value`, a seed, and `population` (mixed, all_unit_cost,
  all_profit_rate).
- **How.** It steps the model itself, period by period, and reads the firms after each
  period, so the model needs no recorder.
- **Output.** In `outputs/runs/<name>/`: the period table, a table with one row per firm and
  period, the run row, one figure, and a short text read-out (outcome, final shares, the E0
  measures, the share decompositions).
- **Panels**, on one time axis, each for one question:

| Panel | Series | Question |
| --- | --- | --- |
| Prices | Posted price by label, or one line when they coincide; price of production of the regulating technique; lowest unit cost in operation | Does the price gravitate, and who is below whom? |
| Capacity and sales | Normal capacity over demand; sales over demand; the band between 1 and u_max | When is the industry short, and when does it work overtime? |
| Demand lost | Share of demand lost | How long and how deep are the shortages? |
| Entry gate | r_new against r̄; the industry rate; periods in which the reserve is withdrawn, shaded | When does capital enter and when does it leave? |
| Firms | Firms with a plant; entries and exits a period | Who enters and who leaves, and when? |
| Selection | Capacity share and market share of the unit-cost label | Which label gains, and through sales or capacity? |
| Choice of technique | Hurdle of the profit-rate label; share of its orders that are not the cheapest | How far apart are the two rules in this run? |
| Techniques | Unit cost by label; capital per unit by label | Is technical change Marx-biased, and for whom? |
| Profit rates | Realised rate by label | Does the rule that maximises the rate realise it? |
| Plants | Capacity ordered by label; capacity leaving by reason (age, cost, idle) | Where does capacity come from and go? |

  With `--firms` the price and share panels draw one thin line per firm, coloured by label.
  The figure follows `figures/style.py`: one colour per label in every panel, no second axis.

**Tests.** Those of v3, one file per step, plus: overtime (sales limit, production order,
u_max = 1 gives the run without overtime); each price rule; the accelerator without a target;
the three levels of the reserve; the viewer on a short run.

## What the other sections of the v3 proposal need

- **Report.** Section 3 presents four price rules and overtime. Section 5.1 shows E0 on
  averages with the cycle, the headline by price rule, and the trade-off between them; 5.4
  treats the price rule as the first condition. Figure 2 is a run of the viewer. Figure 3 gets
  one curve per price rule.
- **Presentation.** Slide 6 ("the unit-cost rule wins") becomes "it wins as far as the cost
  leader sets the price"; slide 9 (realised rates) reports that H6 is not met; slides 10 and
  11 open with the price rule.
- **Timeline.** The dates stand. v3 was built on 10 November, so the rebuild fits before the
  runs of 17 to 19 November.
- **Literature.** Unchanged.

## Decisions for the group

| Decision | Options | Recommendation | Why |
| --- | --- | --- | --- |
| Default price rule | Normal-price cutting; cost-edge cutting; leader-follow | **Set by Ugo's criterion, 10 Nov:** normal-price cutting | The best joint fit: the only rule with a headline beyond drift (0.67) and E0 in most seeds of one population. Cost-edge cutting gives 0.92 and no E0; leader-follow E0 and no headline |
| E0 at the default | Report it as not met; make the accelerator the default investment rule | Report it as not met | E0 holds in 43 and 12 seeds of 50. With the accelerator it holds in 50 and 48, and the headline goes to drift (0.52) |
| What E0 checks | The last period; averages over the run | Averages, with the cycle reported | Under every rule tried the industry cycles; no rule puts capacity in the band at one date in 9 seeds of 10 |
| Ceiling on the demand lost in E0 | 5 %; 10 % | **Decided by Ugo, 10 Nov:** 10 % | Under leader-follow the 5 % ceiling passes in 37 and 25 seeds of 50, the 10 % ceiling in 50 and 49. The ceiling was set after the runs, which the report should say. At the default less than 1 % is lost |
| The cycle | Accept it; look for a rule that damps it | Accept it for the report | It comes from the reserve condition, which the pilot settled. The sensitivity over the reserve shows the alternative: no cycle, and a profit rate of 1 % |
| Overtime premium | None; a premium on overtime output | None | Asked by Ugo; the runs have none |
| What counts in the 1,000 lines | Comments excluded; comments and docstrings excluded | Both excluded | A docstring is a comment for this purpose; to confirm |
| "No draws" under leader-follow | Leave it; isolate it before the report | Isolate it | The unit-cost label wins 0.73 there and the cause is not known |
| Where version 4 is built | A clean tree beside v3; a branch of this one | A clean tree, v3 read-only beside it | As v3 did with v2: the unchanged equations are ported, not inherited |

Not run in v3, so unknown under the new default: E4, E6, Morris and the robustness checks marked
"not run". The reserve, the accelerator and the run without overtime were looked at on 50 seeds
of E0 and 100 seeds of the mixed population only.
