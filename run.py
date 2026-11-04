"""Run the baseline and write outputs/*.csv."""

from pathlib import Path

import pandas as pd

from model import Industry
from model.collector import events_table


ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(exist_ok=True)

industry = Industry()
industry.run()  # the scheduler asserts stock-flow consistency every period

macro = pd.DataFrame(industry.history)
macro.to_csv(OUTPUTS / "macro.csv", index=False)
pd.DataFrame(industry.firm_history).to_csv(OUTPUTS / "firms.csv", index=False)
pd.DataFrame(industry.plant_history).to_csv(OUTPUTS / "plants.csv", index=False)
pd.DataFrame(industry.flow_history).to_csv(OUTPUTS / "flows.csv", index=False)
pd.DataFrame(events_table(industry)).to_csv(OUTPUTS / "events.csv", index=False)

columns = ["t", "n_firms", "price_avg", "share_shaikh", "share_okishio",
           "capacity_total", "profit_rate", "entries", "exits"]
print(macro[columns].tail().to_string(index=False))
print(f"\nOutputs saved in: {OUTPUTS}")
