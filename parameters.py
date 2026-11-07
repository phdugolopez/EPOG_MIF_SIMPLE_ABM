"""All baseline parameter values in one place.

Names follow the notation table of docs/design/mechanism-briefs.md; parameters are upper
case here and passed to the equations under the brief's lower-case Python names
(DELTA -> delta, RBAR -> rbar, RHO -> rho, ...). Defaults the brief leaves open are
recorded in docs/design/choices.md.
"""

SEED: int = 42
PERIODS: int = 200

# --- Technology: Shaikh (2016), Tables 7.10-7.11 -----------------------------------
# name -> (normal output, capital stock, unit cost uc at delta = 10 %)
SHAIKH_PLANTS: dict[str, tuple[float, float, float]] = {
    "C": (120.0, 16_500.0, 78.0),
    "D1": (130.0, 18_500.0, 76.0),
    "D2": (133.0, 21_000.0, 75.0),
}
MENU: tuple[str, ...] = ("C", "D1", "D2")  # techniques on offer for new plants

DELTA: float = 0.10  # depreciation rate, 1/T
PLANT_LIFE: int | None = None  # no maximum age; version 1: 10 (T = 1/delta)
# "time": straight line, delta kappa qbar a period. "use": delta kappa x, so idle plants do not
# depreciate, and PLANT_LIFE counts periods of normal output (wear) instead of age.
DEPRECIATION: str = "time"  # or "use"
PLANT_SIZE: float | None = 20.0  # capacity of every plant (initial, new, entrant); version 1: None, any size
RBAR: float = 0.05  # general rate of profit, set outside the industry; version 1: 0.16
U_MAX: float = 1.2  # output can stretch to U_MAX * capacity
OVERTIME_PREMIUM: float = 0.10  # extra unit operating cost on output above capacity

# --- Initial population ------------------------------------------------------------
# One firm per (plant, type): each of Shaikh's plants goes to one Shaikh and one
# Okishio firm, identical within each pair. One plant of age 0 per firm.
INITIAL_FIRMS: tuple[tuple[str, str], ...] = (
    ("C", "shaikh"),
    ("C", "okishio"),
    ("D1", "shaikh"),
    ("D1", "okishio"),
    ("D2", "shaikh"),
    ("D2", "okishio"),
)
INITIAL_PRICE: float = 100.0
INITIAL_CASH: float = 0.0
INITIAL_DEBT: float = 0.0
DEMAND_TO_CAPACITY: float = 340.0 / 383.0  # brief: demand 340 against capacity 383

# --- Hurdle (the only place the two types differ) ----------------------------------
# type label -> technique rule; swap the values for the label-swap test.
HURDLE_RULES: dict[str, str] = {"shaikh": "unit_cost", "okishio": "profit_rate"}
HURDLE_FLOOR_AT_ZERO: bool = True  # Okishio h = max(0, best rate on the menu)
TAU: float = 0.0  # share of a period's operating cost counted as capital advanced

# --- Pricing (Jake) ----------------------------------------------------------------
# "real_competition": no anchor and no war trigger. Firms follow the lowest price, cut below
# it only with spare capacity and a cost edge, and raise prices when demand went unserved.
# "anchor": the version 1 rule (anchor, band and utilisation-triggered price wars).
PRICING_RULE: str = "real_competition"  # or "anchor", or "leader_follow"
PRICE_CUT: float = 0.02  # c: size of an undercut (both rules; per period in an "anchor" war)
U_FULL: float = 1.0  # utilisation at or above which a firm has no spare capacity
SHORTAGE_RESPONSE: float = 0.5  # rise of the highest price per unit of excess-demand share
EXCESS_DEMAND: str = "normal_capacity"  # shortage: demand above normal capacity, or "unserved"
PRICE_FLOOR: str = "unit_cost"  # floor when following: uc of the best plant, or "operating_cost"
# "leader_follow" rule only (the group notebook's rule; PRICE_CUT is its epsilon):
FLOOR_MARKUP: float = 0.20  # m: floor = (1 + m) x capacity-weighted average uc
LEADER_RISE: float = 0.03  # after excess demand: (1 + rise) x leader; a lone firm's rise
MONOPOLY_CAP: float = 3.0  # a lone firm's price stops at MONOPOLY_CAP x floor
# Anchor rule only:
PRICING_ANCHOR: str = "target_return"  # or "markup", or "leader" (one anchor for all)
MARKUP: float = 0.282  # mu, for PRICING_ANCHOR = "markup"
PRICE_SPEED: float = 0.25  # lambda, speed toward the anchor
PRICE_BAND: float = 0.025  # b, how far above the leader a firm may stay
WAR_PERIODS: int = 2  # T in the pricing rule: periods below U_WAR that start a cut
U_WAR: float = 0.95  # utilisation threshold of a price war

# --- Demand (Pierre-Loup) ----------------------------------------------------------
DEMAND_FORM: str = "replicator"  # or "logit"
CHI: float = 1.0  # selection intensity of the linear quasi-replicator
ETA: float = 1.0  # price elasticity of the logit form, f ~ f_{t-1} p^(-eta)
DEMAND_GROWTH: float = 0.0  # D_t = D_0 (1 + g)^t

# --- Production and accounts (unassigned) ------------------------------------------
RHO: float = 0.05  # interest rate on debt, below RBAR
PAYOUT: float = 0.5  # d, dividends = d * max(0, profit)
REPAYMENT_RATE: float = 0.10  # share of debt repaid each period, from cash
CASH_SHORTFALL: str = "bankruptcy"  # negative cash: bankrupt at the end of the period; version 1: "overdraft"

# --- Scrapping (Vincent) -----------------------------------------------------------
OBSOLESCENCE_PERIODS: int = 2  # N: periods with price below the scrap cost before retirement; version 1: 4
SCRAP_COST: str = "unit_cost"  # cost compared with the price: ucs + delta kappa; version 1: "operating_cost", ucs
IDLE_SCRAPPING: bool = True  # scrap plants the firm did not need for IDLE_PERIODS periods; version 1: False
IDLE_PERIODS: int = 2
REPLACEMENT: bool = True  # replace working plants when the hurdle inequality holds

# --- Investment (Ugo) --------------------------------------------------------------
EXPECTED_GROWTH: float = 0.0  # g in desired capacity
INVESTMENT_SALES_LAG: int = 1  # 1: x_{t-1} as in the brief; 0: this period's sales
DEBT_CAP: float = 2.0  # Lambda: debt for plants up to DEBT_CAP * sales revenue (with BORROWING)
BORROWING: bool = False  # borrow for plants (investment, replacement) up to DEBT_CAP; version 1: True
INVESTMENT_RULE: str = "retained_earnings"  # buy what retained earnings pay for, no debt; version 1: "accelerator"

# --- Technical change ---------------------------------------------------------------
# With TECH_DRAWS, a firm that invests is offered one new plant design, drawn relative to the
# technique it would otherwise build, at its own price. Every design is Marx-biased: more
# capital per unit, lower operating cost. It adopts the design if its hurdle rule prefers it,
# and otherwise invests in its current best technique.
TECH_DRAWS: bool = True  # version 1: False, the menu stays fixed
TECH_CONFLICT: float = 0.5  # share of designs in the conflict zone (only the unit-cost rule adopts)
TECH_STEP: float = 0.05  # largest fall in operating cost ucs per design, as a share

# --- Entry and exit (unassigned) ---------------------------------------------------
ENTRY_WINDOW: int = 5  # k: plants built in the last k periods drive r_new
ENTRY_SPEED: float = 5.0  # theta
MUTATION: float = 0.02  # m: probability that an entrant flips the inherited type
ENTRANT_SIZE: float = 0.5  # phi: entrant capacity / average incumbent capacity
ENTRANT_UNDERCUT: float = 0.01  # anchor pricing only: entrant price = (1 - undercut) * leader
MIN_SHARE: float = 0.01  # f_min: exit below this market share
MIN_FIRMS: int = 2  # floor on the number of firms
