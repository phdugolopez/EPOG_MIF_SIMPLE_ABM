"""One period of the industry (v4-final-model.md, "Schedule").

A period is the tuple STEPS, run in order, then close_period. Every step computes all firms
from the state at the start of the step, so the order of industry.firms never matters. The
run viewer runs the same tuple and reads the firms between two steps.

Each step function reads like its paragraph of the schedule; what a step needs beyond that is
in the helpers that follow it.
"""
from math import fsum, isclose
from typing import NamedTuple

from equations.accounts_depreciation import depreciation
from equations.accounts_dividends import dividends
from equations.accounts_merit_order import dispatch
from equations.common_hurdle import evaluation_price, hurdle
from equations.common_regulating_price import price_of_production, regulating_technique
from equations.common_technique_choice import choose_technique, frontier, technique_cost
from equations.common_unit_cost import unit_cost
from equations.demand_replicator import competitiveness, replicator_shares
from equations.entry_exit_rule import leaving
from equations.entry_new_plant_rate import new_plant_rate
from equations.entry_probability import entry_probability
from equations.investment_accelerator import plants_wanted
from equations.investment_draw_categories import draw_categories
from equations.investment_draw_marx import draw_marx
from equations.investment_draw_neutral import draw_neutral
from equations.investment_retained_earnings import plants_affordable
from equations.pricing_cutting import cutting_price
from equations.pricing_entitlement import (entitled_cost_edge, entitled_normal_price,
                                           entitled_systematic)
from equations.pricing_floor import operating_cost_floor, unit_cost_floor
from equations.pricing_universal import universal_price
from equations.scrapping_below_cost import periods_below_cost, scrap_cost
from equations.scrapping_idle_plants import periods_idle
from equations.scrapping_retirement import retirement_reason
from markets.entry_exit import create_entrant, remove_firm, rescale_shares
from markets.goods_market import allocate
from markets.payments import pay
from markets.plant_market import buy_plant, remove_plant
from model.entities import Firm, Technique
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
        floor = unit_cost_floor([plant_unit_cost(plant, p) for plant in firm.plants])

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
    """
    p = industry.params
    firms = industry.firms

    # Market shares follow the replicator: a firm cheaper than the average gains.
    levels = [competitiveness(firm.price) for firm in firms]
    shares = replicator_shares([firm.share for firm in firms], levels, p.chi)

    # A firm can sell up to u_max times the normal capacity of the plants it offers.
    limits = [p.u_max * fsum(plant.capacity for plant in offered_plants(firm))
              for firm in firms]
    sales, lost = allocate(industry.demand, shares, limits)
    for firm, share, sold in zip(firms, shares, sales):
        firm.share = share
        firm.notional = share * industry.demand
        firm.sales = sold
    industry.lost = lost

    # The shortage signal: demand above the normal capacity in operation, as a share of demand.
    capacity = fsum(firm.capacity for firm in firms)
    industry.excess = max(0.0, industry.demand - capacity) / industry.demand


def offered_plants(firm) -> list:
    """The plants a firm offers at step 2 and runs at step 3."""
    # Those whose operating cost its price covers: the others would lose on every unit.
    return [plant for plant in firm.plants if plant.technique.ucs <= firm.price]


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

    # Only the plants offered at step 2 run.
    offered = offered_plants(firm)
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
    """
    p = industry.params

    # Each firm reads the public menu and the regulating price, which no firm moves here.
    for firm in industry.firms:
        # Four uniforms and one normal, used or not: every cell reads the same numbers.
        u = firm.rng.random(4)
        z = firm.rng.standard_normal()

        # Its hurdle at its evaluation price, and its best technique on the menu it knows.
        menu = industry.public + firm.known
        eval_price = evaluation_price(firm.price, industry.reg_price, p.lam)
        firm.hurdle = hurdle(firm.rule, eval_price, menu, p.delta)
        best = choose_technique(menu, firm.hurdle, p.delta)

        # With a plant in operation it draws a design from that technique with probability pi.
        if firm.active and p.tech_change != "none" and u[0] < p.draw_prob:
            ucs, kappa = draw_design(best, eval_price, u, z, p)
            count(industry, firm, "drawn", 1)
            # It keeps the design if its own rule prefers it; a design that ties is not kept.
            design_cost = technique_cost(ucs, kappa, firm.hurdle, p.delta)
            if design_cost < technique_cost(best.ucs, best.kappa, firm.hurdle, p.delta):
                best = Technique(f"{firm.id}.{industry.time}", ucs, kappa)
                firm.known.append(best)
                menu.append(best)
                firm.hurdle = hurdle(firm.rule, eval_price, menu, p.delta)
                count(industry, firm, "kept", 1)

        # It orders plants of its best technique: paid now, delivered next period.
        plants = plants_ordered(firm, best, p)
        for _ in range(plants):
            buy_plant(industry, firm, best, "ordered")
        # An order is dearer when the unit-cost rule would have chosen another technique.
        if plants > 0 and best is not choose_technique(menu, 0.0, p.delta):
            count(industry, firm, "orders_dearer", plants)


def draw_design(best, eval_price: float, u, z: float, p) -> tuple[float, float]:
    """A design drawn from a firm's best technique, as (ucs, kappa), under the rule that
    `tech_change` names."""
    # The size of the step is in (0, 1], so a design is never the technique itself.
    u_step = 1.0 - u[1]
    if p.tech_change == "marx":
        return draw_marx(best.ucs, best.kappa, u_step, z, p.design_step, p.bias, p.bias_spread)
    if p.tech_change == "neutral":
        return draw_neutral(best.ucs, best.kappa, u_step, u[2], p.design_step)
    return draw_categories(best.ucs, best.kappa, p.delta, eval_price, u[2], u_step, u[3],
                           p.design_step, p.conflict_share)


def plants_ordered(firm, technique, p) -> int:
    """The plants of a technique a firm orders this period, under the rule that `investment`
    names."""
    cost = technique.kappa * p.plant_size
    if p.investment == "retained":
        # Retained earnings: the whole plants its funds pay for, as far as they are in cash.
        return plants_affordable(min(firm.funds, firm.cash), cost)
    # Accelerator: the plants missing for the demand addressed to it, plants on order
    # counted, as far as its cash pays.
    on_order = fsum(plant.capacity for plant in firm.pending_plants)
    wanted = plants_wanted(firm.notional, firm.capacity, on_order, p.plant_size)
    return min(wanted, plants_affordable(firm.cash, cost))


def enter_and_exit(industry) -> None:
    """Step 6, entry and exit (v4-final-model.md, "Schedule", step 6).

    The industry takes three uniforms from its own stream, used or not. Exits first: a firm
    leaves with a share below exit_share or without capacity, in operation or on order,
    while min_firms remain. Then at most one entrant, with a probability that rises with
    r_new above rbar; its label by `entry_label`, its price by `entry_price`.

    Reads the industry's stream; shares and capacities; r_new; the lowest price of a firm
    with a plant in operation; the public menu. Writes firms; shares; the entrant, its price
    and its plants on order; cash.
    """
    p = industry.params
    firms = industry.firms

    # The industry takes three uniforms a period, used or not.
    u_entry, u_parent, u_flip = industry.rng.random(3)

    # Exits first. Capacity counts the plants in operation and on order.
    capacities = [fsum(plant.capacity for plant in firm.plants + firm.pending_plants)
                  for firm in firms]
    flags = leaving([firm.share for firm in firms], capacities, p.exit_share, p.min_firms)
    # The firms that leave; the shares of those that stay are scaled up to sum to 1.
    leavers = [firm for firm, leaves in zip(firms, flags) if leaves]
    for firm in leavers:
        remove_firm(industry, firm)
    if leavers:
        rescale_shares(firms)

    # Then at most one entrant, the more likely the more new plants earn above rbar.
    if u_entry < entry_probability(industry.r_new, p.rbar, p.entry_speed):
        create_entrant(industry, u_parent, u_flip)


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
