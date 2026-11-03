from equations.anchor_price import markup_price, target_return_price
from equations.competitiveness import competitiveness
from equations.depreciation import depreciation
from equations.market_shares import logit_shares, replicator_shares
from equations.offered_capacity import offered_capacity
from equations.dividends import dividends
from equations.firm_profit import firm_profit
from equations.interest_payment import interest_payment
from equations.merit_order import dispatch
from equations.operating_cost import operating_cost
from equations.plant_profit import plant_profit
from equations.posted_price import posted_price
from equations.price_floor import price_floor
from equations.price_war import price_war
from equations.profit_rate import profit_rate
from equations.unit_cost import unit_cost
from markets.credit_market import settle_cash_position
from markets.goods_market import allocate
from markets.payments import pay
from model.collector import check_stock_flow, collect


def run_period(industry) -> None:
    """Order all events in one period. Each step sees only what earlier steps produced."""
    start_period(industry)
    set_prices(industry)  # 1. Pricing
    allocate_demand(industry)  # 2. Demand
    produce_and_account(industry)  # 3. Production and accounts
    collect(industry)
    check_stock_flow(industry)


def start_period(industry) -> None:
    """Plants bought last period arrive; flows are reset; net worth is recorded."""
    industry.flows = {}
    industry.retired = []
    industry.entries = []
    industry.exits = []
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
