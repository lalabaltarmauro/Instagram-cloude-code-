"""Run the S/R flip backtest on every CSV in data/ and write results/.

    python bot/fetch_data.py
    python bot/run_backtest.py
"""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pandas as pd

from sr_strategy import Params, backtest, stats, trades_frame

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT = ROOT / "data", ROOT / "results"

# Cost per side in % of price: fees + spread + slippage, roughly what an MT5 broker charges.
COSTS = {"BTCUSDT_4h": 0.06, "EURUSD_4h": 0.005, "XAUUSD_4h": 0.01}


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["time"])
    return df.set_index("time").sort_index()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    summary = {}
    for path in sorted(DATA.glob("*.csv")):
        name = path.stem
        df = load(path)
        P = Params(cost_pct=COSTS.get(name, 0.05))
        trades, eq = backtest(df, P)
        s = stats(trades, eq)
        s["buy_and_hold_%"] = round(100 * (df["close"].iloc[-1] / df["close"].iloc[P.lookback] - 1), 1)

        # in-sample / out-of-sample split by time (first 60% / last 40%)
        cut = df.index[int(len(df) * 0.6)]
        for label, part in (("first_60%", df[df.index < cut]), ("last_40%", df[df.index >= cut])):
            tr, e = backtest(part, P)
            s[label] = stats(tr, e)

        # robustness: one parameter at a time
        grid = {}
        for key, vals in {"rr": [1.5, 3.0], "zone_atr": [0.3, 0.8], "pivot_len": [3, 8],
                          "max_break_age": [15, 60]}.items():
            for v in vals:
                tr, e = backtest(df, replace(P, **{key: v}))
                st = stats(tr, e)
                grid[f"{key}={v}"] = {k: st.get(k) for k in ("trades", "win_rate_%", "profit_factor",
                                                             "net_return_%", "max_drawdown_%")}
        s["sensitivity"] = grid
        summary[name] = s

        trades_frame(trades).to_csv(OUT / f"{name}_trades.csv", index=False)
        eq.to_csv(OUT / f"{name}_equity.csv", header=["equity"])
        print(name, json.dumps({k: v for k, v in s.items() if k != "sensitivity"}, default=str))

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
