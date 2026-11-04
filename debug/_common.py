"""Shared loading and style for the debugging plots in debug/.

Every script reads the tables run.py wrote to a run folder (CSV or Parquet), never the
model, and writes its figures to RUN_DIR/debug/. Colours and rcParams are the ones
plot_outputs.py uses (it imports them from here): labels shaikh blue and okishio orange,
techniques C / D1 / D2 aqua, violet and red. Another label or technique gets a colour
from a fixed list, in sorted order of names, never in firm order.
"""

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

TYPE_STYLE = {
    "shaikh": {"color": "#2a78d6", "linestyle": "-", "label": "Shaikh (h = 0)"},
    "okishio": {"color": "#eb6834", "linestyle": "--", "label": "Okishio (h = best rate)"},
}
TECHNIQUE_COLOR = {"C": "#1baf7a", "D1": "#6250d6", "D2": "#e34948"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
FAIL = "#d0021b"
WAR_SHADE = {"color": "#f2c14e", "alpha": 0.18, "linewidth": 0}
EXTRA_COLORS = ("#8a6d3b", "#c2549d", "#4c9a2a", "#7f7f7f", "#17becf", "#bcbd22")

RC_PARAMS = {
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2,
    "font.size": 9, "legend.frameon": False,
}
# The debugging pages are dense: legends get a light background over the lines.
DEBUG_RC = {"legend.frameon": True, "legend.framealpha": 0.85, "legend.edgecolor": "none",
            "legend.facecolor": "white"}
plt.rcParams.update({**RC_PARAMS, **DEBUG_RC})

TABLES = ("runs", "macro", "groups", "firms", "plants", "events", "flows")
TEXT_EVENT_COLUMNS = ("group", "rule", "tech", "other_tech", "cause")

# Parameters a plot needs, with the values of parameters.py as fallback when a folder
# has no runs table (the reference runs written before phase 5).
DEFAULTS = {"price_band": 0.025, "u_war": 0.95, "u_max": 1.2, "overtime_premium": 0.10}


def _read(path: Path) -> pd.DataFrame | None:
    parquet, csv = path.with_suffix(".parquet"), path.with_suffix(".csv")
    if parquet.exists():
        return pd.read_parquet(parquet)
    if csv.exists():
        return pd.read_csv(csv)
    return None


@dataclass
class Run:
    """The tables of one run folder, as DataFrames (None when a table is missing)."""

    path: Path
    tables: dict = field(default_factory=dict)

    def __getattr__(self, name):
        tables = self.__dict__.get("tables", {})
        if name in tables:
            return tables[name]
        raise AttributeError(name)

    @property
    def name(self) -> str:
        return self.path.name

    def param(self, name: str):
        runs = self.tables.get("runs")
        if runs is not None and name in runs:
            return runs[name].iloc[0]
        return DEFAULTS[name]

    @property
    def t(self) -> pd.Series:
        return self.macro["t"]

    def wars(self) -> list[tuple[int, int]]:
        """Industry price wars, (first, last) period of each maximal run of war_on, as
        the collector defines them (choices.md)."""
        if "war_on" not in self.macro:
            return []
        runs, start, last = [], None, None
        for t, on in zip(self.macro["t"], self.macro["war_on"].astype(bool)):
            if on and start is None:
                start = t
            if not on and start is not None:
                runs.append((start, last))
                start = None
            last = t
        if start is not None:
            runs.append((start, last))
        return runs

    def out_dir(self) -> Path:
        out = self.path / "debug"
        out.mkdir(parents=True, exist_ok=True)
        return out


def load(run_dir) -> Run:
    """Read every table of a run folder. Text columns of events read as "" when empty."""
    path = Path(run_dir)
    if not path.is_dir():
        raise SystemExit(f"{path} is not a folder: give the folder run.py wrote (--out)")
    tables = {}
    for name in TABLES:
        frame = _read(path / name)
        if frame is None:
            continue
        if name == "events":
            for column in TEXT_EVENT_COLUMNS:
                if column in frame:
                    frame[column] = frame[column].fillna("").astype(str)
        if name == "firms":
            for column in ("exit_cause", "tech_new", "tech_other"):
                if column in frame:
                    frame[column] = frame[column].fillna("").astype(str)
        if name == "plants" and "retire_cause" in frame:
            frame["retire_cause"] = frame["retire_cause"].fillna("").astype(str)
        tables[name] = frame
    if "macro" not in tables:
        raise SystemExit(f"{path} holds no macro table: run `python run.py --out {path}`")
    return Run(path, tables)


def _fallback(name: str, known: dict, names) -> str:
    others = sorted(n for n in names if n not in known)
    return EXTRA_COLORS[others.index(name) % len(EXTRA_COLORS)] if name in others else MUTED


def label_color(label: str, labels=()) -> str:
    if label in TYPE_STYLE:
        return TYPE_STYLE[label]["color"]
    return _fallback(label, TYPE_STYLE, set(labels) | {label})


def tech_color(tech: str, techs=()) -> str:
    """Colour of a technique; for an order of several techniques ("C+D2"), the first."""
    tech = str(tech).split("+")[0]
    if tech in TECHNIQUE_COLOR:
        return TECHNIQUE_COLOR[tech]
    return _fallback(tech, TECHNIQUE_COLOR, set(techs) | {tech})


def shade_wars(ax, run: Run, label: bool = False) -> None:
    """Shade the industry price wars on a time axis."""
    for n, (start, end) in enumerate(run.wars()):
        ax.axvspan(start - 0.5, end + 0.5, **WAR_SHADE,
                   label="price war" if label and n == 0 else None)


def mark_exit(ax, rows: pd.DataFrame, column: str, color=INK) -> None:
    """A cross at the end of a firm's line when the firm left in its last period."""
    if rows.empty or "exited" not in rows:
        return
    last = rows.iloc[-1]
    if bool(last["exited"]) and pd.notna(last[column]):
        ax.plot(last["t"], last[column], marker="x", color=color, markersize=7,
                markeredgewidth=1.8, linestyle="none", zorder=5)


def firm_title(rows: pd.DataFrame, firm_id) -> str:
    first = rows.iloc[0]
    rule = f", {first['rule']}" if "rule" in rows else ""
    return f"firm {firm_id} ({first['group']}{rule}, born {first['born']})"


def save(run: Run, figures, out: Path | None = None) -> list[Path]:
    """Write each (name, figure) to out (default RUN_DIR/debug) as PNG and close it."""
    out = out or run.out_dir()
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, fig in figures:
        path = out / f"{name}.png"
        fig.savefig(path, dpi=130)
        plt.close(fig)
        paths.append(path)
    return paths


def parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("run_dir", type=Path, help="folder written by run.py (--out)")
    return p


def run_script(module_doc: str, figures, add_arguments=None, argv=None) -> list[Path]:
    """The command line every script shares: RUN_DIR plus the script's own options."""
    p = parser(module_doc.strip().split("\n\n")[0])
    if add_arguments:
        add_arguments(p)
    args = p.parse_args(argv)
    run = load(args.run_dir)
    options = {k: v for k, v in vars(args).items() if k != "run_dir"}
    paths = save(run, figures(run, **options))
    for path in paths:
        print(path)
    return paths
