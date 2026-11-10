"""Entities: technique, plant, firm, the rest-of-economy account and the industry.
State keeps v2's names. Objects are compared by identity (eq=False)."""
from dataclasses import dataclass, field
from math import fsum

import numpy as np

from parameters import Parameters


@dataclass(eq=False)
class Technique:
    name: str                          # "C", "D1", "D2", or a design's serial name; no rule reads it
    ucs: float                         # operating cost per unit of normal output (wage = 1)
    kappa: float                       # capital per unit of normal output (capital goods priced 1)
    first_run: int | None = None       # period of its first output; public public_lag periods later


@dataclass(eq=False)
class Plant:
    technique: Technique
    capacity: float                    # normal output a period: plant_size
    cost: float                        # purchase cost, kappa x plant_size, paid when ordered
    book_value: float                  # cost less straight-line depreciation; 0 at age T
    age: int = 0                       # periods in operation
    output: float = 0.0                # this period
    profit: float = 0.0                # this period, after depreciation (read by r_new)
    below_cost: int = 0                # consecutive periods with the price below the scrap cost
    idle: int = 0                      # consecutive periods without output


@dataclass(eq=False)
class Firm:
    id: int                            # serial number: keys the random stream, never breaks a tie
    label: str                         # "shaikh" | "okishio"
    rule: str                          # "unit_cost" | "profit_rate", from the label, at creation
    rng: np.random.Generator
    born: int
    price: float                       # posted this period (last period's until step 1)
    share: float                       # notional replicator share f (A6)
    sales: float = 0.0
    notional: float = 0.0              # share x D_t
    util: float = 1.0                  # sales / capacity of the last period it produced
    hurdle: float = 0.0                # h of its last investment step
    cash: float = 0.0                  # money; moves only through pay()
    funds: float = 0.0                 # investible funds F (A7)
    profit: float = 0.0                # after depreciation
    write_offs: float = 0.0
    cut: bool = False                  # undercut at step 1
    active: bool = False               # had a plant in operation at step 3 of this period
    plants: list[Plant] = field(default_factory=list)            # in operation
    pending_plants: list[Plant] = field(default_factory=list)    # on order, produce next period
    known: list[Technique] = field(default_factory=list)         # its own designs that are not public

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
    rng: np.random.Generator           # entry and inheritance
    demand_0: float
    time: int = 0
    firms: list[Firm] = field(default_factory=list)              # in order of creation
    roe: Account = field(default_factory=Account)
    public: list[Technique] = field(default_factory=list)        # the public menu
    waiting: list[Technique] = field(default_factory=list)       # built, not yet public
    demand: float = 0.0                # D_t
    lost: float = 0.0                  # demand left unserved this period
    excess: float = 0.0                # (D - K) / D if positive: next period's shortage signal
    reg: Technique | None = None       # regulating technique (A8)
    reg_price: float = 0.0             # uc_reg + rbar kappa_reg
    r_new: float | None = None         # set in step 3, read in steps 4 and 6
    next_id: int = 0
    tally: dict = field(default_factory=dict)                    # this period's flows by label
    rows: list[dict] = field(default_factory=list)               # the period table


def new_firm(industry: Industry, label: str, price: float, share: float) -> Firm:
    """A firm joins the industry with the rule of its label and its own random stream, keyed
    by its serial number and not by its place in the list."""
    key = np.random.SeedSequence(industry.seed, spawn_key=(1, industry.next_id))
    rule = getattr(industry.params, "rule_" + label)
    firm = Firm(industry.next_id, label, rule, np.random.default_rng(key), industry.time, price, share)
    industry.next_id += 1
    industry.firms.append(firm)
    return firm
