"""Parameters of version 4 (v4-final-model.md, parameter table and table of options).

Experiments change fields with dataclasses.replace. No other file holds a constant.
"""
from dataclasses import dataclass

LABELS = ("shaikh", "okishio")
EPS = 1e-9                                  # numerical tolerance
MONEY_EPS = 1e-6                            # tolerance on a sum of money or of capacity

# Shaikh 2016, Tables 7.10-7.11: name, operating cost, capital per unit of normal output.
SHAIKH_MENU = (("C", 64.25, 137.50), ("D1", 61.77, 142.31), ("D2", 59.21, 157.89))
SHAIKH_RATE = 0.16                          # the general rate of that table

# One firm for each pair (technique, label): technique, label, normal output.
START = tuple((name, label, output)
              for name, output in (("C", 120.0), ("D1", 120.0), ("D2", 140.0))
              for label in LABELS)

# The levels of every option that takes a name; model.build refuses any other level.
OPTIONS = {
    "rule_shaikh": ("unit_cost", "profit_rate"),
    "rule_okishio": ("unit_cost", "profit_rate"),
    "menu_scaling": ("scaled", "fixed"),
    "pricing": ("cost_edge", "normal_price", "systematic", "universal"),
    "price_floor": ("unit_cost", "operating_cost", "mean_unit_cost"),
    "scrap_cost": ("operating_cost", "unit_cost"),
    "reserve": ("conditional", "always", "never"),
    "tech_change": ("marx", "neutral", "categories", "none"),
    "investment": ("retained", "accelerator"),
    "entry_price": ("undercut", "lowest"),
    "entry_label": ("share", "even"),
}


@dataclass(frozen=True)
class Parameters:
    periods: int = 200

    # Population and demand
    rule_shaikh: str = "unit_cost"          # unit_cost | profit_rate
    rule_okishio: str = "profit_rate"       # unit_cost | profit_rate
    start: tuple = START
    firms_per_pair: int = 1                 # robustness: 2 and 5
    plant_size: float = 20.0                # S; Morris 10-40
    initial_price: float = 100.0
    demand_ratio: float = 340 / 383         # D_0 over initial capacity
    growth: float = 0.0                     # g; E4: 0.01

    # General rate and initial menu
    rbar: float = 0.16                      # E0r: 0.10, 0.05
    menu_scaling: str = "scaled"            # scaled | fixed (robustness)
    plant_life: int = 10                    # T, delta = 1 / T; Morris 7-19

    # Step 1, pricing
    pricing: str = "cost_edge"              # cost_edge | normal_price | systematic | universal
    price_floor: str = "unit_cost"          # unit_cost | operating_cost | mean_unit_cost
    price_cut: float = 0.02                 # c, also the entrant's; Morris 0.01-0.05
    u_full: float = 1.0                     # spare capacity: last utilisation below this
    shortage_step: float = 0.25             # cutting rules; robustness 0.5; Morris 0.1-0.5
    shortage_rise: float = 0.03             # z, universal undercutting
    monopoly_cap: float = 3.0               # a firm alone stops at this multiple of its floor

    # Steps 2 and 3, demand and production
    chi: float = 1.0                        # Morris 0.25-4
    u_max: float = 1.2                      # overtime limit; 1 gives none; Morris 1-1.4
    payout: float = 0.5                     # d; Morris 0.25-0.75

    # Step 4, scrapping
    scrap_cost: str = "operating_cost"      # operating_cost | unit_cost (robustness)
    scrap_periods: int = 2
    reserve: str = "conditional"            # conditional | always | never (sensitivity)

    # Step 5, technical change and investment
    tech_change: str = "marx"               # marx | neutral | categories | none
    bias: float = 1.5                       # beta; E2: 0, 0.5, 1.5, 3; Morris 0.5-3
    bias_spread: float = 0.8                # sigma
    design_step: float = 0.05               # A; Morris 0.02-0.10
    draw_prob: float = 0.2                  # pi; Morris 0.1-0.4
    public_lag: int | None = 2              # L; None: never public (robustness)
    conflict_share: float = 0.5             # q, categories rule
    lam: float = 0.0                        # lambda; E3: 0, 0.25, 0.5, 0.75, 1
    investment: str = "retained"            # retained | accelerator

    # Step 6, entry and exit
    entry_speed: float = 5.0                # theta; Morris 1-10
    mutation: float = 0.02                  # mu; Morris 0-0.05; 0 in E6
    entry_window: int = 5                   # r_new: plants aged this or less
    entry_size: float = 0.5                 # entrant's capacity over the mean capacity
    entry_price: str = "undercut"           # undercut | lowest (robustness)
    entry_label: str = "share"              # share | even (robustness)
    exit_share: float = 0.01
    min_firms: int = 2

    @property
    def delta(self) -> float:
        return 1.0 / self.plant_life
