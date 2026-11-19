# Bot de soporte/resistencia horizontal (flip y retest)

Bot basado en el video "Technical Analysis Series – Horizontal Support/Resistance" (CryptoCred).

## Reglas
1. Máximos y mínimos de giro (pivots) con 5 velas a cada lado.
2. Los pivots cercanos (zona = ±0,5 ATR) se agrupan en un nivel; hacen falta al menos 2 toques.
3. **Flip**: el precio cierra al otro lado de la zona (resistencia rota → soporte, y al revés).
4. **Retest**: en las 30 velas siguientes vuelve a la zona y cierra con una vela a favor.
5. Stop: zona + 1 ATR. Objetivo: 2R. Riesgo: 1 % del capital por operación, una posición a la vez.

## Archivos
- `mt5/SR_Flip_EA.mq5`: Expert Advisor para MetaTrader 5.
- `bot/sr_strategy.py`: la misma lógica en Python, con el backtester.
- `bot/fetch_data.py`, `bot/run_backtest.py`, `bot/plot_results.py`: datos, backtest y gráfico.
- `bot/mtf.py`, `bot/run_trend_backtest.py`: reglas del video (niveles de temporalidad mayor y filtro de tendencia) y su comparación; resultados en `results/trend/`.
- `results/`: resumen (`summary.json`), operaciones (`*_trades.csv`) y `equity.png`.
- `prompt_agente_trading.md`: prompt con el EA para que un agente lo pruebe en MT5.

## Backtest en Python
```bash
pip install -r requirements.txt
python bot/fetch_data.py
python bot/run_backtest.py
python bot/plot_results.py
python bot/run_trend_backtest.py
```

## Opciones del EA (reglas del video)
- `InpLevelTF`: temporalidad de los niveles. `PERIOD_D1` para entrar en H4 (por defecto), `PERIOD_W1` para entrar en D1, `PERIOD_CURRENT` = niveles del propio gráfico.
- `InpTrendMode`: `TREND_EMA` (cierre diario vs EMA 200, por defecto), `TREND_STRUCTURE` (máximos y mínimos crecientes/decrecientes) o `TREND_NONE`.

## Backtest en MT5
1. Copia `mt5/SR_Flip_EA.mq5` en `MQL5/Experts/` (Archivo → Abrir carpeta de datos).
2. Ábrelo en MetaEditor y compílalo (F7).
3. Probador de estrategias (Ctrl+R): Experto `SR_Flip_EA`, símbolo (EURUSD, GBPUSD, USDJPY…), periodo **H4**,
   modelado "1 minuto OHLC" o "Cada tick basado en ticks reales", depósito 10 000.

Diferencias con Python: MT5 calcula el ATR con media simple (Python usa Wilder) y entra al ask/bid con el spread real del broker.

## Resultados (divisas, 9 pares: majors + EURJPY y GBPJPY; datos de Yahoo, costo ~1 pip ida y vuelta)

| Temporalidad | Periodo | Operaciones | Ganadoras | Profit factor | Total |
|---|---|---|---|---|---|
| H4 | 2024–2026 | 1021 | 33,5 % | 0,98 | −13,9R |
| D1 | 2004–2026 | 1042 | 32,0 % | 0,92 | −55,4R |

Con objetivo 2R el punto de equilibrio es 33 % de aciertos: tal como está, la estrategia no tiene ventaja.

### Con las reglas del video (solo a favor de la tendencia, niveles de temporalidad mayor)

| Variante | Entradas / niveles | Operaciones | Ganadoras | Profit factor | Total |
|---|---|---|---|---|---|
| Original | H4 / H4 | 1021 | 33,5 % | 0,98 | −13,9R |
| Video: niveles D1 + EMA 200 | H4 / D1 | 511 | 30,9 % | 0,87 | −45,7R |
| Video: niveles D1 + estructura | H4 / D1 | 355 | 35,2 % | 1,06 | +14,3R |
| Original | D1 / D1 | 1042 | 32,0 % | 0,92 | −55,4R |
| Video: niveles W1 + EMA 200 | D1 / W1 | 586 | 33,3 % | 0,97 | −10,8R |
| Video: niveles W1 + estructura | D1 / W1 | 472 | 32,4 % | 0,95 | −17,5R |

La única variante positiva (H4 con estructura) pasa de profit factor 1,28 en el primer 60 % del periodo a 0,87 en el último 40 %: no es una ventaja estable.
