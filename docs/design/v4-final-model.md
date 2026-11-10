# ABM version 4: final model, analysis plan and build constraints

Proposal of 10 November 2026, for the group to discuss before the code is rebuilt a second time.
It replaces `final-model-proposal.md` and the addendum of `v3-planning-prompt.md` as the
description of the model: the rules that do not change are restated here. Where this document
is silent the rows of `v3-choices.md` hold; `v4-choices.md` lists them under "Kept from v3".
The sections of the v3 proposal on the literature, the report,
the presentation and the division of work stand; the changes they need are in the last section
but one.

Every number comes from version 3's code, with the settings that differ put in place from
`experiments/price_rules.py` (`v3-plan.md`, section 9). The runs are provisional, and nothing
here is a decision until the group records it.

Corrected on 10 November after the coherence review (`v4-review.md`); the decisions taken on
it are in `v4-choices.md`. Three marks are used below. "Fixed menu": a run at r̄ = 0.05 made
on Shaikh's menu as it is, not on the scaled menu of version 4. "100 seeds": a share won from
a script that is not in the tree. "Not run": no run with these settings. The first runs of
version 4 redo all three.

## At a glance

- **Seven changes to the model and three options added.** Overtime comes back, without a
  premium. The general rate is 0.16 by default, the rate of Shaikh's table. At any other rate
  the menu's capital is scaled so that the table still holds at the price of 100 (not run).
  An entrant posts one cut below the lowest price. The shortage step is 0.25 instead of 0.5.
  The accelerator loses its target utilisation. The price rule is the first treatment, with
  four levels, and cost-edge cutting stays the default. The options: the operating-cost
  floor, two other rules of the depreciation reserve, the entrant's label
  copied from an incumbent drawn evenly.
- **How the default was chosen.** By two criteria set by Ugo on 10 November: a general rate
  that matches the menu, and the settings that best fit both E0 (without technical change
  the industry behaves as under real competition) and the headline (the unit-cost rule wins
  beyond drift).
- **Why 16 %.** It is the rate of Shaikh's table: at the initial price of 100 his three
  techniques earn 16.0, 16.9 and 15.8 %. It is also the rate of every run behind this
  document. On the scaled menu 100 is the price of production at any rate, so another rate
  is tested first, on the new code, before it enters an experiment.
- **At the default both hold.** E0 is met in 50 and 49 seeds of 50 in the two populations,
  and the unit-cost rule wins 0.92 of seeds (0.90–0.94), with 0.86 of final capacity.
- **Each piece is needed.** With the entrant at the lowest price, as in v3, E0 fails in every
  seed. Without overtime it holds in 26 and 27 seeds of 50. At 5 % on the fixed menu it holds in
  50 and 31 and the headline is within drift; the scaled menu is not run.
- **The cost.** The mixed population is turbulent: 7 % of demand is lost, and in an average
  run capacity falls to 0.29 of demand at its lowest and the price reaches 1.9 times the
  price of production. These sizes are the model's own: the sources give none.
- **What stays true.** The advantage needs techniques on which the two rules disagree:
  biased draws (0.52 at β = 0, 0.82 to 0.93 from β = 0.5) or the initial menu when no draw
  replaces it (0.98 without draws). It is within drift when the profit-rate rule judges at
  the price of production (0.93 to 0.61). Under universal undercutting the profit-rate rule
  wins (the
  unit-cost rule takes 0.23).
- **What is not settled.** Under the accelerator the headline is within drift (0.56, 100
  seeds). The sign of the gap in realised rates turns with the shortage step. With draws the
  firm posting the lowest price is the cost leader in two periods of three. The scaled menu
  is not run away from 0.16.
- **Two constraints on the rebuild.** Readable code comes before the line count: at most 1,000
  lines of model code, comments and docstrings excluded. And a run viewer, outside that count,
  runs one set of
  parameters on one seed and plots what explains the run.

## What changed from the v3 final model

Rows 1 to 6, 14 and 15 change a rule or a default: seven changes, rows 5 and 6 being one. Rows
7, 13 and 16 add an option. Rows 8 to 10 concern the experiments, rows 11 and 12 the build.

| # | In v3 | In v4 | Why |
| --- | --- | --- | --- |
| 1 | No overtime: output stops at normal capacity | Output up to u_max = 1.2 times normal capacity, at the same operating cost (no premium) | Without it E0 holds in 26 and 27 seeds of 50, and 14 % of demand is lost in the mixed population |
| 2 | General rate r̄ = 0.05; 0.16 as the other level, crossed with E3 and E4 | r̄ = 0.16. Other levels (0.10, then 0.05) are tested first on the scaled menu. One stays in E4 if it meets E0; none in E3 | 0.16 is the rate of Shaikh's table. On the fixed menu at 5 % no rule fitted both E0 and the headline. On the scaled menu the rules rank the initial techniques alike at every rate, so λ crossed with r̄ has lost its reason |
| 3 | An entrant posts the lowest price | It posts c below the lowest price, down to the unit cost of its own plants | It is what brings the price down when no incumbent has a cost edge: without it the price never crosses the price of production and E0 fails in every seed |
| 4 | Accelerator: desired capacity = the demand addressed to the firm over a target utilisation u* = 0.9 | Desired capacity = the demand addressed to the firm; no target | The target was the buffer of a model without overtime |
| 5 | Two price regimes; systematic cutting stood for v2's leader-follow | Four price rules: cost-edge cutting (still the default), normal-price cutting, universal undercutting (leader-follow in v2 and the notebook), systematic cutting | The winner depends on the rule, so the rule is a treatment. v3's systematic cutting is not that rule. It is renamed because every firm cuts whatever its cost: in Shaikh and in Hall and Hitch the followers match the leader's cut, which is cost-edge cutting |
| 6 | The shortage rule and the monopoly cap of v2's leader-follow dropped for the common shortage step | Restored, for universal undercutting only: 3 % above the lowest price after a shortage; a firm alone stops at 3 times its floor; the floor applies to a cut only | They are part of that rule as the group's notebook and v2 have it |
| 7 | One floor: unit cost | The same by default; the operating-cost floor as a robustness option | Under leader-follow at r̄ = 0.05 with the entrant at the lowest price it moved no share won by more than 0.06 and no verdict. Not run under a cutting rule, nor with these settings |
| 8 | E0 read at the last period (capacity within a band in 9 seeds of 10); a profit rate between 0.03 and 0.10 | E0 read on averages over periods 20 to 199 and counted by seed, with two new lines (the price crosses the price of production; at most 10 % of demand is lost); the rate of new plants between 0.6 and 2 times r̄; the spread of rates reported, not counted | A cycle cannot meet a band at one date. The band on the rate is the same one, stated for any r̄, and read on the rate that is equalised |
| 9 | E1 to E4 at the default rule; pricing varied in E3 and E4 only | The four price rules crossed with E0 to E2; three of them, without normal-price cutting, with E3 and E4 | The winner and the size of every effect depend on it |
| 10 | Robustness: u* = 0.8 and 0.95 | Dropped. Added: no overtime, the entrant at the lowest price, the operating-cost floor, a shortage step of 0.5, the entrant's parent drawn evenly, the fixed menu | u* no longer exists |
| 11 | Model code at most 770 lines, blank lines excluded | At most 1,000 lines, comments and docstrings excluded; readability first | Section "Rebuilding the code" |
| 12 | Figure 2 from period tables kept by the harness | A run viewer for any parameters and seed | Every diagnosis of v3 needed a trace of one run |
| 13 | The depreciation reserve is released when r_new ≥ r̄; no other rule in the model | The same by default; an option with two other levels (always released, never released) for a sensitivity check | The reserve sets the profit rate: 6 % when always released, 20 % when never released, against 13 % |
| 14 | After a shortage a firm with no rival above raises its price by 0.5 times the excess-demand share | By 0.25 times that share | It halves the price peaks of the mixed population (1.9 against 3.7 times the price of production) and keeps E0 and the headline |
| 15 | One menu at every r̄: Shaikh's (ucs, κ) | Capital scaled by 0.16 / r̄ and the operating cost lowered by the depreciation added, so the unit costs (78, 76, 75) and the price of 100 are kept | At 0.05 the fixed menu starts 18 % above the price of production and the two rules agree on D2 at that price. Scaled, the table holds at any r̄. Not run |
| 16 | An entrant's label is copied from an incumbent drawn by market share | The same by default; an option draws the incumbent evenly, one vote a firm, for a robustness check | Through entry and exit 0.16 of the market moves to the unit-cost label, against 0.21 through the price |

Not changed: the one rule that differs between the types, the replicator, the
default price rule, scrapping, the default rule of the depreciation reserve, technical change,
exit, the winner, the populations and controls, and the rules of neutrality.

## What the v3 experiments showed

The runs of this section have the settings of version 4 unless a row says otherwise: overtime,
r̄ = 0.16, the undercutting entrant and a shortage step of 0.25. Every run at r̄ = 0.05 is on
the fixed menu. E1, E2 and E3 are stored runs of `python3 -m experiments.price_rules
v4_<rule>`. The E0 counts of the first table were recomputed in the review, every measure
read on periods 20 to 199 (`v4-review.md`, annex D).

### E0 and the headline, rule by rule

E0: single-rule populations without technical change, 50 seeds, measures on periods 20 to 199;
each cell gives the all-unit-cost and the all-profit-rate population. A seed passes when every line
of E0 (section "Experiments") is true in it. The headline is the share of seeds won by the
unit-cost label in the mixed population at the defaults, on 500 seeds.

| Rule | Seeds of 50 that pass E0 | Capacity over demand, mean (range within a run) | Price over the price of production | Times it crosses 1 | Rate of new plants; industry rate | Demand lost | Share won | Final capacity share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cost-edge cutting (default) | 50 / 49 | 1.08 (0.70–1.39) / 1.09 (0.70–1.43) | 0.99 / 0.99 | 24 / 23 | 0.159 / 0.158; 0.132 / 0.130 | 0.003 / 0.003 | 0.92 (0.90–0.94) | 0.86 |
| Normal-price cutting | 50 / 50 | 1.07 (0.71–1.34) / 1.07 (0.71–1.35) | 0.98 / 0.99 | 26 / 27 | 0.158 / 0.158; 0.133 / 0.133 | 0.003 / 0.003 | 0.92 (0.89–0.94) | 0.86 |
| Systematic cutting | 0 / 0 | 0.91 (0.10–2.16) / 0.90 (0.15–2.00) | 1.11 / 1.05 | 21 / 24 | 0.245 / 0.213; 0.191 / 0.177 | 0.160 / 0.130 | 0.76 (0.72–0.80) | 0.75 |
| Universal undercutting | 46 / 43 | 0.93 (0.33–1.31) / 0.92 (0.29–1.31) | 0.95 / 0.96 | 22 / 23 | 0.151 / 0.152; 0.132 / 0.132 | 0.067 / 0.077 | 0.23 (0.19–0.27) | 0.45 |

Every share won is beyond drift (controls between 0.46 and 0.51); under universal undercutting
it is the
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
- **Under universal undercutting every firm posts the same price**, the price moves no market share,
  and the profit-rate label accumulates faster.
- **The rate of new plants sits on r̄; the industry rate is below it.** At the default r_new
  averages 0.159 and 0.158 and the industry rate 0.132 and 0.130. The sources expect this:
  the rate on new investment is equalised, average rates are not.
- **With draws the price leader is often not the cost leader.** In the two controls of E1
  (cost-edge cutting, 50 seeds) the firm posting the lowest price has the lowest unit cost
  in 0.67 and 0.73 of periods, against every period in E0. E0 has no technical change: it
  tests gravitation, not leaders and followers.

### What each setting does

The default with one setting changed. E0 on 50 seeds, counted as before the review (demand
lost and price over the whole run, the industry rate); share won on 100 seeds of the mixed
population, except the first row. All from a script that is not in the tree: to rerun.

| Setting changed | Seeds of 50 that pass E0 | Share won | Demand lost in the mixed population |
| --- | --- | --- | --- |
| None (the default) | 50 / 49 | 0.92 (500 seeds) | 0.069 |
| The entrant posts the lowest price (v3) | 0 / 0 | 0.94 | 0.011 |
| No overtime | 26 / 27 | 0.78 | 0.143 |
| r̄ = 0.05, fixed menu | 50 / 31 | 0.51, within drift (0.57 on 200 seeds, also within drift) | 0.176 |
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

### What the v3 runs gave at 5 % on the fixed menu

At r̄ = 0.05 on the fixed menu, with a shortage step of 0.5 and, but for the last row, the
entrant at the lowest price, fifteen price rules were scored (share won on 500 seeds unless
marked):

| What lets firms without a cost edge cut | Seeds of 50 that pass E0 | Share won |
| --- | --- | --- |
| Nothing (cost-edge cutting) | 0 / 0 | 0.92 |
| A price above the firm's price of production (normal-price cutting) | 43 / 12 | 0.67 |
| The same, with universal undercutting's rise of 3 % after a shortage | 50 / 50 | 0.51 (100 seeds) |
| Every firm cuts (universal undercutting) | 50 / 49 | 0.50 |
| The undercutting entrant | 48 / 5 | 0.68 (100 seeds); a quarter of demand lost |

- **At 5 % the two targets pull apart.** The headline needs the cost leader to cut alone; E0
  needs someone to cut when no firm has a cost edge; each way of allowing the second weakens
  the first.
- **On the fixed menu the price of production is 10 % above the unit cost at 5 %; at 16 % it
  is a third above.** A price near the price of production then stays in the conflict zone
  of the menu, above 85, so the two rules keep choosing differently: the hurdle of the
  profit-rate label is 0.17 at the default, against 0.10 at 5 %.
- **None of this carries to the scaled menu.** There the price of production is a third
  above the unit cost at every rate, and the rules part above a price of 85.1 at every rate.
  Whether a rate other than 0.16 gives a working industry is not known: it is the first
  thing run on the new code (E0r, section "Experiments").

### What holds at the default

Mixed population, 500 seeds at the defaults and 200 in the other cells.

| Measure | Cost-edge (default) | Normal-price | Systematic | Universal undercutting |
| --- | --- | --- | --- | --- |
| Share won for β = 0, 0.5, 1.5, 3 | 0.52, 0.88, 0.93, 0.82 | 0.55, 0.91, 0.94, 0.88 | 0.39, 0.77, 0.78, 0.60 | 0.50, 0.36, 0.21, 0.17 |
| Share won with the neutral set; without draws | 0.66; 0.98 | 0.66; 0.97 | 0.59; 0.72 | 0.52; 0.39 |
| Share won for λ = 0, 0.25, 0.5, 0.75, 1 | 0.93, 0.86, 0.83, 0.62, 0.61 | not run | not run | not run |
| The same at r̄ = 0.05, fixed menu | 0.57, 0.61, 0.51, 0.52, 0.49 | not run | not run | not run |
| Change in sales share through the price | +0.21 | +0.21 | +0.05 | 0.00 |
| Hurdle of the profit-rate label; its orders that are not the cheapest | 0.170; 0.80 | 0.171; 0.80 | 0.171; 0.79 | 0.142; 0.75 |
| Realised profit rate, unit-cost / profit-rate label | 0.148 / 0.151 | 0.149 / 0.152 | 0.164 / 0.156 | 0.133 / 0.135 |
| Price over the price of production; demand lost | 0.97; 0.069 | 0.98; 0.073 | 1.02; 0.111 | 0.93; 0.032 |

- **The advantage needs a menu on which the rules disagree, and does not grow with the
  bias.** At β = 0 the contest is at drift; from β = 0.5 the unit-cost label wins 0.82 to
  0.93, and least at β = 3. With the neutral set it wins 0.66, within drift. Without any
  draw it wins 0.98: the initial menu is such a menu when no draw replaces it. The
  homogeneous start tells the two apart.
- **The evaluation price carries it, and the hurdle does not.** Judged at the price of
  production the profit-rate rule is within drift from λ = 0.75 (0.62 and 0.61). Its hurdle
  rises a little, from 0.170 to 0.183: the market price is already near the price of
  production. What carries the effect is not identified. Between λ = 0 and 1 the orders that
  are not the cheapest fall from 0.80 to 0.73 and the realised rates move from 0.148 / 0.151
  to 0.153 / 0.159.
- **Under universal undercutting the bias works for the profit-rate label**: the unit-cost
  label wins
  0.50, 0.36, 0.21 and 0.17 as β rises.
- **At r̄ = 0.05 on the fixed menu nothing is beyond drift** and 17 to 23 % of demand is
  lost: with the undercutting entrant that menu at that rate does not give a working
  industry.

### Against the pilot

The pilot's cells at r̄ = 0.16 are v2 with overtime and the entrant at the lowest price. Its
cost-edge cells give 0.94–0.97 with 0.72–0.79 of final capacity; the default gives 0.92 with
0.86. Its leader-follow cells give 0.10–0.19; the same rule, universal undercutting, gives 0.23
here. Its industry rate
is 0.14–0.15; here 0.15 at the default and 0.13 under universal undercutting.

## Research questions and hypotheses

- **RQ1 (A).** In a mixed population of unit-cost firms (Shaikh, h = 0) and profit-rate firms
  (h = the best rate at the evaluation price, the criterion of Okishio's theorem), which rule
  does market selection favour under Marx-biased technical change?
- **RQ2 (A).** How does the answer depend on the price rule, and then on the investment rule,
  demand growth and, if a level other than 0.16 meets E0, the general rate?
- **RQ3 (B).** Why does the winner win: through the price or through accumulation, and how
  much of the unit-cost rule's advantage comes from the price at which the profit-rate rule
  judges techniques?

| # | Hypothesis | Experiment | v3 evidence (provisional) |
| --- | --- | --- | --- |
| H1 | The unit-cost rule wins where the lowest-cost firm sets the price | E1 by price rule | Met: 0.92 at the default, 0.92 and 0.76 under the two other cutting rules; under universal undercutting, where no firm's cost sets the price, it loses (0.23). With draws the firm posting the lowest price is the cost leader in 0.67 and 0.73 of periods (controls of E1, 50 seeds): the report says what "sets the price" means |
| H1′ | The profit-rate rule cannot lose systematically | E1 | Fails under the three cutting rules; holds under universal undercutting |
| H2 | The advantage grows with the Marx bias | E2 by price rule | Partly: with draws it needs the bias (0.52 at β = 0, 0.88 at 0.5) but does not grow with it (0.93 at 1.5, 0.82 at 3). Without any draw it wins 0.98 on the initial menu: the homogeneous start tells the bias from the menu |
| H3 | Where selection runs through accumulation it can favour the profit-rate rule | E1, E4, reserve | Met under universal undercutting (0.23); with the reserve never released the default goes to drift (0.42, 100 seeds), and under the accelerator too (0.56, 100 seeds) |
| H4 | The more firms cut, the smaller the advantage | E1 by price rule | Met: 0.92, 0.76 and 0.23 from cost-edge to systematic cutting to universal undercutting |
| H5 | Judged at the price of production the advantage shrinks (the outcome), because the hurdle falls to r̄ or just above it (the mechanism) | E3, E5 | Outcome met: 0.93 → 0.61, within drift from λ = 0.75. Mechanism not met: the hurdle rises, 0.170 to 0.183, since the price is already near the price of production. What carries the effect is open, and E5 looks for it. A result against Shaikh 2016, pp. 320–321 |
| H6 | The profit-rate adopter does not realise the rate it maximises | E1, E5 | Not met: the two labels realise about the same rate (0.151 and 0.148). It was met with a shortage step of 0.5 (0.172 against 0.183) and not met in the v3 runs at 5 % on the fixed menu. The sign turns with the shortage step, which gets a robustness check. A result against Shaikh 2016, Table 7.3, line 5 |

Not tested, as in v3: Okishio's theorem about the general rate, and the emergence of the bias
at a rising wage.

## The model

Six steps a period, after the deliveries that open it, and one rule that differs between the
types.

**Setting.** One industry in a given economy. The money wage is the numéraire and capital goods
are priced 1. Demand is exogenous, D_t = D_0(1 + g)^t, and so is the general rate r̄ = 0.16. A
technique j is a pair (ucs_j, κ_j): operating cost and capital per unit of normal output, with
unit cost uc_j = ucs_j + δκ_j and δ = 1/T. Its price of production is uc_j + r̄κ_j. Plants have
one technique and a normal capacity S = 20. The model's "operating cost" is Shaikh's prime
cost; what he calls operating cost includes depreciation and is the unit cost here.

**Initial industry.** Shaikh's three techniques (2016, Tables 7.10–7.11), with their capital
scaled to the general rate, so that his table holds at any r̄. The unit costs and the initial
price do not move: 78, 76 and 75 for C, D1 and D2, and every price is 100. Capital and operating
cost follow r̄. The scaling is a construction of the model, without a source:

```latex
\kappa_j(\bar r) = \kappa^{S}_j\,\frac{0.16}{\bar r}, \qquad ucs_j(\bar r) = ucs^{S}_j - \delta\,\big(\kappa_j(\bar r) - \kappa^{S}_j\big), \qquad \big(ucs^{S}_j,\ \kappa^{S}_j\big) = (64.25,\ 137.50),\ (61.77,\ 142.31),\ (59.21,\ 157.89)
```

δ is that of the run, 1/T. At r̄ = 0.16 the menu is Shaikh's table at any T, the menu of every
run so far, and the unit costs move with T as in v3. The table below is for T = 10.

| r̄ | C (ucs, κ) | D1 (ucs, κ) | D2 (ucs, κ) | Cost of a plant of C |
| --- | --- | --- | --- | --- |
| 0.16 (default; Shaikh's table) | (64.25, 137.50) | (61.77, 142.31) | (59.21, 157.89) | 2,750 |
| 0.10 | (56.00, 220.00) | (53.23, 227.70) | (49.74, 252.62) | 4,400 |
| 0.05 | (34.00, 440.00) | (30.46, 455.39) | (24.47, 505.25) | 8,800 |

- **The same at every r̄.** The prices of production are 100.0, 98.8 and 100.3. At the price
  of 100 the three techniques earn r̄, 1.054 r̄ and 0.990 r̄: C earns the general rate, D1 has
  a lower cost and a higher rate, D2 the lowest cost and a lower rate than C. The two rules
  part above a hurdle of 0.40 r̄, a price of 85.1, where the profit-rate rule prefers D1 to
  D2; above 0.92 r̄ it also prefers C to D2. So at a given price the rules rank the three
  techniques alike at every r̄.
- **Limit.** Every operating cost must be positive: r̄ above 0.034 at T = 10, above 0.044
  at T = 7. The code refuses a run in which one is not.
- **What moves with r̄ at the start.** A plant costs 0.16 / r̄ times as much, and so do the
  initial cash (the depreciation accumulated on the initial plants) and an entrant's equity:
  3.2 times at 0.05. Profits do not move: at a price of 100 a plant is paid by 40
  plant-periods of retained profit at 0.05, against 12.5 at 0.16, so growth out of profits
  is 3.2 times slower while the entry gate, relative to r̄, is the same. The operating costs
  (24 to 34 at 0.05) are far below any price, so scrapping on cost and the offer test of
  step 2 no longer bind.
- **What moves in technical change.** Depreciation is 18 % of the unit cost of C at 0.16
  and 56 % at 0.05. A design drawn from C is then kept by the unit-cost rule if k < 0.77 at
  r̄ = 0.05 (20 % of draws at β = 1.5), against k < 4.67 at 0.16 (92 %). From D2, the
  technique the unit-cost firms hold after two periods, it is 8 % against 87 %. β stays at
  1.5 at every rate and the share of designs kept is reported: the two thresholds move by
  different factors (6.0 on C, 7.7 on D2), so no single β restores the share.
- **Not run.** Every number of this document at r̄ = 0.05 comes from the fixed menu of v3,
  the row of 0.16 used at every rate. The first runs of version 4 are E0 and E1 on the
  scaled menu at 0.10, then at 0.05 (E0r).

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
h_i = \begin{cases} 0 & \text{unit-cost rule (Shaikh)} \\ \max\Big(0,\ \max_{j \in M_t} \dfrac{p^{e}_{i} - uc_j}{\kappa_j}\Big) & \text{profit-rate rule} \end{cases} \qquad p^{e}_{i} = (1-\lambda)\,p_{i,t} + \lambda\,\big(uc_R + \bar r\,\kappa_R\big)
```

R is the regulating technique, the lowest unit cost among plants in operation. λ = 0 judges at
the firm's own price; λ = 1 at the price of production of R. The profit-rate rule is the
criterion of Okishio's theorem; Duménil and Lévy (2005, p. 209) give it to Marx and the
classics. A tie between techniques goes to the lower κ, then the lower operating cost.

**Schedule.**

0. **Start of the period.** Demand is D_t. The plants ordered in t − 1 are delivered, an
   entrant's included, so an entrant of t − 1 has a plant in operation at step 1 and its
   price counts there. A design becomes public 2 periods after its first plant produced.
1. **Pricing.** Every firm reads last period's prices and last period's excess demand. A
   shortage is last period's demand D above K, the total normal capacity then in operation;
   the excess-demand share is (D − K) / D. The floor is the unit cost of the firm's best
   plant in operation, the one with the lowest unit cost (a tie goes to the lower κ). One
   option, `price_floor`, replaces it for a robustness check by the operating-cost floor:
   the operating cost of the dearest plant the firm ran last period, or of its cheapest
   plant if none ran; the cost edge below is still read on the unit cost. A firm without a
   plant in operation keeps its price, under every rule. A firm's rivals are the other firms
   with a plant in operation. One option, `pricing`, chooses among four rules. In the three
   cutting rules P is the lowest price of the firm's rivals; after a shortage the firm moves
   up to the next higher rival price, or, with no rival above, raises its price by 0.25 times
   the excess-demand share; otherwise it undercuts to (1 − c)P, c = 0.02, when the rule
   entitles it to, and else follows P down. Its price rises only after a shortage or to
   reach its floor. A firm without a rival keeps its price, or takes its floor if that is
   higher; after a shortage it raises its price by the same step, without a cap.
   - *Cost-edge cutting* (default). A firm is entitled to cut with spare capacity (last
     utilisation below 1) and a unit-cost edge over a rival posting P.
   - *Normal-price cutting.* While P is above the firm's own price of production, that of its
     best plant, spare capacity is enough; at or below it, the firm also needs the cost edge.
     A cut is a full (1 − c)P, so it can end up to c below that price of production. In
     Shaikh the centre is the regulating price of production; the firm's own is used here
     because it is what was run.
   - *Systematic cutting.* Spare capacity alone, at any price.
   - *Universal undercutting* (leader-follow in v2 and the notebook). L is the lowest price posted
     last period by a firm that has a plant in operation at this step. After a shortage
     every firm posts (1 + z)L, z = 0.03. Otherwise every firm posts (1 − c)L, or its floor
     if that is higher, whatever its utilisation and its cost. A firm that is alone with a
     plant in operation posts (1 + z) times its price, at most 3 times its floor. The floor
     applies to a cut only: after a shortage, and for a firm alone, a price can be below it,
     as in v2.
2. **Demand.** Market shares follow the replicator below, with E = 1/p and χ = 1. A firm offers
   its plants whose operating cost is at most its price and can sell up to u_max = 1.2 times
   their normal capacity. Sales are the smaller of share × D and that limit; unserved demand
   is re-allocated once, pro rata to the room left; the rest is lost and recorded.
3. **Production and accounts.** The plants a firm offered at step 2 run cheapest first, then
   youngest, up to normal capacity; what is left runs as overtime in the same order, up to
   u_max times capacity, at the same operating cost. A plant that was not offered does not
   run. Every plant in operation ages and depreciates straight-line over
   T. Profit is after depreciation; dividends are d × max(0, profit), d = 0.5; the rest joins
   the investible funds. No debt, interest or bankruptcy. Then, once a period: the regulating
   technique and its price of production uc_R + r̄κ_R, and r_new, the capacity-weighted
   realised rate (profit over purchase cost) of the plants aged 5 periods or less.
4. **Scrapping.** A plant leaves at age T = 10, after 2 consecutive periods with its owner's
   price below its operating cost, or after 2 consecutive periods without output. Its
   depreciation reserve (purchase cost less book value) joins the firm's investible funds if
   r_new ≥ r̄ in that period, or if no plant is in the window of r_new. Otherwise the firm pays
   it to the rest of the economy, as far as its cash allows. The book value left is written
   off. A working plant is never replaced, a departure from Salter (1966, pp. 56–59). One
   option, `reserve`, replaces this condition for the sensitivity check: the reserve always
   joins the funds, or is always paid out. The reserve condition and the idle test are
   devices of the model, without a source; the first is in the spirit of Shaikh (2016,
   p. 264). While the reserve is paid out no plant that retires is replaced.
5. **Technical change and investment.** Draws as below. The firm computes its hurdle and
   picks j*. *Retained earnings* (default): it buys the whole plants of j* that its funds,
   still in cash, pay for. *Accelerator*: it buys the plants missing for its capacity, plants
   on order included, to reach the demand addressed to it, share × D_t, as far as its cash
   pays. There is no target utilisation: overtime is the buffer. The reserve condition of
   step 4 is the same under both rules. A plant ordered in t produces from t + 1.
6. **Entry and exit.** Exits first: a firm leaves with a share below 1 % or without capacity,
   in operation or on order, while 2 firms remain; its cash goes to the rest of the economy.
   Then at most one entrant, with the probability below. Its label is copied from an incumbent
   drawn by market share and flipped with probability μ = 0.02; one option, `entry_label`,
   draws the incumbent evenly instead, one vote a firm, for a robustness check. Its
   technique is chosen by its
   own rule on the public menu, with the lowest price posted by a firm with a plant in
   operation as its own price in p^e. It posts (1 − c) times that price, or the unit cost
   of its plants if that is higher; one option, `entry_price`, makes it post that lowest
   price, as in v3. Its first utilisation is 1, so it does not cut in its first period. Its
   capacity is 0.5 times the
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
In Shaikh the cost leader need not go that far (2016, pp. 263, 316): the depth of the wars is
the model's.

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
| General rate | r̄ | 0.16 | E0r: 0.10, then 0.05, on the scaled menu; E4: the level that meets E0, if one does | Was 0.05, crossed with E3 and E4 |
| Price rule | — | cost-edge cutting | E0 to E2: normal-price, systematic, universal undercutting; E3 and E4: systematic, universal undercutting | Four levels |
| Entrant's price | — | (1 − c) × the lowest price | Robustness: the lowest price | New |
| Overtime limit | u_max | 1.2 | Robustness: 1 (none); Morris 1–1.4 | New |
| Price cut | c | 0.02 | Morris 0.01–0.05 | Also the entrant's |
| Shortage step (the three cutting rules) | — | 0.25 | Robustness: 0.5; Morris 0.1–0.5 | Was 0.5; now screened |
| Spare-capacity threshold (the three cutting rules) | u_full | 1 | Fixed | — |
| Rise after a shortage; cap of a firm alone (universal undercutting) | z; — | 0.03; 3 × floor | Fixed | New, for that option |
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
| Entrant's label | — | copied from an incumbent drawn by market share | Robustness: the incumbent drawn evenly | Option added |
| Periods; D_0 over initial capacity; initial price | — | 200; 340/383; 100 | Fixed | — |
| Share of conflict designs, categories rule | q | 0.5 | Fixed | — |
| First period of the E0 measures | — | 20 | Fixed | An analysis constant, outside the model |
| Target utilisation | u* | — | — | Removed |

| Option | Name in the code | Levels |
| --- | --- | --- |
| Price rule | `pricing` | `cost_edge` (default), `normal_price`, `systematic`, `universal` |
| Price floor | `price_floor` | `unit_cost` (default), `operating_cost` |
| Entrant's price | `entry_price` | `undercut` (default), `lowest` |
| Entrant's label | `entry_label` | `share` (default), `even` |
| Overtime | `u_max` | 1.2 (default); 1 gives none |
| Depreciation reserve | `reserve` | `conditional` (default), `always`, `never` |
| Initial menu | `menu_scaling` | `scaled` (default), `fixed` |
| Investment rule | `investment` | `retained` (default), `accelerator` |
| Technical change | `tech_change` | `marx` (default), `neutral`, `categories`, `none` |
| Scrap cost | `scrap_cost` | `operating_cost` (default), `unit_cost` |
| Lag before a design is public | `public_lag` | 2 (default), none |

## Experiments

Each cell is a mixed population run against its two controls on the same seeds.

**E0, the gate.** Single-rule populations, no draws, 50 seeds, under each price rule. Every
measure is read on periods 20 to 199 and is a column of the run row. A seed passes when every
line below is true in it. E0 holds when at least 9 seeds of 10 pass, in both populations.

- **What the gate stops.** It is on the default: if E0 fails there on the new code, no other
  experiment is read. Under the other price rules E0's verdict is reported beside every
  result.
- **Thresholds.** Two lines are new. The threshold on the crossings is proposed here. The
  ceiling on the demand lost was set at 0.10 by Ugo on 10 November, after the runs; 0.05 was
  proposed first.
- **The rate.** The line is read on the rate of new plants, the one that is equalised
  (Shaikh 2016, pp. 264, 268–271), with the band of v3. The industry rate is reported.
- **What E0 does not test.** It has no technical change, so it tests gravitation, not
  leaders and followers. Its lines are also read on the two controls of E1, which have
  draws, and reported beside it, outside the gate.

| Fact | Measure, on periods 20 to 199 | Threshold | Default, v3 runs: mean; seeds of 50 that pass |
| --- | --- | --- | --- |
| The lowest-cost firm leads the price | Share of periods in which a firm posting the lowest price has the lowest unit cost, among the best plants of the firms in operation | at least 0.9 | 1.00 and 1.00; 50 and 50 |
| The price gravitates around the price of production | Mean over periods of the sales-weighted price over the price of production of the regulating technique | 0.9–1.2 | 0.99 and 0.99; 50 and 50 |
| | Times that ratio passes from one side of 1 to the other between two periods, either way | at least 5 | 24 and 23; 50 and 50 |
| Capacity follows demand | Mean over periods of the normal capacity in operation over demand | 0.9–1.2 | 1.08 and 1.09; 50 and 49 |
| The rate of new plants gravitates around r̄ | Mean of r_new over the periods in which it is defined | 0.6 to 2 times r̄ | 0.159 and 0.158; 50 and 50 |
| Demand is served | Sum of the demand lost over the sum of demand | at most 0.10 | 0.003 and 0.003; 50 and 50 |
| The industry survives | Capacity at the last period | above 0 | 50 and 50 |

E0 is met at the default (50 and 49 seeds of 50) and under normal-price cutting (50 and 50). It
is not met under universal undercutting (46 and 43, where 45 are needed) and fails in every
seed under
systematic cutting. Reported beside E0, and not part of it:

- **The industry rate**: the sum of profits over the sum of the purchase costs of the plants
  in operation; 0.132 and 0.130 at the default.
- **The spread of rates**: the mean over periods of the highest less the lowest rate of a
  firm; 0.12 and 0.12. It is above 0 as soon as two firms differ, so it is no longer a line.
- **Capacity at the last period** within 0.9–1.2 of demand (34 and 37 seeds of 50 at the
  default), and the range of capacity within a run (0.70 to 1.39 and 0.70 to 1.43).
- **The same lines on the controls of E1.** At the default, on 50 seeds, the firm posting
  the lowest price has the lowest unit cost in 0.67 and 0.73 of periods and no seed passes
  that line; the demand lost passes in 37 and 47 seeds and capacity in 42 and 50.

| # | Question | Design | Seeds | Runs |
| --- | --- | --- | --- | --- |
| E0 | Does the industry behave as under real competition? | No draws, two controls, 4 price rules | 50 | 400 |
| E0r | Does another general rate give a working industry? | E0 and E1 at the default rule on the scaled menu, at r̄ = 0.10, then 0.05; β = 1.5; the share of designs kept reported | 50; 500 | 3,200 |
| E1 | Which rule wins, by price rule? | Defaults, 4 price rules | 500 | 6,000 |
| E2 | Does the advantage need the Marx bias, and grow with it? | β = 0, 0.5, 1.5, 3; neutral set; none; 4 price rules | 200 | 14,400 |
| E3 | How much comes from the evaluation price? | λ (5) × price rule (3) | 200 | 9,000 |
| E4 | Where does each rule win? | Price rule (3) × investment rule (2) × g (0, 1 %), then under the categories rule; × r̄ (2) if a second level meets E0 in E0r | 200 | 14,400, or 28,800 with r̄ |
| E5 | Through which channel? | Decomposition of E4; regression of the profit-rate gap on the dearer orders; in E3 at λ = 0 and 1, the orders that are not the cheapest, the realised rates by label and the spread of hurdles across firms | — | 0 |
| E6 | Can one firm of a rule invade the other? | 1 among 9, both ways, with a one-rule control; the default and universal undercutting | 500 | 4,000 |

The three price rules of E3 and E4 are the default, systematic cutting and universal
undercutting. E0
to E6 are 51,400 runs, or 65,800 with r̄ in E4. With Morris (39,000), the reserve (6,400) and
the robustness checks (about 37,000, or 44,000) the whole is about 134,000 runs, or 155,000:
half an hour on 10 workers at v3's speed with these settings (11,200 runs in 2 min 27 s at
the default). E6 keeps v3's design: ten firms on D1, D_0 = 1,065.3, μ = 0.

**Order.** E0 at the default is run and read first. Then E0r, and with it the reruns of what
this document marks "100 seeds" or "not run": the accelerator cell and the shortage step of
0.5 on 500 seeds, and the homogeneous start. Then E1 to E6.

## Sensitivity analysis

- **Morris screening.** The ten parameters of v3 plus u_max and the shortage step: 10
  trajectories on a 4-level grid, 130 points × 3 populations × 100 seeds = 39,000 runs, at
  the default. Outcomes: the share won less the controls' mean, the mean final capacity
  share, the share of demand lost, the share of E0's lines that hold and the gap in
  realised rates between the two labels.
- **Sensitivity over the reserve** (asked by Ugo, 10 November). The rule of the depreciation
  reserve gets three levels: released if r_new ≥ r̄ (default), always released, never
  released. These are arms 4, 2 and 1 of the v2 pilot. Cells: E0 and E1 at each of the two
  other levels, at the default and under universal undercutting: 6,400 runs. A first look at the
  default (E0 on 50 seeds, all-unit-cost population, counted as before the review; share won
  on 100 seeds of the mixed population; from a script that is not in the tree, to rerun):

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
| No overtime (u_max = 1) | E0 and E1 under the 4 price rules | 50; 500 | At the default, 100 seeds: 0.78, and E0 holds in 26 and 27 seeds of 50 |
| The entrant at the lowest price | E0 and E1 at the default | 50; 500 | 100 seeds: 0.94, and E0 holds in no seed |
| Shortage step of 0.5 | E0, E1 and the accelerator cell, at the default | 50; 500 | E0 in 50 and 50 seeds; E1: 0.94 on 500 seeds, realised rates of 0.183 and 0.172; accelerator: 0.84 on 100 seeds |
| Entrant's label copied from an incumbent drawn evenly | E1 at the default and under universal undercutting | 500 | Not run |
| Fixed menu | E0 and E1 at the second level of r̄, if E0r keeps one | 50; 500 | At 0.05: E0 in 50 and 31 seeds of 50; 0.57 on 200 seeds |
| Operating-cost floor | E1 at the default and under universal undercutting | 500 | Not run under a cutting rule, nor with these settings |
| Scrapping on unit cost | E1 and the marx cells of E4 | 200 | Not run with these settings |
| Private diffusion (L = none) | E1 | 200 | Not run |
| Homogeneous start (six firms on D1) | The 6 cells of E2 | 200 | Not run. Run with E0r: it tells the bias from the initial menu |
| 12 and 30 firms | E1 and the 4 cells of E4 with g = 0.01 at the default and under universal undercutting | 200 | Not run |
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
`params.price_floor`; overtime by `params.u_max`; the entrant's price by `params.entry_price`
and its label by `params.entry_label`; the reserve by `params.reserve`; the menu by
`params.menu_scaling`. The table of options above gives every name and its levels. No
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
python -m experiments.show_run --seed 7 pricing=universal rbar=0.05 population=all_unit_cost
```

- **Input.** Any parameter as `name=value`, a seed, and `population` (mixed, all_unit_cost,
  all_profit_rate).
- **How.** The model's period is a tuple of step functions. The viewer runs the same tuple
  and reads the firms after steps 3, 5 and 6, so it sees a firm before it leaves and a share
  before and after entry. The model keeps what v3 kept, the period table and a tally of the
  period's flows, now tallied by firm and summed by label. It gains no recorder for the
  viewer.
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
accelerator without a target; the three levels of the reserve; the entrant's label; the
scaled menu (Shaikh's table at 0.16 at any T; a run with an operating cost that is not
positive refused); the line count without comments and docstrings; the viewer's tables on a
short run, and its figure where matplotlib is installed.

## What the other sections of the v3 proposal need

- **Report.** Section 3 presents four price rules, overtime and the undercutting entrant, at
  r̄ = 0.16. It says once that the model's operating cost is Shaikh's prime cost. It presents
  as devices of the model, without a source: the scaled menu, the reserve condition, idle
  scrapping, the shortage step, the cap of a firm alone, the value of u_max and the weight
  of market share in the entrant's label. It gives the depth of the price wars and the size
  of the cycle as the model's own. H5 and H6 are reported as results against Shaikh. Section
  5.1 shows E0 on averages with the cycle and the headline by price rule;
  5.4 treats the price rule as the first condition. Figure 2 is a run of the viewer. Figure 3
  gets one curve per price rule.
- **Presentation.** Slide 6 keeps "the unit-cost rule wins" and adds "where a cost leader sets
  the price", and waits for E4 before it names the price rule alone, since under the
  accelerator the headline is within drift (0.56, 100 seeds); slide 9 (realised rates) reports
  that the two labels realise the same rate;
  slides 10 and 11 open with the price rule.
- **Timeline.** The dates stand. v3 was built on 10 November, so the rebuild fits before the
  runs of 17 to 19 November.
- **Literature.** To add for pricing and entry: Shaikh 2016, pp. 264 and 274–282, and Hall
  and Hitch 1939. Nakatani 1980, on H1 and H6, is to add to the library and to read.
  `v4-literature-check.md` gives the verdict on each mechanism.

## Decisions for the group

| Decision | Options | Recommendation | Why |
| --- | --- | --- | --- |
| Default general rate | 0.05; 0.16 | **Set by Ugo, 10 Nov:** 0.16 | The menu earns it at its initial price |
| Default price rule and entry | Cost-edge cutting with the undercutting entrant; normal-price cutting with it; the v3 entrant | **Set by Ugo's criterion, 10 Nov:** cost-edge cutting with the undercutting entrant | It meets E0 and gives the headline (0.92). Normal-price cutting does the same (0.92) with one more clause |
| The general rate away from 0.16 | Crossed with E3 and E4; out of E3 and tested first; the fixed menu | **Decided by Ugo, 10 Nov, on the review:** out of E3. E0 and E1 on the scaled menu at 0.10, then 0.05, are the first runs (E0r). r̄ stays in E4 at the level that meets E0, if one does | On the scaled menu the rules rank the initial techniques alike at every rate. On the fixed menu at 0.05 a sixth of demand is lost and nothing is beyond drift. Neither menu is run at 0.10 |
| Shortage step | 0.5; 0.25 | **Decided by Ugo, 10 Nov:** 0.25 | It halves the price peaks (1.9 against 3.7 times the price of production) with the same E0 and headline. The demand lost stays at 7 %, and under the accelerator the headline falls to drift (0.56 against 0.84) |
| What E0 checks | The last period; averages over the run | Averages, with the cycle reported | Capacity at the last period is in the band in 34 and 37 seeds of 50 |
| How E0 is read | By line or by seed; the industry rate or the rate of new plants | **Decided by Ugo, 10 Nov, on the review:** by seed; the line on r_new; the spread reported, not counted; the lines also read on the controls of E1, outside the gate | The rule was stated two ways. r_new averages 0.159 and 0.158 against an industry rate of 0.132 and 0.130 |
| Name of v2's leader-follow rule | Keep it; universal undercutting | **Decided by Ugo, 10 Nov, on the review:** universal undercutting, `pricing = "universal"` | Every firm cuts whatever its cost; price leadership in the sources is cost-edge cutting |
| The entrant's label | The incumbent drawn by market share only; a check with the incumbent drawn evenly | **Decided by Ugo, 10 Nov, on the review:** an option `entry_label` and one robustness check | 0.16 of the market moves to the unit-cost label through entry and exit |
| Ceiling on the demand lost in E0 | 5 %; 10 % | **Decided by Ugo, 10 Nov:** 10 % | Set after the runs, which the report should say. At the default less than 1 % is lost in E0 |
| Overtime premium | None; a premium on overtime output | None | Asked by Ugo; the runs have none |
| What counts in the 1,000 lines | Comments excluded; comments and docstrings excluded | **Settled on the review:** both excluded | A docstring is a comment for this purpose. v3 counts 651 lines that way |
| Initial menu at r̄ ≠ 0.16 | The fixed menu of v3; capital scaled by 0.16 / r̄ at the price of 100; margins scaled by r̄ / 0.16 at the price of production of C | **Asked by Ugo, 10 Nov:** capital scaled, price kept at 100 | Shaikh's table holds at any r̄. Not run: the results at 0.05 must be redone |
| β at r̄ ≠ 0.16, under the scaled menu | Keep 1.5; rescale it so that the same share of designs is kept | **Decided with the general rate, 10 Nov:** keep 1.5 and report the share of designs kept | No single β restores the share on every technique. With β = 1.5 the unit-cost rule keeps 20 % of the designs drawn from C at 0.05 (8 % from D2), against 92 % (87 %) at 0.16: technical change slows, and the two rates are not compared on the same bias |
| Where version 4 is built | A clean tree beside v3; a branch of this one | **Decided by Ugo, 10 Nov, on the review:** a clean tree `../ABM-v4`, a git worktree on a new branch `v4` cut from the head of `v3` and emptied in its first commit; v3 read-only beside it | As v3 did with v2: the unchanged equations are ported, not inherited |

Not run with these settings: the scaled menu at any rate but 0.16, E3 under the three other
price rules, E4, E6, Morris and the robustness checks marked "not run". The reserve, the
accelerator, the shortage step of 0.5,
growth and the two robustness checks with a result were looked at on 50 seeds of E0 and 100
seeds of the mixed population only.
