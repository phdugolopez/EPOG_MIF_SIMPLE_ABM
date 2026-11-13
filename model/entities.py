"""The entities of the model (v4-plan.md, section 4).

Objects are compared by identity (eq=False): two plants with the same numbers are two plants.
A firm holds two stocks of money. `cash` moves only through markets.payments.pay. `funds` is
what the firm may invest: retained profit, released reserves and an entrant's equity, less
the plants bought.
"""
from dataclasses import dataclass, field
from math import fsum

import numpy as np

from parameters import Parameters


@dataclass(eq=False)
class Technique:
    name: str                          # "C", "D1", "D2" or a design's name; no rule reads it
    ucs: float                         # operating cost per unit of normal output
    kappa: float                       # capital per unit of normal output
    first_run: int | None = None       # period of its first output; None until a plant runs


@dataclass(eq=False)
class Plant:
    technique: Technique
    capacity: float                    # normal output a period, S
    cost: float                        # purchase cost, kappa x S, paid when ordered
    book_value: float                  # cost less straight-line depreciation; 0 at age T
    age: int = 0                       # periods in operation
    output: float = 0.0                # this period, overtime included
    profit: float = 0.0                # this period, after depreciation; r_new reads it
    below_cost: int = 0                # consecutive periods with the price below its cost
    idle: int = 0                      # consecutive periods without output


@dataclass(eq=False)
class Firm:
    id: int                            # serial number: keys the stream, never breaks a tie
    label: str                         # "shaikh" | "okishio"
    rule: str                          # "unit_cost" | "profit_rate", looked up at creation
    rng: np.random.Generator           # the firm's own random stream
    born: int                          # period of creation
    price: float                       # posted this period; last period's until step 1
    share: float                       # market share f of the replicator
    sales: float = 0.0
    notional: float = 0.0              # the demand addressed to the firm, share x D_t
    util: float = 1.0                  # sales over normal capacity; above 1 with overtime
    hurdle: float = 0.0                # h of its last step 5
    cash: float = 0.0                  # money; moves only through pay()
    funds: float = 0.0                 # what it may invest
    profit: float = 0.0                # this period, after depreciation
    write_offs: float = 0.0            # book value of the plants it scrapped, cumulated
    capital_in: float = 0.0            # its net worth at entry
    result: float = 0.0                # profit cumulated since entry
    cut: bool = False                  # whether it undercut at step 1
    active: bool = False               # whether it had a plant in operation at step 3
    plants: list[Plant] = field(default_factory=list)            # in operation
    pending_plants: list[Plant] = field(default_factory=list)    # on order, delivered next period
    known: list[Technique] = field(default_factory=list)         # its designs that are not public

    @property
    def capacity(self) -> float:
        """Normal capacity in operation."""
        return fsum(plant.capacity for plant in self.plants)


@dataclass(eq=False)
class Account:
    cash: float = 0.0                  # the rest of the economy


@dataclass(eq=False)
class Industry:
    params: Parameters
    seed: int
    rng: np.random.Generator           # the industry's stream: entry and inheritance
    demand_0: float                    # D_0
    time: int = 0                      # t
    firms: list[Firm] = field(default_factory=list)              # in order of creation
    roe: Account = field(default_factory=Account)                # the rest of the economy
    public: list[Technique] = field(default_factory=list)        # the public menu
    waiting: list[Technique] = field(default_factory=list)       # designs built, not yet public
    demand: float = 0.0                # D_t
    lost: float = 0.0                  # demand no firm served this period
    excess: float = 0.0                # (D - K) / D if positive: next period's shortage signal
    reg: Technique | None = None       # the regulating technique
    reg_price: float = 0.0             # its price of production
    r_new: float | None = None         # set at step 3, read at steps 4 and 6
    next_id: int = 0                   # serial number of the next firm
    tally: list = field(default_factory=list)                    # this period's flows, one a flow
    rows: list[dict] = field(default_factory=list)               # the period table


def new_firm(industry: Industry, label: str, price: float, share: float) -> Firm:
    """A firm joins the industry with the rule of its label and a stream of its own."""
    # The stream is keyed by the run seed and the firm's serial number, not by its place.
    key = np.random.SeedSequence(industry.seed, spawn_key=(1, industry.next_id))
    firm = Firm(
        id=industry.next_id,
        label=label,
        rule=getattr(industry.params, "rule_" + label),
        rng=np.random.default_rng(key),
        born=industry.time,
        price=price,
        share=share,
    )
    industry.next_id += 1
    industry.firms.append(firm)
    return firm
