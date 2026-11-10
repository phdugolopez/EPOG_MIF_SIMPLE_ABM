"""Parameters of version 3: the proposal's table and the addendum A1-A13.
Experiments change fields with dataclasses.replace; no other file holds a constant."""
from dataclasses import dataclass

LABELS = ("shaikh", "okishio")
EPS = 1e-9                               # numerical tolerance
MENU = (("C", 64.25, 137.50), ("D1", 61.77, 142.31), ("D2", 59.21, 157.89))   # name, ucs, kappa (A1)
START = tuple((name, label, output)      # one firm per (technique, label) pair (A2)
              for name, output in (("C", 120.0), ("D1", 120.0), ("D2", 140.0)) for label in LABELS)


@dataclass(frozen=True)
class Parameters:
    periods: int = 200
    # population and demand (A1, A2)
    rule_shaikh: str = "unit_cost"       # unit_cost | profit_rate: the hurdle mapping, label -> rule
    rule_okishio: str = "profit_rate"    # unit_cost | profit_rate
    menu: tuple = MENU
    start: tuple = START                 # (technique, label, normal output) of each initial firm
    firms_per_pair: int = 1              # robustness: 2 and 5
    plant_size: float = 20.0             # S; Morris 10-40
    initial_price: float = 100.0
    demand_ratio: float = 340 / 383      # D_0 / initial capacity: D_0 = 674.7 at the defaults
    growth: float = 0.0                  # g; E4: 0.01
    rbar: float = 0.05                   # general rate: entry gate, replacement condition,
                                         # price of production; E3, E4: 0.16
    plant_life: int = 10                 # T, with delta = 1 / T (A3); Morris 7-19
    # pricing (A5)
    pricing: str = "cost_edge"           # cost_edge | systematic
    price_cut: float = 0.02              # c; Morris 0.01-0.05
    u_full: float = 1.0                  # spare capacity = last utilisation below this
    shortage_step: float = 0.5           # price rise per unit of excess-demand share, no rival above
    # demand (A6)
    chi: float = 1.0                     # Morris 0.25-4
    # accounts
    payout: float = 0.5                  # d; Morris 0.25-0.75
    # scrapping
    scrap_cost: str = "operating_cost"   # operating_cost | unit_cost (robustness)
    scrap_periods: int = 2               # periods below cost, or idle, before a plant leaves
    # technical change (A9)
    tech_change: str = "marx"            # marx | neutral | categories | none
    bias: float = 1.5                    # beta; E2: 0, 0.5, 1.5, 3; Morris 0.5-3
    bias_spread: float = 0.8             # sigma
    design_step: float = 0.05            # A; Morris 0.02-0.10
    draw_prob: float = 0.2               # pi; Morris 0.1-0.4
    public_lag: int | None = 2           # L; None: a design never becomes public (robustness)
    conflict_share: float = 0.5          # q, categories rule only
    # hurdle and investment (A7, A8)
    lam: float = 0.0                     # lambda; E3: 0, 0.25, 0.5, 0.75, 1
    investment: str = "retained"         # retained | accelerator
    u_target: float = 0.9                # accelerator only; robustness: 0.8, 0.95
    # entry and exit (A10)
    entry_speed: float = 5.0             # theta; Morris 1-10
    mutation: float = 0.02               # mu; Morris 0-0.05; 0 in E6
    entry_window: int = 5                # r_new: plants aged this many periods or less
    entry_size: float = 0.5              # entrant's capacity / average incumbent capacity
    exit_share: float = 0.01
    min_firms: int = 2

    @property
    def delta(self) -> float:
        return 1.0 / self.plant_life
