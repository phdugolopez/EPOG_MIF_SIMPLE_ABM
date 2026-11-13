"""The run viewer: one industry, one seed, and what explains the run (v4-plan.md, section 10).

    python3 -m experiments.show_run --seed 7 pricing=universal rbar=0.05 population=all_unit_cost

Any parameter is given as name=value and converted by the type of its field in Parameters;
population is mixed (default), all_unit_cost or all_profit_rate. --firms draws one line a
firm in the price and selection panels, --name names the output folder, --no-figure writes
the tables alone. The files go to outputs/runs/<name>/: periods.csv (the period table),
firms.csv (one row per firm and period), prices.csv (how the prices vary, one row a period),
run.csv (the run row), run.txt (the read-out) and run.pdf, run.png (the figure, where
matplotlib is installed).

The viewer steps the model itself: model.build, then the functions of scheduler.STEPS in
order and close_period, period after period. It reads the firms after steps 3, 5 and 6, so
it sees a firm before it leaves and a share before and after entry. The model has no
recorder for it: its period table is that of model.run for the same parameters and seed.
"""
import argparse
import pathlib
import types
from dataclasses import fields, replace
from math import ceil, fsum, isclose, log, nan, sqrt

from experiments.harness import write_csv
from experiments.populations import POPULATIONS
from experiments.summary import (E0_CAPACITY_BAND, E0_CROSSINGS_MIN, E0_LEADER_MIN,
                                 E0_LOST_MAX, E0_PRICE_BAND, E0_R_NEW_BAND, E0_START, run_row)
from model.model import build
from model.outputs import KEYS, sum_flows
from model.scheduler import (STEPS, close_period, enter_and_exit, invest, plant_unit_cost,
                             produce_and_account, read_quote)
from parameters import Parameters

FOLDER = pathlib.Path("outputs") / "runs"
STATE = ("t", "firm", "label", "rule", "born", "entered", "left", "price", "floor",
         "unit_cost", "kappa", "plants", "capacity", "sales", "util", "profit", "share",
         "hurdle", "cash", "funds", "on_order", "capital_in", "result")
FIRM_COLUMNS = STATE + KEYS + ("share_end",)
PRICE_COLUMNS = ("t", "priced", "price", "price_over_reg", "low", "high", "mean", "sd", "cv",
                 "spread", "change", "war")


def convert(name: str, text: str):
    """A value given on the command line, as the type of the parameter's field."""
    types_of = {field.name: field.type for field in fields(Parameters)}
    if name not in types_of:
        raise ValueError(f"{name} is not a parameter")
    kind = types_of[name]
    if isinstance(kind, types.UnionType):       # int | None: the lag before a design is public
        return None if text.lower() == "none" else int(text)
    if kind not in (int, float, str):
        raise ValueError(f"{name} cannot be set from the command line")
    return kind(text)


def read_settings(pairs: list[str]) -> tuple[dict, str]:
    """The overrides and the population that a list of name=value gives."""
    overrides = {}
    population = "mixed"
    for pair in pairs:
        name, separator, text = pair.partition("=")
        if not separator:
            raise ValueError(f"{pair}: expected name=value")
        if name == "population":
            if text not in POPULATIONS:
                raise ValueError(f"population = {text}: expected one of {', '.join(POPULATIONS)}")
            population = text
        else:
            overrides[name] = convert(name, text)
    return overrides, population


def run_name(pairs: list[str], seed: int) -> str:
    """The name of the output folder: the settings as they were given, and the seed."""
    return "_".join(sorted(pairs) or ["defaults"]) + f"_seed_{seed}"


def after_production(industry, firm) -> dict:
    """What the viewer reads about a firm after step 3: the values the period table reads."""
    p = industry.params
    row = dict.fromkeys(FIRM_COLUMNS)
    row.update(t=industry.time, firm=firm.id, label=firm.label, rule=firm.rule, born=firm.born,
               entered=0, left=0, price=firm.price, plants=len(firm.plants),
               capacity=firm.capacity, sales=firm.sales, util=firm.util, profit=firm.profit,
               share=firm.share, capital_in=firm.capital_in,
               result=firm.result - firm.write_offs)
    if firm.plants:
        # The best plant has the lowest unit cost; a tie goes to the lower capital per unit.
        best = min(firm.plants, key=lambda plant: (plant_unit_cost(plant, p),
                                                   plant.technique.kappa))
        row.update(floor=read_quote(firm, p).floor, unit_cost=plant_unit_cost(best, p),
                   kappa=best.technique.kappa)
    return row


def trace(params: Parameters, seed: int):
    """One run, stepped by hand. Returns the industry, whose rows are the period table, and
    the rows of the firms: one per firm and period, a firm that left in its last period and
    an entrant in its first included."""
    industry = build(params, seed)
    firm_rows = []
    for _ in range(params.periods):
        rows = {}
        for step in STEPS:
            step(industry)
            if step is produce_and_account:
                for firm in industry.firms:
                    rows[firm.id] = after_production(industry, firm)
            if step is invest:
                # Before a firm can leave: its hurdle and its money after its orders.
                for firm in industry.firms:
                    on_order = fsum(plant.capacity for plant in firm.pending_plants)
                    rows[firm.id].update(hurdle=firm.hurdle, cash=firm.cash, funds=firm.funds,
                                         on_order=on_order)
            if step is enter_and_exit:
                staying = {firm.id: firm for firm in industry.firms}
                for number, row in rows.items():
                    row["left"] = int(number not in staying)
                for number, firm in staying.items():
                    if number not in rows:
                        # The entrant of the period: it has no plant in operation yet.
                        rows[number] = after_production(industry, firm)
                        on_order = fsum(plant.capacity for plant in firm.pending_plants)
                        rows[number].update(entered=1, hurdle=firm.hurdle, cash=firm.cash,
                                            funds=firm.funds, on_order=on_order)
                    rows[number]["share_end"] = firm.share
        # The flows of each firm, read in the tally: a firm that left is still in it.
        for number, row in rows.items():
            row.update(sum_flows([flow for flow in industry.tally if flow.firm_id == number]))
        close_period(industry)
        firm_rows += [rows[number] for number in sorted(rows)]
    return industry, firm_rows


def price_spread(period_rows: list[dict], firm_rows: list[dict]) -> list[dict]:
    """How the prices vary, one row a period. Across firms: the posted prices of the firms
    with a plant in operation, their lowest, highest, mean, standard deviation, coefficient of
    variation, and the spread (highest less lowest) over the price of production. Over time:
    the log change of the industry price (weighted by sales) since the period before, and
    whether a firm cut its price."""
    rows = []
    before = None
    # One period row a period: the industry columns are the same on both labels' rows.
    industry = [row for row in period_rows if row["label"] == "shaikh"]
    for period in industry:
        t = period["t"]
        # The firms that post a price at step 3: those with a plant in operation.
        prices = [row["price"] for row in firm_rows
                  if row["t"] == t and row["plants"] > 0 and not row["entered"]]
        row = dict.fromkeys(PRICE_COLUMNS)
        row.update(t=t, priced=len(prices), price_over_reg=period["price_over_reg"],
                   war=period["war"])
        if period["price_over_reg"] is not None:
            row["price"] = period["price_over_reg"] * period["reg_price"]
        if prices:
            mean = fsum(prices) / len(prices)
            sd = sqrt(fsum((price - mean) ** 2 for price in prices) / len(prices))
            row.update(low=min(prices), high=max(prices), mean=mean, sd=sd, cv=sd / mean,
                       spread=(max(prices) - min(prices)) / period["reg_price"])
        if before is not None and row["price"] is not None:
            row["change"] = log(row["price"] / before)
        before = row["price"]
        rows.append(row)
    return rows


def price_read_out(rows: list[dict], start: int) -> list[str]:
    """The lines of the read-out on the variability of prices, from period `start` on."""
    # The periods after the start, and the values of each measure that are defined there.
    kept = [row for row in rows if row["t"] >= start]
    cv = [row["cv"] for row in kept if row["cv"] is not None]
    spread = [row["spread"] for row in kept if row["spread"] is not None]
    level = [row["price_over_reg"] for row in kept if row["price_over_reg"] is not None]
    change = [row["change"] for row in kept if row["change"] is not None]
    if not (cv and level and change):
        return [f"Prices from period {start}: too few periods to measure their variability"]
    mean_level = fsum(level) / len(level)
    sd_level = sqrt(fsum((value - mean_level) ** 2 for value in level) / len(level))
    mean_change = fsum(change) / len(change)
    sd_change = sqrt(fsum((value - mean_change) ** 2 for value in change) / len(change))
    wars = fsum(row["war"] for row in kept) / len(kept)
    return [f"Variability of prices, periods {start} to {rows[-1]['t']}:",
            f"  across firms: coefficient of variation {show(fsum(cv) / len(cv))} on average "
            f"(highest {show(max(cv))}); spread of posted prices over the price of "
            f"production {show(fsum(spread) / len(spread))} on average "
            f"(widest {show(max(spread))})",
            f"  over time: price over the price of production {show(mean_level)} on average, "
            f"standard deviation {show(sd_level)}, from {show(min(level))} to "
            f"{show(max(level))}",
            f"  change of the industry price a period: mean absolute "
            f"{show(fsum(abs(value) for value in change) / len(change))}, standard deviation "
            f"{show(sd_change)}, largest fall {show(min(change))}, largest rise "
            f"{show(max(change))} (log changes)",
            f"  periods in which a firm cuts its price: {show(wars, 2)} of the periods"]


def show(value, digits: int = 3) -> str:
    """A number of the read-out; a dash when it is not defined."""
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, int):
        return str(value)
    return f"{value:.{digits}f}"


def read_out(row: dict, params: Parameters, title: str, prices: list[dict] = ()) -> str:
    """The text read-out of a run: outcome, final shares, the lines of E0 with their
    thresholds, the two decompositions of the change in the unit-cost label's share, and the
    variability of prices when their rows are given."""
    rbar = params.rbar
    lines = [
        ("the lowest-cost firm leads the price", "leader", f"at least {E0_LEADER_MIN}"),
        ("price over the price of production", "price",
         f"{E0_PRICE_BAND[0]} to {E0_PRICE_BAND[1]}"),
        ("times it crosses 1", "crossings", f"at least {E0_CROSSINGS_MIN}"),
        ("capacity over demand", "capacity", f"{E0_CAPACITY_BAND[0]} to {E0_CAPACITY_BAND[1]}"),
        ("rate of new plants", "r_new",
         f"{E0_R_NEW_BAND[0] * rbar:.3f} to {E0_R_NEW_BAND[1] * rbar:.3f}"),
        ("demand lost", "lost", f"at most {E0_LOST_MAX}"),
        ("capacity at the last period above 0", "alive", "yes"),
    ]
    text = [title, "",
            f"Outcome for the unit-cost label: {row['outcome']}",
            f"Final capacity share of the unit-cost label: {show(row['cap_share_end'])}",
            f"Final sales share: {show(row['sales_share_end'])}",
            f"Capacity over demand at the end: {show(row['capacity_over_demand'])}",
            f"Firms at the end: {row['firms_end']:.0f} ({row['entries']:.0f} entries, "
            f"{row['exits']:.0f} exits)",
            f"Demand lost over the run: {show(row['lost_share'])}; output above normal "
            f"capacity: {show(row['overtime_share'])}",
            f"Realised rates, unit-cost and profit-rate label: {show(row['rate_shaikh'])} and "
            f"{show(row['rate_okishio'])}",
            "",
            f"E0, on periods {E0_START} to {params.periods - 1} (a gate only without draws "
            f"and with one rule):"]
    for label, line, threshold in lines:
        passed = row["e0_alive"] if line == "alive" else row[f"e0_{line}_ok"]
        verdict = "passes" if passed else "fails"
        text.append(f"  {label:38s} {show(row['e0_' + line]):>7s}   {threshold:16s} {verdict}")
    text += [f"  every line: {'passes' if row['e0_pass'] else 'fails'}",
             f"  reported: industry rate {show(row['e0_rate_industry'])}, spread of rates "
             f"{show(row['e0_rate_spread'])}, capacity over demand between "
             f"{show(row['e0_capacity_min'], 2)} and {show(row['e0_capacity_max'], 2)}, "
             f"highest price over the price of production {show(row['e0_price_max'], 2)}",
             "",
             "Change in the capacity share of the unit-cost label, by flow:",
             f"  ordered {show(row['dk_ordered'])}, retired {show(row['dk_retired'])}, entry "
             f"{show(row['dk_entry'])}, exit {show(row['dk_exit'])}",
             "Change in its sales share:",
             f"  through the price {show(row['ds_price'])}, entry and exit "
             f"{show(row['ds_entry_exit'])}, rationing {show(row['ds_rationing'])}"]
    if prices:
        text += [""] + price_read_out(list(prices), E0_START)
    return "\n".join(text) + "\n"


def series(rows: list[dict], column: str) -> list[float]:
    """A column as numbers to plot; nan where it is not defined."""
    return [nan if row[column] is None else float(row[column]) for row in rows]


def over(numerators: list[float], denominators: list[float]) -> list[float]:
    """A ratio by period; nan where the denominator is not positive."""
    return [a / b if b > 0.0 else nan for a, b in zip(numerators, denominators)]


def moving_mean(values: list[float], window: int = 5) -> list[float]:
    """The mean of the last `window` periods, this one included."""
    return [fsum(values[max(0, t + 1 - window):t + 1]) / min(window, t + 1)
            for t in range(len(values))]


def add_legend(axis, columns: int = 2) -> None:
    """The legend of a panel, in a band of its own above the series: the vertical axis is
    stretched upwards by the height of the legend, so that no entry sits on a line."""
    handles, _ = axis.get_legend_handles_labels()
    band = 0.05 + 0.10 * ceil(len(handles) / columns)
    low, high = axis.get_ylim()
    axis.set_ylim(low, low + (high - low) / (1.0 - band))
    legend = axis.legend(loc="upper right", ncols=columns, handlelength=1.6,
                         columnspacing=1.0, borderaxespad=0.1)
    # The legend is inside the panel: the layout of the figure does not make room for it.
    legend.set_in_layout(False)


def draw(period_rows: list[dict], firm_rows: list[dict], params: Parameters, title: str,
         by_firm: bool = False):
    """The figure of a run: twelve panels on one time axis, each for one question. Blue is the
    unit-cost label and orange the profit-rate label in every panel; no panel has a second
    axis. Returns the matplotlib figure."""
    import matplotlib.pyplot as plt

    from figures import style

    style.apply()
    colour = {"shaikh": style.UNIT_COST, "okishio": style.PROFIT_RATE}
    name = {"shaikh": "unit-cost label", "okishio": "profit-rate label"}
    rows = {label: [row for row in period_rows if row["label"] == label] for label in colour}
    u, o = rows["shaikh"], rows["okishio"]
    periods = [row["t"] for row in u]
    demand = series(u, "demand")

    def both(column: str) -> list[float]:
        """A column summed over the two labels."""
        return [a + b for a, b in zip(series(u, column), series(o, column))]

    firms = {}
    for row in firm_rows:
        firms.setdefault(row["firm"], []).append(row)

    figure, panels = plt.subplots(6, 2, figsize=(style.WIDTH * 1.5, 13.2), sharex=True,
                                  constrained_layout=True)
    figure.suptitle(title, x=0.01, ha="left", fontsize=9.5)

    # Prices.
    axis = panels[0][0]
    axis.set_title("Does the price gravitate, and who is below whom?")
    axis.plot(periods, series(u, "reg_price"), color=style.MUTED,
              label="price of production")
    lowest_cost = [min((row["unit_cost"] for row in firm_rows
                        if row["t"] == t and row["unit_cost"] is not None), default=nan)
                   for t in periods]
    axis.plot(periods, lowest_cost, color=style.AXIS, linewidth=1.0,
              label="lowest unit cost")
    prices = {label: series(rows[label], "price") for label in colour}
    if by_firm:
        for history in firms.values():
            axis.plot([row["t"] for row in history], series(history, "price"),
                      color=colour[history[0]["label"]], linewidth=0.6, alpha=0.8)
        for label in colour:
            axis.plot([], [], color=colour[label], label=f"a firm, {name[label]}")
    elif all(isclose(a, b, rel_tol=0.005) for a, b in zip(prices["shaikh"], prices["okishio"])
             if a == a and b == b):
        axis.plot(periods, prices["shaikh"], color=style.SECONDARY,
                  label="price of both labels")
    else:
        for label in ("okishio", "shaikh"):
            axis.plot(periods, prices[label], color=colour[label],
                      label=f"price, {name[label]}")
    add_legend(axis)

    # Capacity and sales.
    axis = panels[0][1]
    axis.set_title("When is the industry short, and when does it work overtime?")
    axis.axhspan(1.0, params.u_max, color=style.MUTED, alpha=0.15, linewidth=0,
                 label="overtime band")
    axis.plot(periods, over(both("capacity"), demand), color=style.INK,
              label="capacity over demand")
    axis.plot(periods, over(both("sales"), demand), color=style.MUTED, linewidth=1.0,
              label="sales over demand")
    add_legend(axis)

    # Demand lost.
    axis = panels[1][0]
    axis.set_title("How long and how deep are the shortages? Share of demand lost")
    axis.plot(periods, over(series(u, "lost"), demand), color=style.SECONDARY)
    axis.set_ylim(bottom=0.0)

    # Entry gate.
    axis = panels[1][1]
    axis.set_title("When does capital enter and when does it leave?")
    withdrawn = both("withdrawn")
    for t, amount in zip(periods, withdrawn):
        if amount > 0.0:
            axis.axvspan(t - 0.5, t + 0.5, color=style.MUTED, alpha=0.18, linewidth=0)
    axis.fill_between([], [], color=style.MUTED, alpha=0.18, linewidth=0,
                      label="reserve withdrawn")
    axis.axhline(params.rbar, color=style.INK, linewidth=0.8, label="general rate")
    axis.plot(periods, series(u, "r_new"), color=style.SECONDARY, label="rate of new plants")
    axis.plot(periods, over(both("profit"), both("capital")), color=style.MUTED, linewidth=1.0,
              label="industry rate")
    add_legend(axis)

    # Firms.
    axis = panels[2][0]
    axis.set_title("Who enters and who leaves, and when?")
    with_plant = [sum(1 for row in firm_rows if row["t"] == t and row["plants"] > 0)
                  for t in periods]
    axis.plot(periods, with_plant, color=style.SECONDARY, label="firms with a plant")
    axis.vlines(periods, 0, both("entries"), color=style.INK, linewidth=1.0,
                label="entries (up) and exits (down)")
    axis.vlines(periods, 0, [-count for count in both("exits")], color=style.INK,
                linewidth=1.0)
    axis.axhline(0.0, color=style.AXIS, linewidth=0.8)
    add_legend(axis)

    # Selection.
    axis = panels[2][1]
    axis.set_title("Which label gains, and through sales or capacity?")
    axis.axhline(0.5, color=style.AXIS, linewidth=0.8)
    if by_firm:
        for history in firms.values():
            axis.plot([row["t"] for row in history], series(history, "share"),
                      color=colour[history[0]["label"]], linewidth=0.6, alpha=0.8)
        for label in colour:
            axis.plot([], [], color=colour[label], label=f"a firm, {name[label]}")
    else:
        axis.plot(periods, over(series(u, "capacity"), both("capacity")),
                  color=style.UNIT_COST, label="capacity share, unit-cost label")
        axis.plot(periods, series(u, "share"), color=style.LOW, label="its market share")
    axis.set_ylim(0.0, 1.0)
    axis.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    add_legend(axis)

    # Choice of technique.
    axis = panels[3][0]
    axis.set_title("How far apart are the two rules in this run?")
    hurdle = [nan if value != value else value / params.rbar for value in series(o, "hurdle")]
    axis.plot(periods, hurdle, color=style.PROFIT_RATE,
              label="hurdle of the profit-rate label over the general rate")
    dearer = over(moving_mean(series(o, "orders_dearer"), 10),
                  moving_mean(series(o, "orders"), 10))
    axis.plot(periods, dearer, color=style.MUTED, linewidth=1.0,
              label="share of its orders that are not the cheapest, over 10 periods")
    axis.set_ylim(bottom=0.0)
    add_legend(axis, columns=1)

    # Techniques.
    axis = panels[3][1]
    axis.set_title("Is technical change Marx-biased, and for whom? Unit cost (solid) and\n"
                   "capital per unit (dashed), period 0 = 1")
    for label in ("shaikh", "okishio"):
        for column, dashes in (("unit_cost", ()), ("kappa", (4, 2))):
            values = series(rows[label], column)
            base = next((value for value in values if value == value), nan)
            # One legend entry a label: the title says which line is which measure.
            axis.plot(periods, [value / base for value in values], color=colour[label],
                      dashes=dashes, label=name[label] if column == "unit_cost" else None)
    add_legend(axis)

    # Profit rates.
    axis = panels[4][0]
    axis.set_title("Does the rule that maximises the rate realise it? Realised rate")
    axis.axhline(params.rbar, color=style.INK, linewidth=0.8, label="general rate")
    for label in ("shaikh", "okishio"):
        axis.plot(periods, series(rows[label], "profit_rate"), color=colour[label],
                  label=name[label])
    add_legend(axis, columns=3)

    # Plants.
    axis = panels[4][1]
    axis.set_title("Where does capacity come from and go? Share of demand, 5-period mean;\n"
                   "capacity that leaves is below 0")
    for label in ("shaikh", "okishio"):
        ordered = [a + b for a, b in zip(series(rows[label], "cap_ordered"),
                                         series(rows[label], "cap_entry"))]
        axis.plot(periods, moving_mean(over(ordered, demand)), color=colour[label],
                  label=f"ordered, {name[label]}")
    reasons = (("age", style.INK, ()), ("cost", style.SECONDARY, (4, 2)),
               ("idle", style.MUTED, (1, 1.5)))
    for reason, grey, dashes in reasons:
        leaving = [-value for value in over(both("cap_retired_" + reason), demand)]
        axis.plot(periods, moving_mean(leaving), color=grey, linewidth=1.0, dashes=dashes,
                  label=f"leaving: {reason}")
    axis.axhline(0.0, color=style.AXIS, linewidth=0.8)
    add_legend(axis, columns=3)

    spread_rows = price_spread(period_rows, firm_rows)

    # Spread of prices across firms.
    axis = panels[5][0]
    axis.set_title("How far apart are the firms' prices? Over the price of production")
    reg = series(u, "reg_price")
    low = over(series(spread_rows, "low"), reg)
    high = over(series(spread_rows, "high"), reg)
    axis.fill_between(periods, low, high, color=style.MUTED, alpha=0.3, linewidth=0,
                      label="lowest to highest posted price")
    axis.plot(periods, series(spread_rows, "price_over_reg"), color=style.INK, linewidth=1.0,
              label="price of the industry, weighted by sales")
    axis.axhline(1.0, color=style.AXIS, linewidth=0.8)
    add_legend(axis, columns=1)

    # Volatility of the price over time.
    axis = panels[5][1]
    axis.set_title("How much does the price move? Change a period and dispersion across\n"
                   "firms, in %")
    for t, war in zip(periods, series(spread_rows, "war")):
        if war > 0.0:
            axis.axvspan(t - 0.5, t + 0.5, color=style.MUTED, alpha=0.12, linewidth=0)
    axis.fill_between([], [], color=style.MUTED, alpha=0.12, linewidth=0,
                      label="a firm cuts its price")
    change = [100.0 * value for value in series(spread_rows, "change")]
    axis.vlines(periods, 0.0, change, color=style.SECONDARY, linewidth=1.0,
                label="change of the industry price (log, %)")
    axis.plot(periods, [100.0 * value for value in series(spread_rows, "cv")],
              color=style.INK, linewidth=1.0, label="coefficient of variation across firms")
    axis.axhline(0.0, color=style.AXIS, linewidth=0.8)
    add_legend(axis, columns=1)

    for axis in panels[5]:
        axis.set_xlabel("Period")
        axis.set_xlim(periods[0], periods[-1])
    return figure


def show_run(pairs: list[str], seed: int = 0, name: str | None = None, by_firm: bool = False,
             figure: bool = True, folder: pathlib.Path = FOLDER) -> pathlib.Path:
    """Run one industry with the settings given as name=value, write its files and return
    their folder."""
    overrides, population = read_settings(pairs)
    params = replace(Parameters(), **overrides, **POPULATIONS[population])
    industry, firm_rows = trace(params, seed)
    row = run_row(industry.rows, params, seed)
    title = f"{', '.join(sorted(pairs)) or 'the defaults'}; seed {seed}"

    target = pathlib.Path(folder) / (name or run_name(pairs, seed))
    target.mkdir(parents=True, exist_ok=True)
    write_csv(target / "periods.csv", industry.rows, list(industry.rows[0]))
    write_csv(target / "firms.csv", firm_rows, list(FIRM_COLUMNS))
    prices = price_spread(industry.rows, firm_rows)
    write_csv(target / "prices.csv", prices, list(PRICE_COLUMNS))
    write_csv(target / "run.csv", [row], list(row))
    (target / "run.txt").write_text(read_out(row, params, title, prices))
    if figure:
        try:
            drawn = draw(industry.rows, firm_rows, params, title, by_firm)
        except ImportError:
            print("matplotlib is not installed here: the tables are written, not the figure")
        else:
            drawn.savefig(target / "run.pdf", bbox_inches="tight")
            drawn.savefig(target / "run.png", bbox_inches="tight", dpi=150)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("settings", nargs="*", metavar="name=value",
                        help="a parameter, or population=mixed|all_unit_cost|all_profit_rate")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--firms", action="store_true", help="one line a firm")
    parser.add_argument("--name", help="the output folder, in outputs/runs/")
    parser.add_argument("--no-figure", action="store_true", help="the tables alone")
    arguments = parser.parse_args()
    try:
        written = show_run(arguments.settings, arguments.seed, arguments.name, arguments.firms,
                           not arguments.no_figure)
    except ValueError as refused:
        parser.error(str(refused))
    print((written / "run.txt").read_text())
    print(written)
