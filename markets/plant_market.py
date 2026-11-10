"""Plants are ordered and paid for here, and leave here with their depreciation reserve."""
from equations.scrapping_reserve import reserve_released
from markets.payments import pay
from model.entities import Plant
from model.outputs import count


def buy_plant(industry, firm, technique, cause: str) -> None:
    """The firm pays kappa S now, its funds fall by kappa S, and the plant joins pending_plants:
    it produces from the next period (A4). cause: "ordered" (step 5) or "entry" (step 6)."""
    size = industry.params.plant_size
    cost = technique.kappa * size
    pay(firm, industry.roe, cost)
    firm.funds -= cost
    firm.pending_plants.append(Plant(technique, size, cost, cost))
    count(industry, firm, "cap_" + cause, size)
    count(industry, firm, "orders", 1)


def remove_plant(industry, firm, plant, reason: str) -> None:
    """The plant leaves ("age", "cost" or "idle"). Its reserve, cost - book value, joins the
    funds if reserve_released, else is paid out as far as cash allows; the rest is written off."""
    firm.plants.remove(plant)
    reserve = plant.cost - plant.book_value
    if reserve_released(industry.r_new, industry.params.rbar):
        firm.funds += reserve
        count(industry, firm, "cap_released", plant.capacity)
    else:
        paid = min(reserve, max(firm.cash, 0.0))
        pay(firm, industry.roe, paid)
        count(industry, firm, "withdrawn", paid)
    firm.write_offs += plant.book_value
    count(industry, firm, "cap_retired", plant.capacity)
    count(industry, firm, "cap_retired_" + reason, plant.capacity)
