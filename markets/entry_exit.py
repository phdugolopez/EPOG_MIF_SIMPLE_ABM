"""Entry and exit: capital joins and leaves the industry through the rest of the economy
(v4-final-model.md, "Schedule", step 6).
"""
from math import fsum

from equations.common_hurdle import evaluation_price, hurdle
from equations.common_technique_choice import choose_technique
from equations.common_unit_cost import unit_cost
from equations.entry_inherited_rule import inherited_label
from equations.entry_price import entrant_price
from equations.entry_size import entrant_plants
from markets.payments import pay
from markets.plant_market import buy_plant
from model.entities import Firm, new_firm
from model.outputs import count


def remove_firm(industry, firm) -> None:
    """A firm leaves: its cash goes to the rest of the economy and its plants, in operation
    and on order, leave with it. The caller rescales the shares of the firms that stay."""
    capacity = fsum(plant.capacity for plant in firm.plants + firm.pending_plants)
    count(industry, firm, "exits", 1)
    count(industry, firm, "cap_exit", capacity)
    pay(firm, industry.roe, max(firm.cash, 0.0))
    industry.firms.remove(firm)


def rescale_shares(firms: list) -> None:
    """The shares of the firms that stay sum to 1 again."""
    total = fsum(firm.share for firm in firms)
    for firm in firms:
        if total > 0.0:
            firm.share = firm.share / total
        else:
            firm.share = 1.0 / len(firms)


def create_entrant(industry, u_parent: float, u_flip: float) -> Firm:
    """One firm enters, among the firms that stayed.

    u_parent draws the incumbent whose label it copies and u_flip decides whether the label
    is flipped. Its plants are on order: they are delivered at the start of the next period.
    """
    p = industry.params
    # The incumbents by serial number: the draw of the parent reads them in a fixed order,
    # whatever their place in the industry's list.
    incumbents = sorted(industry.firms, key=lambda firm: firm.id)

    # Its label is copied from an incumbent drawn by market share, or evenly.
    weights = [incumbent.share for incumbent in incumbents]
    if p.entry_label == "even":
        weights = [1.0] * len(incumbents)
    labels = [incumbent.label for incumbent in incumbents]
    label = inherited_label(labels, weights, p.mutation, u_parent, u_flip)

    # The lowest price posted by a firm with a plant in operation; if no firm has one,
    # by any incumbent.
    posting = [incumbent for incumbent in incumbents if incumbent.plants]
    if not posting:
        posting = incumbents
    lowest = min(incumbent.price for incumbent in posting)

    # Its technique is chosen by its own rule on the public menu, with that lowest price as
    # its own price in the evaluation price.
    firm = new_firm(industry, label, lowest, share=0.0)
    eval_price = evaluation_price(lowest, industry.reg_price, p.lam)
    firm.hurdle = hurdle(firm.rule, eval_price, industry.public, p.delta)
    technique = choose_technique(industry.public, firm.hurdle, p.delta)

    # It posts one cut below the lowest price, down to the unit cost of its plants, or
    # that lowest price itself.
    floor = unit_cost(technique.ucs, technique.kappa, p.delta)
    firm.price = entrant_price(lowest, floor, p.price_cut, p.entry_price)

    # Its plants are paid by equity from the rest of the economy.
    capacities = [incumbent.capacity for incumbent in incumbents]
    plants = entrant_plants(capacities, p.entry_size, p.plant_size)
    equity = plants * technique.kappa * p.plant_size
    pay(industry.roe, firm, equity)
    firm.funds += equity
    firm.capital_in = equity
    for _ in range(plants):
        buy_plant(industry, firm, technique, "entry")
    count(industry, firm, "entries", 1)
    if technique is not choose_technique(industry.public, 0.0, p.delta):
        count(industry, firm, "orders_dearer", plants)

    # Its share is its capacity over next period's capacity, and the incumbents' shares
    # are scaled down by as much.
    capacity = plants * p.plant_size
    ahead = fsum(plant.capacity for incumbent in incumbents
                 for plant in incumbent.plants + incumbent.pending_plants)
    firm.share = capacity / (ahead + capacity)
    for incumbent in incumbents:
        incumbent.share *= 1.0 - firm.share
    return firm
