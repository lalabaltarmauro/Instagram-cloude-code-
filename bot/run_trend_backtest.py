"""Compare the S/R flip strategy with and without the video's rules on forex:

  base         levels from the entry timeframe, both directions (original bot)
  trend        + only trade with the daily trend (close vs 200 EMA)
  htf          levels from the higher timeframe, both directions
  htf+trend    higher-timeframe levels + daily EMA trend   <- main "as in the video"
  htf+struct   higher-timeframe levels + daily market structure (HH/HL, LH/LL)

Two setups:
  H4 entries, daily levels    (Yahoo H4 data: 2024-2026)
  D1 entries, weekly levels   (Yahoo D1 data: 2004-2026)

    python bot/fetch_data.py && python bot/run_trend_backtest.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from mtf import MTFParams, closed_index, htf_levels_fn, to_weekly, trend_fn
from fetch_data import PAIRS
from run_backtest import load, params_for, pooled
from sr_strategy import backtest, stats, trades_frame

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT = ROOT / "data", ROOT / "results" / "trend"
MAIN = "htf+trend"
H4, D1, W1 = pd.Timedelta(hours=4), pd.Timedelta(days=1), pd.Timedelta(days=7)


def variants(ltf: pd.DataFrame, ltf_period, daily: pd.DataFrame, htf: pd.DataFrame, htf_period, M):
    d_idx = closed_index(ltf.index, ltf_period, daily.index, D1)
    h_idx = closed_index(ltf.index, ltf_period, htf.index, htf_period)
    lv = htf_levels_fn(htf, h_idx, M)
    ema = trend_fn(daily, d_idx, "ema", M)
    return {
        "base": {},
        "trend": {"side_ok": ema},
        "htf": {"levels_at": lv},
        "htf+trend": {"levels_at": lv, "side_ok": ema},
        "htf+struct": {"levels_at": lv, "side_ok": trend_fn(daily, d_idx, "structure", M)},
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    M = MTFParams()
    summary: dict = {}
    for setup, tf, period in (("H4 entries / D1 levels", "4h", H4), ("D1 entries / W1 levels", "1d", D1)):
        pooled_r: dict[str, list] = {}
        split_r: dict[str, dict[str, list]] = {}
        per_pair = {}
        for pair in PAIRS:
            path = DATA / f"{pair}_{tf}.csv"
            if not path.exists():
                continue
            ltf = load(path)
            daily = load(DATA / f"{pair}_1d.csv")
            htf, htf_period = (daily, D1) if tf == "4h" else (to_weekly(daily), W1)
            P = params_for(path.stem)
            cut = ltf.index[int(len(ltf) * 0.6)]
            for name, hooks in variants(ltf, period, daily, htf, htf_period, M).items():
                trades, eq = backtest(ltf, P, **hooks)
                r = np.array([t.r_multiple for t in trades])
                times = pd.to_datetime([t.entry_time for t in trades], utc=True)
                pooled_r.setdefault(name, []).append(r)
                sp = split_r.setdefault(name, {"first_60%": [], "last_40%": []})
                sp["first_60%"].append(r[times < cut])
                sp["last_40%"].append(r[times >= cut])
                if name == MAIN:
                    per_pair[pair] = stats(trades, eq)
                    trades_frame(trades).to_csv(OUT / f"{pair}_{tf}_trades.csv", index=False)
        summary[setup] = {
            "pooled": {n: {"all": pooled(np.concatenate(v)),
                           **{k: pooled(np.concatenate(x)) for k, x in split_r[n].items()}}
                       for n, v in pooled_r.items()},
            f"per_pair_{MAIN}": per_pair,
        }
        print(f"\n== {setup}")
        for n, s in summary[setup]["pooled"].items():
            a, f, l = s["all"], s["first_60%"], s["last_40%"]
            print(f"  {n:11s} trades {a['trades']:5d}  win {a['win_rate_%']:5}%  PF {a['profit_factor']}  "
                  f"avgR {a['avg_R']:+.3f}  totalR {a['total_R']:+.1f}  | PF first60 {f.get('profit_factor')} "
                  f"last40 {l.get('profit_factor')}")
        for pair, s in per_pair.items():
            print(f"    {pair}: {s}")

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
