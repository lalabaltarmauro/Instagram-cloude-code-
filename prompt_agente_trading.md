# Prompt para el agente de trading (MT5)

Copia todo este archivo en el chat de tu agente de trading. Incluye la tarea y el código completo del EA.

---

Necesito que hagas un backtest en MetaTrader 5 de un Expert Advisor de soporte/resistencia horizontal.
**No operes en real ni en una cuenta demo: solo el Probador de estrategias.**

## Estrategia (flip y retest de soporte/resistencia)
1. Máximos y mínimos de giro: vela cuyo máximo (mínimo) es el más alto (bajo) de 5 velas a cada lado.
2. Los giros cercanos forman un nivel (zona); un nivel necesita al menos 2 toques.
3. Flip: en las últimas 30 velas el precio cerró al otro lado de la zona (resistencia rota → soporte, y al revés).
4. Retest: la última vela cerrada vuelve a la zona, cierra del lado nuevo y es una vela a favor (alcista para comprar, bajista para vender).
5. Entrada en la apertura de la vela siguiente. Stop: borde de la zona + 1 ATR. Objetivo: 2R. Riesgo: 1 % del capital. Una posición a la vez.
6. Reglas del video (opcionales en el EA):
   - **Niveles de temporalidad mayor** (`InpLevelTF`): niveles del diario para entrar en H4, o del semanal para entrar en D1. Zona = ±0,25 ATR de esa temporalidad.
   - **Solo a favor de la tendencia** (`InpTrendMode`): `TREND_EMA` = cierre diario por encima de la EMA 200 → solo compras; por debajo → solo ventas. `TREND_STRUCTURE` = últimos dos máximos y mínimos diarios subiendo → solo compras; bajando → solo ventas; mezclados → no opera.

## Configuraciones a probar
| Config | Gráfico | `InpLevelTF` | `InpTrendMode` |
|---|---|---|---|
| A — original | H4 | `PERIOD_CURRENT` (0) | `TREND_NONE` (0) |
| B — como el video | H4 | `PERIOD_D1` (16408) | `TREND_EMA` (1) |
| C — video con estructura | H4 | `PERIOD_D1` (16408) | `TREND_STRUCTURE` (2) |
| D — video en diario | D1 | `PERIOD_W1` (32769) | `TREND_EMA` (1) |

El resto de parámetros, por defecto.

## Pasos
1. Guarda el código de abajo como `SR_Flip_EA.mq5` en la carpeta `MQL5\Experts\` del terminal (Archivo → Abrir carpeta de datos).
2. Compílalo con MetaEditor (`metaeditor64.exe /compile:"<ruta>\SR_Flip_EA.mq5" /log`). Si hay errores, corrígelos sin cambiar las reglas y dime qué cambiaste.
3. Ejecuta el Probador de estrategias para cada configuración y cada par de esta lista que tenga el broker (respeta sufijos como `EURUSD.m`):
   EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, EURJPY, GBPJPY
   - Fechas: H4 desde 2016-01-01 hasta hoy; D1 desde 2005-01-01 hasta hoy.
   - Modelado: "1 minuto OHLC" (o "Cada tick basado en ticks reales" si el broker los tiene).
   - Depósito 10 000 USD, apalancamiento 1:100.
   - Para automatizarlo, lanza `terminal64.exe /config:"<ruta>\tester.ini"` con un archivo por par y configuración, por ejemplo (config B):
     ```ini
     [Tester]
     Expert=SR_Flip_EA.ex5
     Symbol=EURUSD
     Period=H4
     Model=1
     FromDate=2016.01.01
     ToDate=2026.11.18
     Deposit=10000
     Currency=USD
     Leverage=1:100
     Report=SR_Flip_EURUSD_H4_B
     ReplaceReport=1
     ShutdownTerminal=1

     [TesterInputs]
     InpLevelTF=16408
     InpTrendMode=1
     ```
4. Dame una tabla por configuración y par con: operaciones, % ganadoras, beneficio neto, profit factor, pago esperado y drawdown máximo (%). Añade una fila con el total de todos los pares por configuración.
5. Compáralo con mi backtest en Python (9 pares, datos de Yahoo, que no son los de tu broker):

   | Config | Periodo | Operaciones | Ganadoras | Profit factor |
   |---|---|---|---|---|
   | A — original H4 | 2024–2026 | 1021 | 33,5 % | 0,98 |
   | B — video H4 (D1 + EMA 200) | 2024–2026 | 511 | 30,9 % | 0,87 |
   | C — video H4 (D1 + estructura) | 2024–2026 | 355 | 35,2 % | 1,06 (1,28 en la primera parte, 0,87 en la última) |
   | D — video D1 (W1 + EMA 200) | 2004–2026 | 586 | 33,3 % | 0,97 |

   Si MT5 da algo muy distinto (por ejemplo, profit factor por encima de 1,3 o muchas menos operaciones), revisa por qué antes de sacar conclusiones.
6. **No optimices parámetros para que salga positivo.** Con 2R, el punto de equilibrio es 33 % de aciertos. Si el profit factor total queda cerca de 1, dímelo claramente: significa que la estrategia no tiene ventaja.

## Código del EA (SR_Flip_EA.mq5)
```mql5
//+------------------------------------------------------------------+
//| SR_Flip_EA.mq5                                                   |
//| Horizontal support/resistance "flip and retest" Expert Advisor.  |
//| Same rules as bot/sr_strategy.py:                                |
//|  1. Swing highs/lows with InpPivotLen bars on each side.         |
//|  2. Pivots within one zone (2 * InpZoneATR * ATR) form a level;  |
//|     a level needs at least InpMinTouches pivots.                 |
//|  3. Flip: a close beyond the zone in the last InpMaxBreakAge     |
//|     bars, with the close before it on the other side.            |
//|  4. Retest: the last closed bar re-enters the zone, closes on    |
//|     the new side and is a candle in the trade direction.         |
//|  5. Stop beyond the zone + InpSlATR * ATR, target InpRR * risk,  |
//|     InpRiskPct of equity per trade, one position at a time.      |
//| Optional rules from the video (bot/mtf.py):                      |
//|  - InpLevelTF: take levels from a higher timeframe (D1 levels    |
//|    for H4 entries, W1 for D1). Zone = InpZoneHTFATR * HTF ATR.   |
//|    PERIOD_CURRENT = levels from the chart timeframe (original).  |
//|  - InpTrendMode: only trade with the trend of InpTrendTF:        |
//|    EMA = close above/below InpEMALen EMA; STRUCTURE = last two   |
//|    swing highs and lows both rising (longs) or falling (shorts). |
//| Runs once per new bar, on the chart timeframe (tested on H4).    |
//+------------------------------------------------------------------+
#property version   "1.10"
#property description "Horizontal S/R flip-and-retest EA"

#include <Trade\Trade.mqh>

enum ENUM_TREND_MODE
  {
   TREND_NONE      = 0,   // None (both directions)
   TREND_EMA       = 1,   // Close vs EMA
   TREND_STRUCTURE = 2    // Market structure (HH/HL, LH/LL)
  };

input int    InpPivotLen    = 5;      // Pivot bars on each side
input int    InpLookback    = 300;    // Bars of pivots used for levels
input double InpZoneATR     = 0.5;    // Zone half-width (ATR multiples)
input int    InpMinTouches  = 2;      // Minimum pivots per level
input int    InpMaxBreakAge = 30;     // Max bars between break and retest
input double InpSlATR       = 1.0;    // Stop beyond zone (ATR multiples)
input double InpRR          = 2.0;    // Reward:risk
input double InpRiskPct     = 1.0;    // Risk per trade (% of equity)
input int    InpATRLen      = 14;     // ATR period
input ENUM_TIMEFRAMES InpLevelTF = PERIOD_D1;   // Level timeframe (CURRENT = chart)
input int    InpHTFPivotLen = 5;      // HTF pivot bars on each side
input int    InpHTFLookback = 250;    // HTF bars of pivots used for levels
input double InpZoneHTFATR  = 0.25;   // HTF zone half-width (HTF ATR multiples)
input ENUM_TREND_MODE InpTrendMode = TREND_EMA; // Trend filter
input ENUM_TIMEFRAMES InpTrendTF   = PERIOD_D1; // Trend timeframe
input int    InpEMALen      = 200;    // Trend EMA period
input ulong  InpMagic       = 260519; // Magic number

CTrade   trade;
int      atrHandle    = INVALID_HANDLE;
int      htfAtrHandle = INVALID_HANDLE;
int      emaHandle    = INVALID_HANDLE;
datetime lastBar      = 0;

//+------------------------------------------------------------------+
bool UseHTFLevels()
  {
   return(InpLevelTF != PERIOD_CURRENT && InpLevelTF != _Period);
  }

//+------------------------------------------------------------------+
int OnInit()
  {
   atrHandle = iATR(_Symbol, _Period, InpATRLen);
   if(atrHandle == INVALID_HANDLE)
     {
      Print("iATR failed: ", GetLastError());
      return(INIT_FAILED);
     }
   if(UseHTFLevels())
     {
      htfAtrHandle = iATR(_Symbol, InpLevelTF, 14);
      if(htfAtrHandle == INVALID_HANDLE)
        {
         Print("HTF iATR failed: ", GetLastError());
         return(INIT_FAILED);
        }
     }
   if(InpTrendMode == TREND_EMA)
     {
      emaHandle = iMA(_Symbol, InpTrendTF, InpEMALen, 0, MODE_EMA, PRICE_CLOSE);
      if(emaHandle == INVALID_HANDLE)
        {
         Print("iMA failed: ", GetLastError());
         return(INIT_FAILED);
        }
     }
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetTypeFillingBySymbol(_Symbol);
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(atrHandle != INVALID_HANDLE)
      IndicatorRelease(atrHandle);
   if(htfAtrHandle != INVALID_HANDLE)
      IndicatorRelease(htfAtrHandle);
   if(emaHandle != INVALID_HANDLE)
      IndicatorRelease(emaHandle);
  }

//+------------------------------------------------------------------+
//| Pivot prices of rates r (oldest first) whose pivot bar p lies in |
//| [from, last - k] and is confirmed by bar `last`.                 |
//+------------------------------------------------------------------+
int CollectPivots(const MqlRates &r[], const int from, const int last, const int k, double &piv[])
  {
   ArrayResize(piv, 0);
   int np = 0;
   for(int p = MathMax(from, k); p <= last - k; p++)
     {
      bool isH = true, isL = true;
      for(int q = p - k; q <= p + k; q++)
        {
         if(r[q].high > r[p].high)
            isH = false;
         if(r[q].low < r[p].low)
            isL = false;
        }
      if(isH)
        {
         ArrayResize(piv, np + 1);
         piv[np++] = r[p].high;
        }
      if(isL)
        {
         ArrayResize(piv, np + 1);
         piv[np++] = r[p].low;
        }
     }
   return(np);
  }

//+------------------------------------------------------------------+
//| Trend filter: allowLong / allowShort from closed InpTrendTF bars |
//+------------------------------------------------------------------+
bool TrendAllows(bool &allowLong, bool &allowShort)
  {
   allowLong = true;
   allowShort = true;
   if(InpTrendMode == TREND_NONE)
      return(true);

   if(InpTrendMode == TREND_EMA)
     {
      double e[];
      if(CopyBuffer(emaHandle, 0, 1, 1, e) != 1)
         return(false);
      double c = iClose(_Symbol, InpTrendTF, 1);
      if(c == 0)
         return(false);
      allowLong = (c > e[0]);
      allowShort = !allowLong;
      return(true);
     }

// TREND_STRUCTURE: last two confirmed swing highs and lows
   int k = InpPivotLen;
   MqlRates tr[];
   ArraySetAsSeries(tr, false);
   int got = CopyRates(_Symbol, InpTrendTF, 1, 300, tr);
   if(got < 4 * k + 2)
      return(false);
   int last = got - 1;
   double h1 = 0, h0 = 0, l1 = 0, l0 = 0;
   int nh = 0, nl = 0;
   for(int p = last - k; p >= k && (nh < 2 || nl < 2); p--)
     {
      bool isH = true, isL = true;
      for(int q = p - k; q <= p + k; q++)
        {
         if(tr[q].high > tr[p].high)
            isH = false;
         if(tr[q].low < tr[p].low)
            isL = false;
        }
      if(isH && nh < 2)
        {
         if(nh == 0)
            h1 = tr[p].high;
         else
            h0 = tr[p].high;
         nh++;
        }
      if(isL && nl < 2)
        {
         if(nl == 0)
            l1 = tr[p].low;
         else
            l0 = tr[p].low;
         nl++;
        }
     }
   if(nh < 2 || nl < 2)
      return(false);
   allowLong  = (h1 > h0 && l1 > l0);
   allowShort = (h1 < h0 && l1 < l0);
   return(true);
  }

//+------------------------------------------------------------------+
bool HasPosition()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         (ulong)PositionGetInteger(POSITION_MAGIC) == InpMagic)
         return(true);
     }
   return(false);
  }

//+------------------------------------------------------------------+
//| Cluster sorted pivot prices into levels with >= InpMinTouches.   |
//+------------------------------------------------------------------+
int BuildLevels(double &prices[], double width, double &levels[])
  {
   ArrayResize(levels, 0);
   int n = ArraySize(prices);
   if(n == 0)
      return(0);
   ArraySort(prices);
   double sum = prices[0];
   int    cnt = 1;
   for(int k = 1; k <= n; k++)
     {
      bool closeCluster = (k == n);
      if(!closeCluster)
         closeCluster = (prices[k] - sum / cnt > width);
      if(closeCluster)
        {
         if(cnt >= InpMinTouches)
           {
            int m = ArraySize(levels);
            ArrayResize(levels, m + 1);
            levels[m] = sum / cnt;
           }
         if(k < n)
           {
            sum = prices[k];
            cnt = 1;
           }
        }
      else
        {
         sum += prices[k];
         cnt++;
        }
     }
   return(ArraySize(levels));
  }

//+------------------------------------------------------------------+
//| +1 long, -1 short, 0 none: retest of `level` on bar i.           |
//| r[] is oldest-first; i is the last closed bar.                   |
//+------------------------------------------------------------------+
int FindSignal(const int i, const MqlRates &r[], const double level, const double z)
  {
   int last = MathMax(i - InpMaxBreakAge, 1);
// Long: broke above, now retesting from above
   if(r[i].low <= level + z && r[i].close > level && r[i].close > r[i].open)
     {
      for(int j = i - 1; j >= last; j--)
        {
         if(r[j].close < level - z)
            break;
         if(r[j].close > level + z && r[j - 1].close <= level + z)
            return(1);
        }
     }
// Short: broke below, now retesting from below
   if(r[i].high >= level - z && r[i].close < level && r[i].close < r[i].open)
     {
      for(int j = i - 1; j >= last; j--)
        {
         if(r[j].close > level + z)
            break;
         if(r[j].close < level - z && r[j - 1].close >= level - z)
            return(-1);
        }
     }
   return(0);
  }

//+------------------------------------------------------------------+
double CalcLots(const double riskPrice)
  {
   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE_LOSS);
   if(tickValue <= 0)
      tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tickSize <= 0 || tickValue <= 0 || riskPrice <= 0)
      return(0);
   double money      = AccountInfoDouble(ACCOUNT_EQUITY) * InpRiskPct / 100.0;
   double lossPerLot = riskPrice / tickSize * tickValue;
   double lots       = money / lossPerLot;
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(step > 0)
      lots = MathFloor(lots / step) * step;
   if(lots < vmin)
      return(0);                 // account too small to size this risk: skip
   return(MathMin(lots, vmax));
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   datetime t0 = iTime(_Symbol, _Period, 0);
   if(t0 == 0 || t0 == lastBar)
      return;
   lastBar = t0;
   if(HasPosition())
      return;

   int need = InpLookback + InpMaxBreakAge + 3 * InpPivotLen + 5;
   MqlRates r[];
   ArraySetAsSeries(r, false);
   int got = CopyRates(_Symbol, _Period, 1, need, r);   // closed bars only, oldest first
   if(got < need)
      return;

   double a[];
   if(CopyBuffer(atrHandle, 0, 1, 1, a) != 1)
      return;
   double atr = a[0];
   if(atr <= 0)
      return;

   int i = got - 1;              // last closed bar
   int k = InpPivotLen;

// Trend filter
   bool allowLong, allowShort;
   if(!TrendAllows(allowLong, allowShort))
      return;
   if(!allowLong && !allowShort)
      return;

   double piv[];
   double z;
   if(UseHTFLevels())
     {
      // Levels from closed bars of the higher timeframe
      int hk = InpHTFPivotLen;
      MqlRates hr[];
      ArraySetAsSeries(hr, false);
      int hneed = InpHTFLookback + hk + 1;
      int hgot = CopyRates(_Symbol, InpLevelTF, 1, hneed, hr);
      if(hgot < 2 * hk + 2)
         return;
      double ha[];
      if(CopyBuffer(htfAtrHandle, 0, 1, 1, ha) != 1 || ha[0] <= 0)
         return;
      int j = hgot - 1;
      CollectPivots(hr, j - InpHTFLookback, j, hk, piv);
      z = InpZoneHTFATR * ha[0];
     }
   else
     {
      // Pivots of the chart timeframe confirmed by bar i, inside the lookback
      CollectPivots(r, i - InpLookback, i, k, piv);
      z = InpZoneATR * atr;
     }

   double levels[];
   if(BuildLevels(piv, 2 * z, levels) == 0)
      return;

// Closest level within 3 zones that gives an allowed signal
   int    side = 0;
   double lv   = 0;
   double bestDist = DBL_MAX;
   for(int m = 0; m < ArraySize(levels); m++)
     {
      double d = MathAbs(levels[m] - r[i].close);
      if(d > 3 * z || d >= bestDist)
         continue;
      int s = FindSignal(i, r, levels[m], z);
      if((s == 1 && allowLong) || (s == -1 && allowShort))
        {
         side = s;
         lv = levels[m];
         bestDist = d;
        }
     }
   if(side == 0)
      return;

   double ask   = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid   = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double entry = (side == 1) ? ask : bid;
   double sl    = (side == 1) ? lv - (z + InpSlATR * atr) : lv + (z + InpSlATR * atr);
   double risk  = (entry - sl) * side;
   if(risk <= 0)
      return;
   double tp = entry + side * InpRR * risk;

   long stopsLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   if(MathAbs(entry - sl) < stopsLevel * _Point || MathAbs(tp - entry) < stopsLevel * _Point)
      return;

   double lots = CalcLots(risk);
   if(lots <= 0)
      return;

   sl = NormalizeDouble(sl, _Digits);
   tp = NormalizeDouble(tp, _Digits);
   bool ok = (side == 1)
             ? trade.Buy(lots, _Symbol, 0, sl, tp, "SR flip long")
             : trade.Sell(lots, _Symbol, 0, sl, tp, "SR flip short");
   if(!ok)
      Print("Order failed: ", trade.ResultRetcode(), " ", trade.ResultRetcodeDescription());
  }
//+------------------------------------------------------------------+
```
