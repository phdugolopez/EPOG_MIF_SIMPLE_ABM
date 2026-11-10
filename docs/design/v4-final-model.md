# ABM version 4: final model, analysis plan and build constraints

Proposal of 10 November 2026, for the group to discuss before the code is rebuilt a second time.
It replaces `final-model-proposal.md`, the addendum of `v3-planning-prompt.md` and the rows of
`v3-choices.md` as the description of the model: the rules that do not change are restated here,
so the rebuild reads one document. The sections of the v3 proposal on the literature, the report,
the presentation and the division of work stand; the changes they need are in the last section
but one.

Every number comes from version 3's code, with the settings that differ put in place from
`experiments/price_rules.py` (`v3-plan.md`, section 9). The runs are provisional, and nothing
here is a decision until the group records it.

## At a glance

- **Six changes to the model.** Overtime comes back, without a premium. The general rate is
  0.16 by default, the rate of the menu, and at any other rate the menu's capital is scaled
  so that Shaikh's table still holds at the price of 100 (not run). An entrant posts one cut below the lowest price. The
  shortage step is 0.25 instead of 0.5. The accelerator loses its target utilisation. The
  default price rule stays cost-edge cutting, and the price rule is the first treatment, with
  four levels.
- **How the default was chosen.** By two criteria set by Ugo on 10 November: a general rate
  that matches the menu, and the settings that best fit both E0 (without technical change
  the industry behaves as under real competition) and the headline (the unit-cost rule wins
  beyond drift).
- **Why 16 %.** At the initial price of 100 Shaikh's three techniques earn 16.0, 16.9 and
  15.8 %: 100 is their price of production at 16 %, not at 5 %, where it is 83 to 85.
- **At the default both hold.** E0 is met in 50 and 49 seeds of 50 in the two populations,
  and the unit-cost rule wins 0.92 of seeds (0.90–0.94), with 0.86 of final capacity.
- **Each piece is needed.** With the entrant at the lowest price, as in v3, E0 fails in every
  seed. Without overtime it holds in 26 and 27 seeds of 50. At 5 % it holds in 50 and 31, the
  headline is within drift, and no other rule tried fits both either.
- **The cost.** The mixed population is turbulent: 7 % of demand is lost, and in an average
  run capacity falls to 0.29 of demand at its lowest and the price reaches 1.9 times the
  price of production.
- **What stays true.** The advantage needs the Marx bias (0.52 without it, 0.82 to 0.93 with
  it) and is within drift when the profit-rate rule judges at the price of production (0.93
  to 0.61). Under leader-follow the profit-rate rule wins (the unit-cost rule takes 0.23).
- **Two constraints on the rebuild.** Readable code comes before the line count: at most 1,000
  lines of model code, comments excluded. And a run viewer, outside that count, runs one set of
  parameters on one seed and plots what explains the run.

## What changed from the v3 final model

| # | In v3 | In v4 | Why |
| --- | --- | --- | --- |
| 1 | No overtime: output stops at normal capacity | Output up to u_max = 1.2 times normal capacity, at the same operating cost (no premium) | Without it E0 holds in 26 and 27 seeds of 50, and 14 % of demand is lost in the mixed population |
| 2 | General rate r̄ = 0.05; 0.16 as the other level | r̄ = 0.16; 0.05 as the other level | The menu earns 16 % at its initial price. At 5 % no rule fits both E0 and the headline |
| 3 | An entrant posts the lowest price | It posts c below the lowest price, down to the unit cost of its own plants | It is what brings the price down when no incumbent has a cost edge: without it the price never crosses the price of production and E0 fails in every seed |
| 4 | Accelerator: desired capacity = the demand addressed to the firm over a target utilisation u* = 0.9 | Desired capacity = the demand addressed to the firm; no target | The target was the buffer of a model without overtime |
| 5 | Two price regimes; systematic cutting stood for leader-follow | Four price rules: cost-edge cutting (still the default), normal-price cutting, leader-follow, systematic cutting | The winner depends on the rule, so the rule is a treatment. v3's systematic cutting is not leader-follow |
| 6 | Leader-follow's own shortage rule and monopoly cap dropped for the common shortage step | Restored, for the leader-follow option only: 3 % above the lowest price after a shortage; a firm alone stops at 3 times its floor | They are part of that rule as the group's notebook and v2 have it |
| 7 | One floor: unit cost | The same by default; the operating-cost floor as a robustness option | In the v3 runs it moved no share won by more than 0.06 and no verdict |
| 8 | E0 read at the last period (capacity within a band in 9 seeds of 10); a profit rate between 0.03 and 0.10 | E0 read on averages over the run, from period 20, with two new lines (the price crosses the price of production; at most 10 % of demand is lost); a profit rate between 0.6 and 2 times r̄ | A cycle cannot meet a band at one date; the band on the rate is the same one, stated for any r̄ |
| 9 | E1 to E4 at the default rule; pricing varied in E3 and E4 only | The price rule crossed with E0 to E4 | The winner and the size of every effect depend on it |
| 10 | Robustness: u* = 0.8 and 0.95 | Dropped. Added: no overtime, the entrant at the lowest price, the operating-cost floor | u* no longer exists |
| 11 | Model code at most 770 lines, blank lines excluded | At most 1,000 lines, comments excluded; readability first | Section "Rebuilding the code" |
| 12 | Figure 2 from period tables kept by the harness | A run viewer for any parameters and seed | Every diagnosis of v3 needed a trace of one run |
| 13 | The depreciation reserve is released when r_new ≥ r̄; no other rule in the model | The same by default; an option with two other levels (always released, never released) for a sensitivity check | The reserve sets the profit rate: 6 % when always released, 20 % when never released, against 13 % |
| 14 | After a shortage a firm with no rival above raises its price by 0.5 times the excess-demand share | By 0.25 times that share | It halves the price peaks of the mixed population (1.9 against 3.7 times the price of production) and keeps E0 and the headline |
| 15 | One menu at every r̄: Shaikh's (ucs, κ) | Capital scaled by 0.16 / r̄, operating cost = unit cost − δκ; unit costs (78, 76, 75) and the price of 100 kept | At 0.05 the fixed menu starts 18 % above the price of production and the two rules agree on D2 at that price. Scaled, the table holds at any r̄. Not run |

Not changed: the one rule that differs between the types, the replicator, the
default price rule, scrapping, the default rule of the depreciation reserve, technical change,
exit, the winner, the populations and controls, and the rules of neutrality.

## What the v3 experiments showed

The runs of this section have the settings of version 4 unless a row says otherwise: overtime,
r̄ = 0.16, the undercutting entrant and a shortage step of 0.25.

### E0 and the headline, rule by rule

E0: single-rule populations without technical change, 50 seeds, measures from period 20; each
cell gives the all-unit-cost and the all-profit-rate population. A seed passes when every line
of E0 (section "Experiments") is true in it. The headline is the share of seeds won by the
unit-cost label in the mixed population at the defaults, on 500 seeds.

| Rule | Seeds of 50 that pass E0 | Capacity over demand, mean (range within a run) | Price over the price of production | Times it crosses 1 | Profit rate | Demand lost | Share won | Final capacity share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cost-edge cutting (default) | 50 / 49 | 1.08 (0.70–1.39) / 1.09 (0.70–1.43) | 0.99 / 0.99 | 25 / 24 | 0.132 / 0.130 | 0.002 / 0.003 | 0.92 (0.90–0.94) | 0.86 |
| Normal-price cutting | 50 / 50 | 1.07 (0.71–1.34) / 1.07 (0.70–1.35) | 0.98 / 0.99 | 26 / 27 | 0.133 / 0.133 | 0.002 / 0.003 | 0.92 (0.89–0.94) | 0.86 |
| Systematic cutting | 2 / 0 | 0.91 (0.10–2.16) / 0.90 (0.15–2.00) | 1.11 / 1.05 | 21 / 24 | 0.185 / 0.172 | 0.144 / 0.118 | 0.76 (0.72–0.80) | 0.75 |
| Leader-follow | 46 / 44 | 0.93 (0.33–1.30) / 0.92 (0.29–1.31) | 0.95 / 0.96 | 22 / 23 | 0.132 / 0.132 | 0.061 / 0.069 | 0.23 (0.19–0.27) | 0.45 |

Every share won is beyond drift (controls between 0.46 and 0.51); under leader-follow it is the
profit-rate label that wins.

- **Entry brings the price down, the cost leader takes it further.** While new plants earn
  more than r̄ an entrant arrives and posts one cut below the lowest price, and the incumbents
  follow. So the price falls to the price of production even when no incumbent has a cost
  edge, and crosses it 24 to 25 times in a run. Among incumbents only a cost leader cuts.
- **The unit-cost label wins through the price and through entry and exit.** The replicator
  moves 0.21 of the market to it and entry and exit another 0.16. The two labels realise
  about the same profit rate, 0.148 and 0.151.
- **Normal-price cutting gives the same industry.** It lets a firm without a cost edge cut
  while the price is above its own price of production; with the undercutting entrant that
  adds little.
- **Under leader-follow every firm posts the same price**, the price moves no market share,
  and the profit-rate label accumulates faster.

### What each setting does

The default with one setting changed. E0 on 50 seeds; share won on 100 seeds of the mixed
population, except the first row.

| Setting changed | Seeds of 50 that pass E0 | Share won | Demand lost in the mixed population |
| --- | --- | --- | --- |
| None (the default) | 50 / 49 | 0.92 (500 seeds) | 0.069 |
| The entrant posts the lowest price (v3) | 0 / 0 | 0.94 | 0.011 |
| No overtime | 26 / 27 | 0.78 | 0.143 |
| r̄ = 0.05 | 50 / 31 | 0.51, within drift | 0.176 |
| Shortage step 0.5 (v3) | 50 / 50 | 0.91 | 0.074 |
| Accelerator | 44 / 48 | 0.56, within drift | 0.029 |
| Demand growing by 1 % a period | 48 / 49 | 0.97 | 0.045 |

- **The mixed population is turbulent.** In an average run capacity moves between 0.29 and
  1.49 times demand and the price reaches 1.9 times the price of production. A price war
  between cost leaders runs from the price of production down to the followers' unit cost, a
  quarter lower at 16 %, and for as long as it lasts no plant that retires is replaced.
- **The accelerator is calmer and loses the headline.** It loses 3 % of demand and the price
  peaks at 1.5 times the price of production, but the unit-cost label wins 0.56, within
  drift. With a shortage step of 0.5 it won 0.84 there.
- **With the step of 0.5 of v3 the price peaks at 3.7 times the price of production**; E0
  and the headline are the same.

### Why not 5 %

At r̄ = 0.05 and with the entrant at the lowest price, fifteen price rules were scored (share
won on 500 seeds unless marked):

| What lets firms without a cost edge cut | Seeds of 50 that pass E0 | Share won |
| --- | --- | --- |
| Nothing (cost-edge cutting) | 0 / 0 | 0.92 |
| A price above the firm's price of production (normal-price cutting) | 43 / 12 | 0.67 |
| The same, with leader-follow's rise of 3 % after a shortage | 50 / 50 | 0.51 (100 seeds) |
| Every firm cuts (leader-follow) | 50 / 49 | 0.50 |
| The undercutting entrant | 48 / 5 | 0.68 (100 seeds); a quarter of demand lost |

- **At 5 % the two targets pull apart.** The headline needs the cost leader to cut alone; E0
  needs someone to cut when no firm has a cost edge; each way of allowing the second weakens
  the first.
- **At 5 % the price of production is 10 % above the unit cost; at 16 % it is a third above.**
  A price near the price of production then stays in the conflict zone of the menu, above
  85, so the two rules keep choosing differently: the hurdle of the profit-rate label is
  0.17 at the default, against 0.10 at 5 %.

### What holds at the default

Mixed population, 500 seeds at the defaults and 200 in the other cells.

| Measure | Cost-edge (default) | Normal-price | Systematic | Leader-follow |
| --- | --- | --- | --- | --- |
| Share won for β = 0, 0.5, 1.5, 3 | 0.52, 0.88, 0.93, 0.82 | 0.55, 0.91, 0.94, 0.88 | 0.39, 0.77, 0.78, 0.60 | 0.50, 0.36, 0.21, 0.17 |
| Share won with the neutral set; without draws | 0.66; 0.98 | 0.66; 0.97 | 0.59; 0.72 | 0.52; 0.39 |
| Share won for λ = 0, 0.25, 0.5, 0.75, 1 | 0.93, 0.86, 0.83, 0.62, 0.61 | not run | not run | not run |
| The same at r̄ = 0.05 | 0.57, 0.61, 0.51, 0.52, 0.49 | not run | not run | not run |
| Change in sales share through the price | +0.21 | +0.21 | +0.05 | 0.00 |
| Hurdle of the profit-rate label; its orders that are not the cheapest | 0.170; 0.80 | 0.171; 0.80 | 0.171; 0.79 | 0.142; 0.75 |
| Realised profit rate, unit-cost / profit-rate label | 0.148 / 0.151 | 0.149 / 0.152 | 0.164 / 0.156 | 0.133 / 0.135 |
| Price over the price of production; demand lost | 0.97; 0.069 | 0.98; 0.073 | 1.02; 0.111 | 0.93; 0.032 |

- **The advantage needs the Marx bias and does not grow with it.** At β = 0 the contest is at
  drift; from β = 0.5 the unit-cost label wins 0.82 to 0.93, and least at β = 3. With the
  neutral set it wins 0.66, within drift.
- **The evaluation price carries it.** Judged at the price of production the profit-rate rule
  is within drift from λ = 0.75 (0.62 and 0.61). Its hurdle hardly moves, from 0.170 to
  0.183: the market price is already near the price of production.
- **Under leader-follow the bias works for the profit-rate label**: the unit-cost label wins
  0.50, 0.36, 0.21 and 0.17 as β rises.
- **At r̄ = 0.05 nothing is beyond drift** and 17 to 23 % of demand is lost: with the
  undercutting entrant that level of the rate does not give a working industry.

### Against the pilot

The pilot's cells at r̄ = 0.16 are v2 with overtime and the entrant at the lowest price. Its
cost-edge cells give 0.94–0.97 with 0.72–0.79 of final capacity; the default gives 0.92 with
0.86. Its leader-follow cells give 0.10–0.19; leader-follow gives 0.23 here. Its industry rate
is 0.14–0.15; here 0.15 at the default and 0.13 under leader-follow.

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
| H1 | The unit-cost rule wins where the lowest-cost firm sets the price | E1 by price rule | Met: 0.92 at the default, 0.92 and 0.76 under the two other cutting rules; under leader-follow, where no firm's cost sets the price, it loses (0.23) |
| H1′ | The profit-rate rule cannot lose systematically | E1 | Fails under the three cutting rules; holds under leader-follow |
| H2 | The advantage grows with the Marx bias | E2 by price rule | Partly: it needs the bias (0.52 at β = 0, 0.88 at 0.5) but does not grow with it (0.93 at 1.5, 0.82 at 3) |
| H3 | Where selection runs through accumulation it can favour the profit-rate rule | E1, E4, reserve | Met under leader-follow (0.23); with the reserve never released the default goes to drift (0.42) |
| H4 | The more firms cut, the smaller the advantage | E1 by price rule | Met: 0.92, 0.76 and 0.23 from cost-edge to systematic cutting to leader-follow |
| H5 | Judged at the price of production, the hurdle falls to r̄ or just above it and the advantage shrinks | E3 | Met as to the outcome: 0.93 → 0.61, within drift from λ = 0.75. The hurdle itself hardly moves (0.170 to 0.183), since the price is already near the price of production |
| H6 | The profit-rate adopter does not realise the rate it maximises | E1, E5 | Not met: the two labels realise about the same rate (0.151 and 0.148). It was met with a shortage step of 0.5 (0.172 against 0.183) and not met in the v3 runs at 5 % |

Not tested, as in v3: Okishio's theorem about the general rate, and the emergence of the bias
at a rising wage.

## The model

Six steps a period and one rule that differs between the types.

**Setting.** One industry in a given economy. The money wage is the numéraire and capital goods
are priced 1. Demand is exogenous, D_t = D_0(1 + g)^t, and so is the general rate r̄ = 0.16. A
technique j is a pair (ucs_j, κ_j): operating cost and capital per unit of normal output, with
unit cost uc_j = ucs_j + δκ_j and δ = 1/T. Its price of production is uc_j + r̄κ_j. Plants have
one technique and a normal capacity S = 20.

**Initial industry.** Shaikh's three techniques (2016, Tables 7.10–7.11), with their capital
scaled to the general rate, so that his table holds at any r̄. The unit costs and the initial
price do not move: 78, 76 and 75 for C, D1 and D2, and every price is 100. Capital and operating
cost follow r̄:

```latex
\kappa_j(\bar r) = \kappa^{S}_j\,\frac{0.16}{\bar r}, \qquad ucs_j(\bar r) = uc_j - \delta\,\kappa_j(\bar r), \qquad \big(\kappa^{S}_{C},\ \kappa^{S}_{D1},\ \kappa^{S}_{D2}\big) = (137.50,\ 142.31,\ 157.89)
```

| r̄ | C (ucs, κ) | D1 (ucs, κ) | D2 (ucs, κ) | Cost of a plant of C |
| --- | --- | --- | --- | --- |
| 0.16 (default; Shaikh's table) | (64.25, 137.50) | (61.77, 142.31) | (59.21, 157.89) | 2,750 |
| 0.10 | (56.00, 220.00) | (53.23, 227.70) | (49.74, 252.62) | 4,400 |
| 0.05 | (34.00, 440.00) | (30.46, 455.39) | (24.48, 505.25) | 8,800 |

- **The same at every r̄.** The prices of production are 100.0, 98.8 and 100.3. At the price
  of 100 the three techniques earn r̄, 1.054 r̄ and 0.990 r̄: C earns the general rate, D1 has
  a lower cost and a higher rate, D2 the lowest cost and a lower rate than C. The two rules
  part on D2 when the hurdle is above 0.92 r̄.
- **Limit.** r̄ must be above 0.034, where the operating cost of D2 reaches zero. The code
  refuses a lower rate.
- **What moves with r̄.** A plant costs 0.16 / r̄ times as much, and depreciation is 18 % of
  the unit cost of C at 0.16 and 56 % at 0.05. A design drawn from C is then kept by the
  unit-cost rule if k < 0.77 at r̄ = 0.05 (20 % of draws at β = 1.5), against k < 4.67 at 0.16
  (92 %). β is not rescaled here: see "Decisions for the group".
- **Not run.** Every number of this document at r̄ = 0.05 comes from the fixed menu of v3,
  the row of 0.16 used at every rate.

Each technique is given to one unit-cost and one profit-rate firm. Six firms, identical within
pairs, with 6, 6 and 7 plants: capacity 760 against D_0 = 674.7. Every share is the capacity
share. Plant k of a firm's n plants has age floor(kT/n), so retirements spread over the first T
periods. A firm's cash is the depreciation already accumulated on its plants, which backs the
reserves they release.

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
   moves up to the next higher rival price, or, with no rival above, raises its price by
   0.25 times the excess-demand share; otherwise it undercuts to (1 − c)P, c = 0.02, when the rule
   entitles it to, and else follows P. Its price rises only after a shortage or to reach its
   floor.
   - *Cost-edge cutting* (default). A firm is entitled to cut with spare capacity (last
     utilisation below 1) and a unit-cost edge over a rival posting P.
   - *Normal-price cutting.* While P is above the firm's own price of production, that of its
     best plant, spare capacity is enough; at or below it, the firm also needs the cost edge.
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
   drawn by market share and flipped with probability μ = 0.02. Its technique is chosen by
   its own rule on the public menu at the lowest posted price. It posts (1 − c) times that
   price, or the unit cost of its plants if that is higher. Its capacity is 0.5 times the
   survivors' mean capacity, in whole plants, paid by equity from the rest of the economy and
   delivered next period; its share is its capacity over next period's capacity, and the
   incumbents' shares are scaled down.

```latex
f_{i,t} = f_{i,t-1}\Big[1 + \chi\,\frac{E_{i,t} - \bar E_t}{\bar E_t}\Big], \qquad \bar E_t = \sum_j f_{j,t-1}\,E_{j,t}, \qquad E_{i,t} = 1/p_{i,t}
```

```latex
ucs_n = (1-a)\,ucs_o, \quad \kappa_n = (1+k\,a)\,\kappa_o, \quad a \sim U(0, A], \quad k = \beta\, e^{\sigma z},\ z \sim N(0,1)
```

```latex
\Pr(\text{entry}_t) = \min\Big\{1,\ \theta\,\frac{\max(0,\ r^{new}_t - \bar r)}{\bar r}\Big\}
```

**Pricing and entry in one sentence.** New capital enters while new plants earn more than the
general rate and undercuts to make room, which brings the price down to the price of
production; among the firms in place only a cost leader cuts, down to its rivals' unit cost.

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
| General rate | r̄ | 0.16 | E3 and E4: 0.05 | Was 0.05 |
| Price rule | — | cost-edge cutting | E0 to E2: normal-price, systematic, leader-follow; E3 and E4: systematic, leader-follow | Four levels |
| Entrant's price | — | (1 − c) × the lowest price | Robustness: the lowest price | New |
| Overtime limit | u_max | 1.2 | Robustness: 1 (none); Morris 1–1.4 | New |
| Price cut | c | 0.02 | Morris 0.01–0.05 | Also the entrant's |
| Shortage step (the three cutting rules) | — | 0.25 | Morris 0.1–0.5 | Was 0.5; now screened |
| Spare-capacity threshold (the three cutting rules) | u_full | 1 | Fixed | — |
| Rise after a shortage; cap of a firm alone (leader-follow) | z; — | 0.03; 3 × floor | Fixed | New, for that option |
| Price floor | — | unit cost | Robustness: operating cost | Option added |
| Bias of technical change | β | 1.5 | E2: 0, 0.5, 1.5, 3, neutral set, none; Morris 0.5–3 | — |
| Evaluation-price weight | λ | 0 | E3: 0, 0.25, 0.5, 0.75, 1 | — |
| Investment rule | — | retained earnings | E4: accelerator | Accelerator without u* |
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
| Initial menu | — | Shaikh's table with κ × 0.16 / r̄ | Robustness: the fixed menu of v3 | New |
| Target utilisation | u* | — | — | Removed |

## Experiments

Each cell is a mixed population run against its two controls on the same seeds.

**E0, the gate.** Single-rule populations, no draws, 50 seeds, under each price rule. Measures
over periods 20 to 199. E0 holds when each line below is true in at least 9 seeds of 10 in both
populations. Two lines are new. The threshold on the crossings is proposed here. The ceiling on
the demand lost was set at 0.10 by Ugo on 10 November, after the runs; 0.05 was proposed first.

| Fact | Measure | Threshold | Default, v3 runs: mean; seeds of 50 that pass |
| --- | --- | --- | --- |
| The lowest-cost firm leads the price | Periods in which a firm posting the lowest price has the lowest unit cost | at least 0.9 | 1.00 and 1.00; 50 and 50 |
| The price gravitates around the price of production | Mean of price over price of production | 0.9–1.2 | 0.99 and 0.99; 50 and 50 |
| | Times it crosses 1 | at least 5 | 25 and 24; 50 and 50 |
| Capacity follows demand | Mean of capacity over demand | 0.9–1.2 | 1.08 and 1.09; 50 and 49 |
| The profit rate gravitates around r̄ | Industry rate | 0.6 to 2 times r̄ | 0.132 and 0.130; 50 and 50 |
| Profit rates stay unequal | Mean spread of rates across firms | above 0 | 0.12 and 0.12; 50 and 50 |
| Demand is served | Share of demand lost | at most 0.10 | 0.002 and 0.003; 50 and 50 |
| The industry survives | Capacity at the last period | above 0 | 50 and 50 |

E0 is met at the default (50 and 49 seeds of 50) and under normal-price cutting (50 and 50). It
is one seed short under leader-follow (46 and 44, where 45 are needed) and fails under
systematic cutting. Reported beside E0, and not part of it: capacity at the last period within
0.9–1.2 of demand (34 and 37 seeds of 50 at the default), and the range of capacity within a
run (0.70 to 1.39 and 0.70 to 1.43).

| # | Question | Design | Seeds | Runs |
| --- | --- | --- | --- | --- |
| E0 | Does the industry behave as under real competition? | No draws, two controls, 4 price rules | 50 | 400 |
| E1 | Which rule wins, by price rule? | Defaults, 4 price rules | 500 | 6,000 |
| E2 | Does the advantage need the Marx bias, and grow with it? | β = 0, 0.5, 1.5, 3; neutral set; none; 4 price rules | 200 | 14,400 |
| E3 | How much comes from the evaluation price? | λ (5) × price rule (3) × r̄ (0.16, 0.05) | 200 | 18,000 |
| E4 | Where does each rule win? | Price rule (3) × investment rule (2) × r̄ (2) × g (0, 1 %), then under the categories rule | 200 | 28,800 |
| E5 | Through which channel? | Decomposition of E4; regression of the profit-rate gap on the dearer orders | — | 0 |
| E6 | Can one firm of a rule invade the other? | 1 among 9, both ways, with a one-rule control; the default and leader-follow | 500 | 4,000 |

The three price rules of E3 and E4 are the default, systematic cutting and leader-follow. About
71,600 runs: a quarter of an hour on 10 workers at v3's speed with these settings (11,200 runs
in 2 min 27 s at the default). E6 keeps v3's design: ten firms on D1, D_0 = 1,065.3, μ = 0.

## Sensitivity analysis

- **Morris screening.** The ten parameters of v3 plus u_max and the shortage step: 10
  trajectories on a 4-level grid, 130 points × 3 populations × 100 seeds = 39,000 runs, at
  the default. Outcomes: the share won less the controls' mean, the mean final capacity
  share, the share of demand lost and the share of E0's lines that hold.
- **Sensitivity over the reserve** (asked by Ugo, 10 November). The rule of the depreciation
  reserve gets three levels: released if r_new ≥ r̄ (default), always released, never
  released. These are arms 4, 2 and 1 of the v2 pilot. Cells: E0 and E1 at each of the two
  other levels, at the default and under leader-follow: 6,400 runs. A first look at the
  default (E0 on 50 seeds, all-unit-cost population, from period 20; share won on 100 seeds
  of the mixed population):

| Reserve | Seeds of 50 that pass E0 | Capacity over demand, mean (range within a run) | Price over the price of production | Profit rate | Demand lost | Share won |
| --- | --- | --- | --- | --- | --- | --- |
| Released if r_new ≥ r̄ | 50 / 49 | 1.08 (0.70–1.39) | 0.99 | 0.132 | 0.002 | 0.93 |
| Always released | 0 / 0 | 1.51 (1.48–1.60) | 0.96 | 0.056 | 0.000 | 0.80 |
| Never released | 50 / 35 | 0.96 (0.44–1.43) | 1.08 | 0.195 | 0.052 | 0.42, within drift |

  - **The reserve sets the profit rate.** Always released, the rate falls to 6 %, a third of
    r̄, capacity settles at 1.5 times demand and entry stops. Never released, it is 20 %.
  - **The condition makes the cycle and the gravitation.** With the reserve always released
    the price stays 4 % below the price of production and never crosses it.
  - **The headline needs a reserve.** Always released, the unit-cost label still wins (0.80);
    never released, the contest is at drift.

- **Robustness checks.**

| Check | Cells | Seeds | v3 result |
| --- | --- | --- | --- |
| No overtime (u_max = 1) | E0 and E1 under the 4 price rules | 500 | At the default, 100 seeds: 0.78, and E0 holds in 26 and 27 seeds of 50 |
| The entrant at the lowest price | E0 and E1 at the default | 500 | 100 seeds: 0.94, and E0 holds in no seed |
| Operating-cost floor | E1 at the default and under leader-follow | 500 | Not run with these settings |
| Scrapping on unit cost | E1 and the marx cells of E4 | 200 | Not run with these settings |
| Private diffusion (L = none) | E1 | 200 | Not run |
| Homogeneous start (six firms on D1) | The 6 cells of E2 | 200 | Not run |
| 12 and 30 firms | E1 and the 4 cells of E4 with g = 0.01 | 200 | Not run |
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
`params.price_floor`; overtime by `params.u_max`; the entrant's price by `params.entry_cut`;
the reserve by `params.reserve`. No experiment replaces a function of the model.

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
python -m experiments.show_run --seed 7 pricing=leader_follow rbar=0.05 population=all_unit_cost
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
u_max = 1 gives the run without overtime); each price rule; the entrant's price; the
accelerator without a target; the three levels of the reserve; the viewer on a short run.

## What the other sections of the v3 proposal need

- **Report.** Section 3 presents four price rules, overtime and the undercutting entrant, at
  r̄ = 0.16. Section 5.1 shows E0 on averages with the cycle and the headline by price rule;
  5.4 treats the price rule as the first condition. Figure 2 is a run of the viewer. Figure 3
  gets one curve per price rule.
- **Presentation.** Slide 6 keeps "the unit-cost rule wins" and adds "where a cost leader sets
  the price"; slide 9 (realised rates) reports that the two labels realise the same rate;
  slides 10 and 11 open with the price rule.
- **Timeline.** The dates stand. v3 was built on 10 November, so the rebuild fits before the
  runs of 17 to 19 November.
- **Literature.** Unchanged.

## Decisions for the group

| Decision | Options | Recommendation | Why |
| --- | --- | --- | --- |
| Default general rate | 0.05; 0.16 | **Set by Ugo, 10 Nov:** 0.16 | The menu earns it at its initial price |
| Default price rule and entry | Cost-edge cutting with the undercutting entrant; normal-price cutting with it; the v3 entrant | **Set by Ugo's criterion, 10 Nov:** cost-edge cutting with the undercutting entrant | It meets E0 and gives the headline (0.92). Normal-price cutting does the same (0.92) with one more clause |
| The other level of r̄ | 0.05; an intermediate level such as 0.10 | Try 0.10 before fixing it | At 0.05 a sixth of demand is lost, E0 holds in 31 seeds of 50 in one population and nothing is beyond drift. 0.10 is not run |
| Shortage step | 0.5; 0.25 | **Decided by Ugo, 10 Nov:** 0.25 | It halves the price peaks (1.9 against 3.7 times the price of production) with the same E0 and headline. The demand lost stays at 7 %, and under the accelerator the headline falls to drift (0.56 against 0.84) |
| What E0 checks | The last period; averages over the run | Averages, with the cycle reported | Capacity at the last period is in the band in 34 and 37 seeds of 50 |
| Ceiling on the demand lost in E0 | 5 %; 10 % | **Decided by Ugo, 10 Nov:** 10 % | Set after the runs, which the report should say. At the default less than 1 % is lost in E0 |
| Overtime premium | None; a premium on overtime output | None | Asked by Ugo; the runs have none |
| What counts in the 1,000 lines | Comments excluded; comments and docstrings excluded | Both excluded | A docstring is a comment for this purpose; to confirm |
| Initial menu at r̄ ≠ 0.16 | The fixed menu of v3; capital scaled by 0.16 / r̄ at the price of 100; margins scaled by r̄ / 0.16 at the price of production of C | **Asked by Ugo, 10 Nov:** capital scaled, price kept at 100 | Shaikh's table holds at any r̄. Not run: the results at 0.05 must be redone |
| β at r̄ ≠ 0.16, under the scaled menu | Keep 1.5; rescale it so that the same share of designs is kept | To decide after a first run at 0.05 | With β = 1.5 the unit-cost rule keeps 20 % of the designs drawn from C at 0.05, against 92 % at 0.16: technical change slows, and the two rates are no longer compared on the same bias |
| Where version 4 is built | A clean tree beside v3; a branch of this one | A clean tree, v3 read-only beside it | As v3 did with v2: the unchanged equations are ported, not inherited |

Not run with these settings: E3 under the three other price rules, E4, E6, Morris and the
robustness checks marked "not run". The reserve, the accelerator, the shortage step of 0.5,
growth and the two robustness checks with a result were looked at on 50 seeds of E0 and 100
seeds of the mixed population only.
