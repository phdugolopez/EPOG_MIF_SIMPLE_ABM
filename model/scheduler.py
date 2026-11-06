from equations.anchor_price import leader_anchor, markup_price, target_return_price
from equations.competitiveness import competitiveness
from equations.depreciation import depreciation
from equations.desired_capacity import desired_capacity
from equations.market_shares import logit_shares, replicator_shares
from equations.new_plant_rate import new_plant_rate
from equations.offered_capacity import offered_capacity
from equations.dividends import dividends
from equations.entrant_price import entrant_price
from equations.entry_probability import entry_probability
from equations.exit_conditions import exit_reason
from equations.firm_profit import firm_profit
from equations.hurdle import hurdle
from equations.inherited_rule import inherited_type
from equations.lifetime_profit_rate import lifetime_profit_rate
from equations.interest_payment import interest_payment
from equations.investment import investment
from equations.merit_order import dispatch
from equations.operating_cost import operating_cost
from equations.plant_profit import plant_profit
from equations.posted_price import posted_price
from equations.price_floor import price_floor
from equations.price_war import price_war
from equations.real_competition_price import real_competition_price
from equations.profit_rate import profit_rate
from equations.replacement import replacement_pays
from equations.retirement import periods_below_cost, retirement_reason, scrap_cost
from equations.plant_number import plant_number
from equations.idle_plants import idle_plants
from equations.new_technique import design_category, draw_design
from equations.retained_earnings_investment import retained_earnings_investment
from equations.technique_choice import choose_technique
from equations.unit_cost import unit_cost
from markets.credit_market import settle_cash_position
from markets.entry_exit import create_entrant, remove_firm
from markets.goods_market import allocate
from markets.payments import pay
from markets.plant_market import affordable_spending, buy_plant
from model.collector import check_stock_flow, collect
from model.entities import Technique

# Lines "# {name}" ... "# {endname}" mark the ranges that docs/sections/*.tex include.


# {period}
def run_period(industry) -> None:
    """Order all events in one period. Each step sees only what earlier steps produced."""
    start_period(industry)
    set_prices(industry)  # 1. Pricing
    allocate_demand(industry)  # 2. Demand
    produce_and_account(industry)  # 3. Production and accounts
    scrap_plants(industry)  # 4. Scrapping
    invest(industry)  # 5. Investment
    enter_and_exit(industry)  # 6. Entry and exit
    collect(industry)
    check_stock_flow(industry)
# {endperiod}


def start_period(industry) -> None:
    """Plants bought last period arrive; flows are reset; net worth is recorded."""
    industry.flows = {}
    industry.retired = []
    industry.entries = []
    industry.exits = []
    industry.replacements = 0
    industry.r_new = None
    industry.producers = list(industry.firms)
    for firm in industry.firms:
        firm.plants.extend(firm.pending_plants)
        firm.pending_plants = []
        firm.previous_sales = firm.sales
        for name in (
            "sales", "unmet", "revenue", "operating_cost", "depreciation", "interest",
            "profit", "dividends", "write_offs", "investment", "equity_in",
        ):
            setattr(firm, name, 0.0)
        firm.non_renewal = False
        firm.net_worth_start = firm.net_worth
        firm.producing_plants = list(firm.plants)
    industry.cash_start = {
        "firms": sum(f.cash for f in industry.firms),
        "roe": industry.roe.cash,
    }


# --- 1. Pricing ---------------------------------------------------------------------
# {pricing}


def set_prices(industry) -> None:
    """Firms post p_i from last period's prices, costs, utilisation and excess demand."""
    if industry.parameters.PRICING_RULE == "anchor":
        _anchor_prices(industry)
    else:
        _real_competition_prices(industry)
    # The leader for next period: this period's lowest posted price.
    industry.leader_price = min(f.price for f in industry.firms)


def _real_competition_prices(industry) -> None:
    """Follow the lowest price; undercut it only with spare capacity and a cost edge;
    raise prices after excess demand. No anchor, no war trigger."""
    config = industry.parameters
    active = [f for f in industry.firms if f.plants]
    previous = {f.firm_id: f.price for f in active}  # all firms post at once
    best_uc = {
        f.firm_id: min(unit_cost(p.ucs, p.kappa, config.DELTA) for p in f.plants)
        for f in active
    }
    # Last period: demand = sales + unserved; normal capacity = sales / utilisation.
    last_demand = sum(f.previous_sales for f in industry.firms) + industry.unserved
    if config.EXCESS_DEMAND == "unserved":
        excess = industry.unserved  # demand beyond all output, overtime included
    else:
        last_capacity = sum(
            f.previous_sales / f.util_history[-1]
            if f.util_history and f.util_history[-1] > 0.0 else f.capacity
            for f in industry.firms
        )
        excess = max(0.0, last_demand - last_capacity)  # demand beyond normal capacity
    excess_share = excess / last_demand if last_demand > 0.0 else 0.0
    for firm in active:
        rivals = [f.firm_id for f in active if f.firm_id != firm.firm_id]
        if config.PRICE_FLOOR == "operating_cost":
            floor = price_floor(
                [p.ucs for p in firm.plants],
                [p.capacity for p in firm.plants],
                firm.previous_sales,
                config.U_MAX,
                config.OVERTIME_PREMIUM,
            )
        else:
            floor = best_uc[firm.firm_id]
        util = firm.util_history[-1] if firm.util_history else firm.previous_sales / firm.capacity
        spare = util < config.U_FULL - 1e-9
        firm.price, firm.at_war = real_competition_price(
            previous[firm.firm_id],
            [previous[j] for j in rivals],
            [best_uc[j] for j in rivals],
            best_uc[firm.firm_id],
            floor,
            spare,
            excess_share,
            config.PRICE_CUT,
            config.SHORTAGE_RESPONSE,
        )


def _anchor_prices(industry) -> None:
    """Version 1: move toward an anchor within a band of the leader; cut after a run of
    low utilisation (PRICING_RULE = "anchor")."""
    config = industry.parameters
    active = [f for f in industry.firms if f.plants]
    previous = {f.firm_id: f.price for f in industry.firms}
    averages = {}
    for firm in active:
        weights = [p.capacity for p in firm.plants]
        uc = _average([unit_cost(p.ucs, p.kappa, config.DELTA) for p in firm.plants], weights)
        kappa = _average([p.kappa for p in firm.plants], weights)
        averages[firm.firm_id] = (uc, kappa)
    if config.PRICING_ANCHOR == "leader" and active:
        common_anchor = leader_anchor(
            [target_return_price(*averages[f.firm_id], config.RBAR) for f in active],
            [previous[f.firm_id] for f in active],
        )
    for firm in active:
        uc, kappa = averages[firm.firm_id]
        weights = [p.capacity for p in firm.plants]
        if config.PRICING_ANCHOR == "markup":
            anchor = markup_price(uc, config.MARKUP)
        elif config.PRICING_ANCHOR == "leader":
            anchor = common_anchor
        else:
            anchor = target_return_price(uc, kappa, config.RBAR)
        floor = price_floor(
            [p.ucs for p in firm.plants],
            weights,
            firm.previous_sales,
            config.U_MAX,
            config.OVERTIME_PREMIUM,
        )
        firm.at_war = price_war(firm.util_history, config.WAR_PERIODS, config.U_WAR)
        firm.price = posted_price(
            firm.price, anchor, industry.leader_price, floor, firm.at_war,
            config.PRICE_SPEED, config.PRICE_BAND, config.PRICE_CUT,
        )


def _average(values: list[float], weights: list[float]) -> float:
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)
# {endpricing}


# --- 2. Demand ----------------------------------------------------------------------
# {demand}


def allocate_demand(industry) -> None:
    """Shares from prices, demand allocated within capacity, sales and utilisation."""
    config = industry.parameters
    firms = industry.firms
    prices = [f.price for f in firms]
    previous = [f.share for f in firms]
    if config.DEMAND_FORM == "logit":
        shares = logit_shares(previous, prices, config.ETA)
    else:
        shares = replicator_shares(
            previous, [competitiveness(p) for p in prices], config.CHI
        )
    offered = [
        offered_capacity(
            [p.ucs for p in f.plants],
            [p.capacity for p in f.plants],
            f.price,
            config.U_MAX,
            config.OVERTIME_PREMIUM,
        )
        for f in firms
    ]
    sales, unmet, industry.unserved = allocate(industry.demand(), shares, prices, offered)
    for firm, share, x, lost in zip(firms, shares, sales, unmet):
        firm.share = share
        firm.sales = x
        firm.unmet = lost
        firm.util = x / firm.capacity if firm.capacity > 0.0 else 0.0
        firm.util_history.append(firm.util)
# {enddemand}


# --- 3. Production and accounts -----------------------------------------------------
# {accounts}


def produce_and_account(industry) -> None:
    config = industry.parameters
    for firm in industry.firms:
        produce(firm, config)
        account(industry, firm, config)


def produce(firm, config) -> None:
    """Produce to order: plants run in merit order, lowest operating cost first."""
    ucs = [p.ucs for p in firm.plants]
    normal, overtime = dispatch(
        ucs,
        [p.capacity for p in firm.plants],
        firm.sales,
        config.U_MAX,
        config.OVERTIME_PREMIUM,
    )
    for plant, n, o in zip(firm.plants, normal, overtime):
        plant.output = n + o
        plant.overtime_output = o
    firm.operating_cost = operating_cost(ucs, normal, overtime, config.OVERTIME_PREMIUM)


def account(industry, firm, config) -> None:
    """Profit, dividends and cash; book values fall by depreciation."""
    roe = industry.roe
    firm.revenue = firm.price * firm.sales
    firm.interest = interest_payment(firm.debt, config.RHO)
    for plant in firm.plants:
        dep = depreciation(plant.kappa, plant.capacity, config.DELTA, plant.book_value)
        plant.book_value -= dep
        firm.depreciation += dep
        plant.profit = plant_profit(
            firm.price, plant.ucs, plant.output, plant.overtime_output,
            config.OVERTIME_PREMIUM, dep,
        )
        plant.lifetime_profit += plant.profit
        plant.age += 1
    firm.profit = firm_profit(
        firm.revenue, firm.operating_cost, firm.depreciation, firm.interest
    )
    firm.profit_rate = profit_rate(firm.profit, firm.capital)
    firm.dividends = dividends(firm.profit, config.PAYOUT)
    firm.retained_earnings += firm.profit - firm.dividends

    pay(industry, roe, firm, firm.revenue, "sales")
    pay(industry, firm, roe, firm.operating_cost, "wages and materials")
    pay(industry, firm, roe, firm.interest, "interest")
    pay(industry, firm, roe, firm.dividends, "dividends")
    settle_cash_position(industry, firm)
# {endaccounts}


# --- 4. Scrapping -------------------------------------------------------------------
# {scrapping}


def scrap_plants(industry) -> None:
    """Retire by age or obsolescence (both types alike), then replace with the hurdle."""
    config = industry.parameters
    for firm in industry.firms:
        firm.hurdle = hurdle(
            config.HURDLE_RULES[firm.type], firm.price, firm.known or industry.menu,
            config.DELTA, config.HURDLE_FLOOR_AT_ZERO,
        )
        retired = retire_plants(industry, firm, config)
        if config.REPLACEMENT:
            replace_plants(industry, firm, config)
        if retired and not firm.plants and not firm.pending_plants:
            firm.non_renewal = fails_renewal(retired, config.RBAR)


def retire_plants(industry, firm, config) -> list:
    retired = []
    idle = idle_plants(
        [p.ucs for p in firm.plants], [p.vintage for p in firm.plants],
        [p.capacity for p in firm.plants], firm.sales,
    )
    for plant, is_idle in zip(list(firm.plants), idle):
        plant.periods_below_cost = periods_below_cost(
            plant.periods_below_cost, firm.price,
            scrap_cost(plant.ucs, plant.kappa, config.DELTA, config.SCRAP_COST),
        )
        plant.periods_idle = plant.periods_idle + 1 if is_idle else 0
        reason = retirement_reason(
            plant.age, config.PLANT_LIFE, plant.periods_below_cost,
            config.OBSOLESCENCE_PERIODS, plant.periods_idle,
            config.IDLE_PERIODS if config.IDLE_SCRAPPING else None,
        )
        if reason:
            remove_plant(industry, firm, plant)
            retired.append(plant)
    return retired


def replace_plants(industry, firm, config) -> None:
    """Scrap a working plant when a new technique is cheap enough to justify new capital,
    if the firm can pay for it (cash, then debt up to the cap)."""
    technique = choose_technique(
        firm.known or industry.menu, firm.hurdle, config.DELTA, config.TAU
    )
    for plant in list(firm.plants):
        if not replacement_pays(
            plant.ucs, technique.ucs, technique.kappa, config.DELTA, firm.hurdle
        ):
            continue
        if technique.kappa * plant.capacity > affordable_spending(firm, config.DEBT_CAP):
            continue
        remove_plant(industry, firm, plant)
        buy_plant(industry, firm, technique, plant.capacity)
        industry.replacements += 1


def remove_plant(industry, firm, plant) -> None:
    """Scrap value is zero: any remaining book value is written off."""
    firm.write_offs += plant.book_value
    plant.book_value = 0.0
    firm.plants.remove(plant)
    industry.retired.append(plant)


def fails_renewal(retired, rbar: float) -> bool:
    """A firm whose last plant retires does not rebuild if that capital earned less than
    rbar over its life. Plants of the initial endowment are exempt (no full record)."""
    record = [p for p in retired if not p.initial]
    if not record:
        return False
    profit = sum(p.lifetime_profit for p in record)
    capital_periods = sum(p.purchase_cost * p.age for p in record)
    return lifetime_profit_rate(profit, capital_periods) < rbar
# {endscrapping}


# --- 5. Investment ------------------------------------------------------------------
# {investment}


def invest(industry) -> None:
    """Expected sales, desired capacity, technique chosen with h, cash then capped debt.
    Or (INVESTMENT_RULE = "retained_earnings") whatever retained earnings pay for, whatever
    the demand. With PLANT_SIZE, plants come whole. New plants arrive next period."""
    config = industry.parameters
    size = config.PLANT_SIZE
    for firm in industry.firms:
        if firm.non_renewal:
            continue
        if config.INVESTMENT_RULE == "retained_earnings":
            funds = min(firm.retained_earnings, firm.cash)  # earned, and still in cash
            reference = choose_technique(
                firm.known or industry.menu, firm.hurdle, config.DELTA, config.TAU
            )
            if retained_earnings_investment(funds, reference.kappa, size) <= 0.0:
                continue
            technique = _technique_to_build(industry, firm, config)
            units = retained_earnings_investment(funds, technique.kappa, size)
            if units > 0.0:
                _buy_capacity(industry, firm, technique, units, size)
                firm.retained_earnings -= technique.kappa * units
            continue
        expected_sales = firm.previous_sales if config.INVESTMENT_SALES_LAG else firm.sales
        on_order = sum(p.capacity for p in firm.pending_plants)
        units = investment(
            desired_capacity(expected_sales, config.EXPECTED_GROWTH),
            firm.capacity + on_order,
        )
        if units <= 0.0:
            continue
        technique = _technique_to_build(industry, firm, config)
        affordable = affordable_spending(firm, config.DEBT_CAP) / technique.kappa
        if size is None:
            buy_plant(industry, firm, technique, min(units, affordable))
        else:  # enough whole plants to cover the gap, as many as can be financed
            n = min(plant_number(units, size, "up"), int(affordable / size + 1e-9))
            _buy_capacity(industry, firm, technique, n * size, size)


def _technique_to_build(industry, firm, config):
    """The firm's best known technique under its hurdle; with TECH_DRAWS it is first offered
    a new design, which it adopts (and keeps knowing) if its hurdle prefers it."""
    reference = choose_technique(
        firm.known or industry.menu, firm.hurdle, config.DELTA, config.TAU
    )
    if not config.TECH_DRAWS:
        return reference
    rng = industry.rng
    category = design_category(rng.random(), config.TECH_CONFLICT)
    ucs, kappa = draw_design(
        reference.ucs, reference.kappa, config.DELTA, firm.price, category,
        1.0 - rng.random(), rng.random(), config.TECH_STEP,
    )
    industry.next_design += 1
    design = Technique(name=f"T{industry.next_design}", ucs=ucs, kappa=kappa)
    chosen = choose_technique([reference, design], firm.hurdle, config.DELTA, config.TAU)
    adopted = chosen is design
    industry.draw_log.append((industry.time, firm.firm_id, category, adopted))
    if adopted:
        firm.known.append(design)
    return chosen


def _buy_capacity(industry, firm, technique, units: float, size: float | None) -> None:
    if size is None:
        buy_plant(industry, firm, technique, units)
        return
    for _ in range(round(units / size)):
        buy_plant(industry, firm, technique, size)
# {endinvestment}


# --- 6. Entry and exit --------------------------------------------------------------
# {entry}


def enter_and_exit(industry) -> None:
    exit_firms(industry)
    enter_firm(industry)


def exit_firms(industry) -> None:
    """Exit on negative net worth, a share below f_min, or non-renewal, keeping at least
    MIN_FIRMS firms (those with the highest net worth stay)."""
    config = industry.parameters
    leaving = []
    for firm in industry.firms:
        reason = exit_reason(
            firm.net_worth, firm.share, config.MIN_SHARE, firm.non_renewal,
            bool(firm.plants or firm.pending_plants),
        )
        if reason:
            leaving.append((firm, reason))
    spare = len(industry.firms) - config.MIN_FIRMS
    if len(leaving) > spare:
        leaving.sort(key=lambda fr: (fr[0].net_worth, industry.rng.random()))
        leaving = leaving[: max(0, spare)]
    for firm, reason in leaving:
        remove_firm(industry, firm, reason)


def enter_firm(industry) -> None:
    """At most one entrant, with a probability rising with r^new - rbar. It inherits a rule,
    picks its plant with its own h at its own price, and arrives next period."""
    config = industry.parameters
    recent = [
        p for f in industry.firms for p in f.plants
        if p.vintage > industry.time - config.ENTRY_WINDOW
    ]
    industry.r_new = new_plant_rate(
        [p.profit / p.purchase_cost for p in recent], [p.capacity for p in recent]
    )
    probability = entry_probability(industry.r_new, config.RBAR, config.ENTRY_SPEED)
    if probability > 0.0 and industry.rng.random() < probability:
        admit_entrant(industry)


def admit_entrant(industry) -> None:
    config = industry.parameters
    firm_type = inherited_type(
        [f.type for f in industry.firms], [f.share for f in industry.firms],
        config.MUTATION, industry.rng,
    )
    # Under real-competition pricing an entrant has no price history: it starts at the lowest
    # price posted this period and from its first period of production prices by the same
    # rule as every other firm. Under the anchor rule it undercuts the leader (version 1).
    undercut = config.ENTRANT_UNDERCUT if config.PRICING_RULE == "anchor" else 0.0
    price = entrant_price(industry.leader_price, undercut)
    known = list(industry.menu)
    if config.TECH_DRAWS:  # an entrant can build any technique in use
        names = {t.name for t in known}
        for f in industry.firms:
            for p in f.plants:
                if p.technique not in names:
                    names.add(p.technique)
                    known.append(Technique(name=p.technique, ucs=p.ucs, kappa=p.kappa))
    h = hurdle(config.HURDLE_RULES[firm_type], price, known, config.DELTA,
               config.HURDLE_FLOOR_AT_ZERO)
    technique = choose_technique(known, h, config.DELTA, config.TAU)
    capacities = [f.capacity for f in industry.firms if f.capacity > 0.0]
    if not capacities:
        return
    capacity = config.ENTRANT_SIZE * sum(capacities) / len(capacities)
    if config.PLANT_SIZE is not None:
        capacity = config.PLANT_SIZE * plant_number(capacity, config.PLANT_SIZE)
    entrant = create_entrant(industry, firm_type, price, technique, capacity, config.PLANT_SIZE)
    entrant.hurdle = h
    entrant.known = known
# {endentry}
