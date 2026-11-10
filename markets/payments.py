"""Payments: the only place cash moves (v4-final-model.md, "Randomness and neutrality").

Every account, the rest of the economy included, has a `cash` field. A payment takes from one
and gives to another, so all cash sums to zero in every period.
"""


def pay(payer, payee, amount: float) -> None:
    """Move an amount of cash from the payer to the payee."""
    assert amount >= 0.0, amount
    payer.cash -= amount
    payee.cash += amount
