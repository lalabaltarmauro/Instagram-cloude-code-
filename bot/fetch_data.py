"""Download OHLC data into data/*.csv (columns: time, open, high, low, close).

Forex only, from Yahoo Finance:
  *_4h: 1h bars (about 2 years max on Yahoo) resampled to 4h.
  *_1d: daily bars since 2004.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"


PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "EURJPY", "GBPJPY"]


def yahoo(ticker: str, tf: str) -> pd.DataFrame:
    import yfinance as yf
    if tf == "4h":
        d = yf.download(ticker, interval="1h", period="730d", progress=False, auto_adjust=False)
    else:
        d = yf.download(ticker, interval="1d", start="2004-01-01", progress=False, auto_adjust=False)
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    d = d.rename(columns=str.lower)[["open", "high", "low", "close"]]
    d.index = pd.to_datetime(d.index, utc=True)
    if tf == "4h":
        d = d.resample("4h").agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    d = d.dropna()
    # Yahoo forex has some broken bars (high == low or high < close); drop them
    d = d[(d["high"] > d["low"]) & (d["high"] >= d[["open", "close"]].max(axis=1))
          & (d["low"] <= d[["open", "close"]].min(axis=1))]
    d.index.name = "time"
    return d.reset_index()


def main() -> None:
    DATA.mkdir(exist_ok=True)
    jobs = {f"{p}_{tf}": (lambda p=p, tf=tf: yahoo(f"{p}=X", tf)) for p in PAIRS for tf in ("4h", "1d")}
    for name, fn in jobs.items():
        if len(sys.argv) > 1 and name not in sys.argv[1:]:
            continue
        df = fn()
        df.to_csv(DATA / f"{name}.csv", index=False)
        print(f"{name}: {len(df)} bars {df['time'].iloc[0]} -> {df['time'].iloc[-1]}")


if __name__ == "__main__":
    main()
