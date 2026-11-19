"""Plot bot equity vs buy & hold for each market: python bot/plot_results.py ."""
import sys, json
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
root = sys.argv[1]
summ = json.load(open(f"{root}/results/summary.json"))
fig, axes = plt.subplots(3, 1, figsize=(10, 10))
for ax, name in zip(axes, ["BTCUSDT_4h", "EURUSD_4h", "XAUUSD_4h"]):
    eq = pd.read_csv(f"{root}/results/{name}_equity.csv", index_col=0, parse_dates=True)["equity"]
    px = pd.read_csv(f"{root}/data/{name}.csv", index_col=0, parse_dates=True)["close"]
    px.index = pd.to_datetime(px.index, utc=True).tz_localize(None); eq.index = pd.to_datetime(eq.index, utc=True).tz_localize(None)
    px = px[px.index >= eq.index[0]]
    s = summ[name]
    ax.plot(eq.index, eq.values, color="#2563eb", lw=1.4, label="Bot (1% risk/trade)")
    ax.plot(px.index, 10000 * px / px.iloc[0], color="#9ca3af", lw=1, label="Buy & hold")
    ax.axhline(10000, color="#111", lw=0.5, ls=":")
    ax.set_title(f"{name}: {s['trades']} trades, win {s['win_rate_%']}%, PF {s['profit_factor']}, "
                 f"net {s['net_return_%']}%, max DD {s['max_drawdown_%']}%", fontsize=10)
    if name == "BTCUSDT_4h": ax.set_yscale("log")
    ax.legend(fontsize=8, loc="upper left"); ax.grid(alpha=0.2)
fig.tight_layout(); fig.savefig(f"{root}/results/equity.png", dpi=110)
