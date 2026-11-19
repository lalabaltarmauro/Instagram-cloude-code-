"""Horizontal support/resistance "flip and retest" strategy plus a simple backtester.

Rules (same logic as mt5/SR_Flip_EA.mq5):
  1. Swing highs/lows: a bar whose high (low) is the highest (lowest) of the
     `pivot_len` bars on each side. A pivot is only known `pivot_len` bars later,
     so it is used from that bar on (no look-ahead).
  2. Levels are zones, not lines: half-width = `zone_atr` * ATR(14).
     Pivots (highs and lows) closer than one zone are merged into one level;
     touches = number of pivots in the level. A level needs >= `min_touches`.
  3. Flip: a close beyond the zone (above for longs, below for shorts) within the
     last `max_break_age` bars, with the close before it on the other side.
  4. Retest: the current bar comes back into the zone, closes on the new side of
     the level and is a candle in the trade direction (bull for long, bear for short).
     No close back through the far edge of the zone since the break.
  5. Entry at the next bar's open. Stop = level -/+ `sl_atr` * ATR beyond the zone.
     Target = `rr` * risk. One position at a time, `risk_pct` of equity per trade.
     If stop and target fall in the same bar, the stop is assumed (conservative).
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

import numpy as np
import pandas as pd


@dataclass
class Params:
    pivot_len: int = 5
    lookback: int = 300          # bars of pivots used to build levels
    zone_atr: float = 0.5        # zone half-width in ATRs
    min_touches: int = 2
    max_break_age: int = 30      # bars between break and retest
    sl_atr: float = 1.0          # stop distance beyond the zone, in ATRs
    rr: float = 2.0
    risk_pct: float = 1.0
    cost_pct: float = 0.05       # cost per side, % of price (fees + spread + slippage)
    atr_len: int = 14


@dataclass
class Trade:
    side: int
    entry_time: pd.Timestamp
    entry: float
    stop: float
    target: float
    level: float
    exit_time: pd.Timestamp | None = None
    exit: float | None = None
    r_multiple: float | None = None
    pnl: float | None = None


def atr(df: pd.DataFrame, n: int) -> np.ndarray:
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    prev_c = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum(h - l, np.maximum(abs(h - prev_c), abs(l - prev_c)))
    # Wilder smoothing, same as MT5 iATR's moving average only approximately; close enough.
    out = np.full(len(tr), np.nan)
    if len(tr) < n:
        return out
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(tr)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def pivots(df: pd.DataFrame, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Boolean arrays: is bar i a swing high / swing low (needs k bars on each side)."""
    h, l = df["high"].values, df["low"].values
    n = len(df)
    ph = np.zeros(n, bool)
    pl = np.zeros(n, bool)
    for i in range(k, n - k):
        win_h = h[i - k:i + k + 1]
        win_l = l[i - k:i + k + 1]
        ph[i] = h[i] == win_h.max()
        pl[i] = l[i] == win_l.min()
    return ph, pl


def build_levels(prices: np.ndarray, zone: float, min_touches: int) -> list[tuple[float, int]]:
    """Cluster pivot prices: sorted, merged while within `zone` of the running mean."""
    if len(prices) == 0:
        return []
    p = np.sort(prices)
    levels = []
    cluster = [p[0]]
    for x in p[1:]:
        if x - np.mean(cluster) <= zone:
            cluster.append(x)
        else:
            levels.append((float(np.mean(cluster)), len(cluster)))
            cluster = [x]
    levels.append((float(np.mean(cluster)), len(cluster)))
    return [lv for lv in levels if lv[1] >= min_touches]


def find_signal(i: int, o, h, l, c, a, level: float, z: float, P: Params) -> int:
    """+1 long, -1 short, 0 none, for a retest on bar i of `level`."""
    # Long: break above, retest from above.
    if l[i] <= level + z and c[i] > level and c[i] > o[i]:
        for j in range(i - 1, max(i - P.max_break_age, 1) - 1, -1):
            if c[j] < level - z:          # closed back below: flip failed
                break
            if c[j] > level + z and c[j - 1] <= level + z:
                return 1
    # Short: break below, retest from below.
    if h[i] >= level - z and c[i] < level and c[i] < o[i]:
        for j in range(i - 1, max(i - P.max_break_age, 1) - 1, -1):
            if c[j] > level + z:
                break
            if c[j] < level - z and c[j - 1] >= level - z:
                return -1
    return 0


def backtest(df: pd.DataFrame, P: Params, start_equity: float = 10_000.0):
    df = df.reset_index()
    t = df["time"].values
    o, h, l, c = (df[x].values for x in ("open", "high", "low", "close"))
    a = atr(df, P.atr_len)
    ph, pl = pivots(df, P.pivot_len)
    n = len(df)
    k = P.pivot_len

    equity = start_equity
    eq_curve = np.full(n, np.nan)
    trades: list[Trade] = []
    pos: Trade | None = None
    size = 0.0
    cost = P.cost_pct / 100

    for i in range(max(P.lookback, P.atr_len) + k, n - 1):
        # --- manage open position on bar i
        if pos is not None:
            hit_stop = (l[i] <= pos.stop) if pos.side == 1 else (h[i] >= pos.stop)
            hit_tgt = (h[i] >= pos.target) if pos.side == 1 else (l[i] <= pos.target)
            exit_px = None
            if hit_stop:
                exit_px = pos.stop
                # gap through the stop: fill at the open
                if (pos.side == 1 and o[i] < pos.stop) or (pos.side == -1 and o[i] > pos.stop):
                    exit_px = o[i]
            elif hit_tgt:
                exit_px = pos.target
                if (pos.side == 1 and o[i] > pos.target) or (pos.side == -1 and o[i] < pos.target):
                    exit_px = o[i]
            if exit_px is not None:
                gross = (exit_px - pos.entry) * pos.side * size
                fees = (pos.entry + exit_px) * size * cost
                pos.pnl = gross - fees
                pos.exit, pos.exit_time = exit_px, pd.Timestamp(t[i])
                pos.r_multiple = pos.pnl / (abs(pos.entry - pos.stop) * size)
                equity += pos.pnl
                trades.append(pos)
                pos = None
        eq_curve[i] = equity

        if pos is not None or np.isnan(a[i]):
            continue

        # --- pivots confirmed by bar i (pivot bar <= i - k), inside the lookback
        lo = i - P.lookback
        idx = np.arange(max(lo, 0), i - k + 1)
        piv_prices = np.concatenate([h[idx][ph[idx]], l[idx][pl[idx]]])
        z = P.zone_atr * a[i]
        levels = build_levels(piv_prices, 2 * z, P.min_touches)
        if not levels:
            continue

        # closest valid level to price that produces a signal
        best = None
        for lv, touches in sorted(levels, key=lambda x: abs(x[0] - c[i])):
            if abs(lv - c[i]) > 3 * z:
                break
            s = find_signal(i, o, h, l, c, a, lv, z, P)
            if s:
                best = (s, lv)
                break
        if best is None:
            continue

        side, lv = best
        entry = o[i + 1]
        stop = lv - (z + P.sl_atr * a[i]) if side == 1 else lv + (z + P.sl_atr * a[i])
        risk = (entry - stop) * side
        if risk <= 0:
            continue
        target = entry + side * P.rr * risk
        size = equity * P.risk_pct / 100 / risk
        pos = Trade(side, pd.Timestamp(t[i + 1]), entry, stop, target, lv)

    eq = pd.Series(eq_curve, index=pd.to_datetime(t)).ffill().dropna()
    return trades, eq


def stats(trades: list[Trade], eq: pd.Series, start_equity: float = 10_000.0) -> dict:
    if not trades:
        return {"trades": 0}
    r = np.array([tr.r_multiple for tr in trades])
    pnl = np.array([tr.pnl for tr in trades])
    wins = pnl[pnl > 0].sum()
    losses = -pnl[pnl < 0].sum()
    dd = (eq / eq.cummax() - 1).min()
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    final = eq.iloc[-1]
    cagr = (final / start_equity) ** (1 / years) - 1 if years > 0 and final > 0 else np.nan
    return {
        "trades": len(trades),
        "longs": sum(1 for tr in trades if tr.side == 1),
        "shorts": sum(1 for tr in trades if tr.side == -1),
        "win_rate_%": round(100 * (pnl > 0).mean(), 1),
        "avg_R": round(r.mean(), 3),
        "profit_factor": round(wins / losses, 2) if losses else np.inf,
        "net_return_%": round(100 * (final / start_equity - 1), 1),
        "cagr_%": round(100 * cagr, 1) if not np.isnan(cagr) else None,
        "max_drawdown_%": round(100 * dd, 1),
        "years": round(years, 1),
    }


def trades_frame(trades: list[Trade]) -> pd.DataFrame:
    return pd.DataFrame([asdict(tr) for tr in trades])
