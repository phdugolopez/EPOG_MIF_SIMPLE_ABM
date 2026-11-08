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
(proposed row in section 4). A second, smaller trap: pandas' default CSV float parser is not exact on
every platform (on x86_64 it loses the last digit of some values, on the Mac it does not),
so `experiments.sensitivity.load_runs` now reads with `float_precision="round_trip"`. The stage 4 rows of this session were computed on Linux
(Python 3.13.18); of five stage 1–3 rows checked on that machine, four reproduce exactly
and one (`1_is_neutral_mixed_s7`) differs by 2.2e-16 in one summary observable
(`ucs_spread_mean`), the trajectory being identical.

**Session note.** The connection to the Mac dropped at about 01:30 UTC, after the Part A
commit and after the B3 candidate runs had been written on the Mac, and came back at 04:40
UTC. In between, stage 4 (B2) was computed in the session's container (Linux, x86_64) on the
model code of `55a8d9e`, which the candidate switches do not change at their defaults, and
the B3 cells were run a second time there. Back on the Mac's VM, four stage 4 rows
(`4_anchor_r10_mixed_s3`, `4_lf-acc-g01-cat-r16_mixed_s5`, `4_is15-tau_010_mixed_s2`) and
`1_base_mixed_s4` were rerun after the merge: all reproduce their rows exactly.

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
| 1 | In real competition the lowest-cost capitals are the price leaders; followers' margins are residuals; the lowest-cost condition has the highest *sustainable* profit rate under price cutting, so the lowest-unit-cost technique displaces a rival even when it earns less at the going price (D2 against C at $100) | Shaikh 2016, Table 7.3 rows 1–5 (p. 271); pp. 313–317 (Tables 7.10–7.12, eq. 7.11, fig. 7.22) | share won; `leader_lowest_cost_share`; `d_share_price_all`; `price_to_pp` | `base` [3, mixed, 1–500] 0.81 (0.77–0.84) against 0.48 / 0.50; the leader is the lowest-cost firm in 0.94 of periods; price term of the sales share +0.25; 86 of 120 factorial cells beyond drift, all for the unit-cost rule | **Met**, except in two corners (A.7); but with the version 1 scrapping test (operating cost) the base advantage vanishes (0.55, B2) |
| 2 | Under real competition a capital-using, cost-reducing technique spreads by price cutting and the rate of profit falls even at a given real wage; under the profit-rate criterion it falls only at high wage shares | Shaikh 2016, p. 261; pp. 317–321 (Alternative 2: general rate 16 % → 15.2 %); Michl 2023, pp. 47–48 | `marx_biased_*`; `profit_rate_total` of the two controls | Spreads: realised change is Marx-biased for the unit-cost label in 0.84 of `base` seeds. Rate: an industry where every firm uses the unit-cost rule realises a lower profit rate than one where every firm uses the profit-rate rule (`is_marx_15` [1, controls, 1–200]: 8.5 % against 10.9 %), at similar prices (A.6) | **Met at industry level**; the economy-wide claim is **not testable** (rbar exogenous) |
| 3 | After a cost-cutter takes over, the price first falls, then rises to the new regulating price of production (D2: back up to $101.30) | Shaikh 2016, p. 316 | `price_rise_after_adoption`; `price_to_pp`; figure 5 | Real competition: the price at t = 199 exceeds that at t = 100 in 0.17–0.31 of seeds (innovation set, marx 0.5 to 3) and ends 10–20 % above the price of production; leader-follow: at most 0.06, ending below it (0.85–0.93) | **Met under real competition only** |
| 4 | A technique that raises the profit rate at current prices cannot lower the general rate once new prices of production settle, at a constant real wage (Okishio's theorem) | Okishio 1961 *(not in the library)*, as stated in Shaikh 2016, p. 320; Shaikh 1978, pp. 241–242; Roemer 1979, p. 379; Duménil & Lévy 2005, p. 209 | `profit_rate_okishio` against `profit_rate_shaikh`; controls' `profit_rate_total` | The theorem is about the general rate: **not testable here**, since rbar is a parameter and the money wage is the numéraire (the constant real wage holds by construction, the general rate does not respond). Its micro premise, that the adopter earns the higher rate, fails: `base` 4.5 % (profit-rate label) against 8.4 % | **Not testable**; premise **failed** |
| 5 | A technique that does not pass the profit-rate test is never adopted by a rational capitalist; a higher-cost method can dominate if it has the lower price of production (Sraffa's criterion) | Shaikh 2016, p. 320 n. 36 and p. 322 (stating the standard view); Roemer 1979, p. 379 | `conflict_adopted_shaikh`; `okishio_dearer`; share won | The unit-cost firms adopt every conflict-zone design (`conflict_adopted_shaikh` 1.0) and they are the ones selected; the profit-rate firms' refusals and dearer orders go with losing (`okishio_dearer` 0.49 in seeds the unit-cost rule wins, 0.17 where it loses, stage 2) | **Failed** as a statement about who survives |
| 6 | The two criteria conflict only when technical change is Marx-biased (capital-using, labour-saving) and when the rule is evaluated at prices that the adoption will change; the profit-rate criterion is the right one if prices do not fall after adoption | Duménil & Lévy 2005, p. 209; Michl 2023, pp. 47–48; Shaikh 2016, pp. 323–324 | zone shares; `marx_biased_*`, `gamma_*`, `chi_*`; `no_tech`; the neutral set; anchor cells | Fixed menu: drift (0.51). Neutral set: conflict share 0.04, share won 0.78. Anchor pricing (prices held at each firm's target return) at rbar 0.16: the profit-rate rule wins (0.26) | **Met** |
| 7 | Selection on realised profitability drives accumulation, selection on price drives market share; the balance depends on finance and on the intensity of selection | Nelson & Winter 1982, pp. 17, 19; Duménil & Lévy 1995, p. 217; Metcalfe 1998 *(not in the library)* | `d_share_accum_all` against `d_share_price_all`; the finance arm; CHI | The price term is the larger in 93 % of cells; accumulation decides only with self-finance, growing demand and no entry, where the investment rule flips the winner (`lf-re-g01-cat-r16` 0.32 → 0.85 with the accelerator [3, mixed, 1–500]; no seed borrows); CHI 0.25–4 moves nothing (0.71–0.79) | **Met for the investment rule; not for selection intensity** (A.8) |
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
made at actual and projected market prices, which differ from prices of production. That
was the first reading, written before Part B. **Part B refutes it: the trap is not what
reverses the outcome.** With one anchor for all firms (the leader's target-return price)
the profit-rate rule still wins (0.32), with the *markup* anchor, which favours the lowest
unit cost by construction, it still wins (0.27), and with the accelerator instead of
retained earnings the reversal disappears (0.47, at drift); the reversal sets in between
rbar 0.08 and 0.10, as entry closes (B2). What the anchor runs show (B1) is a closed industry in which
growth is financed out of profits: no entrant arrives (the realised rate on new plants,
5–7 %, never reaches 16 %), the unit-cost firm piles up capital-intensive designs
(capital per unit 160 → 233 → 359 over t = 1–25, 26–75, 76–125 in `1_anchor_r16_mixed_s3`,
against 149 → 167 → 204), so that each unit of retained profit buys it ever less capacity
(capacity added = retained profit / κ of the new plant), its old plants are retired in a
war, and the minimum of two firms keeps a duopoly. Smaller plants make the reversal
stronger, not weaker (0.08 with plants of 10, B2): it is capital per unit, not the
indivisibility of plants, that slows the unit-cost firm. And the retirement in wars is the
decisive step: with the version 1 scrapping test (operating cost, Salter's margin) the same
cell gives the unit-cost rule 0.90 (B2). **The first reversal is a property of the version 2
scrapping test in a closed industry, not of real competition against Okishio.**

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
other rule; and under the categories rule the unit-cost firms build every conflict-zone
design, whose unit-cost saving is small and whose extra capital is large, while leader-follow
pricing does not reward a small cost edge (every firm cuts to its floor whenever capacity
is not short). Under the accelerator, investment follows sales instead of profits, and
sales follow price: the price channel drives accumulation and the unit-cost rule wins.
**The investment rule decides the contest here, which is the second half of the research
question; Part B adds that borrowing plays no part in it** (not one of the 500 seeds of the
twin carries debt: the accelerator is financed out of cash). It does not contradict
Shaikh, whose price-cutting argument needs a firm that can expand capacity to take the
market (p. 314: the cost-cutter "makes room for itself"); with retained earnings, thin
margins and capital-heavy plants the unit-cost firm cannot.

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

What was run, in one table (all with both neutral controls over the same seeds; tables in
`outputs/analysis/`, stage 4 rows appended to `runs.csv` and `cells.csv` with stage = 4,
candidate rows in `outputs/analysis/b3/`):

| Track | Item | Seeds | Done |
|---|---|---|---|
| B1 | Regression of the realised gap and of `shaikh_wins` (stage 2, 17 585 seeds) | existing | yes |
| B1 | Whole-run attribution for the cells of section 6 (figure B1.2) | existing | yes |
| B1 | Anchor reversal: reruns of seeds 3, 4, 5 of `anchor_r16` and seed 3 of `anchor_r05` | reruns | yes |
| B1 | Finance twin side by side, seed 1 (figure B1.7) | reruns | yes |
| B1 | Takeover timing (figure B1.3, `b1_takeover.csv`) | existing | yes |
| B2 | `rc-re-g01-cat-r16` | 1–500 | yes |
| B2 | Anchor threshold: rbar 0.08, 0.10, 0.12, 0.14 (0.05 and 0.16 from stage 1) | 1–200 (0.10, 0.12: 1–500) | yes |
| B2 | Added by Part A: the leader-follow reversal with the best plant's unit cost as floor; with `MIN_FIRMS` = 1; with the accelerator without borrowing. The anchor reversal with one common anchor, with the markup anchor, with the accelerator, with `MIN_FIRMS` = 1 | 1–200 | yes |
| B2 | Finance × CHI: accelerator with borrowing, CHI 0.25 and 0.5, both pricing rules | 1–200 | yes |
| B2 | TAU sweep: 0.05, 0.10, 0.15 (categories), 0.10, 0.25 (marx 1.5) | 1–200 | yes |
| B2 | Added after the first B2 results: plant size 10 and scrapping on operating cost in the reversal cells; scrapping on operating cost at the defaults | 1–200 | yes |
| B3 | Two candidate rules behind new switches, at the base, leader-follow, rbar 0.16 and marx 1.5 cells | 1–200 | yes |

Seeds were cut from the prompt's 500 to 200 for the B2 cells other than the real-competition
twin (later also `anchor_r10`, `anchor_r12` and `scrap_ucs` were taken to 500), as section 6 of the prompt allows: the machine had 4 + 2 cores, not 10 (measured: 17
runs a second on the 4-core machine, 6 on the 2-core one).

### B1. The mechanism, on existing data

**The realised profit-rate gap (open question 2).** OLS over the 17 585 decided mixed seeds
of stage 2 with cell fixed effects, standard errors clustered by the 176 cells
(`b1_regression.csv`):

| Outcome | Specification | `okishio_dearer` | `price_to_pp` | `hhi_mean` | `n_firms_mean` | `war_episodes` | `shaikh_wins` | within R² |
|---|---|---|---|---|---|---|---|---|
| gap | mechanism | **0.075** (0.060, 0.091) | 0.010 (0.003, 0.017) | 0.013 (−0.005, 0.031) | 0.000 (−0.001, 0.001) | 0.0011 (0.0006, 0.0016) | | 0.08 |
| gap | + winner | **0.051** (0.038, 0.065) | 0.011 (0.004, 0.017) | 0.017 (0.002, 0.032) | 0.000 | 0.0011 (0.0007, 0.0016) | **0.038** (0.029, 0.047) | 0.15 |
| gap | prompt's list (+ decomposition) | 0.016 (0.004, 0.029) | 0.011 (0.005, 0.018) | 0.007 (−0.007, 0.020) | 0.000 | 0.0009 (0.0004, 0.0014) | | 0.24 |
| `shaikh_wins` | mechanism | **0.635** (0.558, 0.713) | −0.013 (−0.023, −0.004) | −0.098 (−0.237, 0.041) | −0.001 | −0.0006 | | 0.09 |

(gap = realised profit rate of the unit-cost label minus that of the profit-rate label over
t = 100–199; in the prompt's list `d_share_price_all` and `d_share_accum_all` enter with
0.068 and 0.057: they are parts of the outcome, which is why the second line is the one to
read.) Figure B1.1 plots the gap against `okishio_dearer` with a pooled line for each pricing
rule.

Reading. Among seeds of the same cell *and with the same winner*, every 0.1 more of dearer
orders by the profit-rate firms widens the gap by half a point of profit rate: **Shaikh's
hypothesis holds within cells**. The winner has its own premium of 3.8 points, and
concentration adds a little (HHI coefficient 0.017): **the market-structure hypothesis
holds too, as a separate premium**. The number of firms adds nothing once HHI is in. The
share of dearer orders is also the strongest within-cell predictor of who wins (a 0.18
standard deviation raises the unit-cost rule's chance by 0.11).

**Whole-run attribution** (figure B1.2, `b1_attribution.csv`). The cells of section 6 split
into three groups. *Price, then exits*: `base`, `is_marx_15` (capacity +0.28 and +0.32 through
the exits of profit-rate firms; sales +0.25 and +0.27 through prices). *Accumulation for the
unit-cost rule*: `lf` (+0.09), the leader-follow twin with the accelerator (+0.31), the
operating-cost floor (+0.32) and `anchor_r05` (+0.20). *Accumulation against it*:
`anchor_r16` (−0.21), `lf-re-g01-cat-r16` (−0.18), `rc-re-g01-cat-r16` (−0.20 at 100 seeds).
Entry terms are small everywhere (−0.06 to +0.03): entrants copy the majority, so they move
little share between labels.

**The anchor reversal** (figures A5, B1.4–B1.6; reruns of `1_anchor_r16_mixed_s3`, `_s4`,
`_s5` and `1_anchor_r05_mixed_s3`).

- *When the anchor sets the price.* Wars cover 114, 171 and 131 of the 200 periods in the
  three rbar 0.16 seeds; between wars a firm moves toward its own target-return price within
  2.5 % of the leader. Posted prices are nearly equal for the two labels (t = 1–25: 84.1
  against 84.6 in seed 3), but the anchors part: the unit-cost firm's own uc + 0.16 κ rises
  (100.5, 106.5, 122.2 over t = 1–25, 26–75, 76–125) while the profit-rate firm's falls
  (99.3, 96.3, 95.8), so in every pause the unit-cost firm sits at the top of the band.
- *Which technique each rule orders.* From t = 1–5 the profit-rate firms order D1 and the
  designs drawn from it (seed 3: D1 at t = 1, T2, D1, T7); the unit-cost firms order every
  design (T3, T5, T6, T9 ...), including the conflict-zone ones, whose capital per unit
  climbs from 160 to 359. The two labels reach almost the same unit cost (74.8 against 75.5,
  then 64.7 against 63.2): the extra capital buys the unit-cost firm almost no cost edge.
- *The unit-cost firm's margin.* Its margin per unit is about the profit-rate firm's (9.2
  against 9.1 over t = 1–25), but over a capital twice as large late in the run its rate
  falls (7.3 % against 9.1 % over t = 76–125 in seed 3; −0.67 margin and 5.9 % in seed 5,
  where the price falls below its average unit cost). With capital per unit rising faster
  than its profit, each unit of retained profit buys it less capacity than its rival's;
  obsolescence then retires its old plants in a war (126–128 in seed 3, 131–133 in seed 4,
  77–79 in seed 5: 12, 9 and 6 plants retired with the price below their unit cost for two
  periods).
- *Why entry stops.* The realised rate on plants built in the last five periods averages
  5.3 %, 7.2 % and 6.9 %, against rbar = 16 %: the entry probability is zero in 200, 199 and
  197 of the 200 periods. At rbar 0.05 (seed 3, figure B1.6) the same rate (4.2 %) is above
  rbar often enough for entry in 75 periods, 59 of 61 entrants inherit the unit-cost rule,
  and the profit-rate label has no capacity left after t ≈ 26.

**The finance twin** (figure B1.7, seed 1 under retained earnings and under the accelerator
with borrowing). Under retained earnings the two labels spend alike until t ≈ 100, then the
profit-rate label's spending grows without bound (it reinvests every profit into a growing
market) while the unit-cost label's stops at t ≈ 145; the price falls every period (98 →
48). Under the accelerator the profit-rate label spends almost nothing (10 orders in 200
periods: it loses sales, so it needs no capacity), the unit-cost label spends in bursts
after shortages, and the price climbs back to 103–118. **Debt is zero in both** (at most
6e-11): not one of the 500 seeds of `lf-acd-g01-cat-r16` has a debt-to-sales ratio above
1e-6, against 0.83–0.95 of seeds under real competition with borrowing, where about 1.9
firms go bankrupt per run. What changes for the profit-rate firms is therefore not
borrowing but the volume rule: under the accelerator they stop investing when they stop
selling. The B2 cell without borrowing confirms it: `lf-acc-g01-cat-r16` [4, mixed, 1–200]
0.84 (0.79–0.89), controls 0.54 / 0.50, the same as the twin with borrowing.

**Takeover timing** (figure B1.3, `b1_takeover.csv`). Share of seeds with a takeover, share
of takeovers before t = 100, median `takeover_t`: `base` [3, 1–500] 0.88, 0.44, 107; `lf`
[3, 1–500] 0.92, 0.30, 114; `is_marx_15` [1, 1–200] 0.53, 0.18, 139; `anchor_r16` 0.94, 0.21,
127; `lf-re-g01-cat-r16` [3, 1–500] 0.99, **0.75**, 82; `lf-acd-g01-cat-r16` 0.84, **0.85**,
78; `rc-acd-g01-cat-r16` [2, 1–100] 0.25, 0.80, 70. In the cells that decide the finance
question most takeovers are over before the window opens, so the window statistics (prices,
profit rates, `d_share_*` without `_all`) describe the industry *after* selection, not the
selection itself. Use the `_all` terms for attribution, and read window profit rates as the
winners' and losers' rates in the industry the takeover left behind.

### B2. More cells

| Cell [4, mixed, seeds] | Share won (95 %) | Controls (uc / pr) | Beyond drift | Reading |
|---|---|---|---|---|
| `rc-re-g01-cat-r16` (1–500) | 0.43 (0.39–0.47) | 0.49 / 0.49 | **no** | the real-competition twin is *not* a reversal: 0.32 at 100 seeds was a draw from the tail |
| `anchor_r08` (1–200) | 0.55 (0.47–0.62) | 0.53 / 0.51 | no | |
| `anchor_r10` (1–500) | **0.31** (0.27–0.35) | 0.49 / 0.53 | yes, profit-rate rule | 0.33 at 200 seeds |
| `anchor_r12` (1–500) | 0.46 (0.41–0.51) | 0.50 / 0.48 | no | the dip is confirmed at 500 seeds |
| `anchor_r14` | **0.30** (0.24–0.36) | 0.50 / 0.52 | yes, profit-rate rule | |
| `anchor_r16-leader` (one anchor for all) | **0.32** (0.26–0.39) | 0.49 / 0.54 | yes, profit-rate rule | the reversal does not need each firm's own anchor |
| `anchor_r16-markup` (markup anchor) | **0.27** (0.21–0.34), 17 undecided | 0.52 / 0.52 | yes, profit-rate rule | an anchor that favours the lowest unit cost by construction does not undo it |
| `anchor_r16-acc` (accelerator) | 0.47 (0.40–0.54) | 0.54 / 0.55 | no | the accelerator removes the reversal |
| `anchor_r16-minf1` (`MIN_FIRMS` = 1) | 0.25 (0.20–0.32) | 0.55 / 0.51 | yes, profit-rate rule | the floor of two firms is not the cause |
| `lf-re-g01-cat-r16-flooruc` (unit-cost floor) | **0.045** (0.02–0.08) | 0.50 / 0.54 | yes, profit-rate rule | the strongest profit-rate result of all |
| `lf-re-g01-cat-r16-minf1` | 0.31 (0.25–0.38) | 0.54 / 0.47 | yes, profit-rate rule | as the default (0.32) |
| `anchor_r16-ps10` (plants of 10) | **0.08** (0.05–0.13), 8 undecided | 0.47 / 0.50 | yes, profit-rate rule | finer plants strengthen the reversal |
| `lf-re-g01-cat-r16-ps10` (plants of 10) | **0.13** (0.09–0.18) | 0.55 / 0.52 | yes, profit-rate rule | idem |
| `lf-acc-g01-cat-r16` (accelerator, no borrowing) | **0.84** (0.79–0.89) | 0.54 / 0.50 | yes, unit-cost rule | the twin's flip is the accelerator's |
| `scrap_ucs` (defaults, scrapping on operating cost; 1–500) | 0.55 (0.50–0.59) | 0.44 / 0.49 | **no** (disjoint from one control only) | the base advantage needs the version 2 scrapping test |
| `lf-scrapucs` (leader-follow, scrapping on operating cost) | 0.66 (0.59–0.72) | 0.47 / 0.44 | yes, unit-cost rule | no move (`lf` 0.66 [1, 1–200]): the markup floor keeps prices above unit cost |
| `lf-flooruc-scrapucs` (leader-follow, unit-cost floor, scrapping on operating cost) | 0.70 (0.63–0.76) | 0.48 / 0.50 | yes, unit-cost rule | down from 0.83 (`lf_floor_uc` [1, 1–200]) |
| `is15-scrapucs` (marx 1.5, scrapping on operating cost) | 0.75 (0.68–0.80) | 0.47 / 0.50 | yes, unit-cost rule | down from 0.94, still beyond drift |
| `anchor_r16-scrapucs` | **0.90** (0.84–0.93) | 0.45 / 0.51 | yes, **unit-cost rule** | the anchor reversal is a scrapping effect |
| `lf-re-g01-cat-r16-scrapucs` | **0.31** (0.25–0.38) | 0.54 / 0.47 | yes, profit-rate rule | the leader-follow reversal is not |
| `lf-re-g01-cat-r16-flooruc-scrapucs` | 0.43 (0.36–0.50) | 0.51 / 0.50 | no | the unit-cost floor's amplification is |
| `rc-acd-chi025` / `rc-acd-chi05` (static, rbar 0.05) | 0.65 (0.58–0.71) / 0.65 (0.58–0.71) | 0.43 / 0.46; 0.41 / 0.50 | yes / yes, unit-cost rule | CHI 1: 0.64 [2, 1–100] |
| `lf-acd-chi025` / `lf-acd-chi05` | 0.73 (0.66–0.79) / 0.84 (0.78–0.88) | 0.44 / 0.44; 0.45 / 0.47 | yes / yes, unit-cost rule | |
| `tau_005` / `tau_010` / `tau_015` | 0.77 (0.70–0.82) / 0.79 (0.73–0.84) / 0.81 (0.75–0.86) | 0.48 / 0.47; 0.48 / 0.49; 0.48 / 0.48 | yes, unit-cost rule | no move (`base` 0.81, `tau_025` 0.78) |
| `is15-tau_010` / `is15-tau_025` | 0.98 (0.95–0.99) / 0.96 (0.92–0.98) | 0.53 / 0.48; 0.53 / 0.47 | yes, unit-cost rule | no move (`is_marx_15` 0.94) |

**The anchor threshold** (figure B2.1). With rbar 0.05 (stage 1) 0.66 and 0.26 at 0.16, the
share won falls as rbar rises, but not monotonically (0.55, 0.31, 0.46, 0.30 at 0.08, 0.10,
0.12, 0.14; the cells at 0.10 and 0.12 were taken to 500 seeds and the dip at 0.12 stays), and
it crosses below the controls between 0.08 and 0.10. Two things change with
rbar under the anchor rule: the ranking of target-return prices (on the menu D1 undercuts D2
above rbar ≈ 0.064, C undercuts D2 above ≈ 0.147) and entry (entrants in the window: 15.4 at
0.05, 2.9 at 0.08, 1.1 at 0.10, 0.5 at 0.12, 0.1 at 0.14). The common-anchor cell (0.32)
and the markup-anchor cell (0.27), where the first channel is shut, still reverse, and the
accelerator cell (0.47) does not: **the reversal sets in as entry closes and needs
investment out of retained profits**; it is gradual in rbar but quick between 0.05 and
0.10. The briefs' anchor trap is real on the menu but plays no visible part here.

**The scrapping test, a factor stage 1 did not vary.** Version 2 retires a plant after two
periods with the price below its *unit* cost ucs + δκ (`SCRAP_COST = "unit_cost"`;
version 1 used the operating cost ucs, the margin of Salter, pp. 64–65, and of Shaikh's
Table 7.3, row 1). Stage 1 varied only the number of periods (4 / 4: no move). With the
operating-cost test the defaults lose their result: `scrap_ucs` 0.55 at 500 seeds, at drift, because old
plants stay, prices fall to operating costs (the profit-rate label's hurdle averages 0.004),
the industry rate falls below 5 %, entry stops (0.1 entrants in the window, 2.3 firms at the
end) and the two rules choose alike. Under the innovation set (marx 1.5) the advantage
shrinks (0.94 → 0.75) but survives; under leader-follow nothing moves (0.66), because its
markup floor keeps prices above every plant's unit cost and the test seldom binds. The
anchor reversal becomes a unit-cost win (0.90). So
the base advantage of the unit-cost rule and the anchor reversal both run through the same
mechanism: the unit-cost test retires plants with a large capital charge first, and in a
war those are the unit-cost label's older plants when they are not the newest best
practice (anchor), or the rivals' (base, where the unit-cost label holds the newest
plants and the exits fall on the profit-rate firms).

**What the reversals have in common, and what they do not.** Both live where (1) entry is
closed (rbar 0.16: the industry's rate is above rbar in fewer than 3 of 100 periods),
(2) investment is financed out of retained profits, so that capacity grows by retained
profit over capital per unit of the new plant, which the unit-cost rule keeps raising
(both disappear with the accelerator: 0.47 and 0.85), and (3) the technical-change rule is
the categories rule, under which the profit-rate rule seldom orders a dearer technique
(`okishio_dearer` 0.06–0.10) while the unit-cost rule takes every conflict design, gaining
little cost and much capital. They part on the scrapping test: the anchor reversal needs
it (wars push the price below the unit cost of the unit-cost label's capital-heavy plants,
which obsolescence then retires: 0.90 for the unit-cost rule with operating-cost
scrapping), the leader-follow reversal does not (0.31 either way). Stage 2
says each condition is needed in the leader-follow corner (100 seeds): open entry
(`lf-re-g01-cat-r05`) 0.64; static demand (`lf-re-static-cat-r16`) 0.51; the accelerator
(`lf-acd-g01-cat-r16`) 0.83; the innovation set (`lf-re-g01-is15-r16`) **0.98**. The unit-cost
floor makes it stronger (0.045), not weaker. A rerun of its seed 1 shows how: the
unit-cost label holds 0.55–0.63 of capacity until t = 150, with margins and profit rates
close to the profit-rate label's (6.8 against 7.0 per unit, 8.0 % against 8.6 % over
t = 100–149) but plants far more capital-intensive (402 against 236 per unit); a war of ten
periods then takes the price from 58 to 49 at t = 163, down to the leader's best unit cost,
and 97 plants of the unit-cost label (none of the profit-rate label's) are retired by
obsolescence within 15 periods, because the version 2 scrapping test compares the price with
the plant's *unit* cost ucs + δκ, depreciation included: the capital-heavy vintages fail it
first. Its capacity share falls to 0.02 by t = 199. Shaikh (Table 7.3 row 1, p. 271: price
cutting is limited by operating costs) and Salter (pp. 64–65: old plants run until their
operating cost reaches the total cost of best practice) put the margin at operating cost;
the cells `*-scrapucs` of B2 test whether the reversals depend on this choice. They split
the two reversals: with scrapping on operating cost the anchor reversal turns into a clear
win for the unit-cost rule (0.90), the unit-cost floor's amplification disappears (0.43, at
drift), but the leader-follow reversal stays (0.31). **The anchor reversal is a scrapping
effect; the leader-follow reversal is an accumulation effect.**
This is Nelson and Winter's selection through profitability-keyed investment (pp. 17, 19) in
the one corner where the price channel is silent; it is also the condition Shaikh's
mechanism needs and does not get, a cost-cutter able to expand (p. 314).

**Finance × CHI.** The briefs' second version of the χ trap: with borrowing, weak selection
should let the higher-rate firms out-accumulate the cheaper ones. It does not: with the
accelerator and borrowing the unit-cost rule wins 0.65 at CHI 0.25 and 0.5 under real
competition (0.64 at CHI 1) and 0.73 and 0.84 under leader-follow, all beyond drift. Under
real competition with borrowing the profit-rate firms' hurdle is almost zero (mean 0.013 at
CHI 0.25): prices sit close to costs, so the two rules nearly agree, and what remains is the
unit-cost rule's edge. The accumulation channel does not need weak selection; it needs
self-finance, growth and a closed industry (above).

**TAU.** As the paper argument of A.8 predicts, τ from 0 to 0.25 moves nothing under either technical-change rule (categories 0.77–0.81, marx 1.5 0.96–0.98): drawn designs keep a conflict zone whatever τ.

### B3. Rules under which the profit-rate rule can dominate

**On paper first.** The research question asks *under which conditions* each rule wins, so a
map of where the profit-rate rule dominates belongs to the answer, as long as the condition
is a feature of the economy and not a construction that hands it the win.

1. *The price at which the hurdle is evaluated* (`choices.md`: "own"). Okishio's theorem
   compares techniques at prices of production (Shaikh 2016, p. 320; Shaikh 1978,
   pp. 241–242; Duménil and Lévy 2005, p. 209: prices of production are assumed to
   prevail); Shaikh insists that actual choices are made at actual and projected market
   prices (p. 321), and Duménil and Lévy's test evaluates next period's technology at the
   current wage (2005, pp. 210–211), i.e. at going prices. Shaikh's own argument says where
   evaluation at a lower price leads: there is a range of prices at which the lower-cost
   technique also has the higher rate (pp. 315–317, fig. 7.22), so any rule evaluated at a
   price low enough converges on the unit-cost rule. **Trap it is near**: none (it changes
   what the rule sees, not what it is). Implemented as `HURDLE_PRICE = "regulating"`: the
   profit-rate rule evaluates its hurdle at the price of production uc* + r̄ κ* of the
   lowest-unit-cost technique in operation (the regulating capital, Shaikh 2016,
   pp. 265–266). The leader's price was considered and set aside: under both pricing rules
   followers post the leader's price in most periods, so it would hardly differ from "own".
2. *A hurdle at the general rate* (h = r̄). It is Sraffa's criterion of choice (the lower
   price of production at the ruling rate, Shaikh 2016, p. 320 n. 36), Salter's replacement
   margin with a normal return (1966, pp. 56–57, 84–85), and the K+S payback rule (min p +
   b c, Dosi and Roventini 2025, pp. 37–38) read as δ + h = 1/b. It stops being "the best
   rate at the current price": it is the profit-rate rule evaluated at prices of production
   of its own best technique (at p = min_j (uc_j + r̄ κ_j) the best rate on offer is exactly
   r̄). **Trap it is near**: the anchor trap, if combined with target-return pricing (the
   same criterion in the price and in the choice). Implemented as `HURDLE_TARGET = "rbar"`.
3. *Weak selection with borrowing* is a condition, covered by B2's finance × CHI block.
4. *Demand where capacity is the constraint.* Stage 1: initially unmet demand 0.76 (beyond
   drift, for the unit-cost rule), unmet and growing 2 % 0.46, growing 3 % 0.43 (at drift,
   500 seeds), never a reversal. Growth dilutes rather than reverses because at rbar 0.05 it
   opens entry wide (63.7 entrants in the window and 44 firms at the end under 3 % growth):
   entrants copy the rule of an incumbent drawn by market share, plus 2 % mutation, so heavy
   entry is a neutral copying process that pulls the population toward drift. Only when
   entry is closed does growth turn into the accumulation channel and reverse the outcome
   (B2 above).
5. *An evolving hurdle* (firms move h toward the realised rate of their recent plants): on
   paper only. Since the profit-rate firms realise less than they expect (4.7 % against a
   mean hurdle of 9.4 % in `base`), such a rule would lower their hurdle toward the
   realised rate, i.e. toward the unit-cost rule, as candidates 1 and 2 do; it would be a
   learning version of candidate 2 with the realised industry rate in place of r̄.
   Prediction: drift at the defaults, no dominance. Not implemented.

**Implementation** (following the six steps of `CLAUDE.md`): `equations/regulating_price.py`
(new) and `hurdle_at_general_rate` in `equations/hurdle.py`; the switches `HURDLE_PRICE`
("own" by default) and `HURDLE_TARGET` ("best" by default) in `parameters.py`; one helper in
`model/scheduler.py` (`_hurdle`, `_regulating_price`) called where the hurdle was computed
before (step 4 for incumbents, step 6 for entrants), the regulating price taken once per
period before any plant retires, so that no firm's order matters; tests in
`tests/test_investment.py` (`TestHurdleAlternatives`: the regulating price on Shaikh's menu,
ties by kappa not by order, the general-rate hurdle, the defaults unchanged, the label swap
under each candidate) and both switches in `test_switches_run`. `firm.type` is read only
where it was (the `HURDLE_RULES` lookup and the entrant's inheritance).
**`python -m debug.compare_runs`**: `run.py` at the defaults, before and after the change,
"identical: every shared column of every table within 1e-12", and the same for
leader-follow with the innovation set. Since the two switches add two columns to the
`runs` table, `experiments.sensitivity.rerun` now compares parameters one by one instead of
`param_hash` when the stored row predates a parameter (rows of stages 1–3 still reproduce
exactly: `1_base_mixed_s4`, `3_lf-re-g01-cat-r16_mixed_s7` checked).

**Neutrality check.** Both candidates change only the hurdle of the profit-rate rule: the
unit-cost rule keeps h = 0; the regulating price is an industry price, the same for every
firm, computed from all plants in operation in an order that does not depend on firms; h =
r̄ is a parameter. Neither reads `firm.type` and neither hands one label an advantage by
construction (the label-swap tests pass). Candidate 2 combined with the anchor rule would
put the same criterion in the price and in the choice: not run.

**Results** (stage "b3", seeds 1–200, both controls; `outputs/analysis/b3/cells.csv`,
figure B3.1):

| Cell | Current rule (reference) | h = r̄ (`HURDLE_TARGET`) | regulating price (`HURDLE_PRICE`) |
|---|---|---|---|
| `base` (rc, re, cat, r̄ 0.05) | 0.81 (0.77–0.84) [3, 1–500] | **0.48** (0.41–0.55), controls 0.48 / 0.45 | **0.53** (0.46–0.59), 0.48 / 0.49 |
| `lf` | 0.71 (0.67–0.75) [3, 1–500] | **0.56** (0.49–0.63), 0.47 / 0.49 | **0.48** (0.41–0.55), 0.47 / 0.45 |
| marx 1.5 (`is_marx_15`) | 0.94 (0.90–0.97) [1, 1–200] | 0.76 (0.70–0.81), 0.53 / 0.53 | 0.78 (0.71–0.83), 0.53 / 0.53 |
| r̄ 0.16 (`rbar_16`) | 0.64 (0.57–0.70) [1, 1–200] | 0.63 (0.56–0.69), 0.49 / 0.49 | 0.715 (0.65–0.77), 0.49 / 0.46 |

The eight candidate cells were run twice, on the Mac's VM (Linux, aarch64) before the
connection dropped and in the session's container (Linux, x86_64): the shares won and both
controls' shares agree cell for cell.

Mean hurdle of the profit-rate label: 0.094 (current rule, `base`), 0.050 (both candidates,
`base`), 0.160 and 0.276 at r̄ 0.16; dearer orders 0.51 → 0.08–0.10 at r̄ 0.05.

Reading. **Neither candidate lets the profit-rate rule dominate anywhere.** Evaluated at
prices of production with r̄ = 0.05, the profit-rate rule's hurdle falls from 0.094 to 0.05,
it stops ordering dearer techniques, and it becomes almost the unit-cost rule: the contest
goes to drift under the categories rule and the unit-cost advantage shrinks under marx 1.5
(0.94 → 0.76–0.78, still beyond drift, because the Marx-biased designs keep a conflict zone
at h = 0.05). At r̄ = 0.16 the regulating price is *above* the market price (prices end at
0.57 of the price of production in that cell), the hurdle rises (0.276), the profit-rate
firms order more dearer techniques (0.24) and lose more (0.715). This is the clearest result
of Part B for the presentation: **the unit-cost rule's advantage is the profit-rate rule's
evaluation price**. Okishio's criterion applied at the prices of production of a low
general rate is nearly Shaikh's criterion; applied at the inflated current price of a
growing price war, or at the price of production of a high general rate the market never
reaches, it chooses techniques that the falling price punishes. The industry profit rates of
the controls tell the same story: under the candidates, an industry entirely on the
profit-rate rule realises 8.7–9.4 % against 8.7 % on the unit-cost rule at r̄ 0.05.

---

## 4. What this means for step 5 (proposed rows for `choices.md`, not decisions)

| Proposed row | Proposed status | Why (section) |
|---|---|---|
| Technical change: the marx innovation set (TECH_BIAS 1.5) is the main specification; TECH_BIAS 0.5 and 3 and the neutral set are treatments; the categories rule is the version 1 robustness check; `TECH_DRAWS = False` is reported as the null (no contest) | Treatment (as the results proposed), with the reason now argued from the literature | A.2, A.3, (b) |
| Pricing: real competition and leader-follow are the price-war treatment; the anchor rule is not a treatment but is reported as a closed-entry, self-financed reversal (it reverses from rbar ≈ 0.10, with a common or a markup anchor too, not with the accelerator), not as the briefs' anchor trap | Treatment / reported | A.7, B2 |
| `LEADER_FOLLOW_FLOOR`: the results recommended `unit_cost` for the leader-follow arm (0.83 against 0.66 in stage 1). Before deciding, note that in the closed growing corner the unit-cost floor *strengthens* the profit-rate rule (0.045 against 0.32) | Group decision, with this side effect recorded | B2 |
| Finance: name the arm "investment rule" (retained earnings against the accelerator). Borrowing is inert under leader-follow (no debt in 500 seeds) and matters under real competition (bankruptcies); keep accelerator with and without borrowing as two levels if the group wants to speak of finance proper | Treatment, renamed | B1 (finance twin), B2 |
| rbar: present 0.05 against 0.16 as *open against closed entry*, since that is what it does in the model (industry rate above rbar in 95 against fewer than 3 of 100 periods); both reversals need the closed industry | Treatment (relabelled) | A.9, B2 |
| CHI: fixed at 1; the briefs' trap does not spring because the profit-rate firms do not realise the rate they maximise | Fixed (confirmed) | A.8 |
| `MIN_FIRMS` = 2: no effect on either reversal | Fixed (confirmed) | B2 |
| `SCRAP_COST`: not varied in stages 1–3, yet with the operating-cost test (version 1; Salter's and Shaikh's margin) the defaults go to drift (0.55 at 500 seeds), marx 1.5 falls to 0.75, leader-follow does not move (0.66; 0.70 with the unit-cost floor, against 0.83), and the anchor reversal flips to 0.90. Make it a factor of the next sensitivity run and argue the choice from the texts before fixing it | **Treatment to examine before step 5** | B2 |
| `PLANT_SIZE` = 20: no move at the defaults (stage 1), but plants of 10 strengthen both reversals (0.08, 0.13) | Fixed, with the closed-industry sensitivity recorded | B2 |
| `HURDLE_PRICE` ("own", "regulating") and `HURDLE_TARGET` ("best", "rbar") | **Candidate (analysis, 8 November 2026)**; defaults unchanged; proposed as one robustness treatment, "Okishio at prices of production", since it shows that the contest is about the evaluation price | B3 |
| Reproducibility: Python 3.12 or later to reproduce `runs.csv` rows; CI on 3.13 | Proposed | header |
| Window: report attribution over the whole run (`_all`), not the window, wherever takeovers come before t = 100 | Proposed | B1 |

## 5. Open questions left

1. **The anchor threshold is not monotone** (0.31 at rbar 0.10, 0.46 at 0.12, 0.30 at 0.14;
   the first two at 500 seeds): the dip at 0.12 is not noise. A candidate explanation, not
   tested: on the menu the target-return ranking of C and D2 switches at rbar ≈ 0.147 and that
   of D1 and D2 at ≈ 0.064, so the anchors' ordering of the initial techniques changes inside
   the range. What differs at 0.12 is that the profit-rate firms order dearer techniques more
   often (0.22, against 0.12 at 0.10 and 0.14) and the accumulation term is neutral (+0.01,
   against −0.15 and −0.17); reruns of a few rbar 0.12 seeds against their rbar 0.10 twins
   would tell why.
2. **Plant size in the closed corner.** Plants of 10 make both reversals stronger (0.08 and
   0.13): finer investment lets self-financed accumulation work more smoothly. The default
   of 20 (stage 1: 40 moved nothing at the defaults) is therefore not neutral in the closed
   industry; worth a sentence in the presentation.
3. **The scrapping test.** B2 found that `SCRAP_COST` decides the size of the base result
   (0.81 → 0.55 with the operating-cost test) and the anchor reversal (0.26 → 0.90), and it
   was never varied in stages 1–3. It needs its own stage 1 cell at 200 seeds under both
   pricing rules and the innovation set before step 5, and an argument from the texts: the
   operating-cost margin is Salter's and Shaikh's, the unit-cost test counts a sunk capital
   charge.
4. **The window.** Should the headline statistics move to t = 50–199 or to the whole run?
   In the cells that decide the finance question most takeovers come before t = 100.
5. **Per-mechanism random streams** (results §8.6): still open; the controls depart from 0.5 by
   up to 0.12.
6. **An evolving hurdle** (B3, item 5): not implemented; the prediction (drift) is cheap to
   test once implemented.
7. **The economy-wide Okishio question** (row 4 of section 1) cannot be answered in a
   one-industry model with an exogenous rbar; the controls' industry profit rates (A.6)
   are the nearest the model gets.
8. Documentation details: the dangling "Under the categories rule:" at the end of the
   20-seed neutral-control record in `choices.md`; the 680 / 674.7 demand figure (results
   §8.5).

---

## Appendix: texts opened, with the pages used

Library: Zotero (`tools/zotero.py`, libraries perso and hivemind) and the Calibre library.
Pages are the printed page numbers of the PDF opened (the PDF's own page index in brackets
when it differs).

| Text | Library item | Pages used | For |
|---|---|---|---|
| Shaikh, A. (2016). *Capitalism: Competition, Conflict, Crises*. OUP | Zotero perso BMKVYW2U (PDF in storage 4GGIGFR6) | 260–261, 265–267 (regulating capitals, figs 7.1–7.3), 271–272 (Table 7.3), 296 (turbulent equalisation of rates on new investment), 313–317 (VII.1, Tables 7.10–7.12, eq. 7.11, fig. 7.22), 318–324 (Okishio theorem, Tables 7.16–7.20, n. 36, Park 2001, figs 7.23–7.24), 328 (ch. 8 opening) | rows 1–3, 5, 6, 10; A.1–A.7, A.10, A.11, (b), B3 |
| Shaikh, A. (1978). Political economy and capitalism: notes on Dobb's theory of crisis. *CJE* 2(2) | perso J9AEUKMD | 241–242 | row 4; B3 |
| Shaikh, A. (1980). Marxian competition versus perfect competition. *CJE* 4 | perso EECWZJXJ | 81 | row 1 |
| Roemer, J. (1979). Continuing controversy on the falling rate of profit. *CJE* 3 | perso TX2DFFI7 | 379–380, 382, 385, 388 | rows 4–5 |
| Duménil, G. & Lévy, D. (2005). Testing for the Marxian-classical criterion of technical choice. *Research in Political Economy* 22 | perso LWGHAJ9B (the PDF attached is the whole volume) | 209–213 | rows 4, 6; A.5, A.7; B3 |
| Park, C.-S. (2005). Testing Okishio's criterion of technical choice. *RPE* 22 | same volume | 199 (abstract only) | appendix only |
| Duménil, G. & Lévy, D. (1995). A stochastic model of technical change. *Metroeconomica* 46(3) | perso 48U7VRQQ | 213–214, 217 | rows 7; A.10, (b) |
| Michl, T. (2023). The falling rate of profit as a research program. *New School Economic Review* | perso FX3M6W5I | 36 (abstract), 37, 40–41 (Marx-biased technical change), 46 (prisoner's dilemma, Foley 1986b), 47–48 (conflict of the two viability criteria, switchpoints R and M) | rows 2, 6; A.3, A.6, A.10, (b) |
| Salter, W. E. G. (1966). *Productivity and Technical Change*. CUP | perso FCUBTW7P | 56–57, 64–65, 84–85 (scan, two pages per sheet) | row 9; B3 |
| Nelson, R. & Winter, S. (1982). *An Evolutionary Theory of Economic Change* | hivemind VATF967M | 17, 19, 262 | row 7; A.4, A.7, B2 |
| Foster, L., Haltiwanger, J. & Syverson, C. (2008). Reallocation, firm turnover, and efficiency. *AER* 98(1) | perso QX5VTYKC | 394–395, 397 | row 8; A.8 |
| Dosi, G., Moschella, D., Pugliese, E. & Tamagni, F. (2015). Productivity, market selection, and corporate growth. *Small Business Economics* | perso TVXQ9DA7 | abstract and introduction (online-first PDF, pp. 1–2; no journal pagination) | row 8 |
| Dosi, G. & Roventini, A. (2025). *Agent-based Macroeconomics* | perso TUR32YLD | 37–38 (machine choice and payback rule), 41 (entry) | B3 |
| Silverberg, G., Dosi, G. & Orsenigo, L. (1988). Innovation, diversity and diffusion. *EJ* 98 | perso EBVLD2YA | 1032 | row 11 |
| Seppecher, P., Salle, I. & Lavoie, M. (2018). What drives markups? *ICC* | perso L976DQGR | HAL version, pp. 1, 6 (only the framing; not used for a claim) | appendix only |

**Not available or not opened**, and so not cited for any claim except as reported by the
texts above: Okishio (1961), *Kobe University Economic Review* (Zotero item 3ZDE32J4 has no
file); Marx, *Capital* III, chs 13–15 (only vol. I is in the library; cited through
Duménil and Lévy 2005, p. 209, and Shaikh 2016, p. 265); Metcalfe (1998) (not in the
library); Botwinick (1993) (not in the library; cited through Shaikh 2016, pp. 265, 296);
Tsoulfidis & Tsaliki (2019) (item C69II6XZ, no file; Shaikh 2016, p. 313 reports
Tsoulfidis and Tsaliki 2005, 2011); Baldani & Michl (2000) (scanned PDF without a text layer,
not read; cited through Michl 2023, p. 46); Foley, Michl & Tavani (2019) (the file could not
be opened); Foley (1986, 1999, 2003) (not opened); Okishio (2001) and Park & Zarembka (2005)
(no file); Basu (2021) and Cogliano (2022, in Calibre) are in the library and bear on the
contest (Okishio's theorem; computational classical-Marxian models) but were not opened in
this session. The prompt's list misses two texts the library has and that bear directly on
the contest: **Shaikh (1980)**, the reply on the choice of technique, and **Baldani & Michl
(2000)**, the prisoner's-dilemma formalisation of forced adoption; and Duménil & Lévy (1995),
the stochastic profitability-selection model the DLF framework comes from.
