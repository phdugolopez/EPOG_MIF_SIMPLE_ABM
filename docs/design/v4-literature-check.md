# ABM version 4: check of the proposal against the literature

Check of 10 November 2026 on `v4-final-model.md`. Each mechanism and each variant is compared
with the texts in Zotero (library `perso` unless noted), read in the PDFs on that day. Page
numbers are those of the printed texts. Nothing in the model or the proposal was changed.

Verdicts: **compatible** (the rule is in the source), **simplification** (a known rule, cut
down), **departure** (the source says something else), **no source** (a device of the model).

## At a glance

- **The one rule that differs is sound.** The hurdle form is exactly the profit-rate
  criterion, and h = 0 is Shaikh's unit-cost criterion. λ = 0 and λ = 1 are the two readings
  found in the debate.
- **The default general rate takes the model out of Shaikh's example.** His tables assume a
  normal rate of 16 %. At r̄ = 0.05 the two rules disagree on the starting menu only because
  the starting price (100) is 18 % above the price of production (prix de production).
- **Cost-edge cutting is the rule closest to Shaikh's price leadership.** The model's
  "leader-follow" is not his: every firm undercuts, whatever its cost.
- **Normal-price cutting is defensible.** It joins the two price movements Shaikh
  distinguishes, and its threshold is Andrews's normal price. The variant on the *regulating*
  price of production is closer to the text than the default on the firm's *own*.
- **Three lines of E0 do not measure what real competition (concurrence réelle) predicts**:
  the industry profit rate, the leader line under leader-follow, and E0 without technical
  change.
- **H6 not met is a result against Shaikh, not a defect.** It is what Okishio, Roemer and
  Duménil and Lévy would expect.
- **Two devices have no source**: the conditional release of the depreciation reserve and
  scrapping after two idle periods. One vocabulary clash: Shaikh's "operating cost" is the
  model's *unit cost*.

## Sources read, and what could not be read

| Text | Zotero | Read |
| --- | --- | --- |
| Shaikh 2016, *Capitalism*, ch. 4 and 7 | BMKVYW2U | pp. 159, 261–271, 274–275, 282, 290–291, 314–324 |
| Shaikh 1978, *CJE* 2(2); Shaikh 1980, *CJE* 4 | J9AEUKMD; EECWZJXJ | pp. 241–245; pp. 75–76 |
| Roemer 1979, *CJE* 3 | TX2DFFI7 | pp. 379–383 |
| Duménil & Lévy 2005, *Research in Political Economy* 22 | LWGHAJ9B | pp. 209–213 |
| Park 2005, same volume | 2CCFW5GB | pp. 206–207 (in the PDF of LWGHAJ9B) |
| Michl 2023, *New School Economic Review* 12 | FX3M6W5I | pp. 36–37, 46–47 |
| Duménil & Lévy 1995, *Metroeconomica* 46(3) | 48U7VRQQ | pp. 213–218 |
| Silverberg, Dosi & Orsenigo 1988, *EJ* 98 | EBVLD2YA | pp. 1035–1038 |
| Salter 1966 | FCUBTW7P | pp. 56–59 |
| Dosi & Roventini 2025 | TUR32YLD | sections on timeline, machines, pricing, entry (eqs 6, 10, 11) |
| Nelson & Winter 1982 | VATF967M (hivemind) | ch. 9 and 12, investment and entry passages |
| Hall & Hitch 1939, *OEP* | 632JYJAP | pp. 21–23 |
| Cogliano et al. 2022 (ABM chapter); Basu 2026, *RRPE* | DRGHDBSG; EQUSWFVB | introductions only |

- **No PDF**: Okishio 1961 (3ZDE32J4), Okishio 2001 (BJE3KHR9), Park 2001 (9CUFY49Q). Park 2001
  is known here only through Shaikh 2016, p. 322.
- **PDF without usable text**: Baldani & Michl 2000 (3R3LBMWT), Foley, Michl & Tavani 2019
  (V98SW3XI), Steindl 1952 (LX36ID6E). Not used.
- **Not in the library**: Nakatani 1980, Botwinick 1993, Metcalfe 1998. Nakatani's comment
  bears directly on H1 and H6 and was not read: to add in perso.

## The one rule that differs

| Element | Verdict | Source and remark |
| --- | --- | --- |
| Unit-cost rule, h = 0 | Compatible | Shaikh 2016, pp. 261, 314–317: the lowest unit cost, depreciation included, is the criterion under price-cutting. Michl 2023, p. 46, restates it as a profit-margin criterion |
| Profit-rate rule, hurdle h | Compatible | Minimising ucs + (δ + h)κ with h the best rate at p^e picks the technique with the highest rate at p^e. With h = r̄ it is Sraffa's rule, the lowest price of production (Shaikh 1978, p. 244 n.; 2016, p. 320 n. 36) |
| λ = 0, the firm's own price | Compatible | Duménil & Lévy 2005, p. 209: profitability at going prices and wages, a criterion they give to Marx and the classics, not to Okishio. Shaikh 2016, pp. 261, 321: choices are made at market prices |
| λ = 1, the price of production | Compatible | The setting of Okishio's theorem (Shaikh 1978, pp. 241–242; Roemer 1979, p. 382; Duménil & Lévy 2005, p. 209) |
| Label "Okishio" for the rule | To reword | Duménil & Lévy 2005, p. 209, object to "Okishio's criterion": the theorem is his, the criterion is older. Park 2005, n. 7, uses the name as a convention. "Profit-rate rule" is the safe name |
| p^e the same for every technique | Simplification | Shaikh 2016, pp. 263, 314–316: the cost leader expects to cut the price, so it does not judge at a given price. The unit-cost rule stands for that expectation; no firm forms it |
| "Robust" cost advantage | Not in the model | Shaikh 2016, pp. 261, 321: a method is adopted only if its advantage survives normal fluctuations. The model adopts on any advantage |
| Initial techniques C, D1, D2 | Compatible | Shaikh 2016, Tables 7.10–7.11, p. 315. ucs + κ/10 gives 78, 76 and 75, his unit costs; his depreciation rate is 1/10 (p. 319 n. 35) |

**The general rate.** Shaikh's example has a normal rate of 16 %: 100 is the price of
production of C. Checked by computation on the three techniques:

| | r̄ = 0.05 | r̄ = 0.16 |
| --- | --- | --- |
| Price of production of C, D1, D2 | 84.9, 83.1, 82.9 | 100.0, 98.8, 100.3 |
| Profit-rate rule at p = 100 (λ = 0) | D1 (h = 0.169) | D1 (h = 0.169) |
| Profit-rate rule at the price of production of D2 (λ = 1) | D2 (h = 0.05) | D1 (h = 0.171) |
| Unit-cost rule | D2 | D2 |

- **The rules part on D2 only if the hurdle exceeds 0.147.** At r̄ = 0.05 that needs a price
  well above the price of production. At λ = 1 the two rules choose the same technique: D2
  has the lowest unit cost and the lowest price of production.
- **So H5 at r̄ = 0.05 is partly built in.** The fall of the advantage at λ = 1 follows from
  the low general rate on this menu. In Shaikh (2016, pp. 320–321) the conflict exists at
  prices of production, with a rate of 16 %.
- **On drawn designs the rules still differ at any h > 0.** A design drawn from C is kept if
  k < 4.67 under the unit-cost rule (92 % of draws at β = 1.5), k < 3.12 at h = 0.05 (82 %),
  k < 2.34 at h = 0.10 (71 %), k < 1.80 at h = 0.16 (59 %).
- **r̄ = 0.16 is the case the literature describes.** There the unit-cost label wins only
  under cost-edge cutting. The report should give r̄ = 0.16 the same weight as the default.

## Price rules

| Rule or variant | Verdict | Source and remark |
| --- | --- | --- |
| Cost-edge cutting | Compatible; the closest to Shaikh | Shaikh 2016, pp. 263, 268, 271 (Table 7.3, lines 1–5), 274 n. 9: the lowest-cost capital cuts, the others keep their price in line. Its followers lag by one period, which is Table 7.6 (p. 291), partial price cuts |
| Why it fails E0 | Explained by the text | In Shaikh the price comes down to the price of production through entry and supply outrunning demand (pp. 264, 282), a different movement from price-cutting (p. 316). Cost-edge cutting has only the second |
| Normal-price cutting (default) | Compatible, as a reading | It joins the two movements of p. 316: above the price of production, supply and demand; below, the cost leader alone. The threshold is the normal price of Andrews and Harrod, normal cost plus normal profit (pp. 274–275, 282). Cuts below it by a cost leader are expected (p. 314) |
| Threshold on the firm's own price of production | Departure, small | Shaikh 2016, pp. 268, 271: only the regulating capital earns the normal rate; the others' profits are residuals. The centre is the regulating price of production |
| Variant: threshold on the regulating price of production | Compatible; closer than the default | Same pages. 0.63 against 0.67, E0 in 43 and 8 seeds against 43 and 12 |
| Systematic cutting | Departure as a normal regime | Shaikh 2016, p. 274 n. 9, after Andrews and Brunner: cutting by any firm with idle capacity is the price-cutting of a crisis, distinct from normal price-cutting. Useful as a bound |
| Leader-follow | Departure in the name and the rule | In Shaikh (pp. 268, 271) and in Hall & Hitch 1939 (pp. 22–23) followers match a cut; they do not undercut the leader. In the model every firm posts 2 % below the lowest price each period, whatever its cost. A better name: "universal undercutting" |
| Rise after a shortage (0.5 × excess demand; +3 %) | Compatible, generic | Prices answer to supply and demand around the centre (Shaikh 2016, pp. 264, 316). Hall & Hitch 1939 report prices that do not follow demand in the short run |
| Variant: entrants post 2 % below the lowest price | Compatible | Geroski, in Shaikh 2016, p. 282: entrants tend to undercut incumbents. The default (entrant at the lowest price) is the simplification |
| Variant: shortage step 0.25 | No source | A speed of adjustment |
| Cap of a firm alone (3 × floor) | No source | A guard |
| Floor: unit cost (default) | Compatible | Shaikh 2016, pp. 268, 271, 274: cuts are limited by costs, depreciation included |
| Floor: operating cost (option) | Compatible as distress pricing | Below unit cost a firm still covers prime cost: distress sales in Andrews (Shaikh 2016, p. 268), Salter's abandonment margin (1966, pp. 56–57) |

- **Vocabulary.** Shaikh's "operating cost" includes depreciation (Table 7.1, p. 263; Table
  7.15, p. 319); his prime cost is ucs (p. 316). The model's "operating cost" is his prime
  cost. The report should say so once, or Table 7.3, line 1, will be read against the model.
- **The trade-off of the proposal is in the text.** Shaikh separates price-cutting for market
  share from price-setting on supply and demand (p. 316). The first gives the headline, the
  second E0. He does not say how the two combine in one rule; the default is one answer.

## Overtime, capacity and investment

| Mechanism | Verdict | Source and remark |
| --- | --- | --- |
| Output above normal capacity, u_max = 1.2 | Compatible | Shaikh 2016, p. 159: economic capacity lies below engineering capacity; the gap is a desired reserve for fluctuations of demand. Andrews allows overtime beyond normal output (p. 274 n. 10). The value 1.2 has no source |
| No overtime premium | Simplification, with a cost | Shaikh 2016, pp. 159, 262: normal capacity is the lowest point of average cost. With flat prime cost and depreciation by time, unit cost falls above normal capacity, so normal capacity is no longer that point. Andrews's flat prime cost supports it (p. 274) |
| Accelerator without a target | Compatible | Normal capacity is the target; persistent use of the reserve is the signal to invest (Shaikh 2016, p. 159). A target below 1 belongs to the post-Keynesian accelerator of the earlier versions |
| Retained earnings (default) | Compatible | Nelson & Winter 1982, ch. 12: gross investment out of gross profit after required dividends. Duménil & Lévy 1995, p. 217: profitability gives the cash flow that finances growth |
| No debt, payout 0.5 | Simplification | Duménil & Lévy 1995, p. 217, also count on outside finance won by a profit record |
| A working plant is never replaced | Departure | Salter 1966, pp. 56–59, and the payback rules of Silverberg et al. 1988 (p. 1038) and Dosi & Roventini 2025 (eq. 10) replace a plant when a new one is cheap enough. Diffusion is slower in the model |
| Depreciation reserve released if r_new ≥ r̄ | No source; in the spirit of the text | Shaikh 2016, p. 264: investment speeds up or slows down with the rate of return on new investment, not the average rate. The reserve condition is a device for capital leaving. Since it makes the cycle and sets the profit rate, the report must present it as a choice of the group |
| Reserve always or never released | No source | Sensitivity levels |

## Demand, scrapping, technical change, entry

| Mechanism | Verdict | Source and remark |
| --- | --- | --- |
| Replicator on E = 1/p | Compatible | Silverberg et al. 1988, p. 1037, eqs 1–2; Dosi & Roventini 2025, eq. for market shares. Both add delivery delay or unfilled demand to competitiveness; the model re-allocates unserved demand once instead |
| Exogenous demand growing at g | Compatible | Silverberg et al. 1988, p. 1036 |
| Scrapping when the price is below operating cost | Compatible | Salter 1966, pp. 56–57: a plant is abandoned when it yields no surplus over operating costs |
| Scrapping at age T = 10 | Compatible | Dosi & Roventini 2025: machines older than η are scrapped. Shaikh's rate of depreciation is 1/10 |
| Scrapping after 2 idle periods | No source | A device |
| Marx-biased draws (β, σ) | Compatible with Shaikh; departure from Duménil & Lévy | Shaikh 2016, p. 324, Fig. 7.24: lower operating cost bought with more capital, a skewed innovation set. But every draw of the model is capital-using. In Duménil & Lévy 1995, pp. 214–218, the set is neutral and the bias comes from selection and a rising wage |
| Neutral set (option) | Compatible | Duménil & Lévy 1995, p. 217; Shaikh 2016, Fig. 7.23, p. 323 |
| β = 0 gives drift | Compatible | Without more fixed capital the two criteria coincide (Shaikh 1978, pp. 242–246; 2016, p. 320 n. 36) |
| A design is kept if the firm's own rule prefers it | Compatible | Shaikh 2016, p. 323; Duménil & Lévy 1995, p. 218; Roemer 1979, p. 382 |
| Entry probability rising with r_new − r̄ | Compatible | Shaikh 2016, p. 264: the rate of return on new investment governs the mobility of capital. Nelson & Winter 1982, ch. 12: entry when the industry is profitable |
| Entrant at half the mean size, on the best public technique | Compatible | Dosi & Roventini 2025: entrants are smaller than incumbents and buy recent vintages. Shaikh 2016, p. 261: new investment goes to best practice |
| Label copied by market share, flipped with μ | No source | A device of imitation |
| Exit below 1 % share | Compatible | Dosi & Roventini 2025: firms with a near-zero share leave. No bankruptcy, since there is no debt |
| One industry, r̄ and the wage given | Compatible | The setting of Shaikh 2016, pp. 314–318. Okishio's theorem needs the whole economy and stays untested, as the proposal says |

## E0, the winner and the hypotheses

| Element | Verdict | Source and remark |
| --- | --- | --- |
| The lowest-cost firm leads the price | Compatible | Table 7.3, line 3. Under leader-follow the line is true by construction: all prices are equal |
| Price around the price of production; crossings | Compatible | Shaikh 2016, pp. 268–269: gravitation is read on crossings. A band of 0.9–1.2 accepts a mean of 1.17, which is a lasting excess profit, not a centre |
| Industry profit rate within 0.03–0.10 | Departure | Shaikh 2016, pp. 264, 268–271: the rate on the regulating conditions, on new investment, is equalised; average rates are not. The line should be on r_new: its mean and its crossings of r̄ |
| Profit rates stay unequal | Compatible | Table 7.3, lines 8–9 |
| Capacity follows demand | Compatible | Normal utilisation on average (Shaikh 2016, p. 282) |
| Demand lost at most 10 % | No source | Set after the runs, as the proposal says |
| E0 without technical change | Departure | Shaikh 2016, p. 262: a spread of costs from ongoing technical change is part of competition within an industry. Without draws all firms share one technique: E0 tests gravitation, not leaders and followers. A second E0 with draws in single-rule populations would test both |
| Winner by capacity share against two controls | Compatible | Alchian 1950: survival is read on results, and luck must be told from selection |
| H1, H4 | Compatible | 0.92, 0.67, 0.50 as cutting spreads: Shaikh's advantage of the cost leader needs the leader to cut alone (pp. 263, 268) |
| H1′ | Compatible with Duménil & Lévy 2005 and Roemer 1979 | The profit-rate rule is not beaten under leader-follow; under price-cutting it is, as Shaikh holds |
| H2 | Compatible | Shaikh 2016, pp. 322–324; Michl 2023, p. 47: the conflict of the criteria grows with the capital-using bias |
| H3 | Compatible | Nelson & Winter 1982; Duménil & Lévy 1995, p. 217: profitability selects through growth |
| H5 | Compatible; see the general rate | Shaikh 1978, pp. 241–242 |
| H6 not met | Against Shaikh, with the critics | Table 7.3, line 5: the lowest cost has the highest sustainable rate under price-cutting. In the runs the profit-rate label earns more (0.066 against 0.062) and still loses capacity: selection through sales, not profitability. Michl 2023, p. 46, points to the prisoner's dilemma of Baldani & Michl 2000 as the bridge. Nakatani 1980 is the text to read |

## What this changes in the proposal

| Point | Proposed change |
| --- | --- |
| "Leader-follow" | Rename it; say that cost-edge cutting is Shaikh's price leadership with a lag |
| Default threshold | Consider the regulating price of production: closer to the text, at 0.63 against 0.67 |
| E0, profit-rate line | Read it on r_new, not on the industry rate |
| E0 without draws | Add single-rule runs with draws, or say that E0 tests gravitation only |
| r̄ | Present r̄ = 0.16 as Shaikh's case and r̄ = 0.05 as the model's; state the hurdle of 0.147 |
| H5 | Say that at r̄ = 0.05 the rules agree on the starting menu at λ = 1 |
| H6 | Report it as a result against Table 7.3, line 5 |
| Vocabulary | "Operating cost" in the model is Shaikh's prime cost |
| Reserve condition, idle scrapping | Present both as devices of the model, without a source |
| "Literature: unchanged" | Add Hall & Hitch 1939 and Shaikh's pp. 274–282 for the price rules; add Nakatani 1980 to perso |
