def pay(payer, payee, amount: float) -> None:
    """The only place cash moves: payer.cash - amount, payee.cash + amount."""
    assert amount >= 0.0, amount
    payer.cash -= amount
    payee.cash += amount
