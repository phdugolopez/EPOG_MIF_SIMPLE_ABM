"""Every money flow goes through pay(), which also records the transaction-flow matrix."""


def sector(industry, agent) -> str:
    return "roe" if agent is industry.roe else "firms"


def pay(industry, payer, receiver, amount: float, item: str) -> None:
    """Move cash from payer to receiver and record it in this period's flow matrix."""
    if amount == 0.0:
        return
    payer.cash -= amount
    receiver.cash += amount
    flows = industry.flows.setdefault(item, {"firms": 0.0, "roe": 0.0})
    flows[sector(industry, payer)] -= amount
    flows[sector(industry, receiver)] += amount
