# Graph Report - Instagram-cloude-code-  (2026-11-19)

## Corpus Check
- 11 files · ~4,128 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: .csv 3, (none) 1, .mq5 1)

## Summary
- 73 nodes · 111 edges · 8 communities (6 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7c05363e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_backtest.py
- sr_strategy.py
- caveman
- Rules
- fetch_data.py
- Bot de soporte/resistencia horizontal (flip y retest)
- CLAUDE.md
- .claude/CLAUDE.md

## God Nodes (most connected - your core abstractions)
1. `backtest()` - 12 edges
2. `Rules` - 10 edges
3. `main()` - 7 edges
4. `binance()` - 6 edges
5. `pivots()` - 6 edges
6. `stats()` - 6 edges
7. `trades_frame()` - 6 edges
8. `caveman` - 6 edges
9. `load()` - 5 edges
10. `Params` - 5 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `backtest()`  [EXTRACTED]
  bot/run_backtest.py → bot/sr_strategy.py
- `main()` --calls--> `Params`  [EXTRACTED]
  bot/run_backtest.py → bot/sr_strategy.py
- `main()` --calls--> `trades_frame()`  [EXTRACTED]
  bot/run_backtest.py → bot/sr_strategy.py
- `main()` --calls--> `stats()`  [EXTRACTED]
  bot/run_backtest.py → bot/sr_strategy.py

## Import Cycles
- None detected.

## Communities (8 total, 2 thin omitted)

### Community 0 - "run_backtest.py"
Cohesion: 0.15
Nodes (3): load(), main(), stats()

### Community 1 - "sr_strategy.py"
Cohesion: 0.27
Nodes (8): atr(), backtest(), build_levels(), find_signal(), Params, pivots(), Trade, trades_frame()

### Community 2 - "caveman"
Cohesion: 0.17
Nodes (10): caveman, Example output, How to invoke, See also, What it does, caveman, Persistence, Pre-send check (+2 more)

### Community 3 - "Rules"
Cohesion: 0.20
Nodes (10): 1. Answer first, 2. Kill ceremony, 3. Short word, 4. Articles optional, meaning never, 5. One idea per sentence, 6. Payload verbatim, 7. Tool runs: bounded status, 8. User's language (+2 more)

### Community 4 - "fetch_data.py"
Cohesion: 0.43
Nodes (3): binance(), main(), yahoo_4h()

### Community 5 - "Bot de soporte/resistencia horizontal (flip y retest)"
Cohesion: 0.33
Nodes (5): Archivos, Backtest en MT5, Backtest en Python, Bot de soporte/resistencia horizontal (flip y retest), Reglas

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `backtest()` connect `sr_strategy.py` to `run_backtest.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `caveman` connect `caveman` to `Rules`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `Rules` connect `Rules` to `caveman`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._