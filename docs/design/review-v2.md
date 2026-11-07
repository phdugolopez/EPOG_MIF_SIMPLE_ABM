# Review of version 2 (6 November 2026, revised 7 November)

Scope: branch `v2` at `cc1dd0c`, which commits the leader-follow pricing rule
(`equations/leader_follow_price.py`, `PRICING_RULE = "leader_follow"`) reviewed in draft on
6 November. The 98 tests pass, the label-swap tests included, under every switch listed in
`test_switches_run`. This note reviews what the agreed rules do to the contest, lists the
rule-level issues, proposes the documentation changes that version 2 needs, proposes a
technical-change rule that is Marx-biased by construction while leaving the two types free
to choose differently, and ends with the decisions of 7 November and the plan that follows
from them.

Sections: 1 what version 2 is; 2 findings; 3 documentation changes; 4 technical change;
5 decisions and plan.

**Decision of 7 November (Ugo).** The pricing rule and the technical-change rule (Marx-biased
or neutral set) are the two most sensitive parts of the model. Neither default changes now.
After the collector branch is merged, a first full sensitivity analysis over them and the
other switches decides whether each becomes a fixed version or a treatment. Sections 3 and 4
are written under that decision: they describe switches and treatment arms, not new
defaults.

## 1. What version 2 is

Every version 1 rule stays behind a switch. The defaults are now:

| Mechanism | Version 1 | Version 2 default (switch) | Status |
|---|---|---|---|
| Pricing (1) | Target-return anchor, band, utilisation-triggered war, floor at ucs (`"anchor"`) | No anchor, no trigger: follow the lowest price, undercut only with spare capacity and a cost edge, rise after excess demand, floor at own unit cost (`PRICING_RULE = "real_competition"`) | Committed. The group notebook's rule (`"leader_follow"`: undercut every period capacity is not short, floor at 1.2 × average uc, rise after a shortage, monopoly cap) is committed at `cc1dd0c` behind the switch; not the default |
| Demand (2) | Linear quasi-replicator on 1/p, χ = 1 | Unchanged | |
| Accounts (3) | Overdraft loans cover negative cash | Bankruptcy when cash runs out (`CASH_SHORTFALL = "bankruptcy"`); depreciation by use proposed (`DEPRECIATION = "use"`, default `"time"`) | Committed |
| Scrapping (4) | Age limit 10; 4 periods with price below ucs; plants of any size | No age limit (`PLANT_LIFE = None`); 2 periods with price below uc (`SCRAP_COST = "unit_cost"`, `OBSOLESCENCE_PERIODS = 2`); idle plants scrapped after 2 periods (`IDLE_SCRAPPING`); plants of 20 (`PLANT_SIZE`) | Committed |
| Investment (5) | Accelerator to last sales; cash, then debt up to 2 × sales; fixed menu | All retained earnings spent on whole plants, whatever the demand (`INVESTMENT_RULE = "retained_earnings"`); no borrowing (`BORROWING = False`); one Marx-biased design offered at each investment, half of them in the conflict zone (`TECH_DRAWS`, `TECH_CONFLICT = 0.5`, `TECH_STEP = 0.05`) | Committed |
| Entry and exit (6) | rbar = 0.16; entrants undercut the leader by 1 % | rbar = 0.05; entrants start at the lowest price and then price by the common rule; bankruptcy also on negative cash | Committed |

Not in `v2`: the collector and the share decompositions (branch
`feat-collector-and-metrics`, twelve commits since the fork at `49f7974`; `v2` has five
commits it lacks). A dry-run merge (`git merge-tree`) conflicts in four files:
`markets/entry_exit.py`, `model/collector.py`, `model/scheduler.py`, `tests/test_model.py`.
The collector predates every version 2 rule, so the merge is a reconciliation, not a
fast-forward (section 5, step 0). Without it the version 2 results cannot be split into the
price channel and the accumulation channel, which section 2.2 argues is the first thing to
report.

## 2. Findings

### 2.1 Neutrality holds

- `firm.type` is read in three places: the hurdle lookup (`scheduler.py:331`), the
  inheritance draw for entrants (`scheduler.py:541`) and the collector's grouping. No other
  branch on the label.
- Ties are shared pro rata everywhere (merit order, overflow, technique ties to the first
  listed, exit ties by net worth then a random draw).
- The label swap is tested under every switch, the leader-follow rule included.
- One caveat, not a breach: the single `random.Random` is consumed in firm order, so a
  Shaikh firm and its Okishio twin never see the same design. The swap keeps the order, so
  the test passes, but any result on technical change needs the neutral control of the
  critique (§6): two groups on the same rule under different labels, over the same seeds.
  Add it to the experiment scripts before reporting a Shaikh or Okishio advantage.

### 2.2 The contest version 2 sets up

This is the main point of the review. The agreed rules put both selection channels at full
strength at once, and move the price floor away from Shaikh's.

1. **The accumulation channel is the brief's trap, chosen knowingly.** The investment brief
   warns that "if firms invest all their cash, capacity grows with profits" and the firms
   with the higher profit rate at the going price grow faster. `INVESTMENT_RULE =
   "retained_earnings"` is that rule: capacity is bounded by idle scrapping, not by demand,
   and each type grows with its retained earnings. The choice is legitimate (it is Steindl's
   and Shaikh's accumulation out of profits), but the outcome then mixes two things: who
   wins customers through prices and who accumulates faster. Every result must be reported
   with the decomposition of the collector brief (§4.2 capacity share into net investment,
   entry and exit; §4.3 sales share into price-driven, entry-exit and rationing terms).
   Merge `feat-collector-and-metrics` into `v2` before producing results.
2. **The price channel is at full strength under the leader-follow rule and gated under the
   default.** Under `"real_competition"` a firm cuts only with a cost edge; under
   `"leader_follow"` every firm cuts whenever capacity is not short, so prices fall every
   period to the floors. These are the two ends of the first clause of the research question
   ("how often price wars occur"). Keep both, and name them as that treatment in the docs
   rather than as "default" and "alternative" (decision of 7 November: fixed version or
   treatment, settled by the sensitivity analysis).
3. **The floor has drifted up, away from Shaikh.** Version 1 stopped cuts at the operating
   cost ucs (Shaikh 2016, p. 316, Table 7.3 row 1); the version 2 default stops them at the
   firm's best unit cost uc = ucs + δκ; the leader-follow rule stops them at 1.2 × the
   capacity-weighted average uc of all the firm's plants, idle ones included. Two
   consequences under the leader-follow floor: (a) no plant sells below its unit cost unless
   it is more than 20 % dearer than the firm's average, so obsolescence scrapping ("price
   below uc for two periods") almost never fires and idle scrapping does all the work;
   (b) the margin p − uc never falls to zero, so the Okishio hurdle h never reaches 0 and the
   two rules never agree: price wars never close the conflict zone, which is the mechanism
   the second clause of the question relies on. Make the floor a switch on the leader-follow
   rule as well (`FLOOR_MARKUP = 0` gives uc; reuse `PRICE_FLOOR = "operating_cost"` for ucs),
   and run the three floors as a treatment.
4. **The finance treatment has one arm in the defaults.** `BORROWING = False` and
   `CASH_SHORTFALL = "bankruptcy"` mean no firm ever takes debt (0 bankruptcies over seeds
   1–20). The second clause of the question ("how investment is financed") needs the other
   arm: `BORROWING = True` with the accelerator, or with retained earnings plus a debt cap.
   The switches exist; the documentation should present them as the treatment.
5. **Entry churns at rbar = 0.05.** With θ = 5 the trigger fires almost every period: 67
   entries and 58 exits by share over 200 periods (seeds 1–20), 15 firms at the end, most of
   them entrants at 1 % of the market. ρ = 0.05 now equals rbar. Either lower θ (say 1), or
   raise rbar to 0.10, or keep the churn and report it as a feature of the open industry.
   Decide and record it.

### 2.3 Rule-level issues

1. **Leader-follow, shortage branch.** After excess demand every firm posts (1 + z) L, L the
   lowest price last period. A firm priced above (1 + z) L therefore lowers its price in a
   shortage (the test shows 110 → 103). Every shortage collapses the price distribution to
   one level 3 % above the leader. If this is the notebook's rule, keep it but say so; if not,
   post max{p_{t−1}, (1 + z) L}, or reuse the default rule's rise.
2. **Leader-follow floor over all plants.** The capacity-weighted average includes idle and
   old plants, so a firm that keeps old plants has a higher floor than a firm that scrapped
   them. Defensible, but it couples pricing to scrapping in a way the notebook did not have
   (one plant per firm). State it in `choices.md`.
3. **Technical change (`TECH_DRAWS`).** The current rule cannot answer the question it was
   built for, for six reasons, detailed in section 4.1: the zone is forced by a coin flip,
   no design is ever rejected by a Shaikh firm, there are no capital-saving designs, the
   draw depends on the firm's price, the firm that invests most gets the most draws, and
   designs are private to the adopter but public to entrants. The `choices.md` record already
   says that the Shaikh advantage at q = 0 "comes from prices moving, not from the draws".
4. **Replacement is largely redundant.** With whole plants bought from retained earnings and
   idle scrapping two periods later, each new plant pushes out the firm's oldest plant: the
   hurdle-based replacement (`REPLACEMENT = True`) rarely has anything left to do. Collect
   `industry.replacements` by type and report how often it fires; if it is near zero, say
   that the replacement channel of the scrapping brief is inactive in version 2.
5. **"Adopted" without a plant.** In `_technique_to_build` the design is logged as adopted
   and added to `known` even when the higher κ leaves the firm unable to afford one plant
   (units = 0 after the recomputation). Log "adopted" and "built" separately.
6. **Entrants know more than incumbents.** With `TECH_DRAWS` an entrant can build any
   technique in use; an incumbent knows only the menu and its own adoptions. Entry is thus
   the only diffusion channel. Either document it as a choice or add imitation (section 4.2).
7. **Dead code.** `equations/war_price.py` (`PRICE_WAR = "cost_gated"`) is imported nowhere;
   `choices.md` says the switch was removed. Delete the file. Add `.idea/` to `.gitignore`.
8. **Numbers disagree across documents.** `pricing.tex` says the lowest-cost firm leads in
   187 of 200 periods (version 1 plants and investment, seeds 1–10); the leader-follow row of
   `choices.md` says 58 under the version 2 defaults. Both are right for their
   configuration. Every number in the docs should carry its configuration.
9. **Depreciation by use** is coherent with idle scrapping (an idle plant does not depreciate
   and leaves a larger write-off) and leaves uc and every hurdle unchanged. No objection to
   making it the default once Vincent agrees; until then the docs should say it is proposed.

## 3. Documentation changes

The design reference and the report still describe version 1 in several places. Proposed
changes, file by file. Text in quotation blocks is the proposed wording. Under the decision
of 7 November the docs present the two pricing rules and the two technical-change rules as
treatment arms whose default is frozen until the sensitivity analysis, and every recorded
number names its configuration.

### 3.1 `docs/main.tex`

Title line: "An agent-based model, version 1" → "An agent-based model, version 2".

### 3.2 `docs/sections/overview.tex`

Replace the paragraph "Version 1." by:

> **Version 2.** Each mechanism keeps the starting rule of its brief behind a switch and
> runs by default on the rules agreed on 6 November 2026: plants of fixed size S = 20 with
> no maximum age, scrapped after two periods with the price below their unit cost or two
> periods idle; pricing without anchor or war trigger, where cuts come from cost edges;
> investment of all retained earnings in whole plants, with no borrowing, and one
> Marx-biased design offered at each investment; bankruptcy when cash runs out; entrants
> pricing by the common rule; rbar = 0.05. The pricing rule (cost-edge undercutting, or the
> group's leader-follow rule under which every firm cuts whenever capacity is not short) and
> the technical-change rule (designs drawn by category, or from an innovation set) are the
> model's two most sensitive parts: both are switches, their defaults are frozen, and a
> sensitivity analysis decides whether each becomes a fixed choice or a treatment. Every
> further choice is listed in section "Choices" and in `docs/design/choices.md`, which also
> records the version 1 values. The test industry is Shaikh's three plants (2016, Tables 7.10–7.11): [table
> unchanged]. Each plant is given to one Shaikh and one Okishio firm (six firms, identical
> within each pair) and split into plants of 20; demand is 680 = (340/383) × 766,
> δ = 0.10, rbar = 0.05 and u_max = 1.2.

Replace the paragraph "Baseline run." (it describes the anchor-rule war of t = 2–9 and the
D1/D2 anchor trap, which the defaults no longer produce) by:

> **Baseline run.** Figures 1–5 show the baseline (seed 42, 200 periods, version 2
> defaults). The D1 and D2 firms undercut C from t = 0 and the opening war takes prices from
> 100 to 73 by t = 20; afterwards prices follow unit costs down as designs are adopted
> (Shaikh firms' unit cost 46 at t = 199, price 49), with a cut in 126 of 200 periods and 50
> periods of excess demand after scrapping. With rbar = 0.05 the rate on new plants is above
> rbar almost every period: 43 firms enter and 42 leave, nearly all by falling below 1 % of
> the market. Okishio firms fall below 1 % of the market at t = 75 and entrants that switch
> rule bring them back to 7 % by t = 199; 7 firms remain. Over seeds 1–20 Shaikh firms win
> 16 runs. Whether they win through prices or through accumulation is what the collector's
> decomposition (branch `feat-collector-and-metrics`) will show; until then this is a
> baseline, not a result.

The figures in `outputs/` must be regenerated from the version 2 defaults before the report
is built (CI does it; a local `run.py` + `plot_outputs.py` before `latexmk`).

### 3.3 `docs/sections/schedule.tex`

Steps 5 and 6 of the list:

> 5. **Scrapping.** Hurdles are updated; plants retire by age, obsolescence or idleness
>    (the same for both types); replacement with h.
> 6. **Investment.** Retained earnings buy whole plants (desired capacity under the
>    accelerator); a new design may be offered; technique chosen with h; plants arrive next
>    period.

### 3.4 `docs/sections/pricing.tex`

- First paragraph: add one sentence after "technical change is what renews them":
  "The group's leader-follow rule, in which every firm cuts whenever capacity is not short,
  is the other end of the price-war treatment."
- Paragraph "What it needs from investment": it describes the accelerator baseline at
  rbar = 0.16, which is no longer the default. Replace by:

> **What moves the price in version 2.** Under the version 2 defaults the price does not get
> stuck: retained earnings keep buying plants, idle scrapping keeps capacity near demand,
> and each adopted design gives its owner a cost edge that starts a cut (a cut in 126 of
> 200 periods at seed 42). Shortages come from scrapping, not from under-investment. The
> scratch test with profit-sensitive investment (desired capacity x_{t−1}(1 + β(r_i − rbar)/rbar),
> `docs/design/choices.md`) remains the proposal for the accelerator arm of the finance
> treatment, where the price otherwise stays below the price of production.

- Every number carries its configuration: "187 of 200 (version 1 plants and accelerator,
  seeds 1–10); 58 under the version 2 defaults, 195 under the leader-follow rule".
- The leader-follow paragraph: add the floor (section 2.2, point 3) and the shortage branch
  (section 2.3, point 1) as open questions, in one sentence each.

### 3.5 `docs/sections/accounts.tex`

Add retained earnings to the state, after the cash equation:

> RE_{i,t} = RE_{i,t−1} + Π_{i,t} − Div_{i,t} − (spending on plants)_{i,t}, the funds the
> version 2 investment rule spends (section Investment); an entrant's first plant is paid by
> equity and does not enter RE.

Mention `unpaid_bills` as the rest-of-economy loss under bankruptcy, next to loan losses.

### 3.6 `docs/sections/scrapping.tex`

The "Version 1 rule" paragraph still says "Replacement is on in version 1 ... (cash only
with `BORROWING = False`, the default)": move the finance clause to the version 2 paragraph.
Add after the version 2 paragraph:

> With whole plants bought from retained earnings and scrapped when idle, replacement by the
> hurdle inequality rarely fires: each new plant already pushes out the oldest. The number
> of hurdle replacements per period is collected by type.

### 3.7 `docs/sections/investment.tex`

Add after "Version 2 rules (the defaults)":

> **The two channels.** The retained-earnings rule is the accumulation channel of the brief's
> trap, chosen deliberately: capacity grows with each type's profits, and the firms with
> the higher profit rate at the going price grow faster. The price channel runs alongside
> through market shares. The decomposition of each type's capacity share into net
> investment, entry and exit, and of its sales share into price-driven, entry-exit and
> rationing terms (collector brief, §4.2–4.3), is reported with every result.

In the technical-change paragraph, add the limits of the current rule (section 4.1) and
point to the proposal of section 4 as the version 2.1 rule.

### 3.8 `docs/sections/entry_exit.tex`

After "at most one firm enters a period": "With rbar = 0.05 and θ = 5 the trigger fires
almost every period (67 entries over 200 periods, seeds 1–20); most entrants leave again by
share."

### 3.9 `docs/sections/choices.tex`

Replace the bullet list (its first bullet, "all retire together at t = 9", and the debt-cap
bullet describe version 1):

> - **Plants of fixed size** S = 20, no maximum age. Initial plants are split into plants of
>   20; the version 1 single plants retiring together at t = 9 are gone.
> - **Scrapping** after two periods with the price below the plant's unit cost, or two
>   periods idle; the version 1 rule (age 10, four periods below ucs) stays behind switches.
> - **Investment of all retained earnings** in whole plants, no borrowing; the version 1
>   accelerator with debt up to twice sales revenue stays behind `INVESTMENT_RULE` and
>   `BORROWING`.
> - **Technical change on**: one Marx-biased design per investment, half in the conflict
>   zone; the innovation set (`TECH_CHANGE = "innovation_set"`, `docs/design/review-v2.md`,
>   section 4) is the second arm of the sensitivity analysis.
> - **Okishio hurdle floored at zero** in investment, replacement and entry.
> - **Bankruptcy when cash runs out**, instead of the version 1 overdraft.
> - **Non-renewal at firm level**; the entry trigger is the realised rate on recent plants;
>   rbar = 0.05; entrants price by the common rule.
> - **Overtime premium** of 10 %; a plant runs only if the price covers its operating cost;
>   ties shared pro rata.
> - **Open values:** c = 0.02, η = 0.5 (shortage response), ρ = 0.05, d = 0.5,
>   f_min = 0.01, θ = 5, k = 5, φ = 0.5, m = 0.02, χ = 1, logit η = 1, initial price 100,
>   initial cash and debt zero; leader-follow m = 0.20, z = 0.03, cap 3.

"Adding an alternative rule": "with the version 1 rule as default" → "with the current
default kept as default; changing a default is a group decision recorded in `choices.md`".

### 3.10 `docs/sections/notation.tex` and the briefs' notation table

Add rows: S (`PLANT_SIZE`, capacity of every plant); RE_i (`retained_earnings`); wear_v
(`wear`, output so far in periods of normal output); a, b (`draw_design`: proportional fall
in ucs and rise in κ of a design); q (`TECH_CONFLICT`); m, z (`FLOOR_MARKUP`,
`LEADER_RISE`). Note that m is also the mutation rate of the entry brief: rename the floor
markup μ_f in the text, or `FLOOR_MARKUP` stays and the text says "floor markup".

### 3.11 `docs/design/choices.md`

- Title: "Version 1: choices the brief leaves open" → "Choices the brief leaves open
  (version 2 defaults; version 1 values kept for the record)".
- Intro: add "Version 2 (6 November 2026) changes the defaults of pricing, accounts,
  scrapping, investment and entry; each version 1 rule stays behind a switch. **Default
  (version 2)** in the tables marks the current default; records of runs say which version
  and which pricing rule they used."
- Pricing table: add the floor and the shortage branch of the leader-follow rule as open
  rows (section 2.2 point 3, section 2.3 point 1). The row "War rule ... `PRICE_WAR =
  "cost_gated"` removed" should say the file `war_price.py` is deleted.
- Investment table: the technical-change row gets a sibling row for the innovation set of
  section 4 (status "Switch, in the sensitivity analysis (Ugo)"), and the current rule's
  limits in its "Alternatives" cell.
- Entry table: a row for the churn at rbar = 0.05 (θ, rbar, entrant size as the levers).
- Records: every record heading names the pricing rule and rbar it used.
- New section "Sensitivity analysis (planned)" with the factor table of section 5, step 4,
  to be filled with results as cells are run.
- A status line under the title: "Defaults frozen on 7 November 2026 pending the
  sensitivity analysis; pricing and technical change are treatment arms until then."

### 3.12 `docs/design/mechanism-briefs.md`

The briefs are the frozen specification exported from Claude Docs on 3 November; do not
edit their text. Add one section at the end, before "Sources":

> ## Version 2 amendments (6 November 2026)
>
> The group kept every starting rule behind a switch and changed the defaults as follows.
> Pricing: no anchor and no war trigger; a firm follows the lowest price and undercuts only
> with spare capacity and a cost edge; the floor is its own unit cost (the group notebook's
> leader-follow rule is the alternative). Accounts: bankruptcy when cash runs out, no
> overdraft. Scrapping: plants of S = 20, no maximum age, retirement after two periods with
> the price below unit cost or two periods idle. Investment: all retained earnings spent on
> whole plants, no borrowing; one Marx-biased design offered at each investment. Entry:
> rbar = 0.05; entrants price by the common rule. Order of events unchanged; step 4 now
> retires by age, obsolescence or idleness, step 5 buys from retained earnings. The test
> industry runs at rbar = 5 % (the briefs' 16 % is the version 1 value) with demand 680.
> Notation added: S, RE_i, wear_v, a, b, q, floor markup. Details: `choices.md`; review and
> technical-change proposal: `review-v2.md`.

### 3.13 `CLAUDE.md`, `.gitignore`

- Ownership table, Pricing row: add `leader_follow_price.py`. Delete `war_price.py`.
- "Adding an alternative rule", step 2: as in 3.9.
- `.gitignore`: add `.idea/`.

## 4. Technical change: an innovation set, Marx-biased by construction

Status after 7 November: to be implemented as a switch (`TECH_CHANGE`), default unchanged
(`"categories"`), so that the Marx-biased and neutral innovation sets are cells of the
sensitivity analysis. Nothing below changes a default.

### 4.1 Why the current rule cannot carry the contest

`equations/new_technique.py` draws, for a firm about to invest, one design relative to the
technique it would otherwise build: ucs falls by a share a ≤ 5 %, κ rises by a share b, and b
is placed by a coin flip (q = 0.5) either in the zone both rules adopt, 0 < b < b_O, or in the
conflict zone, b_O ≤ b < b_S, where b_O depends on the firm's own price. Six consequences:

1. **The conflict share is an input, not an outcome.** The research question asks how the
   contest depends on how often price wars occur; the mechanism behind it is that wars close
   the margin and so close the conflict zone. Fixing q by a coin flip removes that mechanism,
   except that the zone vanishes at zero margin.
2. **No design is ever rejected by a Shaikh firm.** Every draw lowers unit cost. The
   unit-cost rule adopts 100 % of designs, the profit-rate rule 1 − q. The innovation set has
   no bad designs, so technical change is a gift that Shaikh firms always take.
3. **No capital-saving designs,** so the second wedge of the critique (dearer, capital-saving
   techniques that only the profit-rate rule adopts, and that expose it in a war) does not
   exist, and realised Marx bias cannot be measured as an outcome: it is imposed.
4. **The draw depends on the firm's price.** Innovation possibilities should not know what
   price the firm posts; here b_O does.
5. **Draws come with investment.** A firm that invests more often is offered more designs,
   so a lead compounds by luck: the records show winner-take-all runs.
6. **Private knowledge, except for entrants.** Only the adopter knows its design; entrants
   can build anything in use; incumbents cannot imitate. Diffusion runs through entry alone.

### 4.2 The proposed rule (`TECH_CHANGE = "innovation_set"`; the current rule stays as `"categories"`)

**Draw.** A design n is drawn relative to a reference technique o as two proportional
changes, with nothing read from the firm but o:

    ucs_n = (1 − a) ucs_o,        a = u · TECH_STEP,          u ~ U(0, 1]
    κ_n   = (1 + b) κ_o,          b = k · a,                  k = TECH_BIAS · exp(TECH_BIAS_SPREAD · z),  z ~ N(0, 1)

Every design is Marx-biased in Shaikh's sense: lower operating cost (labour-saving), more
capital per unit of output (capital-using). k is the capital per unit given up per unit of
operating cost saved (the critique's k = −χ/γ in these units); it is log-normal around the
median `TECH_BIAS` = m with spread `TECH_BIAS_SPREAD` = σ. m is the treatment: how strongly
biased the innovation set is.

**Adoption.** Unchanged: firm i adopts n against o if
ucs_n + (δ + h_i) κ_n < ucs_o + (δ + h_i) κ_o, with h_i from `equations/hurdle.py`. In terms
of k:

    unit-cost rule (h = 0) adopts if      k < k_S     = ucs_o / (δ κ_o)
    profit-rate rule at price p adopts if  k < k_O(p)  = ucs_o / (δ κ_o + max{0, p − uc_o})

Three zones are now outcomes of the draw and of the price: both adopt (k < k_O), conflict
(k_O ≤ k < k_S: only the unit-cost rule adopts), both reject (k ≥ k_S). The conflict zone
closes as the margin p − uc_o closes, so a price war makes the two rules agree and a recovery
reopens their disagreement. That is the mechanism the research question is about.

**Zone shares on the test industry** (reference C, δ = 0.10, σ = 0.8; 50 000 draws each):

| Median k | p = 100: both / conflict / reject | p = 90 | p = 80 | p = 75 (= uc) |
|---|---|---|---|---|
| 0.53 (PWT median, 1960–2019) | 0.94 / 0.06 / 0.00 | 0.98 / 0.02 / 0.00 | 0.99 / 0.00 / 0.00 | 1.00 / 0 / 0 |
| 1.5 | 0.59 / 0.34 / 0.08 | 0.74 / 0.18 / 0.08 | 0.90 / 0.03 / 0.08 | 0.92 / 0 / 0.08 |
| 3.0 | 0.26 / 0.45 / 0.29 | 0.41 / 0.30 / 0.29 | 0.65 / 0.06 / 0.29 | 0.71 / 0 / 0.29 |

For C at p = 100, k_O = 1.80 and k_S = 4.67; for D2, 1.45 and 3.75. Shaikh's own menu in
these units: D1 against C has k = 0.91 (both adopt at 100), D2 against C has k = 1.89
(conflict at 100, both adopt below 98.2), D2 against D1 has k = 2.64 (conflict). At the
data's median bias the two rules agree on 94 % of draws at normal prices and on all of them in
a war: a result in itself (Michl 2023: most Marx-biased change passes both tests). The
contest needs m between 1.5 and 3, and the sweep over m is the headline figure of the critique
(§6) with the conflict share now measured, not set.

**Reference technique** (`TECH_REFERENCE`): `"own"` (as now: the firm's best known technique
under its hurdle, so each type compounds its own path, Shaikh's eq. 7.13 path of ucs falling
and κ rising geometrically) or `"frontier"` (the lowest-uc technique in operation in the
industry, so both types draw from the same point and the contest is only about the choice).
Default `"own"`; run both.

**Timing** (`TECH_DRAW_TIMING`): `"investment"` (as now) or `"period"`: each period each firm
is offered a design with probability `TECH_DRAW_RATE` = λ (say 0.2), whether or not it
invests; an adopted design joins `known` and is built when the firm next invests. Default
`"period"`: it equalises luck across types and separates "offered" from "built".

**Diffusion** (`TECH_DIFFUSION`): `"private"` (as now: the adopter, and entrants) or
`"public"`: a technique becomes known to every firm `IMITATION_LAG` periods (say 2) after
its first plant produces (plants are observable; Salter's vintages are public history).
Default `"public"`: an Okishio firm is then offered the conflict designs Shaikh firms built
and refuses them at its price while the margin lasts, so the contest is between choices,
not between private draws. `"private"` measures the value of secrecy as a treatment.

**Neutral innovation set** (`TECH_SET`): `"marx"` (above) or `"neutral"`: the direction is
uniform on the circle in the plane (Δucs/ucs, Δκ/κ) and the size is u · `TECH_STEP`. Most of
the circle is rejected by both rules, capital-saving designs appear, and so does the second
wedge (dearer and capital-saving: only the profit-rate rule adopts). Realised Marx bias is
then an outcome: the capacity-weighted ucs and κ of each type give γ and χ per period, and the
critique's labels ("Marx-biased change must be an outcome, draws filtered by a rule") are
met. This is the Shaikh (2016, figs 7.23–7.24) and Park (2001) comparison of innovation
sets, and the homogeneous-population validation runs.

**Not proposed for version 2:** Shaikh's robustness margin (adopt only if uc falls by more
than a threshold) would give the unit-cost rule a second parameter; leave it for the
"evolving h" question of the critique (§8, question 1).

### 4.3 Neutrality check

The draw reads the reference technique and nothing else (under `"frontier"`, not even
that). Both rules see the same (a, k). The type enters only through h in the adoption
inequality, as everywhere else. Diffusion is by plant, not by type. The label swap holds by
construction; the neutral control (two groups on the same rule) must be run, since each
twin still sees different draws from the shared generator.

### 4.4 Tests (`tests/test_investment.py`, new class)

1. Every `"marx"` design has lower ucs and higher κ than its reference; `"neutral"`
   designs cover all four quadrants.
2. On 10 000 random draws the zone computed from (k_O, k_S) matches the direct comparison of
   unit costs and of profit rates at p (the critique's test 3).
3. At p = uc_o both rules adopt or reject every draw together.
4. With median k far below k_O(p) the conflict share is near zero; it rises with m; the
   both-reject share rises with m and does not depend on p.
5. For k in (k_O(p), k_S) a Shaikh firm adopts and an Okishio firm at price p refuses: the
   same design, two choices.
6. Public diffusion: a technique built at t is in every firm's `known` at t + L + 1 and in no
   other firm's before.
7. `"period"` timing: a firm that does not invest can still adopt, and builds the design at
   its next investment.
8. Label swap under each switch combination; add them to `test_switches_run`.

### 4.5 Collect

Per draw: t, firm, zone at the firm's price, zone at the leader's price, adopted, built.
Per period and type: share of draws in each zone, realised γ and χ (capacity-weighted ucs
and κ), number of techniques known, number of techniques in use. Per technique: period of
first plant, period at which it reaches half of industry capacity (the diffusion lag).

### 4.6 Implementation (Ugo, investment)

- `equations/innovation_set.py`: `draw_marx(ucs_o, kappa_o, u, z, step, bias, spread)`,
  `draw_neutral(ucs_o, kappa_o, u, theta, step)`, `adoption_zone(ucs_o, kappa_o, delta,
  price, a, b)` returning "both", "unit_cost", "profit_rate" or "none". Pure functions.
- `model/scheduler.py`: `_technique_to_build` branches on `TECH_CHANGE`; a `offer_designs`
  step at the start of `invest` under `"period"` timing; a `diffuse_techniques` call in
  `start_period` under `"public"` diffusion (plants with vintage ≤ t − L add their technique
  to every firm's `known`).
- `parameters.py`: `TECH_CHANGE = "categories"` (until the group switches), `TECH_BIAS = 1.5`,
  `TECH_BIAS_SPREAD = 0.8`, `TECH_SET = "marx"`, `TECH_REFERENCE = "own"`,
  `TECH_DRAW_TIMING = "period"`, `TECH_DRAW_RATE = 0.2`, `TECH_DIFFUSION = "public"`,
  `IMITATION_LAG = 2`.
- `choices.md` rows and the investment section of the report. About 150 lines plus tests.

## 5. Decisions and plan (7 November 2026)

### 5.1 Decisions recorded

- Pricing (`PRICING_RULE`) and technical change (`TECH_DRAWS`, and the innovation set to
  come) are the two sensitive parts of the model. No default changes now. Each becomes a
  fixed choice or a treatment once a first full sensitivity analysis has been run.
- The sensitivity analysis runs after the collector branch is merged, since it needs the
  decompositions, the event log and the neutral-control comparison that branch provides.
- The other findings of section 2 become either small neutral fixes (step 1) or factors of
  the sensitivity analysis (step 4): the floor, the shortage branch, the finance arm, the
  entry churn. None is decided by hand.

### 5.2 Plan

Calendar: simulated seminar on 20 November, report and presentation on 1 December. Steps 0
to 3 should land by 13 November, step 4 by 18 November.

**Step 0. Merge `feat-collector-and-metrics` into `v2`** (Ugo, who signs off the collector;
half a day to a day). **Done on 7 November on branch `v2-collector`**: the reconciliation
is recorded in the collector table of `choices.md`; 197 tests pass; every macro column
shared with `v2` is identical over seeds 42, 1 and 7; `Industry.run()` takes 0.11 s on the
version 2 defaults, `run.py` 0.5 s and `debug.report` 15 s. The branch awaits review and
merge into `v2`.

- Conflicts: `markets/entry_exit.py`, `model/collector.py`, `model/scheduler.py`,
  `tests/test_model.py`. Keep the version 2 logic and the collector's instrumentation; the
  collector never decides.
- The collector predates every version 2 rule. Reconcile: retirement cause `"idle"` in the
  plants table and the event log; the `"bankruptcy"` exit on negative cash and the
  `unpaid_bills` flow in the flow matrix and the stock-flow residuals; `draw_log` (design
  offered, zone, adopted, built) as events; `retained_earnings` and `wear` as firm and plant
  columns; `at_war` under the leader-follow rule; `industry.replacements` by type;
  `requirements.txt` (check what was added and why).
- Done when: the union of both test suites passes; the label swap holds under every switch
  with the new tables (`compare_runs.py --swap-labels`); `run.py` and `python -m
  debug.report outputs` run on the version 2 defaults; the wall time of `run.py` is
  recorded (it sizes step 4); `docs/design/collector.md` is regenerated from the schema.

**Step 1. Small fixes, trajectory-neutral unless stated** (by file owner; two hours in all).
**Done on 7 November on `v2-collector`**: `war_price.py` deleted; adopted and built logged
apart (design, adopt and order events, from the merge); `LEADER_FOLLOW_FLOOR` and
`SHORTAGE_RULE` as switches with the notebook's values as defaults, tested and in
`test_switches_run`; hurdle replacements by group (`n_replace` in `groups`);
`experiments/neutral_control.py` with its smoke test. First result (seeds 1–20, version 2
defaults): the mixed population's 16 of 20 is not beyond the neutral controls' intervals
(12 and 9 of 20); recorded in `choices.md`.

| Fix | File | Owner | Effect on trajectories |
|---|---|---|---|
| Delete `equations/war_price.py`; add `.idea/` to `.gitignore` | shared | Ugo | none |
| Log "adopted" and "built" separately in `_technique_to_build` | `model/scheduler.py` (step 5) | Ugo | none (log only) |
| Leader-follow floor behind its own switch, `LEADER_FOLLOW_FLOOR = "markup"` (1.2 × average uc, the notebook's, stays the rule's default) / `"unit_cost"` / `"operating_cost"` (a separate switch, so that `PRICE_FLOOR`'s default for the other rule is untouched) | `_leader_follow_prices` | Jake | none at defaults |
| Leader-follow shortage branch behind a switch: `SHORTAGE_RULE = "leader"` ((1 + z) L for every firm, the notebook's) / `"no_cut"` (max{p_{t−1}, (1 + z) L}) | same files | Jake | none at defaults |
| Neutral-control script: two groups on the same hurdle rule under different labels over N seeds, compared with `compare_runs.py`; its result reported next to every mixed-population result | `experiments/neutral_control.py` (new folder) | Ugo | none |
| Tests for each switch, added to `test_switches_run`; `choices.md` rows | `tests/`, `docs/design/choices.md` | each owner | none |

Not fixed by hand: the entry churn (rbar, θ), the finance arm (`INVESTMENT_RULE`,
`BORROWING`) and the replacement channel. They enter step 4 as factors or outputs.

**Step 2. Documentation** (section 3; each section's owner for their `.tex`, Ugo for the
overview, the choices, the briefs' amendment and `CLAUDE.md`; two to three hours). **Done
on 7 November (commit e666066 on `v2-collector`)**: every item of section 3 applied; the
report builds without warnings; the owners review their sections in the pull request.

- Everything in section 3, with the wording of the decision: frozen defaults, two treatment
  arms for pricing and two for technical change, every number with its configuration.
- The report's baseline paragraph and figures are regenerated after step 0 and again after
  the fixed version is chosen (step 5).
- `choices.md` gets the status line and the "Sensitivity analysis (planned)" section with the
  factor table below, to be filled as cells are run.
- `CLAUDE.md`: "Adding an alternative rule" says that a default changes only by a group
  decision recorded in `choices.md`; ownership table updated (`leader_follow_price.py`;
  `war_price.py` gone). Production and accounts, entry and exit still need an owner.

**Step 3. Innovation set as a switch** (section 4; Ugo; one day).

- `TECH_CHANGE = "categories"` stays the default; `"innovation_set"` adds `TECH_SET`
  (`"marx"` / `"neutral"`), `TECH_BIAS`, `TECH_BIAS_SPREAD`, `TECH_REFERENCE`,
  `TECH_DRAW_TIMING`, `TECH_DRAW_RATE`, `TECH_DIFFUSION`, `IMITATION_LAG`, with the defaults
  of section 4.6 applying only when the switch is on.
- Tests of section 4.4, the collectors of section 4.5 (they need step 0), label swap under
  each combination, rows in `choices.md`, a paragraph in the investment section.
- Must land before step 4 so that the Marx-biased and neutral sets are cells of the
  analysis.

**Step 4. First full sensitivity analysis** (after steps 0 to 3; Ugo with each owner reading
their mechanism's cells; computing time set by the wall time measured in step 0).

Design: one factor at a time around the version 2 defaults first (about 20 cells, 50 seeds
each, enough to detect a 20-point gap in the share of seeds won, critique §6), then a
factorial over the factors that moved the outcome, 200 seeds for the cells that decide the
fixed version. Seeds fixed across cells so that treatments face the same draws. Every cell
runs its neutral control.

| Factor | Levels | Mechanism |
|---|---|---|
| `PRICING_RULE` | `real_competition`, `leader_follow` | Pricing |
| Floor (`PRICE_FLOOR`) | `operating_cost` (ucs), `unit_cost`, `markup` (leader-follow only) | Pricing |
| `SHORTAGE_RULE` (leader-follow) | `leader`, `no_cut` | Pricing |
| `CHI` (selection intensity) | 0.5, 1, 2 | Demand |
| Technical change | `categories` with q ∈ {0, 0.5}; `innovation_set` marx with m ∈ {0.5, 1.5, 3}; `innovation_set` neutral | Investment |
| `TECH_DIFFUSION` | `private`, `public` | Investment |
| `TECH_DRAW_TIMING` | `investment`, `period` | Investment |
| Finance | `retained_earnings` + `BORROWING = False`; `accelerator` + `BORROWING = True` | Investment |
| `RBAR`, `ENTRY_SPEED` | (0.05, 5), (0.05, 1), (0.16, 5) | Entry |
| `DEPRECIATION` | `time`, `use` | Accounts |

Outputs per cell, from the collector: share of seeds in which Shaikh firms hold more than
half the capacity at t = 199, with a 95 % interval; final capacity and sales shares; the
decomposition of each type's share change into price-driven, accumulation, entry and exit
terms (collector brief §4.2–4.3); share of draws in each adoption zone and the realised γ
and χ by type; periods with a cut, mean price and profit rates over t ≥ 50; entries, exits
and firms at the end; hurdle replacements by type; and the neutral control's share of seeds
won.

Decision rule at the end: a factor whose levels do not change the share of seeds won beyond
the neutral control's interval is fixed at its default; a factor that does becomes a
treatment of the experiments, or is fixed at the level the group argues for from theory,
with the sensitivity recorded in `choices.md`.

**Step 5. Fixed version and report** (after step 4; everyone; before 1 December).

- Defaults set from the decision rule; `choices.md` records each with its cell results;
  `parameters.py` follows.
- Baseline paragraph and figures of the report regenerated; the experiments (mixed
  population, invasion, decomposition) run on the fixed version with the chosen treatments.
