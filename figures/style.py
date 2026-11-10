"""Style shared by the figure scripts: colours by role, thin marks, recessive axes.

A colour follows what it stands for in every figure: blue is the unit-cost label (and what the
unit-cost rule chooses), orange the profit-rate label. Two levels of one quantity take two
steps of one hue. Text is never in a data colour. Both sets pass the colour-blindness checks
on a white surface.
"""
import csv
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SURFACE = "#ffffff"
INK, SECONDARY, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
UNIT_COST, PROFIT_RATE = "#2a78d6", "#eb6834"
LOW, HIGH = "#6da7ec", "#184f95"
LINE, MARKER, RING = 1.5, 6.5, 1.5        # points: 2 px lines, 8 px markers, 2 px surface ring
WIDTH = 6.3                               # inches: the text width of the report
FOLDER = pathlib.Path("outputs/figures")
PRICING = {"cost_edge": "cost-edge cutting", "systematic": "systematic cutting",
           "leader_follow": "leader-follow pricing",
           "leader_follow_ucs": "leader-follow pricing, operating-cost floor",
           "leader_follow_overtime": "leader-follow pricing with overtime",
           "leader_follow_ucs_overtime": "leader-follow pricing with overtime, operating-cost floor",
           "overtime": "with overtime",
           "normal_price_overtime": "normal-price cutting with overtime"}


def apply() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 8.5, "text.color": INK,
        "axes.titlesize": 8.5, "axes.titlelocation": "left", "axes.titlepad": 6.0,
        "axes.labelsize": 8.0, "axes.labelcolor": SECONDARY,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.axisbelow": True,
        "grid.color": GRID, "grid.linewidth": 0.6, "grid.linestyle": "-",
        "xtick.color": AXIS, "ytick.color": AXIS,
        "xtick.labelcolor": SECONDARY, "ytick.labelcolor": SECONDARY,
        "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
        "lines.linewidth": LINE, "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
        "legend.frameon": False, "legend.fontsize": 7.5,
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "pdf.fonttype": 42,
    })


def read(path) -> list[dict]:
    """The rows of a file of the harness."""
    with open(path, newline="") as file:
        return list(csv.DictReader(file))


def number(value) -> float:
    """A cell as a number; nan when it is empty."""
    return float(value) if value not in ("", None) else float("nan")


def dots(axis, x, y, colour, low=None, high=None, line=True, label=None):
    """A series of dots with a surface ring, their 95 % intervals and, if asked, a line."""
    if low is not None:
        axis.vlines(x, low, high, color=colour, linewidth=1.0, zorder=2)
    if line:
        axis.plot(x, y, color=colour, zorder=3)
    axis.plot(x, y, linestyle="none", marker="o", markersize=MARKER, color=colour,
              markeredgecolor=SURFACE, markeredgewidth=RING, zorder=4, label=label)


def save(figure, name: str) -> pathlib.Path:
    """One PDF for the report and one PNG to look at."""
    FOLDER.mkdir(parents=True, exist_ok=True)
    figure.savefig(FOLDER / f"{name}.pdf", bbox_inches="tight")
    figure.savefig(FOLDER / f"{name}.png", bbox_inches="tight", dpi=170)
    plt.close(figure)
    return FOLDER / f"{name}.pdf"
