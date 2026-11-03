"""Draw the baseline figures from outputs/*.csv into outputs/*.png."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

import parameters  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
macro = pd.read_csv(OUTPUTS / "macro.csv")
t = macro["time"]

# Categorical slots (validated): types blue / orange, techniques aqua / violet / red.
TYPE_STYLE = {
    "shaikh": {"color": "#2a78d6", "linestyle": "-", "label": "Shaikh (h = 0)"},
    "okishio": {"color": "#eb6834", "linestyle": "--", "label": "Okishio (h = best rate)"},
}
TECHNIQUE_COLOR = {"C": "#1baf7a", "D1": "#6250d6", "D2": "#e34948"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2,
    "font.size": 9, "legend.frameon": False,
})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUTPUTS / name, dpi=180)
    plt.close(fig)


def label_end(ax, x, y, text, color=INK):
    ax.annotate(text, (x.iloc[-1], y.iloc[-1]), xytext=(4, 0), textcoords="offset points",
                va="center", fontsize=8, color=color)


# 1. Prices
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.fill_between(t, macro["min_price"], macro["max_price"], color="#2a78d6", alpha=0.15,
                linewidth=0, label="Range of posted prices")
ax.plot(t, macro["mean_price"], color="#2a78d6", label="Mean price (sales-weighted)")
ax.axhline(100, color=MUTED, linewidth=1, linestyle=":")
ax.annotate("p = 100", (t.iloc[-1], 100), xytext=(4, 0), textcoords="offset points",
            va="center", fontsize=8, color=MUTED)
ax.set(xlabel="Period", ylabel="Price (wage units)", title="Prices")
ax.legend(loc="lower right")
save(fig, "prices.png")

# 2. Shares by type
fig, ax = plt.subplots(figsize=(7, 3.6))
for firm_type, style in TYPE_STYLE.items():
    ax.plot(t, macro[f"share_{firm_type}"], **style)
    label_end(ax, t, macro[f"share_{firm_type}"], firm_type.capitalize())
ax.set(xlabel="Period", ylabel="Market share", ylim=(0, 1), title="Market shares by type")
ax.legend(loc="upper left")
save(fig, "shares_by_type.png")

# 3. Capacity by technique (stacked) and by type
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4.0), sharey=True)
names = list(parameters.SHAIKH_PLANTS)
ax1.stackplot(t, *[macro[f"capacity_{n}"] for n in names], labels=names,
              colors=[TECHNIQUE_COLOR[n] for n in names], edgecolor="white", linewidth=0.5)
ax1.plot(t, macro["demand"], color=INK, linewidth=1, linestyle=":", label="Demand")
ax1.set(xlabel="Period", ylabel="Normal capacity", title="Capacity by technique")
ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=4)
for firm_type, style in TYPE_STYLE.items():
    ax2.plot(t, macro[f"capacity_{firm_type}"], **style)
ax2.set(xlabel="Period", title="Capacity by type")
ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)
save(fig, "capacity.png")

# 4. Profit rates
fig, ax = plt.subplots(figsize=(7, 3.6))
for firm_type, style in TYPE_STYLE.items():
    ax.plot(t, macro[f"profit_rate_{firm_type}"], **style)
ax.plot(t, macro["r_new"], color="#6250d6", linewidth=1.2, label="r_new (plants of the last k periods)")
ax.axhline(parameters.RBAR, color=MUTED, linewidth=1, linestyle=":")
ax.annotate("rbar", (t.iloc[-1], parameters.RBAR), xytext=(4, 0), textcoords="offset points",
            va="center", fontsize=8, color=MUTED)
ax.set(xlabel="Period", ylabel="Profit rate", title="Profit rates (net, on capital at cost)")
ax.legend(loc="lower right")
save(fig, "profit_rates.png")

# 5. Number of firms
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.step(t, macro["n_firms"], where="post", color=INK, linewidth=1.2, label="All firms")
for firm_type, style in TYPE_STYLE.items():
    ax.step(t, macro[f"n_{firm_type}"], where="post", **style)
ax.set(xlabel="Period", ylabel="Firms", title="Number of firms")
ax.legend(loc="upper right")
save(fig, "n_firms.png")

print(f"Figures saved in: {OUTPUTS}")
