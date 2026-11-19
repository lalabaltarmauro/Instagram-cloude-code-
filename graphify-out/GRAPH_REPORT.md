# Graph Report - Instagram-cloude-code-  (2026-11-19)

## Corpus Check
- 15 files · ~8,997 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 38 file(s) not represented in the graph (top: .csv 36, (none) 1, .mq5 1)
- WARNING: 38 of 55 files seen (69%) have no supported extractor and are missing from this graph entirely. It may look complete while representing only part of the codebase.

## Summary
- 106 nodes · 196 edges · 10 communities (8 shown, 2 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f0435195`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- fetch_data.py
- sr_strategy.py
- caveman
- Rules
- run_backtest.py
- Bot de soporte/resistencia horizontal (flip y retest)
- CLAUDE.md
- .claude/CLAUDE.md
- run_trend_backtest.py
- Prompt para el agente de trading (MT5)

## God Nodes (most connected - your core abstractions)
1. `backtest()` - 15 edges
2. `main()` - 13 edges
3. `htf_levels_fn()` - 11 edges
4. `trend_fn()` - 10 edges
5. `main()` - 10 edges
6. `Rules` - 10 edges
7. `pivots()` - 9 edges
8. `closed_index()` - 8 edges
9. `build_levels()` - 8 edges
10. `stats()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `variants()` --calls--> `htf_levels_fn()`  [EXTRACTED]
  bot/run_trend_backtest.py → bot/mtf.py
- `levels_at()` --calls--> `build_levels()`  [EXTRACTED]
  bot/mtf.py → bot/sr_strategy.py
- `trend_fn()` --calls--> `pivots()`  [EXTRACTED]
  bot/mtf.py → bot/sr_strategy.py
- `main()` --calls--> `load()`  [EXTRACTED]
  bot/run_trend_backtest.py → bot/run_backtest.py
- `main()` --calls--> `params_for()`  [EXTRACTED]
  bot/run_trend_backtest.py → bot/run_backtest.py

## Import Cycles
- None detected.

## Communities (10 total, 2 thin omitted)

### Community 0 - "fetch_data.py"
Cohesion: 0.16
Nodes (3): main(), yahoo(), load()

### Community 1 - "sr_strategy.py"
Cohesion: 0.27
Nodes (6): htf_levels_fn(), levels_at(), atr(), backtest(), build_levels(), pivots()

### Community 2 - "caveman"
Cohesion: 0.17
Nodes (10): caveman, Example output, How to invoke, See also, What it does, caveman, Persistence, Pre-send check (+2 more)

### Community 3 - "Rules"
Cohesion: 0.20
Nodes (10): 1. Answer first, 2. Kill ceremony, 3. Short word, 4. Articles optional, meaning never, 5. One idea per sentence, 6. Payload verbatim, 7. Tool runs: bounded status, 8. User's language (+2 more)

### Community 4 - "run_backtest.py"
Cohesion: 0.21
Nodes (7): main(), params_for(), pooled(), find_signal(), Params, Trade, trades_frame()

### Community 5 - "Bot de soporte/resistencia horizontal (flip y retest)"
Cohesion: 0.22
Nodes (8): Archivos, Backtest en MT5, Backtest en Python, Bot de soporte/resistencia horizontal (flip y retest), Con las reglas del video (solo a favor de la tendencia, niveles de temporalidad mayor), Opciones del EA (reglas del video), Reglas, Resultados (divisas, 9 pares: majors + EURJPY y GBPJPY; datos de Yahoo, costo ~1 pip ida y vuelta)

### Community 8 - "run_trend_backtest.py"
Cohesion: 0.17
Nodes (7): closed_index(), MTFParams, to_weekly(), trend_fn(), main(), variants(), stats()

### Community 9 - "Prompt para el agente de trading (MT5)"
Cohesion: 0.33
Nodes (5): Configuraciones a probar, Código del EA (SR_Flip_EA.mq5), Estrategia (flip y retest de soporte/resistencia), Pasos, Prompt para el agente de trading (MT5)

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `backtest()` connect `sr_strategy.py` to `run_trend_backtest.py`, `fetch_data.py`, `run_backtest.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `trend_fn()` connect `run_trend_backtest.py` to `sr_strategy.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._