from equations.anchor_price import markup_price, target_return_price
from equations.competitiveness import competitiveness
from equations.depreciation import depreciation
from equations.desired_capacity import desired_capacity
from equations.market_shares import logit_shares, replicator_shares
from equations.offered_capacity import offered_capacity
from equations.dividends import dividends
from equations.firm_profit import firm_profit
from equations.hurdle import hurdle
from equations.lifetime_profit_rate import lifetime_profit_rate
from equations.interest_payment import interest_payment
from equations.investment import investment
from equations.merit_order import dispatch
from equations.operating_cost import operating_cost
from equations.plant_profit import plant_profit
from equations.posted_price import posted_price
from equations.price_floor import price_floor
from equations.price_war import price_war
from equations.profit_rate import profit_rate
from equations.replacement import replacement_pays
from equations.retirement import periods_below_cost, retirement_reason
from equations.technique_choice import choose_technique
from equations.unit_cost import unit_cost
from markets.credit_market import settle_cash_position
from markets.goods_market import allocate
from markets.payments import pay
from markets.plant_market import affordable_spending, buy_plant
from model.collector import check_stock_flow, collect


def run_period(industry) -> None:
    """Order all events in one period. Each step sees only what earlier steps produced."""
    start_period(industry)
    set_prices(industry)  # 1. Pricing
    allocate_demand(industry)  # 2. Demand
    produce_and_account(industry)  # 3. Production and accounts
    scrap_plants(industry)  # 4. Scrapping
    invest(industry)  # 5. Investment
    collect(industry)
    check_stock_flow(industry)


def start_period(industry) -> None:
    """Plants bought last period arrive; flows are reset; net worth is recorded."""
    industry.flows = {}
    industry.retired = []
    industry.entries = []
    industry.exits = []
    industry.replacements = 0
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
    industry.cash_start = {
        "firms": sum(f.cash for f in industry.firms),
        "roe": industry.roe.cash,
    }


# --- 1. Pricing ---------------------------------------------------------------------


def set_prices(industry) -> None:
    """Firms post p_i from last period's prices, utilisation and leader."""
    config = industry.parameters
    for firm in industry.firms:
        if not firm.plants:
            continue
        weights = [p.capacity for p in firm.plants]
        uc = _average([unit_cost(p.ucs, p.kappa, config.DELTA) for p in firm.plants], weights)
        kappa = _average([p.kappa for p in firm.plants], weights)
        if config.PRICING_ANCHOR == "markup":
            anchor = markup_price(uc, config.MARKUP)
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
    # The leader for next period: this period's lowest posted price.
    industry.leader_price = min(f.price for f in industry.firms)


def _average(values: list[float], weights: list[float]) -> float:
    return sum(v * w for v, w in zip(values, weights)) / sum(weights)


# --- 2. Demand ----------------------------------------------------------------------


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


# --- 3. Production and accounts -----------------------------------------------------


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

    pay(industry, roe, firm, firm.revenue, "sales")
    pay(industry, firm, roe, firm.operating_cost, "wages and materials")
    pay(industry, firm, roe, firm.interest, "interest")
    pay(industry, firm, roe, firm.dividends, "dividends")
    settle_cash_position(industry, firm)


# --- 4. Scrapping -------------------------------------------------------------------


def scrap_plants(industry) -> None:
    """Retire by age or obsolescence (both types alike), then replace with the hurdle."""
    config = industry.parameters
    for firm in industry.firms:
        firm.hurdle = hurdle(
            config.HURDLE_RULES[firm.type], firm.price, industry.menu, config.DELTA,
            config.HURDLE_FLOOR_AT_ZERO,
        )
        retired = retire_plants(industry, firm, config)
        if config.REPLACEMENT:
            replace_plants(industry, firm, config)
        if retired and not firm.plants and not firm.pending_plants:
            firm.non_renewal = fails_renewal(retired, config.RBAR)


def retire_plants(industry, firm, config) -> list:
    retired = []
    for plant in list(firm.plants):
        plant.periods_below_cost = periods_below_cost(
            plant.periods_below_cost, firm.price, plant.ucs
        )
        reason = retirement_reason(
            plant.age, config.PLANT_LIFE, plant.periods_below_cost,
            config.OBSOLESCENCE_PERIODS,
        )
        if reason:
            remove_plant(industry, firm, plant)
            retired.append(plant)
    return retired


def replace_plants(industry, firm, config) -> None:
    """Scrap a working plant when a new technique is cheap enough to justify new capital,
    if the firm can pay for it (cash, then debt up to the cap)."""
    technique = choose_technique(industry.menu, firm.hurdle, config.DELTA, config.TAU)
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


# --- 5. Investment ------------------------------------------------------------------


def invest(industry) -> None:
    """Expected sales, desired capacity, technique chosen with h, cash then capped debt.
    New plants arrive next period."""
    config = industry.parameters
    for firm in industry.firms:
        if firm.non_renewal:
            continue
        expected_sales = firm.previous_sales if config.INVESTMENT_SALES_LAG else firm.sales
        on_order = sum(p.capacity for p in firm.pending_plants)
        units = investment(
            desired_capacity(expected_sales, config.EXPECTED_GROWTH),
            firm.capacity + on_order,
        )
        if units <= 0.0:
            continue
        technique = choose_technique(industry.menu, firm.hurdle, config.DELTA, config.TAU)
        affordable = affordable_spending(firm, config.DEBT_CAP) / technique.kappa
        buy_plant(industry, firm, technique, min(units, affordable))
