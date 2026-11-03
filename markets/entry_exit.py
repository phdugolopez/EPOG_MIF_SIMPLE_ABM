"""Capital enters and leaves the industry through the rest of the economy."""

from markets.credit_market import default
from markets.payments import pay
from markets.plant_market import buy_plant


def remove_firm(industry, firm, reason: str) -> None:
    """A leaving firm repays what it can, the rest of its debt is a loss of the lender,
    remaining cash goes back to its owners, and its plants are written off (scrap value 0).
    Its customers are shared out in proportion to the other firms' shares."""
    default(industry, firm)
    pay(industry, firm, industry.roe, firm.cash, "equity")
    for plant in firm.plants + firm.pending_plants:
        firm.write_offs += plant.book_value
        plant.book_value = 0.0
    industry.firms.remove(firm)
    firm.exit_reason = reason
    industry.exits.append((firm, reason))
    rescale_shares(industry.firms)


def create_entrant(industry, firm_type: str, price: float, technique, capacity: float):
    """The entrant's owners bring the cost of its plant as equity; the plant arrives next
    period and the entrant starts with a share in proportion to its capacity."""
    incumbents = list(industry.firms)
    firm = industry.new_firm(firm_type, price, share=0.0, born=industry.time)
    cost = technique.kappa * capacity
    pay(industry, industry.roe, firm, cost, "equity")
    firm.equity_in = cost
    buy_plant(industry, firm, technique, capacity)
    next_capacity = sum(
        f.capacity + sum(p.capacity for p in f.pending_plants) for f in incumbents
    )
    firm.share = capacity / (next_capacity + capacity)
    for f in incumbents:
        f.share *= 1.0 - firm.share
    industry.entries.append(firm)
    return firm


def rescale_shares(firms) -> None:
    total = sum(f.share for f in firms)
    if total > 0.0:
        for f in firms:
            f.share /= total
    elif firms:
        for f in firms:
            f.share = 1.0 / len(firms)
