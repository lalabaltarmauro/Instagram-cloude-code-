"""Download OHLC data into data/*.csv (columns: time, open, high, low, close).

BTCUSDT 4h comes from Binance's public market-data mirror (no API key).
EURUSD and gold 1h come from Yahoo Finance (about 2 years max) and are resampled to 4h.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import requests

DATA = Path(__file__).resolve().parent.parent / "data"


def binance(symbol: str, interval: str = "4h", start: str = "2017-09-01") -> pd.DataFrame:
    url = "https://data-api.binance.vision/api/v3/klines"
    start_ms = int(pd.Timestamp(start, tz="UTC").timestamp() * 1000)
    rows = []
    while True:
        r = requests.get(url, params={"symbol": symbol, "interval": interval,
                                      "startTime": start_ms, "limit": 1000}, timeout=30)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows += batch
        start_ms = batch[-1][0] + 1
        if len(batch) < 1000:
            break
        time.sleep(0.2)
    df = pd.DataFrame(rows).iloc[:, :5]
    df.columns = ["time", "open", "high", "low", "close"]
    df["time"] = pd.to_datetime(df["time"], unit="ms", utc=True)
    return df.astype({c: float for c in ["open", "high", "low", "close"]})


def yahoo_4h(ticker: str) -> pd.DataFrame:
    import yfinance as yf
    d = yf.download(ticker, interval="1h", period="730d", progress=False, auto_adjust=False)
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    d = d.rename(columns=str.lower)[["open", "high", "low", "close"]]
    d.index = d.index.tz_convert("UTC")
    d = d.resample("4h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    return d.reset_index().rename(columns={d.index.name or "index": "time"})


def main() -> None:
    DATA.mkdir(exist_ok=True)
    jobs = {
        "BTCUSDT_4h": lambda: binance("BTCUSDT"),
        "EURUSD_4h": lambda: yahoo_4h("EURUSD=X"),
        "XAUUSD_4h": lambda: yahoo_4h("GC=F"),   # gold futures as a proxy for XAUUSD spot
    }
    for name, fn in jobs.items():
        if len(sys.argv) > 1 and name not in sys.argv[1:]:
            continue
        df = fn()
        df.to_csv(DATA / f"{name}.csv", index=False)
        print(f"{name}: {len(df)} bars {df['time'].iloc[0]} -> {df['time'].iloc[-1]}")


if __name__ == "__main__":
    main()
