def debt_repayment(debt: float, repayment_rate: float, cash: float) -> float:
    """R_i,t = min(psi B_i,t, M_i,t): a share of debt repaid, if cash allows."""
    return max(0.0, min(repayment_rate * debt, cash))
