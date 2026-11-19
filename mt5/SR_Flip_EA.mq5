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
//| Runs once per new bar, on the chart timeframe (tested on H4).    |
//+------------------------------------------------------------------+
#property version   "1.00"
#property description "Horizontal S/R flip-and-retest EA"

#include <Trade\Trade.mqh>

input int    InpPivotLen    = 5;      // Pivot bars on each side
input int    InpLookback    = 300;    // Bars of pivots used for levels
input double InpZoneATR     = 0.5;    // Zone half-width (ATR multiples)
input int    InpMinTouches  = 2;      // Minimum pivots per level
input int    InpMaxBreakAge = 30;     // Max bars between break and retest
input double InpSlATR       = 1.0;    // Stop beyond zone (ATR multiples)
input double InpRR          = 2.0;    // Reward:risk
input double InpRiskPct     = 1.0;    // Risk per trade (% of equity)
input int    InpATRLen      = 14;     // ATR period
input ulong  InpMagic       = 260519; // Magic number

CTrade   trade;
int      atrHandle = INVALID_HANDLE;
datetime lastBar   = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   atrHandle = iATR(_Symbol, _Period, InpATRLen);
   if(atrHandle == INVALID_HANDLE)
     {
      Print("iATR failed: ", GetLastError());
      return(INIT_FAILED);
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

// Pivots confirmed by bar i, inside the lookback
   double piv[];
   int np = 0;
   int from = MathMax(i - InpLookback, k);
   for(int p = from; p <= i - k; p++)
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

   double z = InpZoneATR * atr;
   double levels[];
   if(BuildLevels(piv, 2 * z, levels) == 0)
      return;

// Closest level within 3 zones that gives a signal
   int    side = 0;
   double lv   = 0;
   double bestDist = DBL_MAX;
   for(int m = 0; m < ArraySize(levels); m++)
     {
      double d = MathAbs(levels[m] - r[i].close);
      if(d > 3 * z || d >= bestDist)
         continue;
      int s = FindSignal(i, r, levels[m], z);
      if(s != 0)
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
