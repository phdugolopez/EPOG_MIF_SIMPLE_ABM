"""The run table: one row per run, a function of the period table alone (plan, section 6).
U is the label "shaikh" and O the label "okishio" in every population; "end" is t = T, read
from capacity_next and share_end of the last period."""
from math import fsum, isclose, log

U, O = "shaikh", "okishio"
CAPACITY_FLOWS = (("ordered", 1.0), ("retired", -1.0), ("entry", 1.0), ("exit", -1.0))


def total(rows: list[dict], key: str) -> float:
    """Sum of a column over the rows in which it is defined."""
    return fsum(row[key] for row in rows if row[key] is not None)


def ratio(a: float, b: float) -> float | None:
    return a / b if b > 0.0 else None


def average(rows: list[dict], key: str) -> float | None:
    """Mean of a column over the rows in which it is defined."""
    values = [row[key] for row in rows if row[key] is not None]
    return fsum(values) / len(values) if values else None


def growth(rows: list[dict], key: str) -> float | None:
    """ln(x_last / x_first) / (t_last - t_first) over the rows in which x is defined."""
    points = [(row["t"], row[key]) for row in rows if row[key] is not None]
    if len(points) < 2:
        return None
    (t0, x0), (t1, x1) = points[0], points[-1]
    return log(x1 / x0) / (t1 - t0)


def takeover(shares: list[float | None]) -> tuple[int | None, str | None]:
    """First period after which one label holds more than 0.9 of capacity in every remaining
    period (v2 `takeover`). shares: the capacity share of U by period, the end included."""
    for label, held in ((U, [s is not None and s > 0.9 for s in shares]),
                        (O, [s is not None and s < 0.1 for s in shares])):
        if held and held[-1]:
            lost = [t for t, flag in enumerate(held) if not flag]
            return (lost[-1] + 1 if lost else 0), label
    return None, None


def capacity_terms(u: list[dict], o: list[dict]) -> dict:
    """Change in U's capacity share over the run, split by flow (v2 `capacity_share_terms`):
    term_c = sign_c (flow_c,U - s_U,t (flow_c,U + flow_c,O)) / K_t+1, summed over t."""
    terms = dict.fromkeys((name for name, _ in CAPACITY_FLOWS), 0.0)
    for a, b in zip(u, o):
        k, k_next = a["capacity"] + b["capacity"], a["capacity_next"] + b["capacity_next"]
        if k > 0.0 and k_next > 0.0:
            for name, sign in CAPACITY_FLOWS:
                flow = a["cap_" + name] + b["cap_" + name]
                terms[name] += sign * (a["cap_" + name] - a["capacity"] / k * flow) / k_next
    return terms


def sales_terms(u: list[dict]) -> dict:
    """Change in U's sales share over the run, split in three (v2 `sales_share_terms`): price
    (the replicator), entry and exit, and rationing (sales share less notional share)."""
    terms = {"price": 0.0, "entry_exit": 0.0, "rationing": 0.0}
    for before, now in zip(u, u[1:]):
        if before["sales_share"] is not None and now["sales_share"] is not None:
            terms["price"] += now["share"] - before["share_end"]
            terms["entry_exit"] += before["share_end"] - before["share"]
            terms["rationing"] += ((now["sales_share"] - now["share"])
                                   - (before["sales_share"] - before["share"]))
    return terms


def run_row(rows: list[dict], params, seed: int) -> dict:
    """One row for the run: outcome, takeover, decompositions, mechanism observables and the
    Marx-bias measures."""
    u, o = [r for r in rows if r["label"] == U], [r for r in rows if r["label"] == O]
    k_end = u[-1]["capacity_next"] + o[-1]["capacity_next"]
    share_end = ratio(u[-1]["capacity_next"], k_end)
    if share_end is None:
        outcome = "undecided"
    elif isclose(share_end, 0.5):
        outcome = "tie"
    else:
        outcome = "win" if share_end > 0.5 else "loss"
    shares = [ratio(a["capacity"], a["capacity"] + b["capacity"]) for a, b in zip(u, o)]
    takeover_t, takeover_label = takeover(shares + [share_end])
    dk, ds = capacity_terms(u, o), sales_terms(u)
    sigma = [r["sales_share"] for r in u if r["sales_share"] is not None]
    retired = total(rows, "cap_retired")
    industry = [{"t": a["t"],
                 **{key: ratio(fsum(r[key] * r["capacity"] for r in (a, b) if r[key] is not None),
                               a["capacity"] + b["capacity"]) for key in ("ucs", "kappa")}}
                for a, b in zip(u, o)]
    row = {
        "seed": seed, "outcome": outcome, "cap_share_end": share_end,
        "sales_share_end": u[-1]["sales_share"],
        "takeover_t": takeover_t, "takeover_label": takeover_label,
        "dk_ordered": dk["ordered"], "dk_retired": dk["retired"], "dk_entry": dk["entry"],
        "dk_exit": dk["exit"], "dk_accumulation": dk["ordered"] + dk["retired"],
        "dk_resid": (share_end - shares[0] - fsum(dk.values())
                     if share_end is not None and shares[0] is not None else None),
        "ds_price": ds["price"], "ds_entry_exit": ds["entry_exit"],
        "ds_rationing": ds["rationing"],
        "ds_resid": sigma[-1] - sigma[0] - fsum(ds.values()) if sigma else None,
        "price_over_reg": average(u, "price_over_reg"), "war_freq": average(u, "war"),
        "leader_cheapest": average(u, "leader_cheapest"),
        "rate_spread": average([{"x": r["rate_high"] - r["rate_low"]} for r in u
                                if r["rate_high"] is not None], "x"),
        "rate_industry": ratio(total(rows, "profit"), total(rows, "capital")),
        "entries": total(rows, "entries"), "exits": total(rows, "exits"),
        "open_share": fsum(r["r_new"] is None or r["r_new"] >= params.rbar for r in u) / len(u),
        "retired_age": ratio(total(rows, "cap_retired_age"), retired),
        "retired_cost": ratio(total(rows, "cap_retired_cost"), retired),
        "retired_idle": ratio(total(rows, "cap_retired_idle"), retired),
        "g_ucs": growth(industry, "ucs"), "g_kappa": growth(industry, "kappa"),
        "firms_end": sum(r["firms"] + r["entries"] - r["exits"] for r in (u[-1], o[-1])),
        "capacity_end": k_end, "capacity_over_demand": k_end / u[-1]["demand"],
        "util_mean": ratio(total(rows, "sales"), total(rows, "capacity")),
        "lost_share": total(u, "lost") / total(u, "demand"),
    }
    row["marx_biased"] = (row["g_ucs"] is not None and row["g_ucs"] < 0.0 and row["g_kappa"] > 0.0)
    for label, group in ((U, u), (O, o)):
        row["hurdle_" + label] = average(group, "hurdle")
        row[label + "_dearer"] = ratio(total(group, "orders_dearer"), total(group, "orders"))
        row["rate_" + label] = ratio(total(group, "profit"), total(group, "capital"))
        row["entries_" + label], row["exits_" + label] = total(group, "entries"), total(group, "exits")
        row["released_" + label] = ratio(total(group, "cap_released"), total(group, "cap_retired"))
        row["g_ucs_" + label], row["g_kappa_" + label] = growth(group, "ucs"), growth(group, "kappa")
    return row
