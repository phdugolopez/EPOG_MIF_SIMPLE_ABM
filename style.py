"""Colours and matplotlib rcParams shared by plot_outputs.py and the debugging plots in
debug/, defined once so that the two sets of figures cannot drift apart.

Categorical slots (validated): labels shaikh blue and okishio orange; techniques C, D1 and
D2 aqua, violet and red. Each script applies RC_PARAMS itself (plt.rcParams.update):
importing this module changes nothing.
"""

TYPE_STYLE = {
    "shaikh": {"color": "#2a78d6", "linestyle": "-", "label": "Shaikh (h = 0)"},
    "okishio": {"color": "#eb6834", "linestyle": "--", "label": "Okishio (h = best rate)"},
}
TECHNIQUE_COLOR = {"C": "#1baf7a", "D1": "#6250d6", "D2": "#e34948"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

RC_PARAMS = {
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2,
    "font.size": 9, "legend.frameon": False,
}
