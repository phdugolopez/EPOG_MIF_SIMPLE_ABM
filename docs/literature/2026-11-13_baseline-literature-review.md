# Which baseline? Mechanism, literature and a way to settle it

13 November 2026. Written for the group, on the disagreement about the baseline of version 4:
gravitation of the price around the price of production (prix de production), or a price and a
profit rate (taux de profit) that fall. Nothing in the model, in `parameters.py` or in the five
specification documents was changed. Every number below comes from
`docs/literature/scripts/closures.py`, 150 seeds, 200 periods, on the code of this tree.

Status of the sources is given in the last section: read in full, read in part, abstract only,
or cited from memory and still to read. Nothing marked "to read" should go into the report
before someone has opened it.

## At a glance

- **The three runs of seed 7 are three closures, not three calibrations.** With the reserve
  always released and no dividends, capital cannot leave the industry. No shortage ever occurs,
  the price can only fall, and it settles on the unit cost: the profit rate goes to zero.
- **That fall is not Marx's.** It happens without technical change (rate 0.012) and with
  neutral technical change (rate 0.00) as well as with Marx-biased change (0.002). It is an
  overcapacity result (surcapacité), the mechanism of Brenner and Crotty, not a rise in the
  composition of capital.
- **In that regime the experiment loses its treatment.** At a price equal to unit cost the
  hurdle of the profit-rate rule falls to 0.014 (0.171 at the default), so the two rules pick
  the same techniques. The unit-cost label ends with 0.52 of capacity, against 0.87.
- **The falling rate of profit is already in the default, but it shows in the price.** With
  r̄ given from outside, the rate of new plants cannot drift: it is the price of production
  that moves. In an all-unit-cost industry it rises from 100 to 107 (in 94 % of seeds); in an
  all-profit-rate industry it falls to 84 (in every seed). Read at the initial price, that is
  a rate falling from 0.16 to 0.140 under Shaikh's rule and rising to 0.236 under Okishio's.
- **So the group disagrees on a variable the model holds fixed.** Shaikh himself leaves the
  single industry, and lets the general rate move, when he derives the fall (2016, p. 318).
  With an exogenous r̄ the fall of the general rate cannot be an output; forcing it through
  parameters produces a different phenomenon.
- **χ = 5 is not a regime.** The discrete replicator removes a firm priced 25 % above the mean
  in one period, and the exit rule then deletes firms that are sold out and profitable: 57 %
  of demand is lost and the contest is at drift (0.55).
- **A baseline both sides can accept exists.** With a milder bias (β = 0.5) the price falls by
  a quarter over the run, the rate of new plants stays on r̄ (0.166), and the unit-cost rule
  still wins 0.88 of seeds.
- **Proposed way to settle it** (section 4): name the closure; fix the baseline on facts that
  are not the outcome; make capital mobility a treatment with three levels; add two read-outs
  (price of production, rate at the initial price); keep χ at 1 or below.

## 1. What the runs show

Mixed population, 150 seeds. "Early" is periods 0 to 9, "late" periods 150 to 199. The share
won and the capacity share are those of the unit-cost label (`run_row`).

| Cell | Price, early → late | Price of production, late | Price over it, late | Industry rate, late | Rate of new plants, late | Capacity over demand, late | Demand lost | Hurdle of the profit-rate label | Capacity share; share won |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Default | 97.1 → 92.3 | 97.2 | 0.95 | 0.155 | 0.167 | 0.94 | 0.070 | 0.171 | 0.87; 0.94 |
| payout = 0 | 92.2 → 78.4 | 94.5 | 0.83 | 0.102 | 0.115 | 1.02 | 0.004 | 0.116 | 0.67; 0.99 |
| reserve = always | 92.1 → 54.5 | 103.8 | 0.53 | 0.004 | 0.007 | 1.00 | 0.000 | 0.018 | 0.53; 0.80 |
| payout = 0, reserve = always ("captive") | 92.1 → 54.0 | 104.4 | 0.52 | 0.002 | 0.005 | 1.01 | 0.000 | 0.014 | 0.52; 0.75 |
| Captive, no technical change | 93.6 → 83.4 | 100.3 | 0.83 | 0.012 | 0.053 | 1.37 | 0.000 | 0.057 | 0.54; 1.00 |
| Captive, neutral set | 92.6 → 37.7 | 54.6 | 0.69 | −0.002 | 0.005 | 1.03 | 0.000 | 0.019 | 0.51; 0.59 |
| χ = 5, payout = 0 | 92.2 → 84.2 | 100.0 | 0.84 | 0.106 | 0.117 | 1.01 | 0.010 | 0.121 | 0.97; 0.98 |
| χ = 5, captive | 92.0 → 54.4 | 104.4 | 0.52 | 0.002 | 0.006 | 1.01 | 0.000 | 0.015 | 0.66; 0.83 |
| χ = 2 | 97.0 → 113.9 | 96.7 | 1.18 | 0.295 | 0.287 | 0.71 | 0.171 | 0.193 | 0.72; 0.76 |
| χ = 5 | 96.9 → 111.8 | 94.6 | 1.18 | 0.322 | 0.321 | 0.19 | 0.565 | 0.184 | 0.54; 0.55 |
| β = 0.5 | 96.8 → 74.7 | 78.6 | 0.95 | 0.156 | 0.166 | 0.93 | 0.066 | 0.158 | 0.79; 0.88 |
| β = 0.5, captive | 91.8 → 40.6 | 84.7 | 0.48 | 0.002 | 0.004 | 1.00 | 0.000 | 0.016 | 0.52; 0.71 |

In the captive cell 15 % of seeds are exact ties, and the wins are by a hair: the mean
capacity share is 0.52.

### The captive regime: a ratchet on the price

1. **Capital cannot leave.** With `reserve = always` the depreciation of every plant that
   retires returns to the firm's funds whatever the rate of new plants; with `payout = 0`
   all profit does too. The only exit left is the 1 % share rule.
2. **So capacity never falls short of demand.** Each firm can always replace what retires.
   Capacity sits on demand (1.00 to 1.01) and no demand is lost.
3. **So the price never rises.** In the three cutting rules a price goes up only after a
   shortage. Without one, each cut by a firm with a cost edge and spare capacity is kept: a
   ratchet. The price falls until it meets the unit cost of the followers.
4. **Profit goes to zero, and entry stops.** The rate of new plants is far below r̄, so the
   entry gate stays shut (no entry in the seed-7 run). The industry is a closed club of the
   initial firms, replacing their plants out of depreciation alone.
5. **Technical change only sets the level of the floor.** The price follows the unit cost
   down (54 with the Marx bias, 38 with the neutral set, 83 without draws), and the rate is
   zero in the three cases.

### The intermediate regime (χ = 5, payout = 0)

The reserve is still withdrawn when new plants earn less than r̄, so capital does leave, but
all profit is reinvested: capacity catches up with demand faster and shortages are rare (1 %
of demand lost against 7 %). The price spends most of the run below the price of production
(0.84) and the rate settles near 0.11, between r̄ and zero. The centre of gravity has moved
down because the condition that makes capital leave binds only on depreciation.

### χ = 5 alone: a numerical breakdown, not an economic one

In seed 7 the sequence is: a shortage around period 56; firms raise their prices in steps, as
the shortage rule says; posted prices spread by 15 to 40 %. With χ = 5 the replicator
multiplies a firm's share by 1 + 5 × (its relative gap in 1/p), so a firm 15 % dearer than
the average loses two thirds of its share in one period, and one 25 % dearer loses all of it.
Its share falls below 1 % and the exit rule removes it, with plants that were running at full
overtime and at a profit. From period 60 the run is a loop of one entry and one exit a
period, four one-plant firms, capacity at 0.12 of demand. On 150 seeds 57 % of demand is
lost. The discrete replicator is defined only while χ times the largest relative gap stays
below 1, and the damage is already visible at χ = 2 (17 % of demand lost, against 7 %).

## 2. The disagreement is about the closure

Every cost of the model is counted in wage units, and a unit of capital always costs 1. A
technique therefore fixes the unit cost uc and the capital per unit κ, and one relation ties
the two things that are left, the price p and the profit rate r:

```latex
r = \frac{p - uc}{\kappa}
```

One equation, two unknowns: a model needs one more condition to say what p and r do, and
that condition is the closure (bouclage). It is a statement about distribution, since a
lower p hands the gains of productivity to the buyers (1/p is what a wage unit buys of the
product, the product wage, salaire réel en produit) and a higher p leaves them to profit.
Three closures give three "expected behaviours", and each is a known position in the
literature. Corrected on 13 November, late: the third row said the rate moves "down"; with
the mark-up at zero it is zero at every date, and it is with a positive mark-up that it
falls.

| Closure | What is held fixed | What moves with Marx-biased change | Who holds it |
| --- | --- | --- | --- |
| Given general rate (the default): p = uc + r̄ κ | The rate of new plants, at r̄, by entry and by the reserve | The price of production, and so the product wage | Shaikh 2016: p. 264 (entry and exit equalise the rate on new investment), pp. 265–268 (the regulating price of production), p. 316 (after D2 wins, the price rises back to the level that gives 16 %) |
| Constant product wage: p = 100 | The price, at 100 | The rate of the regulating technique, r = (100 − uc) / κ | Okishio 1961; Roemer 1979; Shaikh 2016, pp. 318–322, on two sectors |
| Price follows unit cost: p = (1 + m) uc | The mark-up m on unit cost | The rate, r = m uc / κ: it falls as cost falls and capital rises, whatever the rule. In the captive regime m = 0, so the rate is zero at every date and nothing is left to move | Close to a constant or high wage share: Park 2001; Basu 2026. With sunk capital: Brenner 1998; Crotty 2002 |

The next table reads the runs under the second closure, without changing the model: the regulating technique at the end of the run, its price of production at r̄, and the
rate it would earn at the initial price of 100.

| Cell | Population | Unit cost; κ of the regulating technique | Its price of production (start: 100.3) | Seeds where it ends above 100 | Rate at the initial price (start: 0.16) |
| --- | --- | --- | --- | --- | --- |
| Default | All unit-cost | 52.4; 342 | 107.1 | 0.94 | 0.140 |
| Default | Mixed | 50.4; 296 | 97.9 | 0.41 | 0.170 |
| Default | All profit-rate | 48.8; 217 | 83.6 | 0.00 | 0.236 |
| Captive | All unit-cost | 54.2; 349 | 110.1 | 0.99 | 0.132 |
| Captive | Mixed | 52.5; 330 | 105.4 | 0.89 | 0.144 |
| Captive | All profit-rate | 51.1; 317 | 101.8 | 0.73 | 0.155 |
| β = 0.5 | All unit-cost | 39.3; 295 | 86.5 | 0.00 | 0.207 |
| β = 0.5 | Mixed | 37.4; 259 | 78.8 | 0.00 | 0.245 |
| β = 0.5 | All profit-rate | 35.4; 212 | 69.4 | 0.00 | 0.305 |

- **One technique, three rates.** In the run of seed 7 with systematic cutting and β = 0.5
  the regulating technique at the end has a unit cost of 37.8 and κ = 250. Under the first
  closure its price is 77.8 and its rate 0.16. At the initial price of 100 its rate would be
  0.25. With the initial mark-up of 0.285 on unit cost its price would be 48.6 and its rate
  0.04.
- **Why the price of production can turn up (the U of the captive run).** A design saves a
  share a of the operating cost and adds k a to capital, so it changes the price of
  production by a (k (δ + r̄) κ − ucs). It lowers it only if k is below ucs / ((δ + r̄) κ).
  Operating cost shrinks and capital grows, so that threshold falls: 1.61 at the start of
  that run, 0.40 near period 112, 0.14 at the end. The unit-cost rule keeps every design
  with k below ucs / (δ κ), which is 0.35 at the end. At β = 0.5 only 7 % of draws are above
  the first threshold at the start; at the end the designs kept with k between 0.14 and 0.35
  outnumber those below 0.14. The price of production falls, flattens, then rises. In the
  captive regime the hurdle of the profit-rate label is zero, so both labels do this; in
  the open run that label refuses those designs and the price of production flattens
  without turning.
- **The default reproduces both results.** An industry of profit-rate firms ends with a lower
  price of production in every seed: Okishio's result. An industry of unit-cost firms ends
  with a higher one in 94 % of seeds: at a constant product wage its rate falls from 0.16 to
  0.14, Shaikh's result. This is Park's finding (2001, as reported by
  Shaikh 2016, p. 322): at a constant real wage only Shaikh's criterion gives the falling
  rate.
- **The captive regime reproduces Park's second case.** When the price follows cost down, so
  that the gains of productivity go to the buyers, both criteria give a rising capital
  intensity and a falling rate: even the all-profit-rate industry ends in the conflict zone
  (73 % of seeds). The two rules can no longer be told apart, which is why the contest is
  nearly even there.
- **A side effect to report.** At the default, with a given r̄, the victory of the unit-cost
  rule makes the good dearer in the long run (107 against 84): the cost leader wins the price
  war and the buyers pay for the heavier capital afterwards. It is the single-industry face
  of the falling rate, and it should be said in the report.

## 3. Literature review

Written for sections 2.1 to 2.4 of the draft and for the baseline. Economic terms are given
once in French.

### 3.1 The law and Okishio's theorem (draft 2.1 and 2.2)

Marx's law of the tendential fall of the rate of profit (baisse tendancielle du taux de
profit) rests on mechanisation raising capital per worker faster than the rate of
exploitation. Okishio (1961) showed that, at a given real wage, a technique that raises the
innovator's rate at current prices raises the general rate once prices adjust. Roemer (1979)
extended the result to fixed capital. Two lines of qualification followed.

- **The real wage.** The theorem compares two positions at the same real wage. If the wage
  rises with productivity the rate can fall with viable techniques: Laibman (1982, at a
  constant rate of exploitation), Foley (1986), and the "Marx–Okishio threshold" of the
  textbooks (Basu 2021).
  Basu (2026) restates it by closure: constant real wage, constant wage share, constant
  unemployment rate. With a constant wage share the equilibrium rate can fall after viable
  capital-using, labour-saving change. Duménil and Lévy (1995, 2003) get "trajectories à la
  Marx" from a neutral innovation set and a rising wage.
- **The structure of production and of the market.** Salvadori (1981) and Bidard (1988) give
  counter-examples with joint production. Alberro and Persky extend the theorem to fixed
  capital (1979) and study its revaluation and scrapping under technical change (1981).
  Skott (1992) shows that the conclusion need not hold under imperfect competition, and
  Michl (1994) gives three models with imperfect competition in which the rate declines to
  a steady state. Van Parijs (1980) follows the law up to Shaikh's defence and judges what
  is left of it.

What this gives the report: "the rate falls" is a statement about a closure. Okishio's is the
constant real wage, and the model's default is neither that one nor the constant wage share.

### 3.2 Shaikh's critique and the choice of technique (draft 2.3)

Shaikh (1978) argues that with fixed capital the profit margin and the profit rate part, and
that under price-cutting competition firms take the lowest unit cost even at a lower rate.
Nakatani (1980) replies that the price war does not make the lower-rate technique the better
choice (not read here: to check before it is cited); Shaikh (1980) answers that the firm
with the lower unit cost can always cut the price to a point where it earns more than its
rivals. Roemer (1979) rejects the unit-cost choice as inconsistent with profit
maximisation. Three later texts frame the question as the model does.

- **Selection.** Baldani and Michl (2000) make the adoption a prisoner's dilemma in an
  oligopoly: each firm gains by adopting, and the industry's profit falls. Michl (2023)
  names the two viability conditions and asks for a game-theoretic bridge.
- **Evolution of technique.** Park (2001) simulates both criteria on an innovation set and
  finds the result quoted in section 2. Shaikh (2016, pp. 322–324) rebuilds it with unit
  operating cost and unit capital cost: with a neutral set real competition gives a rising
  rate, with a set skewed towards capital a falling one.
- **Evidence on the criterion.** Duménil and Lévy (2005) and Park (2005) test the
  profit-rate criterion on data. Michl (2023, section V) sums up the wider record: the
  standard viability condition is met by a wide margin in OECD samples, with exceptions
  once developing economies are added (Basu 2010; Campbell and Tavani 2019). Observations
  that meet it are also compatible with the unit-cost rule, so only violations inform.

What this gives the report: aggregate technical change mostly passes Okishio's test. A
baseline in which an all-unit-cost industry fails it in 94 % of seeds (β = 1.5) is at the
strong end of the bias; at β = 0.5 it passes in every seed and the rules still part on
individual orders.

### 3.3 Real competition and the time path of the rate (draft 2.4)

In Shaikh (2016, ch. 7) competition within an industry spreads profit rates, since the price
is set by the lowest reproducible cost, and competition between industries equalises the rate
on new investment of the regulating capitals (capitaux régulateurs), in a turbulent way.
Average rates are not equalised. Two bodies of work bear on the baseline.

- **Theory of gravitation.** Duménil and Lévy (1987) and Flaschel and Semmler (1987) model
  the cross-dual adjustment in which capital moves towards high rates and prices respond to
  excess supply; Nikaido (1983) shows it need not converge. Convergence needs a quantity
  response that is fast enough. In the model that response is entry and the withdrawal of
  the reserve; remove it and the centre of gravity is lost, which is the captive regime.
  Cogliano, Veneziani and Yoshihara (2022) and Wright (2008) obtain classical prices as
  emergent centres in agent-based economies with mobile capital.
- **Evidence.** Mueller (1986) and Mueller and Cubbin (1990) find firm profit differences
  that persist for decades. Glick and Ehrbar (1990) identify only a weak equalisation of
  industry rates in post-war data. Tsoulfidis and Tsaliki (2005) argue, on Greek manufacturing, that
  equalisation shows on the incremental rate of regulating capital and not on average rates. Vaona (2011) finds only
  mixed support across OECD industries, which he attributes to limits on capital mobility;
  the support is stronger for regulating capital in manufacturing (Vaona 2012), and
  Tescari and Vaona (2014) find gravitation of regulating rates in US manufacturing.
  Scharfenaker and Semieniuk (2016) describe a stable, peaked distribution of firm rates.

What this gives the report: the fact to match is a rate on new plants that gravitates and
average rates that stay apart. E0 already reads it that way (rate of new plants 0.159,
industry rate 0.132, spread 0.12). A sector rate stuck at zero beside a general rate of 16 %
has no counterpart in this literature outside periods of crisis.

### 3.4 How strong is selection?

The replicator comes from Silverberg, Dosi and Orsenigo (1988) and the Schumpeter-meeting-
Keynes family (Dosi, Fagiolo and Roventini 2010). The evidence is that market selection is
weak. Bottazzi et al. (2010) find, on Italian and French firms, that efficiency differences
turn into lasting profitability differences while growth is barely related to either. Dosi et
al. (2015) reach the same reading for the United States and Europe. Foster, Haltiwanger and
Syverson (2008) find that selection works on profitability rather than on physical
productivity, and that young plants charge lower prices. A χ of 1 or less is on the side of
this evidence; nothing in it supports 5.

### 3.5 When the price stays below the price of production: sunk capital and overcapacity

The teammates' regime is a known one, and its condition is always the same: capital that
cannot or does not leave.

- **Theory.** Brenner (1998) explains falling manufacturing profitability by lower-cost
  entrants cutting prices while incumbents, whose fixed capital is sunk, stay as long as they
  cover their circulating costs: overcapacity and a lower rate for all. Crotty (1993, 2002)
  describes "coercive competition" and chronic excess capacity where exit is blocked.
  Shaikh (1999) objects that a fall in one sector's relative price does not by itself lower
  the general rate; Duménil and Lévy (2002) dispute Brenner's reading of profit-rate
  differentials. Steindl (1952) and Sylos-Labini (1962) are the older statements of price
  wars limited by the exit of marginal firms.
- **Steel.** In US steel between 1963 and 2002 the minimill displaced integrated producers;
  that reallocation gave about a third of the rise in productivity, and mark-ups fell by half
  (Collard-Wexler and De Loecker 2015). Today the OECD projects excess capacity of 721
  million tonnes by 2027, utilisation towards 70 %, prices at historic lows and profitability
  sharply down since 2021, and ties the persistence to subsidies (OECD 2025).
- **Solar modules.** In 2023 the utilisation of manufacturing capacity fell to 60 % and spot
  module prices by about half (IEA, January 2024). In 2024 prices went below 0.10 dollar a
  watt, below cost for most producers, who reported losses (BloombergNEF, third quarter
  2024; IEA-PVPS 2024).
- **US manufacturing in the 1890s.** Lamoreaux (1985) describes price wars in new,
  capital-intensive industries during the depression, ended by consolidation.

What this gives the report: the falling-price, low-profit industry exists, where a subsidy, a
state owner, a sunk plant or a soft budget keeps capital in. It is the right name for the
captive cell: a scenario with blocked exit, to be reported beside the baseline. In these
sectors the price falls with cost and the profit rate is depressed by overcapacity; none of
them is evidence about the choice of technique.

### 3.6 The bias of technical change

The Marx-biased pattern, labour productivity rising and capital productivity falling, is
documented by Foley, Michl and Tavani (2019), Marquetti (2003), Duménil and Lévy (1995, 2003)
and Basu (2010), with phases in which capital productivity rises instead. Salter (1966) shows
that across industries relative prices follow unit costs. In the model the price of
production falls with a design only when its capital cost rises by less than
ucs / ((δ + r̄) κ) times its cost saving. That threshold is 1.80 on technique C, where 41 %
of the draws at β = 1.5 and σ = 0.8 lie above it, and it falls as techniques get heavier: it
is about 0.2 on the regulating technique at the end of an all-unit-cost run. That is why the
default shows unit cost down by a third and a price of production that hardly moves. It is a
property of β, not of gravitation.

### 3.7 Choosing a baseline without data

Fagiolo, Moneta and Windrum (2007) and Fagiolo et al. (2019) describe indirect calibration:
list the stylised facts first, keep the region of parameters that reproduces them, then run
the experiment inside it. Grimm et al. (2005) call it pattern-oriented modelling and insist
on several patterns at different scales. Both exclude tuning the parameters on the outcome
of interest: a baseline chosen because the profit rate falls in it can no longer test
anything about the profit rate.

## 4. A way to settle the baseline

1. **Write the closure in the paper.** The introduction already says it: one industry in a
   wider economy, r̄ given. Then the rate of new plants gravitates around r̄ by construction
   of the question, and the tendency of the rate to fall is read on the price of production
   and on the rate at the initial price.
2. **Fix the baseline on facts that are not the outcome.** Proposed list, each with its
   source: the rate of new plants gravitates, average rates stay apart (3.3); the price falls
   where unit cost falls (Salter; 3.6); cumulated technical change passes the standard
   viability test more often than not (Michl 2023); demand is served (the E0 line); selection
   is weak (3.4). The default meets the first, fourth and fifth; β decides the second and
   third.
3. **Decide β on the second and third fact.** At β = 0.5 the price falls from 97 to 75, the
   rate of new plants is 0.166, the unit-cost rule wins 0.88. At β = 1.5 the price is flat
   and an all-unit-cost industry fails the viability test in 94 % of seeds. One is the main
   specification and the other the strong-bias case; E2 already holds both.
4. **Make capital mobility a treatment, stated before the runs.** Three levels that exist as
   options: open (default), partial (payout = 0), captive (payout = 0, reserve = always).
   Each side writes its prediction first. The first table of this note is that experiment.
5. **Add two read-outs, no rule.** The price of production of the regulating technique, and
   its rate at the initial price, by population. They show the fall under the unit-cost rule
   (0.16 to 0.14) and the rise under the profit-rate rule (to 0.24) in the default.
6. **Keep χ at 1 or below**, and say why: the evidence of 3.4 and the bound of the discrete
   replicator.

A further step would change the model, so it is only named: let r̄ follow the rate of the
regulating technique at a fixed price, the one-sector reading of Shaikh's two-sector example.
Gravitation would then take place around a centre that falls under one rule and rises under
the other. It is a new option and a departure to register.

## 5. Remarks on the draft introduction

- **"Marx, 1993".** The law is in volume 3 of *Capital* (Penguin edition 1981, reprinted
  1991). 1993 is the date of the Penguin *Grundrisse*. To check against the bibliography.
- **"our findings support the argument of Shaikh".** The results of version 4 are
  conditional: 0.92 where only a cost leader cuts, 0.23 under universal undercutting, drift
  under the accelerator and when the profit-rate rule judges at the price of production.
  The sentence should carry the condition.
- **"abstracts away from feedback … to the economy-wide rate of profit".** This is the
  closure of point 1; the two read-outs of point 5 are what the paper can say about the law.
- **"Standard Interpretation".** Duménil and Lévy (2005, p. 209) give the profit-rate
  criterion to Marx and the classics; the theorem is Okishio's. "Profit-rate rule" is safe.

## 6. Sources and their status

In the library `perso` unless noted. "PDF" means the text was opened for this note.

| Source | Zotero | Status |
| --- | --- | --- |
| Shaikh 2016, *Capitalism*, ch. 7 | BMKVYW2U | PDF, pp. 318–324 read for this note |
| Michl 2023, *New School Economic Review* | FX3M6W5I | PDF, section V read |
| Basu 2026, *RRPE* | EQUSWFVB | Abstract and introduction |
| Okishio 1961; Roemer 1979; Shaikh 1978, 1980 | 3ZDE32J4; TX2DFFI7; J9AEUKMD; EECWZJXJ | As in `v4-literature-check.md` |
| Nakatani 1980, *CJE* | FTABRQQA (inbox) | Not read: to read before 2.3 is written |
| Baldani and Michl 2000; Park 2001; Park 2005; Duménil and Lévy 1995, 2003, 2005 | 3R3LBMWT; 9CUFY49Q; 2CCFW5GB; 48U7VRQQ; KJXJMRR2; LWGHAJ9B | Abstracts; Park 2001 through Shaikh 2016, p. 322 |
| Basu 2010; Basu 2021; Foley, Michl and Tavani 2019 | A8RD2HN7; HGSYEJ78; V98SW3XI | From memory |
| Cogliano et al. 2022 (two texts); Wright 2008 | NY6KI3CY; DRGHDBSG; 3FL6ZR8T | Abstracts |
| Mueller and Cubbin 1990; Scharfenaker and Semieniuk 2016; Tsoulfidis and Tsaliki 2019 | 6JP3A238; HZYQUZC9; C69II6XZ | From memory |
| Silverberg et al. 1988; Dosi et al. 2010; Dosi et al. 2015; Foster et al. 2008 | EBVLD2YA; HHWNJFLG; TVXQ9DA7; QX5VTYKC | From memory |
| Crotty 2002; Steindl 1952; Sylos-Labini 1962; Salter 1966 | HK3JVAM9; LX36ID6E; 2G3FQ2E5; FCUBTW7P | From memory |
| Collard-Wexler and De Loecker 2015, *AER* | V6ZR27GW | Abstract and introduction of the working paper |
| Fagiolo, Moneta and Windrum 2007 | XKW5NTIY | From memory |
| Bottazzi et al. 2010, *ICC* 19(6), doi 10.1093/icc/dtq063 | Not in the library | Abstract |
| Vaona 2011, *IRAE* 25(4), doi 10.1080/02692171.2010.529429; Vaona 2012, *JPKE* 35(1), doi 10.2753/pke0160-3477350107; Tescari and Vaona 2014, *Metroeconomica* 65(3), doi 10.1111/meca.12043 | Not in the library | Abstracts |
| Tsoulfidis and Tsaliki 2005, *RRPE* 37(1), doi 10.1177/0486613404272324 | Not in the library | From memory |
| Duménil and Lévy 1987, *CJE* 11(2), doi 10.1093/oxfordjournals.cje.a035020; Flaschel and Semmler 1987, *Manchester School* 55(1), doi 10.1111/j.1467-9957.1987.tb01287.x; Nikaido 1983, *Zeitschrift für Nationalökonomie* 43(4), doi 10.1007/bf01283185 | Not in the library | From memory |
| Mueller 1986, *Profits in the Long Run*, doi 10.1017/cbo9780511664731; Glick and Ehrbar 1990, *Economic Inquiry* 28(1), doi 10.1111/j.1465-7295.1990.tb00808.x | Not in the library | Abstracts |
| Brenner 1998, *New Left Review* I/229; Shaikh 1999, *Historical Materialism* 5(1), doi 10.1163/156920699100414481; Duménil and Lévy 2002, *RRPE* 34(1), doi 10.1177/048661340203400104 | Not in the library | Secondary accounts only |
| Crotty 1993, *RRPE* 25(1), doi 10.1177/048661349302500101; Lamoreaux 1985, doi 10.1017/cbo9780511665042 | Not in the library | From memory |
| Laibman 1982, *RRPE* 14(2), doi 10.1177/048661348201400209; Michl 1994, *RRPE* 26(4), doi 10.1177/048661349402600403 | Not in the library | Abstracts |
| Foley 1986, *Understanding Capital*, doi 10.4159/9780674037045 | Not in the library | From memory |
| Alberro and Persky 1979, *RRPE* 11(3), doi 10.1177/048661347901100305; Van Parijs 1980, *RRPE* 12(1), doi 10.1177/048661348001200101; Skott 1992, *RRPE* 24(1), doi 10.1177/048661349202400106 | Not in the library | Abstracts |
| Salvadori 1981, *CJE* 5(1), doi 10.1093/oxfordjournals.cje.a035469 | Not in the library | From memory |
| Bidard 1988, *CJE* 12, doi 10.1093/oxfordjournals.cje.a035065; Alberro and Persky 1981, *RRPE* 13(2), doi 10.1177/048661348101300204 | Not in the library; CrossRef notice faulty (author missing; authors doubled): to add by hand in `perso` | From memory; abstract |
| Marquetti 2003, *JEBO* 52(2), doi 10.1016/s0167-2681(03)00021-0 | Not in the library | From memory |
| Campbell and Tavani 2019, *Metroeconomica* 70(4), doi 10.1111/meca.12247 | CJ8IHV92 | Through Michl 2023 |
| Grimm et al. 2005, *Science* 310, doi 10.1126/science.1116681; Fagiolo et al. 2019, doi 10.1007/978-3-319-70766-2_31 | Not in the library | From memory |
| OECD 2025, *Steel Outlook 2025* | Not in the library | Executive summary and press release |
| IEA, January 2024 (as reported by S&P Global); BloombergNEF, third quarter 2024, and IEA-PVPS 2024 (as reported by pv magazine) | Not in the library | Press accounts, not the reports |

Every DOI above was resolved through CrossRef on 13 November 2026. The 25 references "not in
the library" with a sound notice were created in the Zotero Inbox, collection
`2026-11-13_baseline-literature-review`, to be dragged into `perso`. Not created: Bidard 1988
and Alberro and Persky 1981 (faulty notices), and the OECD, IEA and BloombergNEF reports
(no DOI).

Web sources for 3.5:

- OECD, *Steel Outlook 2025*, executive summary:
  <https://www.oecd.org/en/publications/oecd-steel-outlook-2025_28b61a5e-en/full-report/executive-summary_3618ca77.html>
- OECD press release, 27 May 2025:
  <https://www.oecd.org/en/about/news/press-releases/2025/05/surging-excess-capacity-threatens-steel-market-stability-employment-and-decarbonisation-plans.html>
- S&P Global, 12 January 2024, on the IEA's solar supply glut:
  <https://www.spglobal.com/commodity-insights/en/news-research/latest-news/electric-power/011224-world-stuck-in-major-solar-panel-supply-glut-module-prices-plummet-iea>
- pv magazine, 30 August 2024, on BloombergNEF's outlook:
  <https://www.pv-magazine.com/2024/08/30/solar-module-installations-could-hit-592-gw-in-2024>
- Collard-Wexler and De Loecker, working paper: <https://pages.stern.nyu.edu/%7Eacollard/Steel.pdf>
- Bottazzi et al., working paper page: <https://www.lem.sssup.it/WPLem/2009-13.html>
- Vaona 2011: <https://econpapers.repec.org/RePEc:taf:irapec:v:25:y:2011:i:4:p:465-502>

## 7. To reproduce

```bash
python3 docs/literature/scripts/closures.py regimes 150 default payout0 always captive
python3 docs/literature/scripts/closures.py regimes 150 captive_none captive_neutral chi2 chi5
python3 docs/literature/scripts/closures.py regimes 150 chi5_payout0 chi5_captive beta05 beta05_captive
python3 docs/literature/scripts/closures.py populations 150 default captive
python3 docs/literature/scripts/closures.py populations 150 beta05
```

The script reads the model and writes nothing. It was run with Python 3.10, where the tree
asks for 3.12: the figures should be rerun once on the group's interpreter.
