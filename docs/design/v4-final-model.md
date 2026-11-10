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
  its target utilisation. The default price rule becomes leader-follow with the unit-cost
  floor, and the price rule becomes the first treatment, with three levels.
- **Why.** E0 is the gate: without technical change the industry must behave like an industry
  under real competition. Under v3's default it does not: capacity stays at 1.6 times demand
  and the price stops falling after two periods. Under leader-follow with overtime, capacity
  and the price are within 0.9–1.2 of demand and of the price of production, on average over
  a run, in all 50 seeds of both populations.
- **What E0 still does not show.** The industry cycles: within a run capacity moves between
  0.4 and 1.7 times demand, so capacity at the last period is in the band in 20 seeds of 50,
  and more than 5 % of demand is lost in a quarter to a half of the seeds. E0 is restated on
  averages over a run, and the cycle is reported beside it.
- **What it does to the answer.** At the default neither rule wins beyond drift (0.50 of
  seeds). The unit-cost rule wins under cost-edge cutting (0.92), where a cost advantage
  becomes a lower price; the profit-rate rule wins at r̄ = 0.16 under leader-follow and
  systematic cutting (the unit-cost rule wins 0.04 to 0.20 of seeds there). The report's
  answer is "which rule wins depends on whether a cost advantage sets the price".
- **Two constraints on the rebuild.** Readable code comes before the line count: at most 1,000
  lines of model code, comments excluded. And a run viewer, outside that count, runs one set of
  parameters on one seed and plots what explains the run.

## What changed from the v3 final model

| # | In v3 | In v4 | Why |
| --- | --- | --- | --- |
| 1 | No overtime: output stops at normal capacity | Output up to u_max = 1.2 times normal capacity, at the same operating cost (no premium) | Without it 13 to 14 % of demand is lost in E0 under leader-follow; with it 4 to 5 %, and 1 % at the defaults |
| 2 | Accelerator: desired capacity = the demand addressed to the firm over a target utilisation u* = 0.9 | Desired capacity = the demand addressed to the firm; no target | The target was the buffer of a model without overtime. In E0 with overtime, the demand lost is 2 % without the target against 4 % with it |
| 3 | Default price rule: cost-edge cutting | Default: leader-follow with the unit-cost floor | The only rule under which E0 holds on capacity, price and profit rate |
| 4 | Two price regimes; systematic cutting stood for leader-follow | Three price rules: leader-follow, cost-edge cutting, systematic cutting | v3's systematic cutting is not leader-follow: it gives the worst E0. The headline depends on the rule, so the rule is a treatment |
| 5 | Leader-follow's own shortage rule and monopoly cap dropped for the common shortage step | Restored, for leader-follow only: 3 % above the lowest price after a shortage; a firm alone stops at 3 times its floor | They are part of the rule that was run. The common step (half the excess-demand share) sends the price to 3 times the price of production |
| 6 | One floor: unit cost | The same by default; the operating-cost floor as a robustness option | It moves no share won by more than 0.06 and no verdict, so it is not a treatment |
| 7 | E0 read at the last period (capacity within a band in 9 seeds of 10) | E0 read on averages over the run, from period 20, with the cycle reported beside | A cycle cannot meet a band at one date; gravitation is around a centre |
| 8 | H1: the unit-cost rule wins under price competition | H1 depends on the price rule; H4 becomes the central test | 0.92 to 0.98 under cost-edge cutting, drift under leader-follow |
| 9 | E1 to E4 at the default rule; pricing varied in E3 and E4 only | The price rule crossed with E1, E2, E3 and E4 | The effect of the bias and of the evaluation price exists under cost-edge cutting only |
| 10 | Robustness: u* = 0.8 and 0.95 | Dropped. Added: no overtime (u_max = 1), the operating-cost floor | u* no longer exists; the two new checks are already run in v3 |
| 11 | Model code at most 770 lines, blank lines excluded | At most 1,000 lines, comments excluded; readability first | Section "Rebuilding the code" |
| 12 | Figure 2 from period tables kept by the harness | A run viewer for any parameters and seed | Every diagnosis of v3 needed a trace of one run |

Not changed: the one rule that differs between the types, the menu, the replicator, scrapping,
the depreciation reserve and its condition, technical change, entry and exit, the winner, the
populations and controls, and the rules of neutrality.

## What the v3 experiments showed

### E0 by price rule

Single-rule populations without technical change, 50 seeds, measures from period 20. Each cell
gives the all-unit-cost and the all-profit-rate population. "Seeds in the band" counts the seeds
whose average over the run is within 0.9–1.2.

| Rule | Capacity over demand, mean (range within a run) | Seeds in the band | Seeds in the band at the last period | Price over the price of production | Seeds in the band | Times the price crosses the price of production | Profit rate | Demand lost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Leader-follow, overtime | 1.05 (0.39–1.73) / 1.04 (0.30–1.72) | 50 / 50 | 20 / 20 | 1.07 / 1.07 | 50 / 50 | 22 / 22 | 0.067 / 0.069 | 0.041 / 0.053 |
| Leader-follow | 1.13 (0.28–1.95) / 1.11 (0.20–1.92) | 50 / 50 | 10 / 13 | 1.16 / 1.14 | 48 / 50 | 13 / 14 | 0.078 / 0.077 | 0.140 / 0.128 |
| Cost-edge, overtime | 1.63 (1.26–1.93) / 1.52 (0.87–1.92) | 0 / 0 | 0 / 3 | 1.16 / 1.13 | 50 / 43 | 0 / 1 | 0.043 / 0.047 | 0.000 / 0.000 |
| Cost-edge (v3 default) | 1.63 (1.28–1.93) / 2.16 (0.98–2.57) | 0 / 0 | 0 / 1 | 1.16 / 1.40 | 50 / 11 | 0 / 0 | 0.044 / 0.072 | 0.000 / 0.006 |
| Systematic, overtime | 1.43 (0.51–2.43) / 1.44 (0.44–2.60) | 0 / 0 | 6 / 15 | 1.27 / 1.30 | 11 / 14 | 16 / 17 | 0.100 / 0.115 | 0.013 / 0.015 |
| Systematic | 1.86 (0.46–2.74) / 1.85 (0.44–2.84) | 0 / 0 | 7 / 2 | 1.61 / 1.58 | 0 / 0 | 7 / 8 | 0.143 / 0.155 | 0.042 / 0.041 |

In every row the price leader has the lowest unit cost in at least 0.98 of periods, profit rates
are unequal and no seed ends without capacity.

- **Cost-edge cutting cannot meet E0.** Without technical change every firm ends on the same
  technique after two periods, no firm has a cost edge, and nothing lowers the price while
  capacity is idle: the price never crosses the price of production, and entry absorbs the
  profit above r̄ through idle capacity.
- **Systematic cutting overshoots.** Firms cut, but after a shortage the common step raises
  the price by half the excess-demand share in one period, up to 2.5 to 3 times the price of
  production.
- **Leader-follow gravitates.** The price falls 2 % a period while capacity is not short and
  rises 3 % a period after a shortage; it crosses the price of production 22 times in a run,
  and the two populations give the same industry.

### The headline by price rule

Share of seeds won by the unit-cost label in the mixed population. E1 has 500 seeds; the cells at
r̄ = 0.16 and systematic cutting with overtime have 200.

| Rule | Defaults | With overtime | r̄ = 0.16 | r̄ = 0.16 with overtime |
| --- | --- | --- | --- | --- |
| Leader-follow | 0.49 (0.45–0.53) | 0.50 (0.45–0.54) | 0.08 | 0.20 |
| Cost-edge cutting | 0.98 (0.97–0.99) | 0.92 (0.89–0.94) | 0.88 | 0.95 |
| Systematic cutting | 0.56 (0.52–0.61) | 0.57 (0.50–0.64) | 0.04 | 0.05 |

The controls of the cells with 500 seeds are between 0.47 and 0.54. Under leader-follow and
systematic cutting the cells at r̄ = 0.05 are within drift and those at r̄ = 0.16 are beyond it,
on the side of the profit-rate label.

- **The bias of technical change matters under cost-edge cutting only.** With overtime the
  share won is 0.57, 0.75, 0.89 and 0.96 for β = 0, 0.5, 1.5 and 3; under leader-follow it is
  0.43 to 0.48 at every β. Without draws the unit-cost label wins under both (0.99 and 0.73).
- **So does the evaluation price.** Under cost-edge cutting with overtime the share won falls
  from 0.89 to 0.71 as λ goes to 1 at r̄ = 0.05; under leader-follow it is flat.

### Why the price rule decides

- **A lower unit cost is not a higher profit rate.** Under cost-edge cutting the unit-cost
  label wins 0.98 of seeds while earning 0.079 against 0.099.
- **It wins through the price.** With cost-edge cutting the two labels post different prices
  in 0.81 of periods and the replicator moves 0.27 of the market to the unit-cost label (0.18
  with overtime). Under leader-follow every firm posts the same price in every period, and
  that term is exactly zero.
- **Nothing else carries a cost advantage.** A market share moves only through a price
  difference or through entry and exit; capacity beyond a firm's share stays idle and is
  scrapped; entrants copy a label in proportion to market shares.
- **At r̄ = 0.16 the profit-rate label wins by accumulation.** Without overtime the price never
  comes within 13 % of a unit cost, so that label earns the higher rate at every date, and its
  plants cost less per unit of capacity.
- **Not explained.** Under leader-follow without draws the unit-cost label wins 0.73, through
  entry, exit and retirements. The cause is not isolated.

### What does not matter

- **The floor.** With the operating-cost floor the runs of leader-follow are identical in 34
  to 96 % of cases, by experiment, and no verdict changes: the shortage turns the price up
  before either floor is reached.
- **The pilot.** Leader-follow with overtime is the rule of the pilot's systematic cells, and
  cost-edge cutting with overtime that of its cost-edge cells. Both are close to its headline
  (drift and 0.16–0.20 against drift and 0.10–0.19; 0.92 against 0.94–0.97).

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
| H1 | The unit-cost rule wins where the lowest-cost firm sets the price | E1 by price rule | Met under cost-edge cutting (0.92); not under leader-follow, where no firm's cost sets the price (0.50) |
| H1′ | The profit-rate rule cannot lose systematically | E1 | Fails under cost-edge cutting; holds under the other two rules |
| H2 | The advantage grows with the Marx bias | E2 by price rule | Met under cost-edge cutting (0.57 to 0.96); no effect under leader-follow |
| H3 | Where selection runs through accumulation it can favour the profit-rate rule | E3, E4 | Met at r̄ = 0.16 under leader-follow (0.08–0.20) and systematic cutting (0.03–0.12) |
| H4 | When every firm cuts, the margin, the hurdle and the conflict zone narrow and the advantage shrinks | E1, E3 by price rule | Met, and more: with overtime the hurdle falls from 0.105 to 0.068 (0.205 to 0.096 without) and the advantage vanishes, because prices are also equal across firms |
| H5 | Judged at the price of production, the hurdle falls to r̄ or just above it and the advantage shrinks | E3 | Met under cost-edge cutting at r̄ = 0.05 (0.89 → 0.71); not at r̄ = 0.16; no effect under leader-follow |
| H6 | The profit-rate adopter does not realise the rate it maximises | E1, E5 | Not met in v3: the profit-rate label realises the higher rate under every rule (0.099 against 0.079; 0.056 against 0.055) |

Not tested, as in v3: Okishio's theorem about the general rate, and the emergence of the bias
at a rising wage.

## The model

Six steps a period and one rule that differs between the types.

**Setting.** One industry in a given economy. The money wage is the numéraire and capital goods
are priced 1. Demand is exogenous, D_t = D_0(1 + g)^t, and so is the general rate r̄. A technique j
is a pair (ucs_j, κ_j): operating cost and capital per unit of normal output, with unit cost
uc_j = ucs_j + δκ_j and δ = 1/T. Plants have one technique and a normal capacity S = 20.

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
   of the firm's best plant in operation. A firm without a plant in operation keeps its price.
   One option, `pricing`, chooses among three rules.
   - *Leader-follow* (default). L is the lowest price posted last period by a firm with a
     plant in operation. After a shortage every firm posts (1 + z)L, z = 0.03. Otherwise every
     firm posts (1 − c)L, c = 0.02, or its floor if that is higher, whatever its utilisation.
     A firm that is alone with a plant in operation raises its price by z a period, up to 3
     times its floor.
   - *Cost-edge cutting.* R is the lowest price of the firm's rivals. After a shortage the
     firm moves up to the next higher rival price, or, with no rival above, raises its price
     by 0.5 times the excess-demand share. Otherwise it undercuts to (1 − c)R if it has spare
     capacity (last utilisation below 1) and a unit-cost edge over a rival posting R; else it
     follows R. Its price rises only after a shortage or to reach its floor.
   - *Systematic cutting.* The same, with spare capacity alone.
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
   off. A working plant is never replaced.
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

**Technical change.** Each period a firm with a plant in operation draws, with probability
π = 0.2, one design from its best known technique o (A = 0.05, σ = 0.8, β = 1.5). It keeps the
design if its own rule prefers it to o. A design is public 2 periods after its first plant
produces. The neutral set, the categories rule (with its two categories defined at the
evaluation price) and "no draws" are options.

**Overtime, in one place.** Utilisation is sales over normal capacity and can exceed 1. The
shortage signal, the spare-capacity test of the two cutting rules, the idle test and
depreciation by time are those of v3: only the sales limit of step 2 and the production order of
step 3 change. u_max = 1 gives v3 back.

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
| Price rule | — | leader-follow | E1 to E4: cost-edge, systematic | New default; three levels |
| Overtime limit | u_max | 1.2 | Robustness: 1 (none); Morris 1–1.4 | New |
| Rise after a shortage (leader-follow) | z | 0.03 | Morris 0.01–0.06 | New |
| Cap of a firm alone (leader-follow) | — | 3 × floor | Fixed | New |
| Price floor | — | unit cost | Robustness: operating cost | Option added |
| Price cut | c | 0.02 | Morris 0.01–0.05 | — |
| Shortage step (the two cutting rules) | — | 0.5 | Fixed | No longer in the default |
| Spare-capacity threshold (the two cutting rules) | u_full | 1 | Fixed | — |
| Bias of technical change | β | 1.5 | E2: 0, 0.5, 1.5, 3, neutral set, none; Morris 0.5–3 | — |
| Evaluation-price weight | λ | 0 | E3: 0, 0.25, 0.5, 0.75, 1 | — |
| Investment rule | — | retained earnings | E4: accelerator | Accelerator without u* |
| General rate | r̄ | 0.05 | E3 and E4: 0.16 | — |
| Demand growth | g | 0 | E4: 0.01 | — |
| Largest operating-cost cut per design | A | 0.05 | Morris 0.02–0.10 | — |
| Draw probability | π | 0.2 | Morris 0.1–0.4 | — |
| Selection intensity | χ | 1 | Morris 0.25–4 | Nearly inert under leader-follow: prices are equal |
| Payout ratio | d | 0.5 | Morris 0.25–0.75 | — |
| Plant life | T | 10 | Morris 7–19 | — |
| Plant size | S | 20 | Morris 10–40 | — |
| Entry speed | θ | 5 | Morris 1–10 | — |
| Mutation at entry | μ | 0.02 | Morris 0–0.05; 0 in E6 | — |
| Spread of the bias; lag before a design is public | σ; L | 0.8; 2 | Fixed; robustness L = none | — |
| Entry window; entrant's size; exit share; least firms; scrap periods | — | 5; 0.5; 1 %; 2; 2 | Fixed | — |
| Scrap cost | — | operating cost | Robustness: unit cost | — |
| Initial firms per pair | — | 1 | Robustness: 2 and 5 | — |
| Target utilisation | u* | — | — | Removed |

## Experiments

Each cell is a mixed population run against its two controls on the same seeds.

**E0, the gate.** Single-rule populations, no draws, 50 seeds, at the default; the same under
the two cutting rules for the sensitivity panel. Measures over periods 20 to 199. E0 holds when
each line below is true in at least 9 seeds of 10 in both populations. The thresholds on the
crossings and on the demand lost are new and proposed here; the others are v3's.

| Fact | Measure | Threshold | Default, v3 runs |
| --- | --- | --- | --- |
| The lowest-cost firm leads the price | Periods in which a firm posting the lowest price has the lowest unit cost | at least 0.9 | 1.00 |
| The price gravitates around the price of production | Mean of price over price of production; times it crosses 1 | 0.9–1.2; at least 5 | 1.07; 22 |
| Capacity follows demand | Mean of capacity over demand | 0.9–1.2 | 1.05 and 1.04 |
| The profit rate gravitates around r̄ | Industry rate at r̄ = 0.05 | 0.03–0.10 | 0.067 and 0.069 |
| Profit rates stay unequal | Mean spread of rates across firms | above 0 | 0.08 |
| Demand is served | Share of demand lost | at most 0.05 | 0.041 and 0.053 on average; 37 and 25 seeds of 50 |
| The industry survives | Seeds ending without capacity | 0 | 0 |

Not met at the default: the demand lost, which is at most 0.05 in 37 and 25 seeds of 50 where
45 are needed (it is below 0.10 in 50 and 49). The other lines hold in all 50 seeds of both
populations; the price crosses the price of production 16 to 30 times in a run. Reported beside
E0: capacity at the last period within 0.9–1.2 of demand (20 seeds of 50), and the range of
capacity within a run (0.39 to 1.73).

| # | Question | Design | Seeds | Runs |
| --- | --- | --- | --- | --- |
| E0 | Does the industry behave as under real competition? | No draws, two controls, 3 price rules | 50 | 300 |
| E1 | Which rule wins, by price rule? | Defaults, 3 price rules | 500 | 4,500 |
| E2 | Does the advantage grow with the Marx bias? | β = 0, 0.5, 1.5, 3; neutral set; none; 3 price rules | 200 | 10,800 |
| E3 | How much comes from the evaluation price? | λ (5) × price rule (3) × r̄ (0.05, 0.16) | 200 | 18,000 |
| E4 | Where does each rule win? | Price rule (3) × investment rule (2) × r̄ (2) × g (0, 1 %), then under the categories rule | 200 | 28,800 |
| E5 | Through which channel? | Decomposition of E4; regression of the profit-rate gap on the dearer orders | — | 0 |
| E6 | Can one firm of a rule invade the other? | 1 among 9, both ways, with a one-rule control; leader-follow and cost-edge | 500 | 4,000 |

About 66,400 runs: a quarter of an hour on 10 workers at v3's speed with overtime (11,200
runs in 2 min 23 s under leader-follow, 17,200 in 4 min 12 s under the cutting rules). E6
keeps v3's design: ten firms on D1, D_0 = 1,065.3, μ = 0.

## Sensitivity analysis

- **Morris screening.** The ten parameters of v3 plus z and u_max: 10 trajectories on a 4-level
  grid, 130 points × 3 populations × 100 seeds = 39,000 runs. Run once at the default and
  once under cost-edge cutting, since the headline to defend differs between them. Outcomes:
  the share won less the controls' mean, and the mean final capacity share.
- **Robustness checks.**

| Check | Cells | Seeds | v3 result |
| --- | --- | --- | --- |
| No overtime (u_max = 1) | E1 under the 3 price rules | 500 | 0.49, 0.98, 0.56: the verdicts of the runs with overtime |
| Operating-cost floor | E1 at the default | 500 | 0.49 against 0.50 |
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

**Rules as options, not patches.** The three price rules are three pure functions in
`equations/pricing_*.py`, chosen in one place by `params.pricing`; the floor by
`params.price_floor`; overtime by `params.u_max`. No experiment replaces a function of the
model.

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
the viewer on a short run.

## What the other sections of the v3 proposal need

- **Report.** Section 3 presents three price rules and overtime. Section 5.1 shows E0 on
  averages with the cycle, and the headline by price rule; 5.4 treats the price rule as the
  first condition. Figure 2 is a run of the viewer. Figure 3 gets one curve per price rule.
- **Presentation.** Slide 6 ("the unit-cost rule wins") becomes "it wins where a cost advantage
  sets the price"; slide 9 (realised rates) reports that H6 is not met; slides 10 and 11 open
  with the price rule.
- **Timeline.** The dates stand. v3 was built on 10 November, so the rebuild fits before the
  runs of 17 to 19 November.
- **Literature.** Unchanged.

## Decisions for the group

| Decision | Options | Recommendation | Why |
| --- | --- | --- | --- |
| Default price rule | Leader-follow; cost-edge cutting | Leader-follow | It is the only rule that meets E0 on capacity, price and profit rate. The cost is the headline: at the default neither rule wins |
| What E0 checks | The last period; averages over the run | Averages, with the cycle reported | Under every rule tried the industry cycles; no rule puts capacity in the band at one date in 9 seeds of 10 |
| The cycle | Accept it; look for a rule that damps it | Accept it for the report | It comes from the reserve condition, which the pilot settled; overtime halves the periods with lost demand |
| Overtime premium | None; a premium on overtime output | None | Asked by Ugo; the runs have none |
| Floor after a shortage (leader-follow) | As run: (1 + z)L even below the floor; never below the floor | As run | It happens in at most 0.01 % of periods in the cells checked; changing it would need a rerun |
| What counts in the 1,000 lines | Comments excluded; comments and docstrings excluded | Both excluded | A docstring is a comment for this purpose; to confirm |
| Morris | At the default only; also under cost-edge cutting | Both | The headline to defend is under cost-edge cutting, the default is leader-follow |
| "No draws" under leader-follow | Leave it; isolate it before the report | Isolate it | The unit-cost label wins 0.73 there and the cause is not known |
| Where version 4 is built | A clean tree beside v3; a branch of this one | A clean tree, v3 read-only beside it | As v3 did with v2: the unchanged equations are ported, not inherited |

Not run in v3, so unknown under the new default: E4, E6, Morris and the robustness checks marked
"not run". The accelerator without a target was run on E0 and on 100 seeds of the mixed
population only (the unit-cost label wins 0.44).
