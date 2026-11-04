def entrant_price(leader_price: float, undercut: float) -> float:
    """Entrants start a little below the leader's price (Geroski, in Shaikh 2016, p. 282)."""
    return (1.0 - undercut) * leader_price
