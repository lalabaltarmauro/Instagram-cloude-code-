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
- `results/`: resumen (`summary.json`), operaciones (`*_trades.csv`) y `equity.png`.

## Backtest en Python
```bash
pip install -r requirements.txt
python bot/fetch_data.py
python bot/run_backtest.py
python bot/plot_results.py .
```

## Backtest en MT5
1. Copia `mt5/SR_Flip_EA.mq5` en `MQL5/Experts/` (Archivo → Abrir carpeta de datos).
2. Ábrelo en MetaEditor y compílalo (F7).
3. Probador de estrategias (Ctrl+R): Experto `SR_Flip_EA`, símbolo (XAUUSD, EURUSD, BTCUSD…), periodo **H4**,
   modelado "1 minuto OHLC" o "Cada tick basado en ticks reales", depósito 10 000.

Diferencias con Python: MT5 calcula el ATR con media simple (Python usa Wilder) y entra al ask/bid con el spread real del broker.
