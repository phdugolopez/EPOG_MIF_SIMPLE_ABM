"""Initial menu: Shaikh's table with its capital scaled to the general rate.

    kappa_j = kappa^S_j x 0.16 / rbar
    ucs_j   = ucs^S_j - delta (kappa_j - kappa^S_j)

Source: v4-final-model.md, "Initial industry"; v4-choices.md, decision 12. The unit costs
and the price of 100 are those of Shaikh's table at every rbar: only capital and operating
cost move. At rbar = 0.16 the menu is the table itself, at any delta. Under the option
"fixed" it is the table at every rbar. A menu with an operating cost that is not positive
is refused.
"""


def scaled_menu(shaikh_menu: tuple, shaikh_rate: float, rbar: float, delta: float,
                scaling: str) -> list[tuple]:
    """The initial menu as (name, ucs, kappa), in the order of Shaikh's table."""
    if scaling == "fixed":
        return list(shaikh_menu)
    scale = shaikh_rate / rbar
    menu = []
    for name, ucs_shaikh, kappa_shaikh in shaikh_menu:
        kappa = kappa_shaikh * scale
        ucs = ucs_shaikh - delta * (kappa - kappa_shaikh)
        if ucs <= 0.0:
            raise ValueError(f"rbar = {rbar}: the operating cost of {name} is {ucs:.2f}")
        menu.append((name, ucs, kappa))
    return menu
