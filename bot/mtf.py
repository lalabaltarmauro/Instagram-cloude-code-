"""Higher-timeframe levels and trend filters for the S/R flip strategy.

Only higher-timeframe (HTF) bars that are fully closed when the lower-timeframe
(LTF) bar closes are used, so there is no look-ahead.

- Levels: pivots of the HTF (e.g. daily levels for H4 entries, weekly levels
  for D1 entries), merged into zones of +-`zone_htf_atr` * HTF ATR.
- Trend "ema": daily close above its 200 EMA -> longs only, below -> shorts only.
- Trend "structure": last two daily swing highs and lows both rising -> longs only,
  both falling -> shorts only, mixed -> no trades.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from sr_strategy import atr, build_levels, pivots


@dataclass
class MTFParams:
    htf_pivot_len: int = 5
    htf_lookback: int = 250      # HTF bars of pivots used for levels
    zone_htf_atr: float = 0.25   # zone half-width in HTF ATRs
    min_touches: int = 2
    ema_len: int = 200
    trend_pivot_len: int = 5


def to_weekly(daily: pd.DataFrame) -> pd.DataFrame:
    """Weekly bars (Monday-based) from daily bars; index = week start."""
    w = daily.resample("W-MON", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    return w


def closed_index(ltf_times: pd.DatetimeIndex, ltf_period: pd.Timedelta,
                 htf_times: pd.DatetimeIndex, htf_period: pd.Timedelta) -> np.ndarray:
    """For each LTF bar, index of the last HTF bar closed by the time the LTF bar closes (-1 if none)."""
    ltf_close = (ltf_times + ltf_period).values
    htf_close = (htf_times + htf_period).values
    return np.searchsorted(htf_close, ltf_close, side="right") - 1


def htf_levels_fn(htf: pd.DataFrame, idx: np.ndarray, M: MTFParams):
    """levels_at(i, atr_i) for sr_strategy.backtest, using HTF pivots."""
    hh, ll = htf["high"].values, htf["low"].values
    ph, pl = pivots(htf, M.htf_pivot_len)
    a_h = atr(htf, 14)
    k = M.htf_pivot_len
    cache: dict[int, tuple] = {}

    def levels_at(i: int, _atr_i: float):
        j = int(idx[i])
        if j in cache:
            return cache[j]
        if j < k + 14 or np.isnan(a_h[j]):
            cache[j] = ([], 0.0)
            return cache[j]
        rng = np.arange(max(j - M.htf_lookback, 0), j - k + 1)   # pivots confirmed by HTF bar j
        prices = np.concatenate([hh[rng][ph[rng]], ll[rng][pl[rng]]])
        z = M.zone_htf_atr * a_h[j]
        cache[j] = (build_levels(prices, 2 * z, M.min_touches), z)
        return cache[j]

    return levels_at


def trend_fn(daily: pd.DataFrame, idx: np.ndarray, mode: str, M: MTFParams):
    """side_ok(i) for sr_strategy.backtest from a daily trend definition."""
    c = daily["close"].values
    if mode == "ema":
        e = daily["close"].ewm(span=M.ema_len, adjust=False).mean().values

        def side_ok(i: int):
            j = int(idx[i])
            if j < M.ema_len:
                return ()
            return (1,) if c[j] > e[j] else (-1,)
        return side_ok

    if mode == "structure":
        k = M.trend_pivot_len
        ph, pl = pivots(daily, k)
        hh, ll = daily["high"].values, daily["low"].values
        hi_idx, lo_idx = np.flatnonzero(ph), np.flatnonzero(pl)

        def side_ok(i: int):
            j = int(idx[i])
            hs = hi_idx[hi_idx <= j - k][-2:]     # pivots confirmed by daily bar j
            ls = lo_idx[lo_idx <= j - k][-2:]
            if len(hs) < 2 or len(ls) < 2:
                return ()
            up = hh[hs[1]] > hh[hs[0]] and ll[ls[1]] > ll[ls[0]]
            down = hh[hs[1]] < hh[hs[0]] and ll[ls[1]] < ll[ls[0]]
            return (1,) if up else (-1,) if down else ()
        return side_ok

    raise ValueError(mode)
