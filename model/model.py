import random

import parameters
from model.entities import Firm, Plant, RestOfEconomy, Technique
from model.scheduler import run_period


def build_menu(config) -> dict[str, Technique]:
    """Techniques from Shaikh's table: kappa = K / q, ucs = uc - delta kappa."""
    menu = {}
    for name, (output, capital, uc) in config.SHAIKH_PLANTS.items():
        kappa = capital / output
        menu[name] = Technique(name=name, ucs=uc - config.DELTA * kappa, kappa=kappa)
    return menu


class Industry:
    """Container for firms, the rest of the economy, the menu and the simulation history."""

    def __init__(self, config=parameters) -> None:
        self.parameters = config
        self.time: int = 0
        self.rng = random.Random(config.SEED)
        self.techniques = build_menu(config)
        self.menu = [self.techniques[name] for name in config.MENU]
        self.roe = RestOfEconomy()
        self.firms: list[Firm] = []
        self.next_firm_id = 0
        self.next_plant_id = 0

        for technique_name, firm_type in config.INITIAL_FIRMS:
            technique = self.techniques[technique_name]
            capacity = config.SHAIKH_PLANTS[technique_name][0]
            firm = self.new_firm(firm_type, config.INITIAL_PRICE, share=0.0, born=0)
            firm.cash = config.INITIAL_CASH
            firm.debt = config.INITIAL_DEBT
            firm.plants.append(
                self.new_plant(technique, capacity, vintage=0, initial=True)
            )
        total_capacity = sum(f.capacity for f in self.firms)
        self.initial_demand = config.DEMAND_TO_CAPACITY * total_capacity
        for firm in self.firms:
            firm.share = firm.capacity / total_capacity
            firm.previous_sales = firm.share * self.initial_demand
            firm.sales = firm.previous_sales
        self.roe.loans = sum(f.debt for f in self.firms)
        self.money = self.roe.cash + sum(f.cash for f in self.firms)

        self.leader_price = min(f.price for f in self.firms)
        self.unserved = 0.0
        self.replacements = 0
        self.r_new = None
        self.flows: dict[str, dict[str, float]] = {}
        self.retired: list[Plant] = []
        self.entries: list[Firm] = []
        self.exits: list[tuple[Firm, str]] = []
        self.previous_profit = sum(f.profit for f in self.firms)
        self.previous_investment = 0.0

        self.history: list[dict] = []
        self.firm_history: list[dict] = []
        self.plant_history: list[dict] = []
        self.flow_history: list[dict] = []
        self.events: list[dict] = []  # the event log, written by model.collector.log_event
        self.record: dict = {}  # the collector's copy of values later steps overwrite
        self.n_check_fail = 0  # periods with a failing check (CHECKS_RAISE = False)

    def demand(self, time: int | None = None) -> float:
        """D_t = D_0 (1 + g)^t, insensitive to the industry price."""
        t = self.time if time is None else time
        return self.initial_demand * (1.0 + self.parameters.DEMAND_GROWTH) ** t

    def new_firm(self, firm_type: str, price: float, share: float, born: int) -> Firm:
        firm = Firm(
            firm_id=self.next_firm_id, type=firm_type, price=price, share=share, born=born
        )
        self.next_firm_id += 1
        self.firms.append(firm)
        return firm

    def new_plant(
        self, technique: Technique, capacity: float, vintage: int, initial: bool = False
    ) -> Plant:
        plant = Plant(
            plant_id=self.next_plant_id,
            technique=technique.name,
            ucs=technique.ucs,
            kappa=technique.kappa,
            capacity=capacity,
            vintage=vintage,
            book_value=technique.kappa * capacity,
            initial=initial,
        )
        self.next_plant_id += 1
        return plant

    def step(self) -> None:
        run_period(self)
        self.time += 1

    def run(self, periods: int | None = None) -> None:
        for _ in range(self.parameters.PERIODS if periods is None else periods):
            self.step()
