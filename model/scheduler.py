"""One period: six steps, each computed for all firms from the state at the start of the step,
so the order of industry.firms never matters (plan, section 3)."""
from math import fsum

from equations.accounts_depreciation import depreciation
from equations.accounts_dividends import dividends
from equations.accounts_merit_order import dispatch
from equations.common_hurdle import evaluation_price, hurdle
from equations.common_regulating_price import price_of_production, regulating_technique
from equations.common_technique_choice import choose_technique, technique_cost
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
from equations.pricing_floor import price_floor
from equations.pricing_rule import posted_price
from equations.scrapping_below_cost import periods_below_cost, scrap_cost
from equations.scrapping_idle_plants import periods_idle
from equations.scrapping_retirement import retirement_reason
from markets.entry_exit import create_entrant, remove_firm, rescale_shares
from markets.goods_market import allocate
from markets.payments import pay
from markets.plant_market import buy_plant, remove_plant
from model.entities import Technique
from model.outputs import count, record_end, record_production, reset_tally
from parameters import LABELS


def period(industry) -> None:
    """Period t: deliveries, the six steps, the outputs and the checks."""
    start_period(industry)
    set_prices(industry)
    allocate_demand(industry)
    produce_and_account(industry)
    scrap_plants(industry)
    invest(industry)
    enter_and_exit(industry)
    record_end(industry)
    check(industry)
    industry.time += 1


def start_period(industry) -> None:
    """Step 0: demand of the period; plants ordered last period are delivered (A4); a design
    becomes public public_lag periods after its first plant produces (A9); new tally."""
    p, t = industry.params, industry.time
    industry.demand = industry.demand_0 * (1.0 + p.growth) ** t
    for firm in industry.firms:
        for plant in firm.pending_plants:
            if plant.technique.first_run is None:
                plant.technique.first_run = t
                industry.waiting.append(plant.technique)
        firm.plants += firm.pending_plants
        firm.pending_plants = []
    if p.public_lag is not None:
        for technique in [w for w in industry.waiting if w.first_run + p.public_lag <= t]:
            industry.waiting.remove(technique)
            industry.public.append(technique)
            for firm in industry.firms:
                if technique in firm.known:
                    firm.known.remove(technique)
    reset_tally(industry)


def set_prices(industry) -> None:
    """Step 1, pricing (A5). Every firm reads last period's prices, its own utilisation, last
    period's excess demand and the unit cost of each firm's best plant in operation. Rivals
    are the other firms with a plant in operation; a firm without one has no spare capacity."""
    p = industry.params
    state = [(firm, firm.price, price_floor([unit_cost(q.technique.ucs, q.technique.kappa, p.delta)
                                             for q in firm.plants])) for firm in industry.firms]
    for firm, previous, cost in state:
        rivals = [(price, c) for other, price, c in state if other is not firm and other.plants]
        firm.price, firm.cut = posted_price(
            previous, [price for price, _ in rivals], [c for _, c in rivals], cost,
            bool(firm.plants) and firm.util < p.u_full, industry.excess,
            p.pricing == "cost_edge", p.price_cut, p.shortage_step)


def allocate_demand(industry) -> None:
    """Step 2, demand (A6). Notional shares follow the replicator on E = 1 / p. A firm offers
    its plants whose operating cost is at most its price and sells its notional demand up to
    that; the rest is re-allocated once, then lost. excess is next period's shortage signal."""
    p, firms = industry.params, industry.firms
    shares = replicator_shares([firm.share for firm in firms],
                               [competitiveness(firm.price) for firm in firms], p.chi)
    offered = [fsum(q.capacity for q in firm.plants if q.technique.ucs <= firm.price)
               for firm in firms]
    sales, industry.lost = allocate(industry.demand, shares, offered)
    for firm, share, sold in zip(firms, shares, sales):
        firm.share, firm.notional, firm.sales = share, share * industry.demand, sold
    capacity = fsum(firm.capacity for firm in firms)
    industry.excess = max(0.0, industry.demand - capacity) / industry.demand


def produce_and_account(industry) -> None:
    """Step 3, production and accounts. Plants run cheapest first, then youngest; every plant
    in operation ages and depreciates; profit is after depreciation and retained profit joins
    the funds. Then the regulating price (A8) and r_new (A7, A10) are set, once a period."""
    p = industry.params
    for firm in industry.firms:
        plants = firm.plants
        outputs = dispatch([q.technique.ucs for q in plants], [q.age for q in plants],
                           [q.capacity for q in plants], firm.sales)
        for plant, output in zip(plants, outputs):
            charge = depreciation(plant.cost, plant.book_value, p.delta)
            plant.output = output
            plant.profit = (firm.price - plant.technique.ucs) * output - charge
            plant.book_value -= charge
            plant.age += 1
        pay(industry.roe, firm, firm.price * firm.sales)
        pay(firm, industry.roe, fsum(q.technique.ucs * q.output for q in plants))
        firm.profit = fsum(q.profit for q in plants)
        paid = dividends(firm.profit, p.payout)
        pay(firm, industry.roe, paid)
        count(industry, firm, "dividends", paid)
        firm.funds += firm.profit - paid
        firm.active = bool(plants)
        if plants:
            firm.util = firm.sales / firm.capacity
    plants = [plant for firm in industry.firms for plant in firm.plants]
    if plants:
        industry.reg = regulating_technique([plant.technique for plant in plants], p.delta)
        industry.reg_price = price_of_production(industry.reg.ucs, industry.reg.kappa, p.delta, p.rbar)
    recent = [plant for plant in plants if plant.age <= p.entry_window]
    industry.r_new = new_plant_rate([plant.profit / plant.cost for plant in recent],
                                    [plant.capacity for plant in recent])
    record_production(industry)


def scrap_plants(industry) -> None:
    """Step 4, scrapping. A plant leaves at age T, after scrap_periods consecutive periods with
    its owner's price below its scrap cost, or after as many periods without output."""
    p = industry.params
    for firm in industry.firms:
        for plant in list(firm.plants):
            cost = scrap_cost(plant.technique.ucs, plant.technique.kappa, p.delta, p.scrap_cost)
            plant.below_cost = periods_below_cost(plant.below_cost, firm.price, cost)
            plant.idle = periods_idle(plant.idle, plant.output)
            reason = retirement_reason(plant.age, p.plant_life, plant.below_cost, plant.idle,
                                       p.scrap_periods)
            if reason:
                remove_plant(industry, firm, plant, reason)


def invest(industry) -> None:
    """Step 5, technical change and investment (A7 to A9). Every firm takes four uniforms and
    one normal, used or not (Q9), and judges techniques at p^e. An active firm draws a design
    with probability pi from its best technique and keeps it if its rule prefers it. It then
    orders plants of its best technique: those its funds, still in cash, pay for, or those
    its notional demand over u* lacks, as far as cash pays."""
    p = industry.params
    for firm in industry.firms:
        u, z = firm.rng.random(4), firm.rng.standard_normal()
        menu = industry.public + firm.known
        eval_price = evaluation_price(firm.price, industry.reg_price, p.lam)
        firm.hurdle = hurdle(firm.rule, eval_price, menu, p.delta)
        best = choose_technique(menu, firm.hurdle, p.delta)
        if firm.active and p.tech_change != "none" and u[0] < p.draw_prob:
            if p.tech_change == "marx":
                design = draw_marx(best.ucs, best.kappa, 1.0 - u[1], z, p.design_step, p.bias,
                                   p.bias_spread)
            elif p.tech_change == "neutral":
                design = draw_neutral(best.ucs, best.kappa, 1.0 - u[1], u[2], p.design_step)
            else:
                design = draw_categories(best.ucs, best.kappa, p.delta, eval_price, u[2],
                                         1.0 - u[1], u[3], p.design_step, p.conflict_share)
            count(industry, firm, "drawn", 1)
            if (technique_cost(*design, firm.hurdle, p.delta)
                    < technique_cost(best.ucs, best.kappa, firm.hurdle, p.delta)):
                best = Technique(f"{firm.id}.{industry.time}", *design)
                firm.known.append(best)
                menu.append(best)
                firm.hurdle = hurdle(firm.rule, eval_price, menu, p.delta)
                count(industry, firm, "kept", 1)
        cost = best.kappa * p.plant_size
        if p.investment == "retained":
            plants = plants_affordable(min(firm.funds, firm.cash), cost)
        else:
            on_order = fsum(q.capacity for q in firm.pending_plants)
            plants = min(plants_wanted(firm.notional, p.u_target, firm.capacity, on_order,
                                       p.plant_size), plants_affordable(firm.cash, cost))
        for _ in range(plants):
            buy_plant(industry, firm, best, "ordered")
        if plants and best is not choose_technique(menu, 0.0, p.delta):
            count(industry, firm, "orders_dearer", plants)


def enter_and_exit(industry) -> None:
    """Step 6, entry and exit (A10). A firm leaves below exit_share or without capacity, in
    operation or on order, while min_firms remain; then at most one entrant joins the
    survivors. The industry takes three uniforms a period, used or not (Q9)."""
    p, firms = industry.params, industry.firms
    u_entry, u_parent, u_flip = industry.rng.random(3)
    capacities = [fsum(q.capacity for q in firm.plants + firm.pending_plants) for firm in firms]
    out = leaving([firm.share for firm in firms], capacities, p.exit_share, p.min_firms)
    for firm in [firm for firm, flag in zip(firms, out) if flag]:
        remove_firm(industry, firm)
    if any(out):
        rescale_shares(firms)
    if u_entry < entry_probability(industry.r_new, p.rbar, p.entry_speed):
        create_entrant(industry, u_parent, u_flip)


def check(industry) -> None:
    """Asserted every period: money is conserved, no cash is negative, shares sum to 1, and
    next period's capacity is this period's less retirements and exits plus orders and entry."""
    t, firms = industry.time, industry.firms
    cash = industry.roe.cash + fsum(firm.cash for firm in firms)
    assert abs(cash) < 1e-6 + 1e-9 * abs(industry.roe.cash), f"t={t}: all cash sums to {cash}"
    assert all(firm.cash > -1e-6 for firm in firms), f"t={t}: a firm's cash is negative"
    shares = fsum(firm.share for firm in firms)
    assert abs(shares - 1.0) < 1e-9, f"t={t}: shares sum to {shares}"
    planned = fsum(row["capacity_next"] for row in industry.rows[-len(LABELS):])
    actual = fsum(q.capacity for firm in firms for q in firm.plants + firm.pending_plants)
    assert abs(planned - actual) < 1e-6, f"t={t}: capacity {actual} against {planned} planned"
