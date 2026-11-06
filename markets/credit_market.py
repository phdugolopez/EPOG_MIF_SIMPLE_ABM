"""Loans between firms and the rest of the economy, the industry's only lender."""

from equations.debt_repayment import debt_repayment
from markets.payments import pay


def borrow(industry, firm, amount: float) -> None:
    """A loan moves cash from the rest of the economy to the firm and raises its debt."""
    if amount <= 0.0:
        return
    pay(industry, industry.roe, firm, amount, "loans")
    firm.debt += amount
    industry.roe.loans += amount


def repay(industry, firm, amount: float) -> None:
    if amount <= 0.0:
        return
    pay(industry, firm, industry.roe, amount, "loans")
    firm.debt -= amount
    industry.roe.loans -= amount


def settle_cash_position(industry, firm) -> None:
    """With cash left, repay a share of debt. A negative balance is covered by an overdraft
    loan outside the debt cap (CASH_SHORTFALL = "overdraft", version 1), or stays as bills
    the firm could not pay ("bankruptcy"): it then goes bankrupt at the end of the period.
    """
    if firm.cash < 0.0:
        if industry.parameters.CASH_SHORTFALL == "overdraft":
            borrow(industry, firm, -firm.cash)
    else:
        repay(
            industry,
            firm,
            debt_repayment(firm.debt, industry.parameters.REPAYMENT_RATE, firm.cash),
        )


def default(industry, firm) -> None:
    """A leaving firm pays what it can; the rest of its debt is a loss of the lender."""
    repay(industry, firm, min(firm.cash, firm.debt))
    loss = firm.debt
    firm.debt = 0.0
    industry.roe.loans -= loss
    industry.roe.loan_losses += loss
