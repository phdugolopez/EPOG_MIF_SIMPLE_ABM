"""Firms buy plants from the rest of the economy; plants arrive next period."""

from equations.borrowing_capacity import borrowing_capacity
from markets.credit_market import borrow
from markets.payments import pay


def affordable_spending(firm, debt_cap: float) -> float:
    """Cash first, then debt up to the cap relative to this period's sales revenue."""
    return max(0.0, firm.cash) + borrowing_capacity(firm.debt, firm.revenue, debt_cap)


def buy_plant(industry, firm, technique, capacity: float, cause: str = "expansion") -> None:
    """Pay for a plant from cash, borrowing the gap; it arrives next period.

    cause ("expansion", "replacement" or "entry") is recorded in the event log only."""
    from model.collector import log_order  # here: model imports markets at load time

    if capacity <= 0.0:
        return
    cost = technique.kappa * capacity
    borrow(industry, firm, max(0.0, cost - max(0.0, firm.cash)))
    pay(industry, firm, industry.roe, cost, "plants")
    firm.investment += cost
    firm.pending_plants.append(
        industry.new_plant(technique, capacity, vintage=industry.time + 1)
    )
    log_order(industry, firm, firm.pending_plants[-1], cost, cause)
