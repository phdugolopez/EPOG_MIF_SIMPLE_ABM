from dataclasses import dataclass, field


@dataclass(frozen=True)
class Technique:
    """A technique on the menu: unit operating cost and capital per unit of output."""

    name: str
    ucs: float
    kappa: float


@dataclass
class Plant:
    plant_id: int
    technique: str
    ucs: float
    kappa: float
    capacity: float  # normal output
    vintage: int  # first period in which the plant produces
    book_value: float
    initial: bool = False  # part of the initial endowment
    age: int = 0  # periods of operation completed
    output: float = 0.0
    overtime_output: float = 0.0  # part of output above normal capacity
    profit: float = 0.0  # this period: (p - ucs) x - premium - depreciation
    lifetime_profit: float = 0.0
    periods_below_cost: int = 0

    @property
    def purchase_cost(self) -> float:
        return self.kappa * self.capacity


@dataclass
class Firm:
    firm_id: int
    type: str  # "shaikh" or "okishio": a label, read only by equations/hurdle.py
    price: float
    share: float
    cash: float = 0.0
    debt: float = 0.0
    hurdle: float = 0.0
    plants: list[Plant] = field(default_factory=list)
    pending_plants: list[Plant] = field(default_factory=list)  # arrive next period
    born: int = 0

    # Flows of the current period, reset by the scheduler.
    sales: float = 0.0
    previous_sales: float = 0.0
    util: float = 0.0
    unmet: float = 0.0
    revenue: float = 0.0
    operating_cost: float = 0.0
    depreciation: float = 0.0
    interest: float = 0.0
    profit: float = 0.0
    profit_rate: float = 0.0
    dividends: float = 0.0
    write_offs: float = 0.0
    investment: float = 0.0  # spending on new plants, replacements included
    equity_in: float = 0.0
    at_war: bool = False
    non_renewal: bool = False
    net_worth_start: float = 0.0
    util_history: list[float] = field(default_factory=list)

    @property
    def capacity(self) -> float:
        return sum(p.capacity for p in self.plants)

    @property
    def capital(self) -> float:
        """Capital at purchase cost of the plants in operation."""
        return sum(p.purchase_cost for p in self.plants)

    @property
    def book_value(self) -> float:
        return sum(p.book_value for p in self.plants + self.pending_plants)

    @property
    def net_worth(self) -> float:
        return self.cash + self.book_value - self.debt


@dataclass
class RestOfEconomy:
    """Buyers, workers, suppliers of materials and plants, lenders and owners in one account."""

    cash: float = 0.0
    loans: float = 0.0
    loan_losses: float = 0.0
