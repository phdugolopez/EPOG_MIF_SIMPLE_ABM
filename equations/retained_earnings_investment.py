import math


def retained_earnings_investment(funds: float, kappa: float, plant_size: float | None) -> float:
    """INVESTMENT_RULE = "retained_earnings": capacity bought from retained earnings,
    without borrowing and whatever the demand: as many whole plants of size plant_size as
    the funds pay for at kappa per unit of capacity (with plant_size None, all of them).
    funds = profit after depreciation and interest, less dividends, accumulated and not yet
    spent on plants (and held as cash). Returns capacity in units."""
    if funds <= 0.0:
        return 0.0
    if plant_size is None:
        return funds / kappa
    return math.floor(funds / (kappa * plant_size) + 1e-9) * plant_size
