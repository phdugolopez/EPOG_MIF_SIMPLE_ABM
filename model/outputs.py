"""The period table: one row per period and label, kept in industry.rows. It observes and never
decides: it draws no random number and writes nothing a rule reads."""
from math import fsum

from parameters import LABELS

KEYS = ("dividends", "cap_retired", "cap_retired_age", "cap_retired_cost", "cap_retired_idle",
        "cap_released", "withdrawn", "cap_ordered", "cap_exit", "cap_entry",
        "orders", "orders_dearer", "drawn", "kept", "entries", "exits")


def reset_tally(industry) -> None:
    """A new tally of the period's flows, by label."""
    industry.tally = {label: dict.fromkeys(KEYS, 0.0) for label in LABELS}


def count(industry, firm, key: str, amount: float) -> None:
    """Add a flow of this period to the tally of the firm's label."""
    industry.tally[firm.label][key] += amount


def record_production(industry) -> None:
    """The two rows of period t, written at the end of step 3: before any plant or firm leaves.
    Stage 2 writes the stocks the checks need; stage 3c adds the other columns of the plan."""
    for label in LABELS:
        firms = [firm for firm in industry.firms if firm.label == label]
        industry.rows.append({
            "t": industry.time, "label": label, "rule": getattr(industry.params, "rule_" + label),
            "firms": len(firms),
            "capacity": fsum(firm.capacity for firm in firms),
            "share": fsum(firm.share for firm in firms),
            "notional": fsum(firm.notional for firm in firms),
            "sales": fsum(firm.sales for firm in firms),
        })


def record_end(industry) -> None:
    """Completes the two rows of t after step 6: the flows of the tally, next period's capacity
    and the stocks of the label's firms at the end of the period."""
    for row in industry.rows[-len(LABELS):]:
        firms = [firm for firm in industry.firms if firm.label == row["label"]]
        flows = industry.tally[row["label"]]
        row.update(flows)
        row["capacity_next"] = (row["capacity"] - flows["cap_retired"] + flows["cap_ordered"]
                                - flows["cap_exit"] + flows["cap_entry"])
        row["share_end"] = fsum(firm.share for firm in firms)
        row["cash"] = fsum(firm.cash for firm in firms)
        row["funds"] = fsum(firm.funds for firm in firms)
        row["write_offs"] = fsum(firm.write_offs for firm in firms)
