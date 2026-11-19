# Graph Report - Instagram-cloude-code-  (2026-11-19)

## Corpus Check
- 12 files · ~6,037 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: .csv 18, (none) 1, .mq5 1)
- WARNING: 20 of 34 files seen (59%) have no supported extractor and are missing from this graph entirely. It may look complete while representing only part of the codebase.

## Summary
- 79 nodes · 118 edges · 12 communities (7 shown, 5 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `733d8d40`
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
- sr_strategy.py
- Prompt para el agente de trading (MT5)
- pandas
- find_signal

## God Nodes (most connected - your core abstractions)
1. `backtest()` - 12 edges
2. `main()` - 10 edges
3. `Rules` - 10 edges
4. `Bot de soporte/resistencia horizontal (flip y retest)` - 6 edges
5. `trades_frame()` - 6 edges
6. `stats()` - 6 edges
7. `pivots()` - 6 edges
8. `caveman` - 6 edges
9. `load()` - 5 edges
10. `Params` - 5 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `backtest()`  [EXTRACTED]
  bot/run_backtest.py → bot/sr_strategy.py
- `main()` --calls--> `stats()`  [EXTRACTED]
  bot/run_backtest.py → bot/sr_strategy.py
- `main()` --calls--> `trades_frame()`  [EXTRACTED]
  bot/run_backtest.py → bot/sr_strategy.py
- `params_for()` --calls--> `Params`  [EXTRACTED]
  bot/run_backtest.py → bot/sr_strategy.py

## Import Cycles
- None detected.

## Communities (12 total, 5 thin omitted)

### Community 1 - "sr_strategy.py"
Cohesion: 0.42
Nodes (4): atr(), backtest(), build_levels(), pivots()

### Community 2 - "caveman"
Cohesion: 0.17
Nodes (10): caveman, Example output, How to invoke, See also, What it does, caveman, Persistence, Pre-send check (+2 more)

### Community 3 - "Rules"
Cohesion: 0.20
Nodes (10): 1. Answer first, 2. Kill ceremony, 3. Short word, 4. Articles optional, meaning never, 5. One idea per sentence, 6. Payload verbatim, 7. Tool runs: bounded status, 8. User's language (+2 more)

### Community 4 - "run_backtest.py"
Cohesion: 0.39
Nodes (4): main(), params_for(), pooled(), Params

### Community 5 - "Bot de soporte/resistencia horizontal (flip y retest)"
Cohesion: 0.29
Nodes (6): Archivos, Backtest en MT5, Backtest en Python, Bot de soporte/resistencia horizontal (flip y retest), Reglas, Resultados (divisas, 9 pares: majors + EURJPY y GBPJPY; datos de Yahoo, costo ~1 pip ida y vuelta)

### Community 8 - "sr_strategy.py"
Cohesion: 0.38
Nodes (3): stats(), Trade, trades_frame()

### Community 9 - "Prompt para el agente de trading (MT5)"
Cohesion: 0.40
Nodes (4): Código del EA (SR_Flip_EA.mq5), Estrategia (flip y retest de soporte/resistencia), Pasos, Prompt para el agente de trading (MT5)

## Knowledge Gaps
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `caveman` connect `caveman` to `Rules`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `Rules` connect `Rules` to `caveman`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `backtest()` connect `sr_strategy.py` to `sr_strategy.py`, `pandas`, `find_signal`, `run_backtest.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._