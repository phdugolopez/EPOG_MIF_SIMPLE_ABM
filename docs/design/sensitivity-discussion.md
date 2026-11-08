# The first sensitivity analysis read against the literature (discussion for 20 November)

Written on 8 November 2026 (unattended session, branch `feature/analysis` cut from
`feature/sensitivity` at `55a8d9e`), for the group to read before the simulated seminar of
20 November and the choice of the fixed version (step 5 of `review-v2.md`). It reads
`sensitivity-results.md` against the texts the group works from, illustrates each finding
with seed-level runs, and goes further where the results leave a hole (Part B). Nothing in
it is a decision: section 4 proposes rows for `choices.md`.

**How to read the numbers.** Every number carries its cell, population and seeds, written
`[stage, population, seeds]`; `mixed` means label "shaikh" on the unit-cost rule (h = 0) and
label "okishio" on the profit-rate rule (h = best rate at the firm's price), and the two
neutral controls put both labels on one rule (`all_unit_cost`, `all_profit_rate`). *Share
won* is the share of decided seeds in which the label "shaikh" (the unit-cost rule) holds
more than half of producing capacity at t = 199, with its 95 % Wilson interval; *beyond
drift* means the mixed interval is disjoint from both controls' intervals. All cell numbers
come from `outputs/sensitivity/cells.csv`, seed numbers from `runs.csv` (row = `run_id`),
new tables and figures from `outputs/analysis/`. Page numbers refer to the texts listed in
the appendix; a claim about a text I could not open is marked *(from memory, not checked)*.

**Reproducibility note (new).** The rows of `runs.csv` are reproduced exactly by
`experiments.sensitivity rerun` only on Python 3.12 or later: Python 3.12 changed `sum()` on
floats to compensated summation, so on Python 3.10 a rerun of `1_base_mixed_s4` diverges
in 36 observables (checked on 8 November; on 3.13 it reproduces the row exactly). CI runs
3.11; `requirements.txt` should pin `python_requires >= 3.12` or the README should say so
(proposed row in section 4). The stage 4 rows of this session were computed on Linux
(Python 3.13.18); of five stage 1–3 rows checked on that machine, four reproduce exactly
and one (`1_is_neutral_mixed_s7`) differs by 2.2e-16 in one summary observable
(`ucs_spread_mean`), the trajectory being identical.

---

## 1. The question and what the literature predicts

The research question (`CLAUDE.md`): in an industry where cheaper techniques often need more
capital per unit of output, does market selection favour the firms that equip new plants at
the lowest unit cost (Shaikh, h = 0) or at the highest profit rate at the current price
(Okishio, h = best rate on offer), and how does the answer depend on price wars and on how
investment is financed? The table turns the literature into claims that the results can
meet or fail. Observables are those of `sensitivity-plan.md`, section 3.

| # | Claim | Who, where | Observable(s) | What the results say | Verdict |
|---|---|---|---|---|---|
| 1 | In real competition the lowest-cost capitals are the price leaders; followers' margins are residuals; the lowest-cost condition has the highest *sustainable* profit rate under price cutting, so the lowest-unit-cost technique displaces a rival even when it earns less at the going price (D2 against C at $100) | Shaikh 2016, Table 7.3 rows 1–5 (p. 271); pp. 313–317 (Tables 7.10–7.12, eq. 7.11, fig. 7.22) | share won; `leader_lowest_cost_share`; `d_share_price_all`; `price_to_pp` | `base` [3, mixed, 1–500] 0.81 (0.77–0.84) against 0.48 / 0.50; the leader is the lowest-cost firm in 0.94 of periods; price term of the sales share +0.25; 86 of 120 factorial cells beyond drift, all for the unit-cost rule | **Met**, except in two corners (A.7) |
| 2 | Under real competition a capital-using, cost-reducing technique spreads by price cutting and the rate of profit falls even at a given real wage; under the profit-rate criterion it falls only at high wage shares | Shaikh 2016, p. 261; pp. 317–321 (Alternative 2: general rate 16 % → 15.2 %); Michl 2023, pp. 47–48 | `marx_biased_*`; `profit_rate_total` of the two controls | Spreads: realised change is Marx-biased for the unit-cost label in 0.84 of `base` seeds. Rate: an industry where every firm uses the unit-cost rule realises a lower profit rate than one where every firm uses the profit-rate rule (`is_marx_15` [1, controls, 1–200]: 8.5 % against 10.9 %), at similar prices (A.6) | **Met at industry level**; the economy-wide claim is **not testable** (rbar exogenous) |
| 3 | After a cost-cutter takes over, the price first falls, then rises to the new regulating price of production (D2: back up to $101.30) | Shaikh 2016, p. 316 | `price_rise_after_adoption`; `price_to_pp`; figure 5 | Real competition: the price at t = 199 exceeds that at t = 100 in 0.17–0.31 of seeds (innovation set, marx 0.5 to 3) and ends 10–20 % above the price of production; leader-follow: at most 0.06, ending below it (0.85–0.93) | **Met under real competition only** |
| 4 | A technique that raises the profit rate at current prices cannot lower the general rate once new prices of production settle, at a constant real wage (Okishio's theorem) | Okishio 1961 *(not in the library)*, as stated in Shaikh 2016, p. 320; Shaikh 1978, pp. 241–242; Roemer 1979, p. 379; Duménil & Lévy 2005, p. 209 | `profit_rate_okishio` against `profit_rate_shaikh`; controls' `profit_rate_total` | The theorem is about the general rate: **not testable here**, since rbar is a parameter and the money wage is the numéraire (the constant real wage holds by construction, the general rate does not respond). Its micro premise, that the adopter earns the higher rate, fails: `base` 4.5 % (profit-rate label) against 8.4 % | **Not testable**; premise **failed** |
| 5 | A technique that does not pass the profit-rate test is never adopted by a rational capitalist; a higher-cost method can dominate if it has the lower price of production (Sraffa's criterion) | Shaikh 2016, p. 320 n. 36 and p. 322 (stating the standard view); Roemer 1979, p. 379 | `conflict_adopted_shaikh`; `okishio_dearer`; share won | The unit-cost firms adopt every conflict-zone design (`conflict_adopted_shaikh` 1.0) and they are the ones selected; the profit-rate firms' refusals and dearer orders go with losing (`okishio_dearer` 0.49 in seeds the unit-cost rule wins, 0.17 where it loses, stage 2) | **Failed** as a statement about who survives |
| 6 | The two criteria conflict only when technical change is Marx-biased (capital-using, labour-saving) and when the rule is evaluated at prices that the adoption will change; the profit-rate criterion is the right one if prices do not fall after adoption | Duménil & Lévy 2005, p. 209; Michl 2023, pp. 47–48; Shaikh 2016, pp. 323–324 | zone shares; `marx_biased_*`, `gamma_*`, `chi_*`; `no_tech`; the neutral set; anchor cells | Fixed menu: drift (0.51). Neutral set: conflict share 0.04, share won 0.78. Anchor pricing (prices held at each firm's target return) at rbar 0.16: the profit-rate rule wins (0.26) | **Met** |
| 7 | Selection on realised profitability drives accumulation, selection on price drives market share; the balance depends on finance and on the intensity of selection | Nelson & Winter 1982, pp. 17, 19; Duménil & Lévy 1995, p. 217; Metcalfe 1998 *(not in the library)* | `d_share_accum_all` against `d_share_price_all`; the finance arm; CHI | The price term is the larger in 93 % of cells; accumulation decides only with self-finance, growing demand and no entry, where finance flips the winner (`lf-re-g01-cat-r16` 0.32 → 0.85 with the accelerator and borrowing [3, mixed, 1–500]); CHI 0.25–4 moves nothing (0.71–0.79) | **Met for finance; not for selection intensity** (A.8) |
| 8 | Selection is weak in the data: relative productivity explains little of firm growth, and survival turns on profitability and demand more than on physical productivity | Dosi et al. 2015 (abstract, introduction); Foster, Haltiwanger & Syverson 2008, pp. 394, 397 | CHI 0.25 cells | χ = 0.25 delays takeovers (mean `takeover_t` 174 against 117) without changing the winner (0.71 [1, mixed, 1–200]) | Not a test of the data; **the briefs' χ trap does not spring** |
| 9 | Vintages coexist; old plants run until their operating cost reaches the total cost of best practice (normal return included), so the vintage spread and the replacement margin set the pace of diffusion | Salter 1966, pp. 56–57, 64–65, 84–85 | `ucs_spread_mean`; `capital_age_*`; `replacements_*` | Spread: 1.23 (`base`); replacements ≈ 0 everywhere at the defaults; capital ages equal in `base` (14.0 / 13.9) but 32.6 against 22.7 for the losing unit-cost label in `lf-re-g01-cat-r16` | **Partly met**; the replacement margin is never reached |
| 10 | Entry equalises the profit rate on new investment in the regulating capitals across industries, and is how the winning practice spreads | Shaikh 2016, pp. 265, 296 (citing Botwinick 1993, ch. 5, *not in the library*) | `entries`, `d_share_entry_all`, `r_new_mean`, `periods_above_rbar`; rbar 0.16 cells | rbar 0.05: `r_new_mean` 0.054 against rbar 0.05, the industry rate above rbar in 95 of 100 periods, entrants inherit the majority rule; rbar 0.16: the rate is above rbar in 0.3–2.3 of 100 periods, entry stops, and both reversals live there | **Met at rbar 0.05**; at 0.16 the carrier is shut |
| 11 | Diffusion takes time and is shaped by learning and by who knows what | Silverberg, Dosi & Orsenigo 1988, p. 1032 | `is_private` against `is_marx_15` | 0.87 (0.82–0.91) against 0.94 (0.90–0.97): overlapping | **No effect** on the winner |

---

## 2. Part A: the findings read against the literature

Figure A0 (`outputs/analysis/figures/A0_summary_section6.png`) places every cell of section 6
of the results against its controls: the grey band is the union of the two controls'
intervals, a coloured dot is beyond drift (blue for the unit-cost rule, orange for the
profit-rate rule), a grey dot is not.

### A.1 The base result and its controls

**Result.** `base` [3, mixed, 1–500]: the unit-cost rule wins 0.81 (0.77–0.84) of seeds;
controls 0.48 (all unit cost) and 0.50 (all profit rate); mean final capacity share of the
unit-cost label 0.80; no undecided seed. The leader-follow arm `lf` [3, mixed, 1–500]: 0.71
(0.67–0.75), controls 0.50 / 0.49. Both beyond drift, and the 10-point gap between the two
pricing rules is itself beyond the intervals.

**Literature.** Row 1: Shaikh's real competition predicts this outcome for D2-type
techniques (lower unit cost, lower profit rate at the going price): the lowest-cost capital
cuts the price until its rival's advantage disappears (pp. 314–316), and in Table 7.3 the
regulating capitals are the price leaders (row 3) and the lowest-cost condition has the
highest sustainable rate under price cutting (row 5, p. 271). The neoclassical and Sraffian
view he contrasts with it predicts the opposite selection (C or D1 dominates D2, p. 315).
**Agrees with Shaikh.** The controls matter: they sit at 0.48–0.50, so the 0.81 is not a
label effect of the single random stream (which moves controls by up to 0.12 elsewhere,
results §8.6).

**Example: `1_base_mixed_s4` (figure A1).** The first dearer order of a profit-rate firm
comes at t = 2 (67 dearer orders in the run, `okishio_dearer` 0.62). The unit-cost label's
capacity share is 0.81 at t = 50 and 0.93 at t = 100; it takes over (> 90 % of capacity to
the end) at t = 93. Over the run the unit-cost firms place 691 orders against 108, 111 of
the 124 entrants inherit the unit-cost rule, and the realised rates over t = 100–199 are
14.2 % against 3.0 %. The decomposition over the whole run credits the unit-cost label with
+0.27 of sales share through prices, and +0.19 accumulation, +0.18 entry, +0.12 exits on the
capacity side. The price is not monotone: 99 at t = 0, 62 at t = 100, a spike to 211 at
t = 150 when a shortage follows a wave of scrapping (the excess-demand step of the real
competition rule), 78 at t = 199; `price_to_pp` 1.29. Exits are by share from t = 23 on,
for both labels, until the profit-rate firms are gone.

**Example of the other outcome: `1_base_mixed_s1` (figure A2).** Seed 1 is one of the
0.19 of `base` seeds the profit-rate rule wins: no takeover, the unit-cost label holds 0.49
of capacity at t = 100 and 0.17 at t = 199. Here the profit-rate firms order dearer
techniques less often (`okishio_dearer` 0.38, against 0.51 on average), 59 of 89 entrants
inherit the profit-rate rule once it has the majority, and the decomposition runs against
the unit-cost label on every term (prices −0.31, accumulation −0.14, exits −0.20). The
realised rates are close (9.8 % against 10.6 %). What decides it is who leads when the
churn of entry starts: inheritance by market share makes entry a copying process that
amplifies the early majority (A.9).

### A.2 No technical change, no contest

**Result.** `no_tech` (`TECH_DRAWS = False`, fixed menu C, D1, D2) [1, mixed, 1–200]: 0.51
(0.44–0.58), controls 0.45 / 0.45; no takeover in any seed; no entry in the window
(`r_new_mean` −0.01); profit rates 6.2 % against 5.9 %; `okishio_dearer` 0.10.

**Literature.** Shaikh's own figure explains the drift. The profit rate of each technique is
linear in the price (eq. 7.11), and below $85 D2 has the highest profit rate of the three
(p. 317, fig. 7.22). On the fixed menu the price falls below that point early (mean price
over t = 50–199: 77.0 [1, mixed, 1–200]), after which the profit-rate rule picks D2 exactly
as the unit-cost rule does: the profit-rate label's mean hurdle is 0.013 and only 0.10 of
its orders are not the cheapest technique, almost all of them before the price falls. The
two rules become one rule and drift follows. Shaikh's point that the lower-cost method
dominates "in real cost-cutting competition" (p. 317) holds here in the weakest sense: the
profit-rate firms end up choosing it too. **Agrees with Shaikh, and shows why a fixed menu
cannot stage the contest**: the conflict has to be reopened at the current price by a
*stream* of new designs, which is how Shaikh (pp. 322–324) and the Duménil–Lévy–Foley
framework he builds on pose it (section (b) below).

**Example.** None needed: no seed has a takeover. The menu is the test industry, not the
model.

### A.3 Categories against the innovation set

**Result.** [1, mixed, 1–200]: categories q = 0.5 (`base`) 0.81, q = 0 (`cat_q0`) 0.62;
innovation set marx 0.5 / 1.5 / 3 0.80 / 0.94 / 0.97, neutral 0.78. In stage 2 the
categories rule averages 0.67 (10 of 24 cells beyond drift) against 0.76–0.91 for the
innovation sets. The realised conflict share is 0.50 under categories (an input), 0.14–0.19
under the marx sets and 0.04 under the neutral set (outcomes), yet the innovation set gives
the larger advantage.

**Literature.** Row 6. The conflict between the criteria needs Marx-biased change: with
neutral innovation possibilities real competition yields a rising profit rate, as the
Okishio theorem does (Shaikh 2016, pp. 323–324, fig. 7.23); with a negative correlation
between cost and capital margins (his Table 7.9, Compustat) the criteria part
(fig. 7.24). Michl (2023, pp. 47–48) states the same condition in wage–profit terms: the
criteria conflict when the new technique raises the maximum profit margin but its
wage–profit curve crosses the old one (a switchpoint), and for wages between the two
switchpoints Shaikh's criterion adopts techniques that lower the profit rate at the
existing wage. **Agrees**, with one twist the literature does not predict: the size of the
advantage is not proportional to the share of conflict draws. Under the categories rule half
the draws are conflict draws by construction, yet the advantage is smaller (0.81) than under
the marx 1.5 set (0.94, conflict share 0.19). What carries the advantage is the profit-rate
firms' *orders* of dearer techniques (A.5): under the innovation set a profit-rate firm
compares a design with its best known technique at its own price, and with capital-using
designs its best technique is often an older, less capital-intensive one, so it keeps
ordering a technique that is not the cheapest known (`okishio_dearer` 0.79 under marx 1.5
against 0.51 under categories).

**Example: `2_rc-re-static-is15-r16_mixed_s1` (figure A4).** Real competition, retained
earnings, static demand, innovation set marx 1.5, rbar 0.16. 186 of the profit-rate firms'
215 orders are dearer than the cheapest known technique (`okishio_dearer` 0.87, first at
t = 3, last at t = 199); the unit-cost label holds 0.51 at t = 50, 0.75 at t = 100 and
takes over at t = 170, through prices (+0.47) and exits (+0.40), not accumulation (+0.01).
The price ends at 2.1 times the price of production of the cheapest technique in use, after
a shortage: the price signature of A.11.

### A.4 The channel: prices, then exits, not accumulation

**Result.** Over the 212 mixed cells of stages 1 and 2 the whole-run price term of the
unit-cost label's sales share correlates 0.80 with the share won and the accumulation term
0.60; the price term is the larger in 93 % of cells (results, §5). In `base` [3, mixed,
1–500] the unit-cost label gains +0.25 of sales share through prices and +0.28 of capacity
share through the exits of profit-rate firms, while accumulation nets to −0.003 and entry
to +0.03 (figure B1.2).

**Literature.** Row 1 and row 7. Shaikh's mechanism runs through the price: the cost-cutter
"makes room for itself" by cutting (p. 314) and the rival's market share and then its
plants go (p. 316). Nelson and Winter's selection runs through investment keyed to
profitability (pp. 17, 19), and so does Duménil and Lévy's (1995, p. 217: profitability
generates the cash flow that finances growth). **The model sides with Shaikh on the
channel**: the profit-rate firms do not accumulate faster at the defaults, because they do
not realise the higher rate (A.6), and because idle scrapping (`IDLE_SCRAPPING`, two idle
periods) destroys capacity that sales do not use, so accumulation without customers does
not stick. The exits are the second half of Shaikh's story (the old regulating capital "is
doomed", p. 314): in `base` they carry more capacity share than any other term.

**Example.** `1_base_mixed_s4` (A.1): prices +0.27, exits +0.12, but also accumulation
+0.19 and entry +0.18 once the unit-cost label leads: the channels compound after the
takeover.

### A.5 The mechanism: the profit-rate rule's switch to dearer techniques

**Result.** `okishio_dearer` (share of profit-rate orders that are not the cheapest known
technique) correlates 0.77 with the share won across cells, the strongest of all
observables; 0.49 in stage 2 seeds won by the unit-cost rule against 0.17 in seeds it loses;
0.51 in `base`, 0.79–0.85 under the marx sets, 0.10 on the fixed menu. Within cells (B1,
cell fixed effects, 17 585 decided stage 2 seeds) a one-standard-deviation increase in
`okishio_dearer` (0.18) raises the probability that the unit-cost rule wins by 0.11
(coefficient 0.64, 95 % interval 0.56–0.71).

**Literature.** This is Shaikh's case in Tables 7.10–7.12: the profit-rate rule picks the
technique with the higher rate at the ruling price ($100), the lower-cost one drives the
price down to where the ranking of profit rates reverses (below $85 in fig. 7.22, p. 317),
and from then on the dearer choice is a handicap. Okishio's rule is not irrational at the
price it sees; it is evaluated at a price that the cost-cutters' adoption will lower.
**Agrees.** It also matches Duménil and Lévy's point (2005, p. 209) that the criterion
itself is classical; what decides is the price at which it is applied (row 6, and the B3
candidate on the evaluation price).

**Example.** Compare the two `base` seeds: 67 dearer orders in seed 4 (unit-cost takeover
at t = 93) and an `okishio_dearer` of 0.38 in seed 1 (profit-rate win); in the anchor and
leader-follow reversals (A.7) the profit-rate firms almost never order dearer techniques
(0.06–0.10), so the mechanism is absent and something else decides.

### A.6 Realised profit rates and prices

**Result.** The unit-cost firms earn the higher realised profit rate: `base` [3, mixed,
1–500] 8.4 % against 4.7 % (results: 8.4 % against 4.5 % in stage 1); across stage 2
decided seeds 11.1 % against 8.8 % where the unit-cost rule wins, and 7.8 % against 9.9 %
where the profit-rate rule wins (13 956 and 3 644 seeds): **the winner earns more,
whichever rule it uses**. Seeds won by the unit-cost rule have *higher* mean prices (74.5
against 62.3) and end at the price of production of the cheapest running technique
(`price_to_pp` 1.13 under real competition) rather than below it (0.87). The leader is the
lowest-cost firm in 0.94 of periods (`base`).

**A result the literature frames but the results document did not state: selection picks
the rule that lowers the industry's profit rate.** Compare the two neutral controls of the
same cell, i.e. an industry in which every firm uses one rule (`profit_rate_total`, mean
over t = 100–199, 95 % interval of the mean; [stage, control, seeds]):

| Cell | All unit cost | All profit rate | Mixed | Share won (mixed) |
|---|---|---|---|---|
| `base` (categories) [3, 1–500] | 8.72 % (8.50–8.94) | 9.03 % (8.81–9.26) | 8.85 % | 0.81 |
| `is_neutral` [1, 1–200] | 8.58 % (8.34–8.83) | 9.60 % (9.15–10.04) | 8.85 % | 0.78 |
| `is_marx_15` [1, 1–200] | 8.50 % (8.21–8.79) | 10.91 % (10.48–11.35) | 9.18 % | 0.94 |
| `is_marx_3` [1, 1–200] | 7.87 % (7.56–8.18) | 10.81 % (10.39–11.23) | 8.49 % | 0.97 |
| `rc-re-static-is3-r16` [3, 1–500] | 12.03 % (11.59–12.47) | 18.67 % (18.26–19.07) | 13.70 % | 0.99 |

Under the Marx-biased innovation sets an industry run on the unit-cost rule realises a
profit rate 2.4 to 6.6 points lower than the same industry run on the profit-rate rule, at
similar prices (mean price over t = 50–199: 76.8 against 74.9 under marx 1.5) and similar
unit costs at the end (51.7 against 50.4): the difference is capital per unit of output.
Yet in the mixed industry the unit-cost rule is selected in 0.94–0.99 of seeds. This is
Shaikh's claim of p. 261 and pp. 320–322 at the scale of one industry (the cost-cutting
criterion forced by competition lowers the rate of profit relative to the profit-rate
criterion, at a given real wage) and it is the prisoner's dilemma that Foley (1986, p. 131,
cited by Michl 2023, p. 46) and Baldani and Michl (2000, *scanned, not read*) see in Marx:
each capitalist is forced to adopt what lowers the common rate. Under the categories rule
the difference is small and the intervals touch, because half the designs are adopted by
both rules. **Figure A8** shows the table with its intervals. On the fixed menu the
ordering is reversed (`no_tech` [1, controls, 1–200]: 8.81 % all unit cost against 5.75 %
all profit rate), but for a reason that has nothing to do with capital intensity: when every
firm builds D2, no firm keeps a cost edge, the real-competition rule never cuts, and the
price stays high (mean 94.1 over t = 50–199, against 76.0).

**(a) Why does the profit-rate rule not realise the higher profit rate it maximises at the
current price?** Two hypotheses, which Part B (B1) separates with the stage 2 seeds:

1. *Shaikh's argument.* The rate the profit-rate firm maximises is computed at its own
   current price; the cost-cutters' adoptions then lower the price, and at the lower price
   the dearer technique earns less than the cheaper one (fig. 7.22: D2 overtakes D1 below
   $85, p. 317). The firm locks capital into a technique whose rate is never earned. This
   predicts that the realised gap grows with the share of dearer orders, *among seeds with
   the same winner*.
2. *Market structure.* The rate is a price leader's premium: whoever wins leads a more
   concentrated market (HHI 0.24 where the unit-cost rule wins, 0.34 where it loses, stage
   2) and posts the higher price; the rule does not matter once the winner is known. This
   predicts that the gap goes with the winner and with concentration, not with
   `okishio_dearer` once the winner is controlled.

B1's answer, in one line: **both, and Shaikh's mechanism survives the control** (gap on
`okishio_dearer` 0.051 per unit, 95 % interval 0.038–0.065, holding the winner and
concentration fixed within cells; the winner's own premium is 0.038, 0.029–0.047;
concentration adds little, 0.017 per unit of HHI, 0.002–0.032).

**For the presentation**, the group can say: the profit-rate rule maximises the rate at a
price that its rivals' choices will not let it keep; the realised rate then goes to the
cost-cutters, and on top of that to whichever firm leads. The model reproduces Shaikh's
mechanism; it does not reproduce a rule that is irrational at the price it sees.

### A.7 The two reversals

The profit-rate rule wins beyond drift in two configurations only.

**(i) `anchor_r16`** (version 1 anchor pricing: each firm moves toward its own target-return
price uc + rbar κ, wars after low utilisation; rbar 0.16) [1, mixed, 1–200]: 0.26
(0.20–0.33), 13 undecided seeds, controls 0.53 / 0.51. At rbar 0.05 (`anchor_r05`) 0.66,
at drift. In the reversal: 0.05 entries in the window, two firms at the end (`n_firms_end`
2.04), HHI 0.74, both channels against the unit-cost label (prices −0.18, accumulation
−0.21 over the whole run), `okishio_dearer` 0.10, `price_to_pp` 0.54.

*Literature.* The pricing brief named this trap before anything was run
(`mechanism-briefs.md`, "The trap: the anchor price decides the winner"): a target-return
anchor makes the technique with the lowest uc + r̄ κ the cheapest in normal times, which at
r̄ = 0.16 is C or D1, not D2 (C 100, D1 98.8, D2 100.3; at r̄ = 0.05: D2 82.9, D1 83.1,
C 84.9). That ranking is Sraffa's criterion of choice (the lower price of production at the
ruling rate, Shaikh 2016, p. 320 n. 36), and it is the profit-rate rule's criterion with h
= r̄. In other words the anchor rule builds the Okishio criterion into the price, which is
the situation Duménil and Lévy (2005, p. 209) and Okishio's theorem presuppose: prices of
production prevail. Shaikh's answer to that situation (p. 321) is that actual choices are
made at actual and projected market prices, which differ from prices of production. **The
reversal is the briefs' trap sprung, not a refutation of Shaikh.** The model adds the
mechanism by which it works (B1): with every firm anchored on its own uc + 0.16 κ, the
capital-heavy unit-cost firm posts the higher normal price, loses share, earns little
(2.2 % in `1_anchor_r16_mixed_s3` over t = 100–199, against 8.7 %), cannot finance new
plants out of retained earnings, keeps old plants, and its capacity is retired when a war
drives the price below their unit cost; no entrant comes in at rbar 0.16 to carry the
unit-cost rule, and the minimum of two firms keeps a duopoly.

*Example: `1_anchor_r16_mixed_s3` (figure A5).* First dearer order at t = 1 (17 in all);
the unit-cost label holds 0.54 of capacity at t = 50 and 0.42 at t = 100; four exits, all
by non-renewal (o16, s59, s98, o127); no entry; at t = 129 the last unit-cost plants are
retired and the label's capacity falls to zero; the firm stays as one of the two firms
`MIN_FIRMS` keeps. Price 100 → 71 (t = 50) → 68 (t = 100) → 51 (t = 199).

**(ii) `lf-re-g01-cat-r16`** (leader-follow, retained earnings, demand growing 1 %,
categories, rbar 0.16) [3, mixed, 1–500]: 0.32 (0.28–0.36), controls 0.49 / 0.49; its
finance twin `lf-acd-g01-cat-r16` (accelerator with borrowing) [3, mixed, 1–500]: **0.85**
(0.82–0.88). In the reversal: 0.24 entries in the window, `n_firms_end` 2.01, HHI 0.91,
profit-rate firms earning more (6.3 % against 3.3 %), `okishio_dearer` 0.06, the unit-cost
label's capital older (32.6 against 22.7 periods), takeovers early (median t = 82; 0.75 of
them before t = 100). In the twin: 7.0 entries, 9.4 firms, both channels for the unit-cost
label (+0.32 prices, +0.31 accumulation).

*Literature.* Row 7. This is Nelson and Winter's selection through investment keyed to
profitability (pp. 17, 19) and Duménil and Lévy's (1995, p. 217) profitability-financed
growth, in the one corner where it can work: demand grows, so capacity rather than price
is the constraint; investment is self-financed, so capacity grows with retained profits,
and at a common price the technique with the higher profit rate yields more capacity per
unit of profit (units = retained earnings / κ); no entrant arrives at rbar 0.16 to carry the
other rule; and the leader-follow floor (1.2 × the average unit cost of *all* the firm's
plants) lets a firm with older plants post a higher price, so the firm that stops
investing also loses on price. Under the accelerator with borrowing, investment follows
sales instead of profits, and sales follow price: the price channel drives accumulation and
the unit-cost rule wins. **The finance rule decides the contest here, which is the second
half of the research question.** It does not contradict Shaikh, whose price-cutting
argument needs a firm that can expand capacity to take the market (p. 314: the
cost-cutter "makes room for itself"); with retained earnings and low margins the unit-cost
firm cannot.

*Example: `3_lf-re-g01-cat-r16_mixed_s1` against `3_lf-acd-g01-cat-r16_mixed_s1`
(figures A6, A7; same seed).* Retained earnings: 5 dearer orders, all before t = 13; the
unit-cost label holds 0.55 at t = 50 and 0.46 at t = 100, then loses steadily as the
profit-rate firms place 765 orders against 178 (the unit-cost firms' last order is at
t ≈ 145); takeover by the profit-rate label at t = 132; four exits by share (o54, o76, s80,
s93), no entry; the price falls every period, 98 → 78 → 62 → 48; capital age of the
unit-cost label 54 periods at t = 199 against 14. Accelerator with borrowing: 2 dearer
orders; the profit-rate firms place only 10 orders in the whole run (they lose sales, so
the accelerator does not ask them to invest), the unit-cost firms 339; takeover by the
unit-cost label at t = 73; 8 entrants, all inheriting the unit-cost rule; the price falls to
about 75 by t = 75 and then rises to 103–118 under recurring shortages.

### A.8 The factors that move nothing

**Result.** CHI 0.25 / 0.5 / 2 / 4: 0.71 / 0.79 / 0.75 / 0.79 [1, mixed, 1–200], none
beyond `base`'s interval; logit with η = 1 identical to the replicator; floor of the default
rule (0.74); excess-demand signal (0.76); entry speed θ = 1 (0.79); scrapping 4 / 4 (0.78);
depreciation by use (0.75); plant size 40 (0.79); τ = 0.25 (0.78); the hurdle floor (inert);
the leader-follow shortage branch (inert).

**Literature: the χ trap.** The demand brief warned that weak selection would let the
firms with higher profit rates win by accumulating faster, and that selection is weak in the
data (Dosi et al. 2015; Foster, Haltiwanger & Syverson 2008, p. 397, where demand
differences, not physical productivity, dominate survival). The trap does not spring, for
three reasons visible in the runs: (1) the profit-rate firms do not have the higher
realised rate to accumulate with (A.6), so a slow market does not hand them anything;
(2) idle plants are scrapped after two idle periods, so capacity that sales do not use
disappears; (3) χ sets the *speed* of share movements, not their direction, and the share
won is read at t = 199: at χ = 0.25 the mean takeover comes at t = 174 instead of 117, and
fewer seeds have finished (cap share 0.63), but the same rule leads. In the phase block χ
interacts with finance (results §3): with borrowing under real competition a *higher* χ
hurts the unit-cost rule. **The briefs' trap assumed that the Okishio firm earns the rate it
maximises; the model says it does not, which disarms the trap.**

τ: the briefs note that on the fixed menu τ above about 0.12 makes D2 stop being a conflict
case against C (at p = 100, r_D2 = 25 / (157.9 + 59.2 τ) exceeds r_C = 22 / (137.5 + 64.25 τ)
for τ > 0.119), while `tau_025` still gives 0.78. Drawn designs keep a conflict zone because
for a *local* design the profit-rate rule adopts iff b < (1 + h τ) a ucs_o / ((δ + h) κ_o)
while the unit-cost rule adopts iff b < a ucs_o / (δ κ_o): the zone between exists whenever
h > 0 and δ τ < 1, i.e. always (τ only widens the profit-rate rule's acceptance by the
factor 1 + h τ, about 1.02 at h = 0.09). Under the categories rule the placement of
conflict draws (`draw_design`) does not even read τ, so q = 0.5 of draws still fall where
only the unit-cost rule adopts. The menu loses its conflict because D2 against C is one
large, discrete step; a stream of small Marx-biased steps keeps one. A τ sweep is therefore
predictable on paper and was given the lowest priority in Part B.

### A.9 Demand met and turnover

**Result.** Unmet demand is below 3 % of demand except under the anchor rule (`anchor_r16`
7.6 %, `anchor_r05` 10.3 %) and the leader-follow operating-cost floor (25.7 %, where the
industry collapses in 81 of 200 seeds); it does not move with the winner (correlation
0.06). Turnover: more entry and more firms where the unit-cost rule wins (19.9 entries in
the window against 13.3; HHI 0.24 against 0.34, stage 2); bankruptcies only with borrowing
(0.6 against 0.3 per seed).

**Literature.** Row 10. Shaikh's entry equalises the profit rate on new investment
(p. 296); here `r_new_mean` is 0.054 against rbar 0.05 in `base` and the industry rate is
above rbar in 95 of 100 periods, so the trigger fires almost every period (review-v2 §2.2,
point 5, called it churn). Entrants copy the rule of an incumbent drawn by market share
(`equations/inherited_rule.py`), so entry is a copying process that carries whichever rule
has the majority: that is why entry is Shaikh's long-run carrier only *after* the price
channel has made the unit-cost rule the majority, and why it amplified the profit-rate
majority in `1_base_mixed_s1`. At rbar 0.16 the industry rate is above rbar in 0.3–2.3 of
100 periods, entry stops, and the two reversals both sit there. **Agrees with Shaikh on
entry as carrier; adds that the carrier is neutral (it copies the majority).**

### A.10 Marx bias as an outcome

**Result.** Realised change is Marx-biased (γ > 0 and χ > 0 for the label's plants between
t = 100 and t = 199) for the unit-cost label in 0.84 of `base` seeds against 0.29 for the
profit-rate label; under the neutral set for neither (0.00 / 0.005: capital-saving designs
dominate); under marx 1.5 1.00 / 0.71.

**Literature.** Michl (2023, pp. 37–41) reviews the evidence of Marx-biased technical change
(falling capital productivity with rising labour productivity, the "fossil production
function"); Shaikh (2016, p. 324) reads the same pattern in Compustat data (Table 7.9).
Duménil and Lévy (1995, p. 214) assume neutral, local innovation and obtain the bias from
selection under a rising labour cost. **The model cannot reproduce Duménil and Lévy's route:
the money wage is the numéraire, so labour never gets dearer, and a neutral set selected at
a fixed wage produces capital-saving change.** With a fixed wage, Marx bias must be assumed
in the innovation set; it is then reproduced as an outcome mostly by the unit-cost label.

### A.11 The price signature

**Result.** Under real competition the price at t = 199 exceeds the price at t = 100 in 0.17
(marx 0.5) to 0.31 (marx 3) of seeds and ends 10–20 % above the price of production of the
cheapest technique in use; under leader-follow at most 0.06, ending below it (0.85–0.93)
(figure 5 of the results). `base` [3, mixed, 1–500]: 0.23 of seeds, `price_to_pp` 1.05.

**Literature.** Row 3. Shaikh (p. 316) predicts the D2 price path exactly: the price falls
while the new regulating capital shoulders the old one aside, then rises to the new
regulating price of production, which for a capital-using technique is *higher* than the
old one ($101.30 against $100); he notes that this rise is what the neoclassical and
Sraffian approach rules out (p. 316). **Agrees under real
competition**, where the rise comes through the shortage step (prices move up to the next
rival's price or by 0.5 × the excess-demand share), as in `1_base_mixed_s4` (spike to 211 at
t = 150) and `2_rc-re-static-is15-r16_mixed_s1` (2.1 × the price of production at t = 199).
Leader-follow matches every price to the leader and cuts every period, so the rise has no
room. The rise in the model comes from shortages after scrapping, not from entry pricing at
the normal rate as in Shaikh's account (entry at rbar 0.05 is permanent, so it cannot pull
the price up to a target).

### (b) The technical-change rule is the model, not a detail

`no_tech` at drift (A.2) means the research question is answered by the technical-change
rule. What each rule assumes about the direction of innovation:

- **Categories** (`equations/new_technique.py`): every design lowers the unit cost of the
  firm's reference technique (ucs falls by a ≤ 5 %, κ rises by b with b < b_S), so the
  unit-cost rule adopts every design; a coin flip (q = 0.5) puts the design in the conflict
  zone b_O ≤ b < b_S, computed at the firm's own price. Innovation is cost-reducing by
  construction, Marx-biased by construction, and the conflict share is an input
  (`review-v2.md` §4.1, points 1–4).
- **Innovation set, marx** (`equations/innovation_set.py`): ucs falls by a, κ rises by k a
  with k log-normal around TECH_BIAS; some designs raise unit cost and are rejected by both
  rules; zones are outcomes of the draw and of the price. Marx-biased by construction,
  cost-reducing or not by draw.
- **Innovation set, neutral**: direction uniform on the circle; Marx bias is not assumed.

Which does the literature support? Shaikh (pp. 322–324) frames the question as one about
the *probabilities* of the two kinds of technical change and argues, with Marx, that
cost-reduction typically comes with more capital per unit (negative correlation in
Table 7.9); Michl (2023, pp. 37–41) and Foley (as reported by Michl) treat Marx-biased
technical change as the empirical pattern; Duménil and Lévy (1995, p. 214) start from
neutral, local innovation and obtain the bias through rising wages. With a fixed wage the
model can only take the first route, so **the marx innovation set is the specification the
literature supports for this model, the neutral set is its natural robustness check, and
the categories rule is a stylised version of the marx set with the conflict share fixed at
q** (its advantage is that q is a transparent treatment). The group should present the
technical-change rule as the model's core assumption, with `no_tech` as the null.

---

## 3. Part B: going further

*(Part B is written in the second commit.)*

---

## Appendix: texts opened, with the pages used

*(Completed with Part B.)*
