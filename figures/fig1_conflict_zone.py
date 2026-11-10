"""Figure 1: the conflict zone on Shaikh's menu. No run: the three techniques of the table.

    python -m figures.fig1_conflict_zone

Left: the profit rate of each technique against the price, at the rate of the table, 0.16.
Right: the same rates less the rate of D2, the technique with the lowest unit cost; above a
price of 85.15 another technique has the higher rate, so the two rules choose differently.
On the scaled menu the rates are those of the table times rbar / 0.16 at every price, so
the two panels keep their shape, and the prices at which the rules part, at every rate.
"""
import matplotlib.pyplot as plt

from equations.common_profit_rate import profit_rate_at_price
from equations.common_regulating_price import price_of_production
from equations.common_unit_cost import unit_cost
from figures import style
from parameters import SHAIKH_MENU, SHAIKH_RATE, Parameters

DELTA = Parameters().delta
MENU = {name: (ucs, kappa) for name, ucs, kappa in SHAIKH_MENU}
COLOURS = {"C": style.MUTED, "D1": style.PROFIT_RATE, "D2": style.UNIT_COST}
NAMES = {"C": "C (unit cost 78.0)", "D1": "D1 (76.0)", "D2": "D2 (75.0, the lowest)"}


def rate(name: str, price: float) -> float:
    """The profit rate of a technique at a price, in per cent."""
    return 100.0 * profit_rate_at_price(price, *MENU[name], DELTA)


def crossing(first: str, second: str) -> float:
    """The price at which two techniques have the same rate."""
    cost_a, kappa_a = unit_cost(*MENU[first], DELTA), MENU[first][1]
    cost_b, kappa_b = unit_cost(*MENU[second], DELTA), MENU[second][1]
    return (cost_a * kappa_b - cost_b * kappa_a) / (kappa_b - kappa_a)


def main():
    style.apply()
    prices = [70.0 + 0.25 * i for i in range(161)]
    figure, (levels, gaps) = plt.subplots(1, 2, figsize=(style.WIDTH, 2.7),
                                          constrained_layout=True)
    for name in ("C", "D1", "D2"):
        levels.plot(prices, [rate(name, price) for price in prices], color=COLOURS[name],
                    label=NAMES[name])
        gaps.plot(prices, [rate(name, price) - rate("D2", price) for price in prices],
                  color=COLOURS[name])
        gaps.annotate(name, (110.0, rate(name, 110.0) - rate("D2", 110.0)), xytext=(4, 0),
                      textcoords="offset points", va="center", fontsize=7.5, color=style.INK)
    levels.set_title("Profit rate of each technique at the price, %")
    levels.set_xlabel("Price")
    levels.legend(loc="upper left", handlelength=1.6)
    gaps.set_title("The same rates, less the rate of D2, points")
    gaps.set_xlabel("Price")
    edge = crossing("D1", "D2")
    gaps.axvspan(edge, 110.0, color=style.MUTED, alpha=0.10, linewidth=0)
    gaps.text(110.0, -1.42, "conflict zone: another technique\nhas a higher rate than D2",
              ha="right", va="bottom", fontsize=7.5, color=style.SECONDARY)
    gaps.annotate(f"{edge:.2f}", (edge, 0.0), xytext=(-3, 5), textcoords="offset points",
                  ha="right", fontsize=7.5, color=style.SECONDARY)
    regulating = price_of_production(*MENU["D2"], DELTA, SHAIKH_RATE)
    gaps.axvline(regulating, color=style.AXIS, linewidth=0.8)
    gaps.text(regulating, 1.86, " price of production\n of D2, at every r̄", fontsize=6.5,
              color=style.SECONDARY, va="top")
    gaps.set_ylim(-1.5, 1.9)
    for axis in (levels, gaps):
        axis.set_xlim(70.0, 110.0)
    return style.save(figure, "fig1_conflict_zone")


if __name__ == "__main__":
    print(main())
