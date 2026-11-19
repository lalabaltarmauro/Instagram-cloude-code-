"""Plot cumulative R per forex pair (H4 and D1) from results/*_trades.csv: python bot/plot_results.py"""
import json
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "results"
summary = json.loads((OUT / "summary.json").read_text())

fig, axes = plt.subplots(2, 1, figsize=(11, 10))
for ax, tf, label in zip(axes, ("4h", "1d"), ("H4", "D1")):
    for path in sorted(OUT.glob(f"*_{tf}_trades.csv")):
        tr = pd.read_csv(path, parse_dates=["exit_time"])
        if tr.empty:
            continue
        tr = tr.sort_values("exit_time")
        ax.plot(tr["exit_time"], tr["r_multiple"].cumsum(), lw=1.2, label=path.stem.split("_")[0])
    p = summary["pooled"][tf]["all"]
    ax.axhline(0, color="#111", lw=0.6, ls=":")
    ax.set_title(f"{label} — all pairs: {p['trades']} trades, win {p['win_rate_%']}%, "
                 f"avg {p['avg_R']}R, PF {p['profit_factor']}, total {p['total_R']}R", fontsize=10)
    ax.set_ylabel("Cumulative R (1R = 1% risk)")
    ax.legend(fontsize=8, ncol=5, loc="upper left")
    ax.grid(alpha=0.2)
fig.tight_layout()
fig.savefig(OUT / "equity.png", dpi=110)
