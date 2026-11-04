"""Every debugging page of one run in one PDF: RUN_DIR/debug/report.pdf.

    python -m debug.report RUN_DIR

Runs checks, firm_panel --all, plant_gantt, merit_order at three representative periods,
events_timeline, capacity_bridge and flow_matrix, in that order, and writes their pages
with matplotlib's PdfPages (no PNGs). The periods of the merit order: the first period of
the first price war, the first rebuild (the first period in which plants are retired at
step 4 and plants are ordered) and the last period; a period that does not exist in the
run is skipped and duplicates are dropped. A page whose tables the folder lacks (a run
written before the collector's event log or groups table) is skipped with a note.
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from debug import (capacity_bridge, checks, events_timeline, firm_panel, flow_matrix,
                   merit_order, plant_gantt)
from debug._common import load


def representative_periods(run) -> list[int]:
    periods = []
    wars = run.wars()
    if wars:
        periods.append(int(wars[0][0]))
    events = run.tables.get("events")
    if events is not None:
        retired = set(events[(events["event"] == "retire") & (events["step"] == 4)]["t"])
        ordered = set(events[events["event"] == "order"]["t"])
        rebuilds = sorted(retired & ordered)
        if rebuilds:
            periods.append(int(rebuilds[0]))
    periods.append(int(run.t.max()))
    return sorted(set(periods))


# Each page's script and the tables it needs; a page whose tables the folder lacks (a
# run written before the collector's phase 3 or 4) is skipped with a note.
NEEDS = {
    "checks": ("macro",), "firm_panel": ("firms", "plants"),
    "plant_gantt": ("firms", "plants"), "merit_order": ("firms", "plants"),
    "events_timeline": ("firms", "events"), "capacity_bridge": ("groups",),
    "flow_matrix": ("flows",),
}


def pages(run):
    def wanted(name):
        if run.has(*NEEDS[name]):
            return True
        print(f"skipping {name}: no {', '.join(NEEDS[name])} table in {run.path}")
        return False

    if wanted("checks"):
        yield from checks.figures(run)
    if wanted("firm_panel"):
        yield from firm_panel.figures(run, all=True)
    if wanted("plant_gantt"):
        yield from plant_gantt.figures(run)
    if wanted("merit_order"):
        for t in representative_periods(run):
            yield from merit_order.figures(run, t=[t])
    if wanted("events_timeline"):
        yield from events_timeline.figures(run)
    if wanted("capacity_bridge"):
        yield from capacity_bridge.figures(run)
    if wanted("flow_matrix"):
        yield from flow_matrix.figures(run)


def main(argv=None) -> Path:
    p = argparse.ArgumentParser(description=__doc__.strip().split("\n\n")[0])
    p.add_argument("run_dir", type=Path, help="folder written by run.py (--out)")
    args = p.parse_args(argv)
    run = load(args.run_dir)
    print(checks.report(run))
    path = run.out_dir() / "report.pdf"
    n = 0
    with PdfPages(path) as pdf:
        for _, fig in pages(run):
            pdf.savefig(fig)
            plt.close(fig)
            n += 1
    print(f"{path} ({n} pages)")
    return path


if __name__ == "__main__":
    main()
