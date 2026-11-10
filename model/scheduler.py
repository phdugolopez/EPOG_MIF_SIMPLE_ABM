"""One period: six steps, each computed for all firms from the state at the start of the step,
so the order of industry.firms never matters (plan, section 3)."""
from math import fsum

from equations.accounts_depreciation import depreciation
from equations.accounts_dividends import dividends
from equations.accounts_merit_order import dispatch
from equations.common_regulating_price import price_of_production, regulating_technique
from equations.common_unit_cost import unit_cost
from equations.entry_new_plant_rate import new_plant_rate
from equations.pricing_floor import price_floor
from equations.pricing_rule import posted_price
from equations.scrapping_below_cost import periods_below_cost, scrap_cost
from equations.scrapping_idle_plants import periods_idle
from equations.scrapping_retirement import retirement_reason
from markets.payments import pay
from markets.plant_market import remove_plant
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
    """Step 2, demand (A6). Reads prices, shares, D_t and plants; writes firm.share (notional),
    firm.notional, firm.sales, industry.lost and industry.excess. Stub of stage 2: shares stay
    as they are and a firm sells min(share x D, capacity) (stage 3b)."""
    for firm in industry.firms:
        firm.notional = firm.share * industry.demand
        firm.sales = min(firm.notional, firm.capacity)
    capacity = fsum(firm.capacity for firm in industry.firms)
    industry.lost = industry.demand - fsum(firm.sales for firm in industry.firms)
    industry.excess = max(0.0, industry.demand - capacity) / industry.demand


def produce_and_account(industry) -> None:
    """Step 3, production and accounts. Plants run cheapest first, then youngest, up to the
    firm's sales; every plant in operation ages and depreciates. The firm is paid its sales
    and pays its operating costs and dividends; profit is after depreciation, and retained
    profit joins the funds. Then the regulating price (A8) and r_new (A7, A10) are set, once a
    period and before any plant leaves, the same for every firm."""
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
    its owner's price below its scrap cost, or after as many periods without output. Its
    reserve is released or withdrawn by remove_plant, on the r_new of step 3."""
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
    """Step 5, technical change and investment (A7 to A9). Reads prices, reg_price, the public
    menu, firm.known, funds, cash, notional demand and capacity, and the firm's stream; writes
    firm.hurdle and firm.known, and calls buy_plant for each plant ordered.
    Stub of stage 2: no design is drawn and no plant is ordered (stage 3d)."""


def enter_and_exit(industry) -> None:
    """Step 6, entry and exit (A10). Reads shares, capacity in operation and on order, r_new,
    prices, the public menu and the industry's stream; exits first (remove_firm), then at most
    one entrant among the survivors (create_entrant). Stub of stage 2: nothing (stage 3b)."""


def check(industry) -> None:
    """Asserted every period: money is conserved, no firm's cash is negative, shares sum to 1,
    and next period's capacity is this period's less retirements and exits plus orders and
    entry."""
    t, firms = industry.time, industry.firms
    cash = industry.roe.cash + fsum(firm.cash for firm in firms)
    assert abs(cash) < 1e-6, f"t={t}: all cash sums to {cash}"
    assert all(firm.cash > -1e-6 for firm in firms), f"t={t}: a firm's cash is negative"
    shares = fsum(firm.share for firm in firms)
    assert abs(shares - 1.0) < 1e-9, f"t={t}: shares sum to {shares}"
    planned = fsum(row["capacity_next"] for row in industry.rows[-len(LABELS):])
    actual = fsum(q.capacity for firm in firms for q in firm.plants + firm.pending_plants)
    assert abs(planned - actual) < 1e-6, f"t={t}: capacity {actual} against {planned} planned"
