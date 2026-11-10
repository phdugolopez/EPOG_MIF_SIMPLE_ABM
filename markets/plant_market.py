"""The plant market: a plant is bought, and a plant leaves with its depreciation reserve
(v4-final-model.md, "Schedule", steps 4 to 6).
"""
from equations.scrapping_reserve import reserve_released
from markets.payments import pay
from model.entities import Plant
from model.outputs import count


def buy_plant(industry, firm, technique, cause: str) -> None:
    """The firm orders one plant of a technique and pays for it now.

    The plant is delivered at the start of the next period. cause is "ordered" for an order
    of step 5 and "entry" for a plant of an entrant.
    """
    size = industry.params.plant_size
    cost = technique.kappa * size

    # The plant is paid in cash and out of the funds.
    pay(firm, industry.roe, cost)
    firm.funds -= cost

    # It is on order until the next period opens.
    plant = Plant(technique, capacity=size, cost=cost, book_value=cost)
    firm.pending_plants.append(plant)
    count(industry, firm, "cap_" + cause, size)
    count(industry, firm, "orders", 1)


def remove_plant(industry, firm, plant, reason: str) -> None:
    """A plant leaves its firm; reason is "age", "cost" or "idle".

    Its depreciation reserve joins the funds or is paid to the rest of the economy, by the
    option `reserve`. The book value left is written off.
    """
    p = industry.params
    firm.plants.remove(plant)

    # The reserve is what the plant has depreciated so far.
    reserve = plant.cost - plant.book_value
    if reserve_released(p.reserve, industry.r_new, p.rbar):
        firm.funds += reserve
        count(industry, firm, "cap_released", plant.capacity)
    else:
        # The firm pays the reserve out as far as its cash allows.
        paid = min(reserve, max(firm.cash, 0.0))
        pay(firm, industry.roe, paid)
        count(industry, firm, "withdrawn", paid)

    # What is left of its value is lost.
    firm.write_offs += plant.book_value
    count(industry, firm, "cap_retired", plant.capacity)
    count(industry, firm, "cap_retired_" + reason, plant.capacity)
