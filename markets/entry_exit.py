"""Capital enters and leaves the industry through the rest of the economy."""

from markets.credit_market import default
from markets.payments import pay
from markets.plant_market import buy_plant


def remove_firm(industry, firm, reason: str) -> None:
    """A leaving firm repays what it can, the rest of its debt is a loss of the lender,
    remaining cash goes back to its owners, and its plants are written off (scrap value 0).
    Its customers are shared out in proportion to the other firms' shares. Bills it could
    not pay (negative cash, CASH_SHORTFALL = "bankruptcy") are a loss of the rest of the
    economy."""
    industry.log_exit(firm, reason)
    if firm.cash < 0.0:
        shortfall = -firm.cash
        pay(industry, industry.roe, firm, shortfall, "unpaid bills")
        industry.roe.unpaid_bills += shortfall
    default(industry, firm)
    pay(industry, firm, industry.roe, firm.cash, "equity")
    for plant in firm.plants + firm.pending_plants:
        firm.write_offs += plant.book_value
        plant.book_value = 0.0
    industry.firms.remove(firm)
    firm.exit_reason = reason
    industry.exits.append((firm, reason))
    rescale_shares(industry.firms)


def create_entrant(industry, firm_type: str, price: float, technique, capacity: float,
                   plant_size: float | None = None, hurdle: float = 0.0, known=None):
    """The entrant's owners bring the cost of its plant as equity; the plant arrives next
    period and the entrant starts with a share in proportion to its capacity. With a
    plant_size, capacity (a multiple of it) comes as plants of that size. hurdle and
    known (the h the entrant chose its technique with, and the techniques it can build)
    are set before the order so that the event log reads them."""
    incumbents = list(industry.firms)
    firm = industry.new_firm(firm_type, price, share=0.0, born=industry.time)
    firm.hurdle = hurdle
    firm.known = list(known) if known else []
    cost = technique.kappa * capacity
    pay(industry, industry.roe, firm, cost, "equity")
    firm.equity_in = cost
    if plant_size is None:
        buy_plant(industry, firm, technique, capacity, cause="entry")
    else:
        for _ in range(round(capacity / plant_size)):
            buy_plant(industry, firm, technique, plant_size, cause="entry")
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
