"""Run the S/R flip backtest on every forex CSV in data/ and write results/.

    python bot/fetch_data.py
    python bot/run_backtest.py
    python bot/plot_results.py
"""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from sr_strategy import Params, backtest, stats, trades_frame

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT = ROOT / "data", ROOT / "results"

# Cost per side in % of price (spread + commission + slippage).
# 0.005% is about 0.5 pip on EURUSD per side, ~1 pip round trip.
COST_MAJOR, COST_CROSS = 0.005, 0.007
CROSSES = {"EURJPY", "GBPJPY"}

SENSITIVITY = {"rr": [1.5, 3.0], "zone_atr": [0.3, 0.8], "pivot_len": [3, 8], "max_break_age": [15, 60]}


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["time"])
    return df.set_index("time").sort_index()


def params_for(name: str) -> Params:
    pair = name.split("_")[0]
    return Params(cost_pct=COST_CROSS if pair in CROSSES else COST_MAJOR)


def pooled(r: np.ndarray) -> dict:
    """Stats over the R multiples of many pairs together."""
    if len(r) == 0:
        return {"trades": 0}
    gains, losses = r[r > 0].sum(), -r[r < 0].sum()
    return {"trades": int(len(r)), "win_rate_%": round(100 * (r > 0).mean(), 1),
            "avg_R": round(float(r.mean()), 3), "total_R": round(float(r.sum()), 1),
            "profit_factor": round(float(gains / losses), 2) if losses else None}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    data = {p.stem: load(p) for p in sorted(DATA.glob("*.csv"))}
    summary: dict = {"per_pair": {}, "pooled": {}, "sensitivity_pooled": {}}

    for tf in ("4h", "1d"):
        names = [n for n in data if n.endswith(f"_{tf}")]
        all_r, first_r, last_r = [], [], []
        for name in names:
            df, P = data[name], params_for(name)
            trades, eq = backtest(df, P)
            s = stats(trades, eq)
            summary["per_pair"][name] = s
            trades_frame(trades).to_csv(OUT / f"{name}_trades.csv", index=False)
            r = np.array([t.r_multiple for t in trades])
            times = pd.to_datetime([t.entry_time for t in trades], utc=True)
            cut = df.index[int(len(df) * 0.6)]
            all_r.append(r)
            first_r.append(r[times < cut])
            last_r.append(r[times >= cut])
            print(name, json.dumps(s))
        summary["pooled"][tf] = {
            "all": pooled(np.concatenate(all_r)),
            "first_60%_of_time": pooled(np.concatenate(first_r)),
            "last_40%_of_time": pooled(np.concatenate(last_r)),
        }
        print(f"POOLED {tf}", json.dumps(summary["pooled"][tf]))

        sens = {}
        for key, vals in SENSITIVITY.items():
            for v in vals:
                rs = [np.array([t.r_multiple for t in backtest(data[n], replace(params_for(n), **{key: v}))[0]])
                      for n in names]
                sens[f"{key}={v}"] = pooled(np.concatenate(rs))
        summary["sensitivity_pooled"][tf] = sens
        for k, v in sens.items():
            print(f"  {tf} {k}: {v}")

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
