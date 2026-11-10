"""One period of the industry (v4-final-model.md, "Schedule").

A period is the tuple STEPS, run in order, then close_period. Every step computes all firms
from the state at the start of the step, so the order of industry.firms never matters. The
run viewer runs the same tuple and reads the firms between two steps.

State of the build: steps 0, 1, 3 and 4, close_period and check are final. Steps 2, 5 and 6
are the stubs of stage 2, each with its final signature and a docstring that says what it
reads and writes; stages 3b and 3d write their bodies.
"""
from math import fsum, isclose
from typing import NamedTuple

from equations.accounts_depreciation import depreciation
from equations.accounts_dividends import dividends
from equations.accounts_merit_order import dispatch
from equations.common_regulating_price import price_of_production, regulating_technique
from equations.common_technique_choice import frontier
from equations.common_unit_cost import unit_cost
from equations.entry_new_plant_rate import new_plant_rate
from equations.pricing_cutting import cutting_price
from equations.pricing_entitlement import (entitled_cost_edge, entitled_normal_price,
                                           entitled_systematic)
from equations.pricing_floor import operating_cost_floor
from equations.pricing_universal import universal_price
from equations.scrapping_below_cost import periods_below_cost, scrap_cost
from equations.scrapping_idle_plants import periods_idle
from equations.scrapping_retirement import retirement_reason
from markets.payments import pay
from markets.plant_market import remove_plant
from model.entities import Firm
from model.outputs import count, record_end, record_production
from parameters import EPS, LABELS, MONEY_EPS


def start_period(industry) -> None:
    """Step 0, the start of the period (v4-final-model.md, "Schedule", step 0).

    Demand is D_t. The plants ordered last period are delivered, an entrant's included, so an
    entrant of t - 1 has a plant in operation at step 1. A design joins the public menu
    public_lag periods after its first plant produced.

    Reads time, growth, pending_plants, waiting and public_lag. Writes demand; plants and
    pending_plants; first_run; public, waiting and known; an empty tally.
    """
    p = industry.params
    t = industry.time

    # Demand grows at the rate g from D_0.
    industry.demand = industry.demand_0 * (1.0 + p.growth) ** t

    # The plants ordered last period are in operation from now on.
    for firm in industry.firms:
        for plant in firm.pending_plants:
            # A technique that runs for the first time is dated, and waits to become public.
            if plant.technique.first_run is None:
                plant.technique.first_run = t
                industry.waiting.append(plant.technique)
        firm.plants += firm.pending_plants
        firm.pending_plants = []

    # The designs that have waited public_lag periods become public.
    if p.public_lag is not None:
        publish_designs(industry)

    # The tally of the period's flows starts empty.
    industry.tally = []


def publish_designs(industry) -> None:
    """The designs dated public_lag periods ago join the public menu and leave their owner's
    list; the public menu keeps its frontier."""
    p = industry.params
    # The designs whose first plant produced public_lag periods ago, or earlier.
    due = [technique for technique in industry.waiting
           if technique.first_run + p.public_lag <= industry.time]
    for technique in due:
        industry.waiting.remove(technique)
        industry.public.append(technique)
        for firm in industry.firms:
            if technique in firm.known:
                firm.known.remove(technique)
    industry.public = frontier(industry.public, p.delta)


class Quote(NamedTuple):
    """What step 1 reads about one firm, taken before any price changes."""
    firm: Firm
    price: float           # the price it posted last period
    cost: float            # the unit cost of its best plant
    normal_price: float    # the price of production of its best plant
    floor: float           # the lowest price it may cut to
    spare: bool            # whether it had spare capacity last period


def set_prices(industry) -> None:
    """Step 1, pricing (v4-final-model.md, "Schedule", step 1).

    Every firm with a plant in operation posts a price from last period's prices and last
    period's shortage, under the rule that `pricing` names and above the floor that
    `price_floor` names. A firm without a plant in operation keeps its price.

    Reads each firm's price, util and plants (unit cost, kappa, last output), and
    industry.excess. Writes firm.price and firm.cut.
    """
    p = industry.params

    # Read every firm before any price changes: the firms move at the same time.
    # Only the firms with a plant in operation set a price.
    quotes = [read_quote(firm, p) for firm in industry.firms if firm.plants]

    # No firm has cut yet this period.
    for firm in industry.firms:
        firm.cut = False

    # Each firm posts its price from what the others posted last period.
    for own in quotes:
        # A firm's rivals are the other firms with a plant in operation.
        rivals = [other for other in quotes if other.firm is not own.firm]
        if p.pricing == "universal":
            price, has_cut = universal_step(own, quotes, industry.excess, p)
        else:
            price, has_cut = cutting_step(own, rivals, industry.excess, p)
        own.firm.price = price
        own.firm.cut = has_cut


def read_quote(firm, p) -> Quote:
    """The quote of a firm with a plant in operation."""
    # The best plant has the lowest unit cost; a tie goes to the lower capital per unit.
    best = min(firm.plants, key=lambda plant: (plant_unit_cost(plant, p), plant.technique.kappa))
    cost = plant_unit_cost(best, p)

    if p.price_floor == "operating_cost":
        # The operating costs of the plants that ran last period, and of every plant it owns.
        ran = [plant.technique.ucs for plant in firm.plants if plant.output > EPS]
        owned = [plant.technique.ucs for plant in firm.plants]
        floor = operating_cost_floor(ran, owned)
    else:
        floor = cost

    return Quote(
        firm=firm,
        price=firm.price,
        cost=cost,
        normal_price=cost + p.rbar * best.technique.kappa,
        floor=floor,
        spare=firm.util < p.u_full,
    )


def cutting_step(own: Quote, rivals: list[Quote], excess: float, p) -> tuple[float, bool]:
    """The price of a firm under one of the three cutting rules, and whether it cut."""
    return cutting_price(
        previous=own.price,
        rival_prices=[rival.price for rival in rivals],
        entitled=is_entitled(own, rivals, p),
        excess=excess,
        floor=own.floor,
        cut=p.price_cut,
        shortage_step=p.shortage_step,
    )


def is_entitled(own: Quote, rivals: list[Quote], p) -> bool:
    """Whether the price rule lets the firm undercut the lowest price of its rivals."""
    if not rivals:
        return False
    lowest = min(rival.price for rival in rivals)
    # The unit costs of the rivals that posted that lowest price.
    costs_at_lowest = [rival.cost for rival in rivals if isclose(rival.price, lowest)]

    if p.pricing == "systematic":
        return entitled_systematic(own.spare)
    if p.pricing == "normal_price":
        return entitled_normal_price(own.spare, own.cost, costs_at_lowest, lowest,
                                     own.normal_price)
    return entitled_cost_edge(own.spare, own.cost, costs_at_lowest)


def universal_step(own: Quote, quotes: list[Quote], excess: float, p) -> tuple[float, bool]:
    """The price of a firm under universal undercutting, and whether it cut."""
    # L, the lowest price posted last period by a firm with a plant in operation.
    lowest = min(quote.price for quote in quotes)
    return universal_price(
        previous=own.price,
        lowest=lowest,
        floor=own.floor,
        excess=excess,
        alone=len(quotes) == 1,
        cut=p.price_cut,
        rise=p.shortage_rise,
        cap=p.monopoly_cap,
    )


def plant_unit_cost(plant, p) -> float:
    """The unit cost of a plant's technique."""
    return unit_cost(plant.technique.ucs, plant.technique.kappa, p.delta)


def allocate_demand(industry) -> None:
    """Step 2, demand (v4-final-model.md, "Schedule", step 2).

    Market shares follow the replicator on E = 1 / p. A firm offers its plants whose
    operating cost is at most its price and sells up to u_max times their normal capacity;
    unserved demand is re-allocated once and the rest is lost. The shortage signal of the
    next period is demand above the normal capacity in operation.

    Reads share, price, the plants (operating cost, capacity) and demand. Writes firm.share,
    firm.notional and firm.sales; industry.lost and industry.excess.

    Stub of stage 2: shares stay as they are, a firm offers every plant, and nothing is
    re-allocated. Stage 3b writes the body.
    """
    p = industry.params

    # Each firm sells the demand addressed to it, up to the overtime limit on its capacity.
    for firm in industry.firms:
        firm.notional = firm.share * industry.demand
        firm.sales = min(firm.notional, p.u_max * firm.capacity)

    # What no firm serves is lost.
    industry.lost = industry.demand - fsum(firm.sales for firm in industry.firms)

    # The shortage signal: demand above the normal capacity in operation, as a share of demand.
    capacity = fsum(firm.capacity for firm in industry.firms)
    industry.excess = max(0.0, industry.demand - capacity) / industry.demand


def produce_and_account(industry) -> None:
    """Step 3, production and accounts (v4-final-model.md, "Schedule", step 3).

    The plants a firm offered at step 2 run cheapest first, then youngest, to normal
    capacity, then to u_max times it in the same order. Every plant in operation ages and
    depreciates. Profit is after depreciation; dividends are paid and the rest joins the
    funds. Then, once a period: the regulating price and r_new, and the rows of the period.

    Reads sales, price and the offered plants. Writes output, profit, book_value and age of
    each plant; cash through pay; firm.profit, firm.funds, firm.util and firm.active;
    industry.reg, reg_price and r_new; the two rows of the period.
    """
    # Each firm produces what it sold at step 2, then settles its accounts.
    for firm in industry.firms:
        run_plants(firm, industry.params)
        settle_accounts(industry, firm)

    # Once a period, before any plant leaves, the same for every firm.
    set_regulating_price(industry)
    set_new_plant_rate(industry)

    # The two rows of the period.
    record_production(industry)


def run_plants(firm, p) -> None:
    """The production of a firm: the plants it offered run in merit order, overtime
    included; every plant in operation depreciates and ages, with or without output."""
    # No plant has run yet this period.
    for plant in firm.plants:
        plant.output = 0.0

    # The plants offered at step 2: those whose operating cost the firm's price covers.
    offered = [plant for plant in firm.plants if plant.technique.ucs <= firm.price]
    outputs = dispatch(
        ucs=[plant.technique.ucs for plant in offered],
        ages=[plant.age for plant in offered],
        capacity=[plant.capacity for plant in offered],
        quantity=firm.sales,
        u_max=p.u_max,
    )
    for plant, output in zip(offered, outputs):
        plant.output = output

    # The profit of a plant is after its depreciation of the period.
    for plant in firm.plants:
        charge = depreciation(plant.cost, plant.book_value, p.delta)
        plant.profit = (firm.price - plant.technique.ucs) * plant.output - charge
        plant.book_value -= charge
        plant.age += 1


def settle_accounts(industry, firm) -> None:
    """The accounts of a firm for the period: sales, operating costs, profit, dividends and
    what joins the funds."""
    p = industry.params

    # Sales come in and operating costs go out.
    revenue = firm.price * firm.sales
    operating_cost = fsum(plant.technique.ucs * plant.output for plant in firm.plants)
    pay(industry.roe, firm, revenue)
    pay(firm, industry.roe, operating_cost)

    # A share of a positive profit is paid out; the rest, or a loss, joins the funds.
    firm.profit = fsum(plant.profit for plant in firm.plants)
    paid = dividends(firm.profit, p.payout)
    pay(firm, industry.roe, paid)
    count(industry, firm, "dividends", paid)
    firm.funds += firm.profit - paid

    # Utilisation is sales over normal capacity, so it passes 1 with overtime. A firm
    # without a plant in operation keeps its last utilisation.
    firm.active = bool(firm.plants)
    if firm.plants:
        firm.util = firm.sales / firm.capacity


def set_regulating_price(industry) -> None:
    """The regulating technique, the lowest unit cost in operation, and its price of
    production."""
    p = industry.params
    techniques = [plant.technique for firm in industry.firms for plant in firm.plants]
    # Without a plant in operation the last regulating technique stays.
    if techniques:
        reg = regulating_technique(techniques, p.delta)
        industry.reg = reg
        industry.reg_price = price_of_production(reg.ucs, reg.kappa, p.delta, p.rbar)


def set_new_plant_rate(industry) -> None:
    """r_new, the realised rate of the plants aged entry_window periods or less."""
    p = industry.params
    # The plants in operation that are in the window.
    recent = [plant for firm in industry.firms for plant in firm.plants
              if plant.age <= p.entry_window]
    rates = [plant.profit / plant.cost for plant in recent]
    capacities = [plant.capacity for plant in recent]
    industry.r_new = new_plant_rate(rates, capacities)


def scrap_plants(industry) -> None:
    """Step 4, scrapping (v4-final-model.md, "Schedule", step 4).

    A plant leaves at age T, after scrap_periods consecutive periods with its owner's price
    below its cost, or after as many consecutive periods without output. Its reserve joins
    the funds or is paid out, by the option `reserve` (markets.plant_market.remove_plant).

    Reads age, output, the owner's price and r_new. Writes below_cost and idle; plants;
    funds or cash; write_offs.
    """
    p = industry.params

    # Each plant counts its periods below cost and without output, and leaves if a reason
    # holds. The list is copied because a plant that leaves is taken out of firm.plants.
    for firm in industry.firms:
        for plant in list(firm.plants):
            technique = plant.technique
            cost = scrap_cost(technique.ucs, technique.kappa, p.delta, p.scrap_cost)
            plant.below_cost = periods_below_cost(plant.below_cost, firm.price, cost)
            plant.idle = periods_idle(plant.idle, plant.output)
            reason = retirement_reason(plant.age, p.plant_life, plant.below_cost, plant.idle,
                                       p.scrap_periods)
            if reason is not None:
                remove_plant(industry, firm, plant, reason)


def invest(industry) -> None:
    """Step 5, technical change and investment (v4-final-model.md, "Schedule", step 5).

    Every firm takes four uniforms and one normal from its own stream, used or not. It
    computes its hurdle at its evaluation price and picks its best technique on the public
    menu and its own designs. With a plant in operation it may draw a design, kept if its own
    rule prefers it. It then orders plants: those its funds, still in cash, pay for, or those
    missing for the demand addressed to it, as far as its cash pays.

    Reads the firm's stream; the public menu and firm.known; price and reg_price; funds, cash,
    notional, capacity and the plants on order. Writes hurdle and known; pending_plants, cash
    and funds through markets.plant_market.buy_plant.

    Stub of stage 2: no number is drawn, no design is made and no plant is ordered. Stage 3d
    writes the body.
    """


def enter_and_exit(industry) -> None:
    """Step 6, entry and exit (v4-final-model.md, "Schedule", step 6).

    The industry takes three uniforms from its own stream, used or not. Exits first: a firm
    leaves with a share below exit_share or without capacity, in operation or on order,
    while min_firms remain. Then at most one entrant, with a probability that rises with
    r_new above rbar; its label by `entry_label`, its price by `entry_price`.

    Reads the industry's stream; shares and capacities; r_new; the lowest price of a firm
    with a plant in operation; the public menu. Writes firms; shares; the entrant, its price
    and its plants on order; cash.

    Stub of stage 2: no number is drawn, no firm leaves and none enters. Stage 3b writes the
    body.
    """


def close_period(industry) -> None:
    """The end of the period: the rows are completed, the checks run, time moves on."""
    # The flows of the period, next period's capacity and the closing stocks.
    record_end(industry)

    # Money, shares and capacity add up.
    check(industry)

    # The next period.
    industry.time += 1


def check(industry) -> None:
    """What is asserted at the end of every period.

    All cash sums to zero, no firm's cash is negative, shares sum to 1, and next period's
    capacity is this period's less retirements and exits plus orders and entry.
    """
    t = industry.time
    firms = industry.firms

    # Money: all cash, the rest of the economy included, sums to zero.
    cash = industry.roe.cash + fsum(firm.cash for firm in firms)
    tolerance = MONEY_EPS + EPS * abs(industry.roe.cash)
    assert abs(cash) < tolerance, f"t={t}: all cash sums to {cash}"
    assert all(firm.cash > -MONEY_EPS for firm in firms), f"t={t}: a firm's cash is negative"

    # Shares.
    shares = fsum(firm.share for firm in firms)
    assert abs(shares - 1.0) < EPS, f"t={t}: shares sum to {shares}"

    # Capacity: what the rows of the period announce is what the firms hold, on order included.
    planned = fsum(row["capacity_next"] for row in industry.rows[-len(LABELS):])
    actual = fsum(plant.capacity for firm in firms for plant in firm.plants + firm.pending_plants)
    assert abs(planned - actual) < MONEY_EPS, f"t={t}: capacity {actual}, {planned} planned"


# The steps of a period, in order. The viewer runs them one by one.
STEPS = (start_period, set_prices, allocate_demand, produce_and_account,
         scrap_plants, invest, enter_and_exit)


def period(industry) -> None:
    """Period t: the seven steps, then the end of the period."""
    for step in STEPS:
        step(industry)
    close_period(industry)
