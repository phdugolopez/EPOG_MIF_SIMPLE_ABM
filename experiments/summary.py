"""The run row: one row per run, a function of the period table alone (v4-plan.md, section 8).

U is the label "shaikh" and O the label "okishio" in every population. "End" is t = T, read
from capacity_next and share_end of the last period. The E0 measures are read on periods
E0_START to the last (v4-final-model.md, "Experiments", E0; v4-choices.md, decisions 3 to 8).
"""
from math import fsum, isclose, log

U = "shaikh"
O = "okishio"
CAPACITY_FLOWS = (("ordered", 1.0), ("retired", -1.0), ("entry", 1.0), ("exit", -1.0))

# E0: the first period read, and the threshold of each line. Analysis constants, outside
# the model. The band on the rate of new plants is in multiples of the general rate.
E0_START = 20
E0_LEADER_MIN = 0.9
E0_PRICE_BAND = (0.9, 1.2)
E0_CROSSINGS_MIN = 5
E0_CAPACITY_BAND = (0.9, 1.2)
E0_R_NEW_BAND = (0.6, 2.0)
E0_LOST_MAX = 0.10
E0_LINES = ("leader", "price", "crossings", "capacity", "r_new", "lost", "alive")
INVADED_ABOVE = 0.1


def total(rows: list[dict], key: str) -> float:
    """Sum of a column over the rows in which it is defined."""
    return fsum(row[key] for row in rows if row[key] is not None)


def ratio(numerator: float, denominator: float) -> float | None:
    """A ratio, undefined when its denominator is not positive."""
    if denominator > 0.0:
        return numerator / denominator
    return None


def mean(values: list[float]) -> float | None:
    """Mean of the values that are defined; undefined without one."""
    defined = [value for value in values if value is not None]
    if not defined:
        return None
    return fsum(defined) / len(defined)


def average(rows: list[dict], key: str) -> float | None:
    """Mean of a column over the rows in which it is defined."""
    return mean([row[key] for row in rows])


def growth(rows: list[dict], key: str) -> float | None:
    """ln(x_last / x_first) / (t_last - t_first) over the rows in which x is defined."""
    points = [(row["t"], row[key]) for row in rows if row[key] is not None]
    if len(points) < 2:
        return None
    (t_first, x_first), (t_last, x_last) = points[0], points[-1]
    return log(x_last / x_first) / (t_last - t_first)


def outcome(share: float | None) -> str:
    """The run for the unit-cost label: undecided without capacity at the end, a tie at
    exactly one half, else a win or a loss."""
    if share is None:
        return "undecided"
    if isclose(share, 0.5):
        return "tie"
    return "win" if share > 0.5 else "loss"


def takeover(shares: list[float | None]) -> tuple[int | None, str | None]:
    """First period after which one label holds more than 0.9 of capacity in every remaining
    period. shares: the capacity share of U by period, the end included."""
    held_by = ((U, [share is not None and share > 0.9 for share in shares]),
               (O, [share is not None and share < 0.1 for share in shares]))
    for label, held in held_by:
        if held and held[-1]:
            lost = [t for t, flag in enumerate(held) if not flag]
            return (lost[-1] + 1 if lost else 0), label
    return None, None


def capacity_terms(u: list[dict], o: list[dict]) -> dict:
    """Change in U's capacity share over the run, split by flow:
    term_c = sign_c (flow_c,U - s_U,t (flow_c,U + flow_c,O)) / K_t+1, summed over t."""
    terms = dict.fromkeys((name for name, _ in CAPACITY_FLOWS), 0.0)
    for a, b in zip(u, o):
        capacity = a["capacity"] + b["capacity"]
        capacity_next = a["capacity_next"] + b["capacity_next"]
        if capacity > 0.0 and capacity_next > 0.0:
            for name, sign in CAPACITY_FLOWS:
                flow = a["cap_" + name] + b["cap_" + name]
                own = a["cap_" + name] - a["capacity"] / capacity * flow
                terms[name] += sign * own / capacity_next
    return terms


def sales_terms(u: list[dict]) -> dict:
    """Change in U's sales share over the run, split in three: the price (the replicator),
    entry and exit, and rationing (sales share less market share)."""
    terms = {"price": 0.0, "entry_exit": 0.0, "rationing": 0.0}
    for before, now in zip(u, u[1:]):
        if before["sales_share"] is not None and now["sales_share"] is not None:
            terms["price"] += now["share"] - before["share_end"]
            terms["entry_exit"] += before["share_end"] - before["share"]
            terms["rationing"] += ((now["sales_share"] - now["share"])
                                   - (before["sales_share"] - before["share"]))
    return terms


def crossings(ratios: list[float | None]) -> int:
    """Times a ratio passes from one side of 1 to the other between two periods, either way.
    A period in which it is undefined, or exactly 1, is on neither side and is skipped."""
    sides = [value > 1.0 for value in ratios if value is not None and value != 1.0]
    return sum(before != now for before, now in zip(sides, sides[1:]))


def within(value: float | None, band: tuple[float, float], scale: float = 1.0) -> bool:
    """Whether a measure is defined and inside a band, its two ends included."""
    return value is not None and band[0] * scale <= value <= band[1] * scale


def e0_measures(u: list[dict], o: list[dict], rbar: float, capacity_end: float) -> dict:
    """The measures of E0 on periods E0_START to the last, the verdict of each line and of
    the seed. The industry columns are the same on both rows: they are read on U's."""
    window = [(a, b) for a, b in zip(u, o) if a["t"] >= E0_START]
    rows = [a for a, _ in window]
    both = [row for pair in window for row in pair]
    capacity = [ratio(a["capacity"] + b["capacity"], a["demand"]) for a, b in window]
    prices = [row["price_over_reg"] for row in rows]
    spreads = [row["rate_high"] - row["rate_low"] for row in rows
               if row["rate_high"] is not None]
    measures = {
        "leader": average(rows, "leader_cheapest"),
        "price": mean(prices),
        "crossings": crossings(prices),
        "capacity": mean(capacity),
        "r_new": average(rows, "r_new"),
        "lost": ratio(total(rows, "lost"), total(rows, "demand")),
        "alive": capacity_end > 0.0,
    }
    passed = {
        "leader": measures["leader"] is not None and measures["leader"] >= E0_LEADER_MIN,
        "price": within(measures["price"], E0_PRICE_BAND),
        "crossings": measures["crossings"] >= E0_CROSSINGS_MIN,
        "capacity": within(measures["capacity"], E0_CAPACITY_BAND),
        "r_new": within(measures["r_new"], E0_R_NEW_BAND, rbar),
        "lost": measures["lost"] is not None and measures["lost"] <= E0_LOST_MAX,
        "alive": measures["alive"],
    }
    columns = {"e0_" + line: measures[line] for line in E0_LINES}
    columns.update({f"e0_{line}_ok": passed[line] for line in E0_LINES if line != "alive"})
    columns["e0_pass"] = all(passed.values())
    columns["e0_lines"] = sum(passed.values()) / len(E0_LINES)
    columns["e0_rate_industry"] = ratio(total(both, "profit"), total(both, "capital"))
    columns["e0_rate_spread"] = mean(spreads)
    columns["e0_capacity_min"] = min((value for value in capacity if value is not None),
                                     default=None)
    columns["e0_capacity_max"] = max((value for value in capacity if value is not None),
                                     default=None)
    columns["e0_price_max"] = max((value for value in prices if value is not None),
                                  default=None)
    return columns


def industry_techniques(u: list[dict], o: list[dict]) -> list[dict]:
    """The capacity-weighted operating cost and capital per unit of the industry, by period."""
    rows = []
    for a, b in zip(u, o):
        row = {"t": a["t"]}
        for key in ("ucs", "kappa"):
            weighted = fsum(r[key] * r["capacity"] for r in (a, b) if r[key] is not None)
            row[key] = ratio(weighted, a["capacity"] + b["capacity"])
        rows.append(row)
    return rows


def run_row(rows: list[dict], params, seed: int, mutant: str | None = None) -> dict:
    """One row for the run: outcome, takeover, the two decompositions, what the mechanisms
    show, the measures of the Marx bias and the measures of E0. mutant is the label of the
    single invader in E6, None elsewhere."""
    u = [row for row in rows if row["label"] == U]
    o = [row for row in rows if row["label"] == O]
    capacity_end = u[-1]["capacity_next"] + o[-1]["capacity_next"]
    share_end = ratio(u[-1]["capacity_next"], capacity_end)
    shares = [ratio(a["capacity"], a["capacity"] + b["capacity"]) for a, b in zip(u, o)]
    takeover_t, takeover_label = takeover(shares + [share_end])
    dk = capacity_terms(u, o)
    ds = sales_terms(u)
    sales_shares = [row["sales_share"] for row in u if row["sales_share"] is not None]
    retired = total(rows, "cap_retired")
    techniques = industry_techniques(u, o)
    spreads = [{"spread": row["rate_high"] - row["rate_low"]} for row in u
               if row["rate_high"] is not None]

    dk_resid = None
    if share_end is not None and shares[0] is not None:
        dk_resid = share_end - shares[0] - fsum(dk.values())
    ds_resid = None
    if sales_shares:
        ds_resid = sales_shares[-1] - sales_shares[0] - fsum(ds.values())

    row = {
        "seed": seed,
        "outcome": outcome(share_end),
        "cap_share_end": share_end,
        "sales_share_end": u[-1]["sales_share"],
        "takeover_t": takeover_t,
        "takeover_label": takeover_label,
        "dk_ordered": dk["ordered"],
        "dk_retired": dk["retired"],
        "dk_entry": dk["entry"],
        "dk_exit": dk["exit"],
        "dk_accumulation": dk["ordered"] + dk["retired"],
        "dk_resid": dk_resid,
        "ds_price": ds["price"],
        "ds_entry_exit": ds["entry_exit"],
        "ds_rationing": ds["rationing"],
        "ds_resid": ds_resid,
        "price_over_reg": average(u, "price_over_reg"),
        "war_freq": average(u, "war"),
        "leader_cheapest": average(u, "leader_cheapest"),
        "rate_spread": average(spreads, "spread"),
        "rate_industry": ratio(total(rows, "profit"), total(rows, "capital")),
        "entries": total(rows, "entries"),
        "exits": total(rows, "exits"),
        "open_share": mean([row["r_new"] is None or row["r_new"] >= params.rbar for row in u]),
        "retired_age": ratio(total(rows, "cap_retired_age"), retired),
        "retired_cost": ratio(total(rows, "cap_retired_cost"), retired),
        "retired_idle": ratio(total(rows, "cap_retired_idle"), retired),
        "g_ucs": growth(techniques, "ucs"),
        "g_kappa": growth(techniques, "kappa"),
        "firms_end": sum(r["firms"] + r["entries"] - r["exits"] for r in (u[-1], o[-1])),
        "capacity_end": capacity_end,
        "capacity_over_demand": capacity_end / u[-1]["demand"],
        "util_mean": ratio(total(rows, "sales"), total(rows, "capacity")),
        "lost_share": ratio(total(u, "lost"), total(u, "demand")),
        "overtime_share": ratio(total(rows, "overtime"), total(rows, "sales")),
    }
    row["marx_biased"] = (row["g_ucs"] is not None and row["g_ucs"] < 0.0
                          and row["g_kappa"] > 0.0)
    for label, group in ((U, u), (O, o)):
        row["hurdle_" + label] = average(group, "hurdle")
        row[label + "_dearer"] = ratio(total(group, "orders_dearer"), total(group, "orders"))
        row["rate_" + label] = ratio(total(group, "profit"), total(group, "capital"))
        row["entries_" + label] = total(group, "entries")
        row["exits_" + label] = total(group, "exits")
        row["released_" + label] = ratio(total(group, "cap_released"),
                                         total(group, "cap_retired"))
        row["kept_" + label] = ratio(total(group, "kept"), total(group, "drawn"))
        row["g_ucs_" + label] = growth(group, "ucs")
        row["g_kappa_" + label] = growth(group, "kappa")

    # H6: the gap in realised rates between the two labels.
    row["rate_gap"] = None
    if row["rate_" + U] is not None and row["rate_" + O] is not None:
        row["rate_gap"] = row["rate_" + U] - row["rate_" + O]

    row.update(e0_measures(u, o, params.rbar, capacity_end))

    # E6: the final capacity share of the label of the single invader.
    row["mutant_share_end"] = None
    row["invaded"] = None
    if mutant is not None and share_end is not None:
        row["mutant_share_end"] = share_end if mutant == U else 1.0 - share_end
        row["invaded"] = row["mutant_share_end"] > INVADED_ABOVE
    return row
