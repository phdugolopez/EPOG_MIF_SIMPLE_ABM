# ABM final phase: simplified model, analysis plan and report outline

Proposal of 9 November 2026, for the group to discuss before the code is rebuilt. Copy of the
shared doc (<https://claude.ai/artifact/2d7NxURvJpcK6YuXRm8s3b>), which holds the live version,
the two figures and the decision tracker. Every number comes from the v2 sensitivity runs
(`outputs/sensitivity/cells.csv`, stages 1–4) and from `sensitivity-discussion.md`. Nothing here
is a decision until it is recorded in `v3-choices.md` (`choices.md` is the version 2 record,
frozen on 9 November). Revised on 9 November after a review against the literature and the v2
runs: four decisions (mechanism test, financing of replacement, status of the v2 numbers, E7) are
in the last rows of the decision table, and the group still has to confirm them. Revised again on
10 November after the v2 pilot (section "Pilot in v2"): the depreciation reserve is released only
when new plants earn the general rate.

## At a glance

Rebuild the model around the one equation that separates the two rules, and write the report as
"which rule wins, and where" (question A), explained by "the price at which profitability is
judged" (question B).

- **Prediction to retest.** Under Marx-biased technical change (progrès technique biaisé à la
  Marx), v2 found that selection favours the unit-cost rule beyond drift: 0.81 of seeds at the v2
  defaults (500 seeds), 0.94 under the innovation set (200 seeds), against 0.38–0.56 for the
  neutral controls. Those runs scrap on unit cost with no maximum age; the v2 cell closest to the
  rebuilt model (innovation set, scrapping on operating cost) gives 0.75, still beyond drift. The
  v2 pilot of 10 November, at the rebuilt model's settings, gives 0.94–0.97 under cost-edge
  cutting, with 0.72–0.79 of final capacity (section "Pilot in v2").
- **Mechanism.** The profit-rate rule judges techniques at the current market price. Above the
  price of production (prix de production) its hurdle is high (0.094 against r̄ = 0.05), so it
  refuses capital-using, cost-reducing designs and keeps dearer plants that price cutting then
  punishes. Judged at prices of production its hurdle falls to r̄, not to 0: at r̄ = 0.05 the
  contest goes to drift under the categories rule (0.48–0.53) and the advantage shrinks but stays
  under the innovation set (0.94 → 0.78); at r̄ = 0.16 it does not shrink (0.64 → 0.715).
- **Where the profit-rate rule wins.** In v2, only where accumulation selects instead of price:
  closed entry (r̄ = 0.16), investment out of retained earnings, growing demand, and only under
  the categories rule (0.32 at 500 seeds). The same corner gives 0.98 to the unit-cost rule under
  the innovation set. The reversal also rests on v2's markup floor and scrapping test: with the
  unit-cost floor and scrapping on operating cost, as in the rebuilt model, the same cell is at
  drift (0.43, 200 seeds). In the pilot the profit-rate rule wins under systematic cutting at r̄ =
  0.16 (0.10–0.19), where the price channel is nil.
- **Model.** Core + entry/exit: one industry, Shaikh's three techniques, six firms in identical
  pairs. About 600 lines and five switches, against about 5,100 lines and 25 switches in v2.
- **Treatments.** Bias of technical change, evaluation price, price-war regime, investment rule,
  level of the general rate, demand growth.
- **Analysis.** Mixed population against two neutral controls, share of seeds won with Wilson
  intervals, whole-run decomposition into price, accumulation, entry and exit.
- **Sensitivity.** Morris screening on 10 continuous parameters, plus five discrete robustness
  checks: plant life, categories rule, diffusion, homogeneous start, number of firms.
- **Deliverables.** A 10-page report in seven sections and a 13-slide talk. The 20 November
  seminar shows the v2 results and the plan; 1 December shows the rebuilt model.

## Answers to the group's open questions

The technical-change rule decides the answer; demand and r̄ matter only through entry and
accumulation.

### Which technical-change rule?

Use the innovation set (marx, bias β) as the model, the neutral set and "no draws" as its
controls, and the categories rule as a labelled robustness check.

- Without draws the contest is at drift (0.51, interval 0.44–0.58). Every advantage comes from
  how the two rules treat new designs.
- The categories rule fixes three things by construction: every design cuts unit cost, half of
  them sit in the conflict zone (q = 0.5) whatever the price, and a conflict design's capital per
  unit is drawn up to where unit cost barely falls.
- The innovation set draws a design from the reference technique alone. The conflict zone becomes
  an outcome of the draw and of the price (realised share 0.14–0.19 at β = 1.5–3).
- Literature: Shaikh (2016, pp. 322–324) and Michl (2023, pp. 37–41) treat Marx-biased change as
  the empirical pattern. Duménil & Lévy (1995, p. 214) start from neutral change and get the bias
  through rising wages, which a fixed wage rules out here. Park (2001) simulates both criteria in
  that framework (reported in Shaikh 2016, p. 322; not yet opened).
- Consequence: both reversals exist only under categories. In the closed corner there,
  profit-rate firms seldom order a dearer technique (6–10 % of orders) while unit-cost firms take
  every conflict design, gaining little cost and much capital. Why the innovation set behaves
  otherwise in the same corner (0.98) is one diagnostic for E4.

Share of seeds won by the unit-cost rule (95 % Wilson interval; seeds). Neutral controls range
from 0.38 to 0.55 across these cells; below that band the profit-rate rule wins. The closed
corner is leader-follow pricing, retained earnings, 1 % demand growth and r̄ = 0.16.

| Technical-change rule | Default cell | Closed corner |
| --- | --- | --- |
| No draws | 0.51 (0.44–0.58; 200) | not run |
| Neutral set | 0.78 (0.71–0.83; 200) | 0.75 (0.66–0.82; 100) |
| Categories (v2 default) | 0.81 (0.77–0.84; 500) | **0.32** (0.28–0.36; 500) |
| Marx β = 0.5 | 0.80 (0.73–0.85; 200) | not run |
| Marx β = 1.5 | 0.94 (0.90–0.97; 200) | 0.98 (0.97–0.99; 500) |
| Marx β = 3 | 0.97 (0.93–0.98; 200) | 1.00 (0.96–1.00; 100) |

### Why does the unit-cost rule win?

Three steps, each measured in v2:

1. **Evaluation price.** The profit-rate firm's hurdle h is the best rate at its own current
   price: 0.094 on average in the base cell, against r̄ = 0.05. With h high, the choice rule
   ucs + (δ + h)κ penalises capital, so it turns down capital-using, cost-reducing designs. In the
   base cell 51 % of its orders are not the cheapest technique it knows (`okishio_dearer`);
   across stage 2 seeds, 49 % where it loses against 17 % where it wins.
2. **Price selection.** Prices fall toward the lowest unit cost: the leader is the lowest-cost
   firm in 94 % of periods. In the base cell the unit-cost label gains +0.25 of sales share
   through prices and +0.28 of capacity share through the exits of profit-rate firms;
   accumulation nets to zero.
3. **Realised rates.** The rule that maximises the rate (taux de profit) at the current price
   realises the lower one: 4.5 % against 8.4 %. The micro premise of Okishio's theorem fails out
   of equilibrium.

The test that brackets the mechanism: judge the profit-rate rule at the price of production of the
regulating capital (capital régulateur) instead of its own price. Its hurdle then falls to r̄, and
the rule minimises uc + r̄κ, Sraffa's criterion (Shaikh 2016, p. 320 n. 36), not the unit cost. At
r̄ = 0.05 the advantage disappears under the categories rule (0.81 → 0.53 under real competition,
0.71 → 0.48 under leader-follow) and shrinks under the innovation set (0.94 → 0.78, still beyond
drift). At r̄ = 0.16 (categories) it does not shrink (0.64 → 0.715): on Shaikh's menu D2 has the
higher rate only below a price of about 85, and its price of production is 82.9 at r̄ = 0.05 but
100.3 at r̄ = 0.16 (at D2's price of production the higher-cost technique C again has the higher
rate, Shaikh 2016, p. 316). The advantage therefore has two parts: the market price standing above
the price of production, and the r̄κ term that remains at it. This is question B.

### Is demand important?

Demand allocation yes, the demand level hardly.

- The replicator on price is the price channel itself: without it there is no price selection.
  Its form and intensity do not matter (logit with η = 1 equals χ = 1; χ from 0.25 to 4 gives
  0.71–0.79).
- Level and growth move the result only through entry and accumulation. Factorial main effects:
  static 0.79, growing 1 % 0.81, initially unmet 0.86.
- At 3 % growth the result goes to drift (0.43 at 500 seeds). Entry opens wide (63.7 entrants,
  44 firms at the end), and entrants copy rules by market share, a neutral process.
- With entry closed, growth feeds the accumulation channel: the leader-follow corner gives 0.32
  with 1 % growth and 0.51 with static demand.
- Unmet demand stays below 3 % and does not move with the winner (correlation 0.06).
- Keep exogenous demand with growth g ∈ {0, 1 %}. Drop the unmet start and 3 % growth.

### Is the exogenous profit rate important?

Yes, as an entry gate rather than a price. In the core model r̄ does two jobs: entry, with
probability θ·max(0, r_new − r̄)/r̄, and the price of production uc* + r̄κ* used in question B. In
E3 the two jobs move together: r̄ = 0.16 raises the price of production used at λ > 0 and also
closes entry, so that arm is read against the E4 cells at λ = 0 (decided 9 Nov; a separate rate
for the evaluation price was considered and not kept). With the replacement condition of 10
November r̄ gets a third job, the centre of gravity of the profit rate: in the pilot the industry
rate is 6 % at r̄ = 0.05 and 14–15 % at 0.16, and entry stays active at both, so the report
presents r̄ as the level of the general rate, not as open against closed industry.

- At r̄ = 0.05 the industry rate is above r̄ in 95 of 100 periods: entry is open. At 0.16 it is
  above in fewer than 3: entry is closed.
- Stage 1: 0.81 → 0.64 from 0.05 to 0.16. In the factorial the average effect is small (0.83
  against 0.80) and large only under categories (0.70–0.74 → 0.59–0.64).
- Both reversals need r̄ = 0.16. Present r̄ as "open against closed industry": Shaikh's
  equalisation of rates on new investment through entry (2016, pp. 265, 296).
- Keep it exogenous, since the model is one industry in a given economy. The economy-wide Okishio
  claim (the general rate once new prices of production settle) cannot be tested here; the
  report should say so.

## Research questions and hypotheses

- **RQ1 (A).** In a mixed population of unit-cost firms (Shaikh, h = 0) and profit-rate firms
  (Okishio, h = best rate at the evaluation price), which rule does market selection favour
  under Marx-biased technical change?
- **RQ2 (A).** How does the answer depend on the price-war regime (guerres des prix), the
  investment rule, open or closed entry, and demand growth?
- **RQ3 (B).** Why does the winner win: how much of the advantage comes from the price at which
  the profit-rate rule judges techniques, and how much from the general rate that stays in its
  hurdle at prices of production?

| # | Hypothesis | Source | Experiment | v2 evidence |
| --- | --- | --- | --- | --- |
| H1 | The unit-cost rule wins under price competition; the lowest-cost firm leads prices | Shaikh 2016, Table 7.3, pp. 313–317 | E1, E2 | Met: 0.81 (categories), 0.94 (innovation set); pilot 0.94–0.97 |
| H1′ | The profit-rate rule cannot lose systematically: no capitalist adopts a technique that lowers the rate at current prices | Roemer 1979, pp. 379 (cost-reducing innovations), 386 (the criterion with fixed capital, at current prices); Duménil & Lévy 2005, p. 209 (more profitable at going prices: Marx's and the classics' criterion) | E1 | Fails as a statement about who survives |
| H2 | The criteria conflict only for capital-using, cost-reducing designs, so the advantage grows with the Marx bias | Shaikh 2016, pp. 315, 318; Michl 2023, pp. 47–48 | E2 | Partly: no draws 0.51; β = 0.5, 1.5, 3 give 0.80, 0.94, 0.97; but the neutral set, which contains such designs, already gives 0.78 |
| H3 | With profit-financed investment and closed entry, selection runs through accumulation and can favour the profit-rate rule | Nelson & Winter 1982, pp. 17, 19; Duménil & Lévy 1995, p. 217 | E4 | Met under categories and v2's markup floor only: 0.32, and 0.85 with the accelerator; at drift (0.43) with the unit-cost floor and scrapping on operating cost; pilot: 0.10–0.19 under systematic cutting at r̄ = 0.16 (innovation set) |
| H4 | Systematic price cutting narrows the margin p − uc, hence the hurdle and the conflict zone, so the advantage shrinks | Group conjecture (review-v2, section 4) | E4 | Mixed: 0.81 → 0.71 at the defaults, but 0.79 against 0.84 on average in the factorial |
| H5 | Judged at the price of production, the profit-rate rule's hurdle falls to r̄: the advantage shrinks, and vanishes only where r̄κ is too small to change the choice | Shaikh 2016, pp. 315–317, 320 n. 36, 321 | E3 | Partly: categories 0.81 → 0.53 and 0.71 → 0.48 (drift); innovation set 0.94 → 0.78 (beyond drift); r̄ = 0.16 0.64 → 0.715 |
| H6 | Under price cutting the lowest-cost technique has the highest sustainable rate, so the profit-rate adopter does not realise the rate it maximises | Shaikh 2016, pp. 313–317 | E1, E5 | Met: 4.5 % against 8.4 % in the base cell |

Not tested, and the report should say so: Okishio's theorem about the general rate of profit,
since r̄ is exogenous and the money wage is the numéraire. Nor H7, that neutral, local innovation
selected at a rising wage produces Marx-biased change (Duménil & Lévy 1995, p. 214; Park 2001): at
a fixed wage v2's neutral set gives capital-saving change, Marx-biased in 0 % of seeds. E7 was
dropped on 9 November and the question goes to the discussion as an extension.

## The simplified model (core + entry/exit)

Six steps a period and one rule that differs between the types; v2's defaults are kept wherever v2
showed a choice matters, plus a finite plant life.

**Setting.** One industry in a given economy: money wage = numéraire (w = 1), exogenous demand
D_t = D_0(1 + g)^t, exogenous general rate r̄, δ = 0.10. A technique j is a pair (ucs_j, κ_j):
operating cost and capital per unit of normal output, with unit cost uc_j = ucs_j + δκ_j. Plants
have one technique and a fixed size S = 20. The initial industry is Shaikh's C, D1 and D2 (2016,
Tables 7.10–7.11), each given to one unit-cost and one profit-rate firm: six firms, identical
within pairs, capacity 760 against demand 674.7.

**The one rule that differs** (choice of technique, choix de technique). At every order, for
investment or entry, a firm picks

```latex
j^{*}_{i} = \arg\min_{j \in M_t} \big[\, ucs_j + (\delta + h_i)\,\kappa_j \,\big]
```

```latex
h_i = \begin{cases} 0 & \text{unit-cost rule (Shaikh)} \\ \max\Big(0,\ \max_{j \in M_t} \dfrac{p^{e}_{i} - uc_j}{\kappa_j}\Big) & \text{profit-rate rule (Okishio)} \end{cases} \qquad p^{e}_{i} = (1-\lambda)\,p_{i,t} + \lambda\,\big(uc_R + \bar r\,\kappa_R\big)
```

With h equal to the best rate at p^e, the argmin is the technique with the highest rate at p^e,
so one line covers both rules. λ = 0 is v2 (own current price); λ = 1 is the price of production
of the regulating technique R, the lowest unit cost in operation (v2's
`HURDLE_PRICE = "regulating"`). λ is the knob of question B.

**Schedule.**

1. **Pricing.** Each firm sees last period's lowest price R. After a shortage (demand above normal
   capacity) it moves up to the next higher rival price. Otherwise it undercuts to (1 − c)R, c =
   0.02, if it has spare capacity (last period's utilisation below 1) and, under *cost-edge
   cutting* (real competition, the default), a unit-cost edge over a firm posting R; under
   *systematic cutting* (leader-follow) spare capacity is enough. Else it follows R. Floor in both
   regimes: the unit cost of its best plant. The share of periods with a cut is recorded as the
   price-war frequency.
2. **Demand.** Shares follow the replicator below with E = 1/p and χ = 1. Sales are capped by
   offered capacity; unserved demand goes pro rata to firms with spare capacity, the rest is lost.
3. **Production and accounts.** Plants run cheapest first, up to normal capacity, with no
   overtime. Profit after depreciation by time; dividends 0.5 × max(0, profit). No debt, interest
   or bankruptcy.
4. **Scrapping.** A plant retires at age T = 10 (= 1/δ), after 2 periods with the price below its
   operating cost ucs (capital is sunk), or after 2 periods idle. No replacement of working
   plants.
5. **Technical change and investment.** Draws as below. *Retained earnings* (autofinancement, the
   default): buy as many whole plants of j* as its investible funds, still in cash, pay for:
   accumulated retained profits plus the depreciation reserves of the plants that have left
   (retired at age T, scrapped or idle), released only in periods when r^new_t ≥ r̄, the signal of
   the entry gate; otherwise the reserve is withdrawn and paid out to the rest of the economy, so
   that capital leaves the industry when new plants earn less than the general rate. Replacement
   is thus paid out of depreciation and net expansion out of profit (decided 10 Nov after the v2
   pilot: with profits alone the profit rate settles at 20 %, with the reserve always released
   near zero, with this condition around r̄). *Accelerator*: desired capacity = f_i,t·D_t / u*,
   the demand addressed to the firm before the capacity cap over a target utilisation u* = 0.9;
   buy the plants missing to reach it, if cash allows. Without overtime, sales never exceed
   capacity, so a sales-based accelerator would never expand.
6. **Entry and exit.** One entrant with the probability below, of size 0.5 × the average
   incumbent's capacity, technique chosen by its own rule on the public menu, rule copied from an
   incumbent drawn by market share and flipped with probability μ = 0.02, price by the common
   rule. Exit when the share falls below 1 % or no capacity is left; at least 2 firms remain.

```latex
f_{i,t} = f_{i,t-1}\Big[1 + \chi\,\frac{E_{i,t} - \bar E_t}{\bar E_t}\Big], \qquad \bar E_t = \sum_j f_{j,t-1}\,E_{j,t}, \qquad E_{i,t} = 1/p_{i,t}
```

```latex
ucs_n = (1-a)\,ucs_o, \quad \kappa_n = (1+k\,a)\,\kappa_o, \quad a \sim U(0, A], \quad k = \beta\, e^{\sigma z},\ z \sim N(0,1)
```

```latex
\Pr(\text{entry}_t) = \min\Big\{1,\ \theta\,\frac{\max(0,\ r^{new}_t - \bar r)}{\bar r}\Big\}
```

**Technical change.** Each period, with probability π = 0.2, a firm draws one design from its best
known technique o (equation above; A = 0.05, σ = 0.8, β = 1.5). It keeps the design if its own
rule prefers it to o; a design becomes public 2 periods after its first plant. β = 0 gives pure
operating-cost cuts, which both rules adopt. The neutral set (direction uniform on the circle) and
the categories rule stay as robustness switches of about 20 lines each; "no draws" is the null.
r^new_t is the capacity-weighted realised rate of the plants built in the last 5 periods, with θ =
5.

**Randomness and neutrality.** One random stream per firm, spawned from the run seed, so a firm's
draws never depend on its place in the list; the two controls then sit at 0.5 by symmetry (v2:
0.38–0.56 from one shared stream). The type label is read only in the hurdle and in inheritance;
one label-swap test guards this. Python 3.12 or later, since the float sum changed in 3.12.

| Parameter | Symbol | Default | Varied in |
| --- | --- | --- | --- |
| Bias of technical change | β | 1.5 | E2: 0, 0.5, 1.5, 3, neutral set, none; Morris 0.5–3 |
| Evaluation-price weight | λ | 0 | E3: 0, 0.25, 0.5, 0.75, 1 |
| Price-war regime | — | cost-edge cutting | E4: systematic cutting |
| Investment rule | — | retained earnings | E4: accelerator |
| General rate (entry gate; replacement condition; price of production at λ > 0) | r̄ | 0.05 | E3 and E4: 0.16 |
| Demand growth | g | 0 | E4: 0.01 |
| Largest operating-cost cut per design | A | 0.05 | Morris 0.02–0.10 |
| Draw probability per period | π | 0.2 | Morris 0.1–0.4 |
| Price cut | c | 0.02 | Morris 0.01–0.05 |
| Selection intensity | χ | 1 | Morris 0.25–4 |
| Payout ratio | d | 0.5 | Morris 0.25–0.75 |
| Depreciation rate | δ | 0.10 | Morris 0.05–0.15 |
| Plant size | S | 20 | Morris 10–40 |
| Entry speed | θ | 5 | Morris 1–10 |
| Mutation at entry | μ | 0.02 | Morris 0–0.05 |
| Plant life (scrapping on operating cost) | T | 10 | Robustness: 5 and 20 |
| Spread of bias | σ | 0.8 | Fixed |
| Lag before a design is public | L | 2 | Fixed |
| Target utilisation (accelerator only) | u* | 0.9 | Robustness: 0.8 and 0.95 in the accelerator cells of E4 |
| Spare-capacity threshold (pricing) | u_full | 1 | Fixed |
| Initial firms per (technique, rule) pair | k | 1 (6 firms) | Robustness: 2 and 5 (12 and 30 firms), demand scaled by k |

**Code target.** Keep the template's layout (`equations/`, `markets/`, `model/`) with about 20
equation files instead of 36, each named `equations/<step>_<equation>.py` after the loop step that
uses it (`pricing_floor.py`, `demand_replicator.py`; `common_` for definitions several steps
share, such as the unit cost), two output tables (per period and label; one summary row per run)
instead of seven, and no debug suite. About 600 lines of model and 200 of experiments.

## What to drop from version 2, and why

| v2 piece | Evidence from the sensitivity runs | Decision |
| --- | --- | --- |
| Anchor pricing (v1 rule) | Its reversal (0.26 at r̄ = 0.16) becomes a unit-cost win with operating-cost scrapping (0.90) and vanishes with the accelerator (0.47) | Drop; one sentence in the report |
| Leader-follow markup floor, monopoly cap, own shortage rule | Markup floor 0.66 against 0.83 with the unit-cost floor; operating-cost floor leaves no capacity in 81 of 200 seeds | Replace by the common floor and shortage step (group decision) |
| Logit demand | η = 1 reproduces χ = 1 to within 1e-12 | Drop |
| χ as a treatment | 0.25 to 4 moves nothing (0.71–0.79) | Fix at 1; Morris range |
| Borrowing, debt, interest, repayment, bankruptcy | No debt in any of the 500 seeds of the leader-follow twin; accelerator with or without debt 0.63 / 0.59 | Drop; "finance" becomes "investment rule" |
| Replacement of working plants | About zero replacements in every cell | Drop |
| τ, capital advanced as wages | 0 to 0.25 moves nothing under either technical-change rule | Drop |
| Hurdle floor switch, no-cut shortage branch | Inert at the defaults | Hard-code or drop |
| "Unserved" excess-demand signal, unmet start, 3 % growth | No move, or drift at 4–20 times the run time | Drop |
| Depreciation by use | No move (0.75) | Drop; depreciation by time over a plant life of 10 periods |
| Draws per investment, frontier reference, private diffusion | Per investment pushes the share to 1 by compounding; the other two move nothing | Drop; draws per period, own reference, public after 2 periods |
| Categories rule (v2 default) | Imposes the conflict share; hosts both reversals | Keep as a robustness switch |
| Collector (40 KB), schema (28 KB), 9 debug scripts | Built to debug v2 | Two output tables; keep the share decomposition |

Overtime is dropped too (decided 9 Nov): output stops at normal capacity, so demand above it goes
to firms with spare capacity or is lost. Kept although untested: idle scrapping, dividends, the
floor of 2 firms.

## Model analysis

Seven experiments, each a mixed population run against the two neutral controls on the same
seeds. Total budget about 38,400 runs, under an hour on
10 workers at v2's speed (21,600 runs in 23 minutes).

**Outcome measures.**

- **Share won**: share of decided seeds in which the unit-cost label holds more than half of
  producing capacity at t = 200, with its 95 % Wilson interval. *Beyond drift* = interval
  disjoint from both controls' intervals.
- **Final capacity share**, whose mean is reported beside the share won, and **takeover date**.
  Exact ties at one half are counted apart and left out of the share won (decided 10 Nov: with six
  stable firms the pilot had up to 73 ties in 200 seeds, which v2 counted as losses).
- **Decomposition** of the unit-cost label's capacity share over the whole run into price,
  accumulation, exit and entry terms. Whole run, not t = 100–199: in the cells that matter most
  takeovers happen before t = 100.
- **Mechanism observables**: mean hurdle of the profit-rate label; share of its orders that are
  not the cheapest known technique (`okishio_dearer`); realised profit rate by label; price over
  the regulating price of production; price-war frequency; entries.

| # | Question | Design | Seeds | Exhibit in the report |
| --- | --- | --- | --- | --- |
| E0 | Without technical change, does the industry show Shaikh's real-competition facts? | Single-rule populations, no draws: leader = lowest-cost firm, price against the regulating price of production, unequal margins and profit rates | 50 | One panel of a typical run |
| E1 | Which rule wins at the defaults? | Mixed and both controls, β = 1.5 | 500 | Typical run (prices, capacity shares) and share won |
| E2 | Does the advantage grow with Marx bias? | β = 0, 0.5, 1.5, 3; neutral set; no draws | 200 | Share won against β, controls as a band |
| E3 | How much of the advantage comes from the evaluation price (B)? | λ = 0, 0.25, 0.5, 0.75, 1 under both price-war regimes and r̄ = 0.05, 0.16: 20 cells | 200 | Share won and mean hurdle against λ, one curve per r̄ |
| E4 | Where does each rule win (A)? | Price-war regime × investment rule × r̄ (0.05, 0.16) × g (0, 1 %): 16 cells, then the same 16 under the categories rule | 200 | Two 4 × 4 heat maps |
| E5 | Through which channel does the winner win? | Decomposition of the E4 cells; within-cell regression of the profit-rate gap on `okishio_dearer` (v2: +0.075, interval 0.060–0.091) | E4 runs | Bars of the four terms in four cells |
| E6 | Can one firm of a rule invade a population of the other? | 1 firm of one rule among 9 of the other, both ways; control = the same set-up with one rule | 500 | Invasion rate against its control |

There is no docking against v2: E0 is the check that the rebuilt code behaves like an industry
under real competition before E1–E6 are read; the v2 pilot below gives the numbers to compare them
with.

## Pilot in v2 (run 10 November)

Four arms of eight v2 cells at the rebuilt model's settings were run on 10 November (4,800 runs
each, no error). They settle the financing of replacement and give the reference numbers for E1
and E4.

- **Settings.** Innovation set with β = 1.5, `SCRAP_COST = "operating_cost"`, `PLANT_LIFE = 10`,
  retained earnings; pricing (real competition; leader-follow with `LEADER_FOLLOW_FLOOR =
  "unit_cost"`) × r̄ (0.05, 0.16) × g (0, 1 %); 3 populations × 200 seeds. Arms 2 to 4 stagger the
  initial ages (addendum A3) and patch their rule in from the launch script: no file of v2 is
  changed.

| Arm | Financing of replacement | Industry profit rate | Unit-cost rule under cost-edge cutting | Under systematic cutting |
| --- | --- | --- | --- | --- |
| 1 | Retained profits only (v2 switches) | 20–21 % | 0.64–1.00 (0.64, at r̄ = 0.16 and g = 0, is not beyond drift) | 0.12–0.46; at r̄ = 0.16 up to 113 seeds of 200 end with no capacity |
| 2 | Reserve always released | 0.5–2.5 % | 0.82–0.95, but 0.53–0.56 of final capacity | Drift |
| 3 | Reserve released if the firm's own choice earns r̄ at its price | 7–8 % at r̄ = 0.05, 14–15 % at 0.16 | 0.98–1.00 at r̄ = 0.05; 0.25–0.37 at 0.16 | Drift at r̄ = 0.05; 0.02–0.04 at 0.16 |
| 4 (kept) | Reserve released if r^new ≥ r̄ | 6 % at r̄ = 0.05, 14–15 % at 0.16 | 0.94–0.97, with 0.72–0.79 of final capacity | Drift at r̄ = 0.05; 0.10–0.19 at 0.16 |

Share of seeds won by the unit-cost rule, exact ties left out (`cells.csv` keeps v2's measure,
which counts a tie as a loss).

- **Arm 1.** Capacity holds only at r = (δ + g)/(1 − d): 170–197 entries a run, and a price at
  1.77 times the price of production at r̄ = 0.05. v2 also gives every initial plant age 0, so the
  whole initial capacity retires at t = 9.
- **Arm 2.** Capacity holds (101–103 % of demand, 6 to 8 firms), but the rate falls to g/(1 − d)
  and the hurdle of the profit-rate rule to 0.01–0.03: the two rules nearly coincide.
- **Arm 3.** The condition reads the firm's own technique, and the unit-cost firms fail it more
  often (reserve released for 61 % of their plants against 81 % at r̄ = 0.16, 40 seeds). Its
  reversal under cost-edge cutting is an artefact of the condition.
- **Arm 4.** The condition is the same for every firm (reserve released for 74 % and 76 % of
  plants at r̄ = 0.05, 38 % and 40 % at 0.16, 30 seeds). The rate gravitates around r̄, the price
  stays at 0.93–1.11 times the price of production and capacity at 99–109 % of demand. At r̄ =
  0.05 the hurdle (0.06–0.08) and the dearer orders (46–65 %) are close to v2's (0.094, 51 %).
  Entry stays active (47–140 entries a run), also at r̄ = 0.16.
- **Not covered.** v2 keeps overtime and its own shortage rule, systematic cutting is v2's
  leader-follow with the unit-cost floor, and the withdrawn reserve stays in cash instead of being
  paid out. The pilot is a reference, not a docking.
- **Files.** `outputs/pilot/arm1` to `arm4` of the v2 checkout (`runs.csv`, `cells.csv`), with
  `run_pilot_arm1.py` to `run_pilot_arm4.py`.

## Sensitivity analysis

Screen the ten continuous parameters of the parameter table with Morris elementary effects, then
run five discrete robustness checks; the report gets one figure and one table. The point to show
is that the headline (E1) and the mechanism (E3) do not rest on the values the model fixes.

- **Outcome.** Y = share won by the mixed population minus the mean share won by the two
  controls, at 100 seeds per point; second outcome, the mean final capacity share of the
  unit-cost label.
- **Design.** Morris (1991) with the μ* measure of Campolongo et al. (2007): 10 trajectories on a
  4-level grid over the ranges of the parameter table, so 10 × (10 + 1) = 110 points, × 3
  populations × 100 seeds = 33,000 runs, about 35 minutes on 10 workers.
- **Reading.** μ* = overall influence, σ = interaction or non-linearity. At 100 seeds a share has
  a 95 % interval of about ±0.10, so a μ* below 0.10 is not told apart from noise. Each parameter
  above it gets a one-at-a-time sweep at 200 seeds.
- **Why Morris.** Ten parameters with known interactions (χ × investment rule in v2) are too many
  for one-at-a-time and too few runs for Sobol indices; ten Broeke et al. (2016) compare the
  options for ABMs. Seeds per point follow the interval widths: ±0.07 at 200 seeds, ±0.04 at 500
  (Lee et al. 2015 on replication counts).

| Check | Why | Cells | Seeds | v2 result |
| --- | --- | --- | --- | --- |
| Plant life T = 5 and 20 | T = 1/δ is a convention: a shorter life retires capital-heavy vintages sooner, a longer one keeps old plants running | E1 and the 16 E4 cells | 200 | Not run: v2 had no maximum age |
| Categories rule | Hosts both reversals; conflict share imposed at q = 0.5 | The 16 E4 cells (already in E4) | 200 | Corner 0.32; average 0.67 |
| Private diffusion | Who knows which design (Silverberg, Dosi & Orsenigo 1988) | E1 | 200 | 0.87 against 0.94, no move |
| Homogeneous start | All six firms on D1, so no initial cost edge; never varied in v2 | E1, E2 | 200 | Not run |
| Number of firms: 6, 12, 30 | Drift weakens as the population grows, and a closed industry keeps its initial firms; v2 always started with 6 | E1 and the 4 closed-entry, growing cells of E4 | 200 | Not run |

The scrapping rule is fixed by the group: operating cost with a plant life of 10 periods, the
margin of Salter (1966, pp. 64–65) and Shaikh (2016, Table 7.3). With no maximum age, v2 found
this margin lowered the result (0.81 → 0.55 under categories, 0.94 → 0.75 under the Marx set)
because old plants never left; here the finite life retires them. Unit-cost scrapping (v2) stays
as a robustness switch.

## Links to the literature

Twenty-eight texts are in the Zotero library (checked on 9 November 2026 with `tools/zotero.py`;
perso unless noted): five of the methods references were added since the first check. The texts
marked — are not in the library and must be added before they are cited.

| Role | Text | Zotero | Use in the report |
| --- | --- | --- | --- |
| Choice of technique | Okishio 1961, *Kobe University Economic Review* | 3ZDE32J4, no PDF | The theorem; cite through Roemer and Shaikh unless the PDF turns up |
| | Roemer 1979, *CJE* 3 | TX2DFFI7 | H1′: the criterion, for cost-reducing innovations (p. 379) and with fixed capital at current prices (p. 386) |
| | Shaikh 1978, *CJE* 2(2) | J9AEUKMD | Criterion stated at prices of production (pp. 241–242): H5 |
| | Shaikh 1980, *CJE* 4 | EECWZJXJ | Reply on the choice of technique (p. 81) |
| | Shaikh 2016, *Capitalism* | BMKVYW2U | Real competition (concurrence réelle), regulating capitals, Table 7.3 (p. 271), pp. 313–324: H1, H2, H5, H6 and the test industry (Tables 7.10–7.11, p. 315) |
| | Okishio 2001, *CJE* 25(4) | BJE3KHR9, no PDF | How competition forms production prices: background for B; not yet opened |
| | Duménil & Lévy 2005, *Research in Political Economy* 22 | LWGHAJ9B | Comment on Park (2005): the profit-rate criterion at going prices is Marx's and the classics', not Okishio's own (p. 209); US data for 1948–2002 satisfy it (pp. 210–214): H1′ and the discussion. The attached PDF is the whole volume |
| | Park 2001, *Research in Political Economy* 19 | 9CUFY49Q, no PDF | Okishio's against Shaikh's criterion, simulated in the Duménil–Lévy–Foley framework (reported in Shaikh 2016, p. 322): closest precedent for the two rules and for H7; not yet opened |
| | Michl 2023, *New School Economic Review* | FX3M6W5I | Conflict of the viability criteria (pp. 47–48): H2; Marx-biased change (pp. 37–41) |
| | Foley, Michl & Tavani 2019, *Growth and Distribution* | V98SW3XI | Viability criterion, Marx-biased change; the PDF did not open in the v2 analysis, retry |
| | Basu 2010, *Metroeconomica* | A8RD2HN7 | Marx-biased technical change; not yet opened |
| | Basu 2026, *Review of Radical Political Economics* | EQUSWFVB | Technical change and the rate of profit in classical-Marxian growth models; the most recent treatment, read first |
| | Baldani & Michl 2000, *RRPE* | 3R3LBMWT | Forced adoption as a prisoner's dilemma; scan without a text layer |
| Selection and industry dynamics | Nelson & Winter 1982 | hivemind VATF967M | Selection through profitability-keyed investment (pp. 17, 19): H3 |
| | Duménil & Lévy 1995, *Metroeconomica* 46(3) | 48U7VRQQ | Stochastic technical change and selection (pp. 213–217): H3, the technical-change rule |
| | Silverberg, Dosi & Orsenigo 1988, *EJ* 98 | EBVLD2YA | Replicator demand and diffusion (p. 1032) |
| | Salter 1966, *Productivity and Technical Change* | FCUBTW7P | Vintages and the scrapping margin (pp. 56–57, 64–65, 84–85) |
| | Dosi & Roventini 2025, *Agent-based Macroeconomics* | TUR32YLD | Machine choice and payback rule (pp. 37–38) |
| | Dosi 2007, statistical regularities of industries | GJDWC56G | Stylised facts for E0 |
| | Dosi et al. 2015 (*SBE*); Foster, Haltiwanger & Syverson 2008 (*AER*) | TVXQ9DA7; QX5VTYKC | Weak selection in the data: why χ is not the lever |
| Computational classical-Marxian | Cogliano, Veneziani & Yoshihara 2022, *Journal of Economic Surveys* | NY6KI3CY | Where the model sits; not yet opened |
| | Cogliano, Veneziani & Yoshihara 2022, "An agent-based approach to classical competitive prices" | DRGHDBSG | Closest ABM precedent; read before the seminar |
| Methods | Grimm et al. 2020, ODD protocol (*JASSS*) | JIHGLM2R | Model description in the appendix |
| | Morris 1991 (*Technometrics*); Campolongo, Cariboni & Saltelli 2007 (*Environmental Modelling & Software*) | DS57QSIN; X29VV2GM | Screening design and μ* |
| | ten Broeke, van Voorn & Ligtenberg 2016; Lee et al. 2015 (both *JASSS*) | BTRNEF9Q; Lee: — | Choice of method; number of replications |
| | Fagiolo, Moneta & Windrum 2007 (*Computational Economics*) | XKW5NTIY | Validation by stylised facts |
| | Metcalfe 1998; Botwinick 1993 (books) | — | Replicator selection; entry and the equalisation of rates |
| | Nakatani 1980, *CJE* 4(1), comment on Shaikh's price-cutting argument (DOI 10.1093/oxfordjournals.cje.a035437) | — | To add and read for H1: title and DOI checked on CrossRef; author's name from memory, text not read |

## Structure of the 10-page report

Seven sections, 10 pages, six figures and three tables; results get 3 pages and the model 2.5.
Write it as a new `report.tex` in the existing LaTeX project, with the full model description as
an ODD appendix (whether appendices count toward the 10 pages is to be asked of Funalot and
Bassi).

| § | Section | Pages | Content | Exhibits |
| --- | --- | --- | --- | --- |
| 1 | Introduction | 0.75 | The Okishio–Shaikh controversy in one paragraph; RQ1–RQ3; the answer in two sentences; what an evolutionary test adds | — |
| 2 | Literature and hypotheses | 1.25 | Choice of technique (Okishio, Roemer, Shaikh, Duménil & Lévy, Michl, Park, Basu); real competition (Shaikh, Salter); evolutionary selection (Nelson & Winter, Silverberg et al., Metcalfe); computational classical-Marxian work (Cogliano et al.) | Table 1: H1–H6 |
| 3 | Model | 2.5 | Setting; the one equation; technical change; price-war regimes; demand; investment; scrapping; entry and exit; neutrality | Figure 1: the conflict zone on Shaikh's menu (D2 has the lowest unit cost, 75, but at p = 100 D1 has the higher rate, 16.86 % against 15.83 %); Table 2: parameters |
| 4 | Experimental design | 1 | Mixed population against controls; share won and Wilson intervals; beyond drift; decomposition; seeds | — |
| 5 | Results | 3 | 5.1 Headline and null (E0, E1); 5.2 Bias of technical change (E2); 5.3 Mechanism: evaluation price and general rate, realised rates, dearer orders (E3, E5); 5.4 Conditions and channels (E4, E5); 5.5 Where the profit-rate rule wins: the categories corner, invasion (E6) | Figure 2: typical run; Figure 3: share won against β and against λ; Figure 4: E4 heat maps; Figure 5: decomposition bars |
| 6 | Sensitivity analysis | 0.75 | Morris screening; discrete robustness checks, the scrapping test argued | Figure 6: μ* against σ; Table 3: robustness |
| 7 | Discussion and conclusion | 0.75 | Okishio's theorem: its micro premise fails out of equilibrium, its macro claim is not tested here. Limits: fixed wage, exogenous r̄ and demand, one industry, no credit. Extensions: bias emerging from neutral innovation at a rising wage (Duménil & Lévy, Park), several industries, a stock-flow consistent closure | — |

The schedule diagram goes in the slides, not the report: the numbered schedule takes less room on
the page.

## Structure of the presentation

Thirteen slides, one skeleton for both dates: on 20 November the result slides show v2 and the
last slide the rebuild plan; on 1 December they show the rebuilt model. Four blocks, one speaker
each.

- **Block 1, question and model.** (1) Two ways to choose a technique; which one does the market
  select? (2) The controversy on one menu: at p = 100, D2 is the cheapest technique and D1 the
  most profitable. (3) The model in one picture: one industry, six firms, six steps a period.
  (4) The only difference: h = 0 against h = the best rate at the evaluation price.
- **Block 2, method and results.** (5) Mixed population against two neutral controls: what
  "beyond drift" means. (6) The unit-cost rule wins (0.81, 0.94 against 0.38–0.56); no technical
  change, no contest (0.51). (7) The more Marx-biased the change, the larger the advantage.
- **Block 3, mechanism.** (8) The evaluation price: judged at the price of production, the
  advantage shrinks to what the general rate leaves (drift under categories, 0.78 under the
  innovation set). (9) The profit-rate firms do not realise the rate they maximise (4.5 % against
  8.4 %).
- **Block 4, conditions and robustness.** (10) The map of conditions: price channel against
  accumulation channel. (11) Where the profit-rate rule wins: a closed, self-financed, growing
  industry, under the categories rule and v2's markup floor only; the accelerator flips it (0.32 →
  0.85). (12) Robustness: Morris screening and the scrapping test. (13) Conclusion and limits; on
  20 November, the rebuild plan and the questions for the audience.

## Timeline and division of work

The rebuilt model gets five days of coding before the 20 November seminar. The v2 pilot was run on
10 November.

| Dates (2026) | Step |
| --- | --- |
| 10–11 Nov | Pilot in v2 (run 10 Nov), then group meeting: freeze the spec (decisions below) |
| 12–16 Nov | Write the simplified code |
| 17–19 Nov | E0–E3 runs, seminar slides |
| 20 Nov | Simulated seminar |
| 21–25 Nov | E4–E6 runs, Morris screening, robustness checks |
| 26–29 Nov | Write the report |
| 30 Nov | Final slides, rehearsal |
| 1 Dec | Report and presentation due |

| Member | Code, 12–16 Nov | Runs | Report | Slides |
| --- | --- | --- | --- | --- |
| Ugo | Hurdle and evaluation price, technical change, investment, run loop | E2, E3, Morris | §1, §5.3, §7 with Jake | Block 3: mechanism |
| Jake | Pricing: one rule, two regimes | E4 | Pricing in §3, §5.4, §7 with Ugo | Block 4: conditions and robustness |
| Pierre-Loup | Demand; entry and exit | E1, E6 | §2, demand and entry in §3, §5.1, §5.5 | Block 2: method and results |
| Vincent | Scrapping, accounts, outputs and the share decomposition | E0, robustness checks | Scrapping in §3, §4, §6 | Block 1: question and model |

## Decisions the group needs to take

Status on 9 November: every row below is agreed as recommended except the questions for Funalot
and Bassi, which are still to be asked. The last five rows were decided by Ugo on 9 and 10
November, after the review and the v2 pilot, and are still to be confirmed by the group; so is the
revised row on r̄.

| Decision | Options | Recommendation | Why |
| --- | --- | --- | --- |
| Technical-change rule | Innovation set main; categories main; both side by side | Innovation set main, categories as robustness; emergent bias left to the discussion (E7 dropped 9 Nov) | Reversals exist only under categories; the innovation set makes the conflict zone an outcome |
| Scrapping test | Unit cost (v2); operating cost (Salter, Shaikh) | **Decided 9 Nov:** operating cost with a plant life of 10 periods | Salter's and Shaikh's margin: capital is sunk, so a plant runs while it covers its operating cost; the finite life retires old vintages, which v2 lacked |
| Pricing rule | v2's two rules as they are; one rule with a "who cuts" switch and a common unit-cost floor | One rule, two regimes | The markup floor never lets the hurdle reach 0; one floor makes the regimes differ only in how often firms cut |
| Investment factor | "Finance" with borrowing; "investment rule" without debt | Investment rule, no debt | Borrowing is inert under leader-follow and close to inert under real competition |
| Evaluation price | Two ends only; continuous λ | Continuous λ (5 levels), crossed with r̄ (0.05, 0.16) | A dose-response curve is the cleanest exhibit for question B |
| r̄ in the text | "General rate"; "open against closed industry" | **Revised 10 Nov:** level of the general rate (centre of gravity of the profit rate, and entry gate) | With the replacement condition the rate gravitates around r̄ and entry stays active at 0.16 (47–52 entries a run in the pilot) |
| 20 November seminar | v2 results and the rebuild plan; wait for v3 | v2 results and the plan | v3 results will be at most two days old by then |
| Questions for Funalot and Bassi | — | Ask now | Do references and appendices count in the 10 pages? Length of each presentation? Is the template layout required? |
| Mechanism test (H5, E3) | Reword only; cross E3 with r̄; a separate rate for the evaluation price | **Decided 9 Nov:** reword H5 and cross E3 with r̄ (0.05, 0.16) | At prices of production the hurdle falls to r̄, not to 0: v2 gives drift under categories but 0.78 under the innovation set and 0.715 at r̄ = 0.16. r̄ = 0.16 also closes entry, so that arm is read against E4 |
| Financing of replacement | Retained profits only (v2); reserve always released; reserve released on a condition (the firm's own technique; the entry signal) | **Decided 10 Nov after the pilot:** reserve released only when r^new ≥ r̄, else withdrawn and paid out; net expansion out of retained profits | Profits alone give a profit rate of 20 %, the reserve always released a rate near zero; with the condition on the entry signal the rate gravitates around r̄, and the condition is the same for every firm (pilot, arms 1 to 4) |
| Status of the v2 numbers | An answer to defend; predictions to retest, with a v2 pilot | **Decided 9 Nov:** predictions, and a pilot of 8 v2 cells before the spec is frozen (run 10 Nov, four arms) | 0.81, 0.94 and 0.32 come from unit-cost scrapping, no maximum age and the markup floor; the closest v2 cells give 0.75 and 0.43 |
| Emergent bias (E7, H7) | Keep E7; pose it in real terms; comparative statics; drop | **Decided 9 Nov:** drop E7, H7 goes to the discussion | A rising money wage with prices that rise only after a shortage squeezes margins to zero, so h → 0 and the rules coincide; H7 is in neither Table 1 nor the slides |
| Ties and the winner | Ties counted as losses (v2); ties counted apart | **Decided 10 Nov:** exact ties counted apart; mean final capacity share reported beside the share won | With six stable firms the pilot had up to 73 ties in 200 seeds, which pulled the controls down to 0.30 |
