"""The neutral control of the critique (section 6): two groups that follow the same hurdle
rule under different labels, over the same seeds as the mixed population.

    python -m experiments.neutral_control [--seeds N] [--periods T] [--out DIR] [overrides]

Under neutral drift a label takes over in a share of seeds equal to its starting share
(one half here); every mixed-population result must beat that benchmark. The script runs
three populations over seeds 1..N: the mixed population of parameters.py (shaikh =
unit_cost, okishio = profit_rate), both labels on the unit-cost rule, and both labels on
the profit-rate rule. For each it reports the share of seeds in which the label "shaikh"
holds more than half of the producing capacity at the last period, with a 95 % Wilson
interval, and the mean final capacity and sales shares of that label. The rows go to
DIR/neutral_control.csv; one line per seed and population goes to
DIR/neutral_control_seeds.csv. Overrides are parameter assignments such as
PRICING_RULE=leader_follow or CHI=2 (values parsed as Python literals, strings as is).
"""

import argparse
import ast
import math
from pathlib import Path

import pandas as pd

import run
from model import Industry

ROOT = Path(__file__).resolve().parent.parent

POPULATIONS = {
    "mixed": None,  # HURDLE_RULES of parameters.py (or of the overrides)
    "all_unit_cost": {"shaikh": "unit_cost", "okishio": "unit_cost"},
    "all_profit_rate": {"shaikh": "profit_rate", "okishio": "profit_rate"},
}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95 % Wilson interval for a share of k successes in n trials."""
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def final_shares(industry) -> tuple[float, float]:
    """Capacity and sales shares of the label "shaikh" in the last period."""
    last = industry.history[-1]
    capacity = last["capacity_shaikh"] + last["capacity_okishio"]
    sales = last["sales_shaikh"] + last["sales_okishio"]
    return (last["capacity_shaikh"] / capacity if capacity > 0.0 else float("nan"),
            last["sales_shaikh"] / sales if sales > 0.0 else float("nan"))


def run_seed(seed: int, periods: int, rules, **overrides) -> dict:
    config = run.configure(seed, **overrides)
    if rules is not None:
        config.HURDLE_RULES = dict(rules)
    config.PERIODS = periods
    industry = Industry(config)
    industry.run()
    capacity_share, sales_share = final_shares(industry)
    return {
        "seed": seed,
        "capacity_share_shaikh": capacity_share,
        "sales_share_shaikh": sales_share,
        "shaikh_wins": capacity_share > 0.5,
        "n_firms": industry.history[-1]["n_firms"],
    }


def neutral_control(seeds: int, periods: int, **overrides) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summary rows (one per population) and seed rows (one per seed and population)."""
    rows, summary = [], []
    for population, rules in POPULATIONS.items():
        results = [run_seed(seed, periods, rules, **overrides) for seed in range(1, seeds + 1)]
        for r in results:
            rows.append({"population": population, **r})
        wins = sum(r["shaikh_wins"] for r in results)
        low, high = wilson(wins, len(results))
        summary.append({
            "population": population,
            "seeds": len(results),
            "shaikh_wins": wins,
            "share_won": wins / len(results),
            "won_low": low,
            "won_high": high,
            "mean_capacity_share": sum(r["capacity_share_shaikh"] for r in results) / len(results),
            "mean_sales_share": sum(r["sales_share_shaikh"] for r in results) / len(results),
        })
    return pd.DataFrame(summary), pd.DataFrame(rows)


def parse_overrides(items: list[str]) -> dict:
    overrides = {}
    for item in items:
        name, _, value = item.partition("=")
        if not _ or not name.isupper():
            raise SystemExit(f"override must look like NAME=value with an upper-case NAME: {item}")
        try:
            overrides[name] = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            overrides[name] = value
    return overrides


def main(argv=None) -> pd.DataFrame:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--seeds", type=int, default=50, help="seeds 1..N (default 50)")
    parser.add_argument("--periods", type=int, default=None,
                        help="periods per run (default: PERIODS of parameters.py)")
    parser.add_argument("--out", type=Path, default=ROOT / "outputs" / "experiments")
    parser.add_argument("overrides", nargs="*", help="NAME=value parameter overrides")
    args = parser.parse_args(argv)
    overrides = parse_overrides(args.overrides)
    periods = args.periods if args.periods is not None else run.configure().PERIODS
    summary, rows = neutral_control(args.seeds, periods, **overrides)
    args.out.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.out / "neutral_control.csv", index=False)
    rows.to_csv(args.out / "neutral_control_seeds.csv", index=False)
    print(summary.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print(f"\nSeeds 1-{args.seeds}, {periods} periods, overrides {overrides or 'none'}. "
          f"Saved in: {args.out}")
    return summary


if __name__ == "__main__":
    main()
