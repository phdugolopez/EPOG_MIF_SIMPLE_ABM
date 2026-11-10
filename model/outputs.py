"""The tally of a period's flows and the period table (v4-plan.md, sections 4 and 8).

The table has one row per period and label, in industry.rows. It observes and never decides:
it draws no random number and writes nothing a rule reads. Undefined values are None.

The tally is a list with one entry a flow, kept by firm. The table sums the entries of a
label; the run viewer sums those of a firm. A firm that left at step 6 is still in the tally
of its last period.
"""
from math import fsum
from typing import NamedTuple

from parameters import LABELS

# The flows of a period, in the order of their columns in the period table.
KEYS = ("dividends", "cap_retired", "cap_retired_age", "cap_retired_cost", "cap_retired_idle",
        "cap_released", "withdrawn", "cap_ordered", "cap_exit", "cap_entry",
        "orders", "orders_dearer", "drawn", "kept", "entries", "exits")


class Flow(NamedTuple):
    """One flow of the period."""
    firm_id: int           # the serial number of the firm
    label: str             # its label
    key: str               # one of KEYS
    amount: float


def count(industry, firm, key: str, amount: float) -> None:
    """Add a flow of this period to the tally, under the firm that made it."""
    assert key in KEYS, key
    industry.tally.append(Flow(firm.id, firm.label, key, amount))


def sum_flows(entries: list[Flow]) -> dict:
    """The total of each flow over some entries of the tally.

    The sums are exact (math.fsum), so no total depends on the order of the firms.
    """
    amounts = {key: [] for key in KEYS}
    for flow in entries:
        amounts[flow.key].append(flow.amount)
    totals = {}
    for key in KEYS:
        totals[key] = fsum(amounts[key])
    return totals


def record_production(industry) -> None:
    """The two rows of the period, written at the end of step 3: before any plant or firm
    leaves.

    Stage 2 writes the identity of the row and the stocks that close_period and check read.
    Stage 3c writes the other columns of section 8 of the plan.
    """
    for label in LABELS:
        # The firms that carry this label.
        group = [firm for firm in industry.firms if firm.label == label]
        row = {
            "t": industry.time,
            "label": label,
            "rule": getattr(industry.params, "rule_" + label),
            "firms": len(group),
            "capacity": fsum(firm.capacity for firm in group),
            "share": fsum(firm.share for firm in group),
            "notional": fsum(firm.notional for firm in group),
            "sales": fsum(firm.sales for firm in group),
        }
        industry.rows.append(row)


def record_end(industry) -> None:
    """The two rows of the period are completed after step 6.

    They gain the flows of the tally, next period's capacity and the closing stocks.
    """
    for row in industry.rows[-len(LABELS):]:
        # The flows of the label's firms, those that left this period included.
        entries = [flow for flow in industry.tally if flow.label == row["label"]]
        row.update(sum_flows(entries))

        # Next period's capacity: what is in operation, less what left, plus what is on order.
        row["capacity_next"] = (row["capacity"] - row["cap_retired"] - row["cap_exit"]
                                + row["cap_ordered"] + row["cap_entry"])

        # The closing stocks of the firms that carry the label and are still in the industry.
        group = [firm for firm in industry.firms if firm.label == row["label"]]
        row["share_end"] = fsum(firm.share for firm in group)
        row["cash"] = fsum(firm.cash for firm in group)
        row["funds"] = fsum(firm.funds for firm in group)
        row["write_offs"] = fsum(firm.write_offs for firm in group)

        # Their mean hurdle; undefined without a firm.
        row["hurdle"] = None
        if group:
            row["hurdle"] = fsum(firm.hurdle for firm in group) / len(group)
