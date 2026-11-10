"""Whether the depreciation reserve of a plant that leaves joins the firm's funds.

    conditional:  r_new >= rbar, or r_new is undefined (no plant in its window)
    always:       yes
    never:        no

Source: v4-final-model.md, "Schedule", step 4, and the option `reserve`. The reserve is the
purchase cost less the book value. When it is not released the firm pays it to the rest of
the economy, as far as its cash allows.
"""


def reserve_released(rule: str, r_new: float | None, rbar: float) -> bool:
    """True when the reserve joins the funds, false when it is paid out."""
    if rule == "always":
        return True
    if rule == "never":
        return False
    return r_new is None or r_new >= rbar
