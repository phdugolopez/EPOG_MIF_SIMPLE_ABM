"""Capital enters and leaves the industry through the rest of the economy (A10)."""
from math import fsum

from equations.common_hurdle import evaluation_price, hurdle
from equations.common_technique_choice import choose_technique
from equations.entry_inherited_rule import inherited_label
from equations.entry_size import entrant_plants
from markets.payments import pay
from markets.plant_market import buy_plant
from model.entities import new_firm
from model.outputs import count


def remove_firm(industry, firm) -> None:
    """The firm leaves: its cash goes to the rest of the economy and its plants, in operation
    and on order, are written off. The caller rescales the shares of the firms that stay."""
    count(industry, firm, "exits", 1)
    count(industry, firm, "cap_exit", fsum(q.capacity for q in firm.plants + firm.pending_plants))
    pay(firm, industry.roe, max(firm.cash, 0.0))
    industry.firms.remove(firm)


def rescale_shares(firms: list) -> None:
    """The shares of the firms that stay sum to 1 again."""
    total = fsum(firm.share for firm in firms)
    for firm in firms:
        firm.share = firm.share / total if total > 0.0 else 1.0 / len(firms)


def create_entrant(industry, u_parent: float, u_flip: float):
    """One entrant: label inherited by share, price = the lowest posted, technique by its own
    rule on the public menu at that price, plants paid by equity and delivered next period,
    share = its capacity over next period's capacity; the incumbents' shares are scaled down."""
    p = industry.params
    incumbents = sorted(industry.firms, key=lambda firm: firm.id)
    label = inherited_label([firm.label for firm in incumbents],
                            [firm.share for firm in incumbents], p.mutation, u_parent, u_flip)
    price = min(firm.price for firm in [f for f in incumbents if f.plants] or incumbents)
    plants = entrant_plants([firm.capacity for firm in incumbents], p.entry_size, p.plant_size)
    firm = new_firm(industry, label, price, share=0.0)
    eval_price = evaluation_price(price, industry.reg_price, p.lam)
    firm.hurdle = hurdle(firm.rule, eval_price, industry.public, p.delta)
    technique = choose_technique(industry.public, firm.hurdle, p.delta)
    equity = plants * technique.kappa * p.plant_size
    pay(industry.roe, firm, equity)
    firm.funds += equity
    for _ in range(plants):
        buy_plant(industry, firm, technique, "entry")
    count(industry, firm, "entries", 1)
    if technique is not choose_technique(industry.public, 0.0, p.delta):
        count(industry, firm, "orders_dearer", plants)
    capacity = plants * p.plant_size
    ahead = fsum(q.capacity for f in incumbents for q in f.plants + f.pending_plants)
    firm.share = capacity / (ahead + capacity)
    for incumbent in incumbents:
        incumbent.share *= 1.0 - firm.share
    return firm
