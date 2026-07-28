from django.shortcuts import render
from .forms import StockScreenerForm
import pandas as pd
import datetime as dt
import yfinance as yf
import importlib.util
import os

## future warning on access scalar but turns out maybe series 

def stock_screener_view(request):
    result = None
    if request.method == 'POST':
        form = StockScreenerForm(request.POST)
        if form.is_valid():
            search_period = form.cleaned_data['search_period'] ## form.cleaned_data return validated input in dictionary
            result = run_stock_screener(search_period)
    else:
        form = StockScreenerForm()

    return render(request, 'stock_screener/screener.html', {'form': form, 'result': result})

def run_stock_screener(search_period):
    csvfilename = os.path.join(os.path.dirname(__file__),'data/new_stocklist2.csv')
    stocklist = pd.read_csv(csvfilename, engine="python", encoding="utf-8-sig")
    stocklist = stocklist['Symbol'].tolist()
    start = dt.datetime.now() - dt.timedelta(days=150)
    now = dt.datetime.now()

    def find_amount(data, i):
        try:
            volume = data['Volume'].iloc[-i]
            close = data['Close'].iloc[-i]

            # Ensure we get scalar value but not Series
            if hasattr(volume, 'item'):
                volume = volume.item()
            if hasattr(close, 'item'):  
                close = close.item()
            return float(close * volume)
        
        except (IndexError, ValueError, TypeError):
            return 0

    def cross(parameter1, parameter2, i): # parameter can be 'Volume', 'Close', 1 is smaller 2 is larger 
        try:
            # Use .item() to ensure we get scalar values
            val1_prev = parameter1.iloc[-i-1]
            if hasattr(val1_prev, 'item'):
                val1_prev = val1_prev.item()
            
            val2_prev = parameter2.iloc[-i-1]
            if hasattr(val2_prev, 'item'):
                val2_prev = val2_prev.item()
                
            val1_curr = parameter1.iloc[-i]
            if hasattr(val1_curr, 'item'):
                val1_curr = val1_curr.item()
                
            val2_curr = parameter2.iloc[-i]
            if hasattr(val2_curr, 'item'):
                val2_curr = val2_curr.item()
                
            return ((float(val1_prev) < float(val2_prev)) and (float(val1_curr) > float(val2_curr)))
        except (IndexError, ValueError, TypeError):
            return False

    def cross_within_period(parameter1, parameter2, begin, period): 
        for i in range(begin, begin + period + 1):
            if cross(parameter1, parameter2, i):
                return i
        return 0
    # Bulk-download ALL symbols in a few batched yf.download() calls instead of
    # one HTTP session per ticker. This keeps us under Yahoo's rate limit
    # (HTTP 429) and is far faster than a per-ticker loop. See bulk_fetch.py for
    # why asyncio around yfinance does not work (yfinance is blocking on top of
    # `requests`, so a coroutine still runs calls serially).
    from .bulk_fetch import bulk_download
    stock_data = bulk_download(
        stocklist,
        start,
        now,
        batch_size=100,           # ~100 tickers per yf.download call
        inter_batch_delay=0.75,   # throttle between batches to avoid 429
    )

    MA_upward_trend = []
    for stock, df in stock_data.items():
        if len(df) < 80:
            continue

        if find_amount(df, 2) < 2e7:
            continue

        # Calculate moving averages - keep as Series for cross detection
        MA20 = df["Close"].rolling(window=20).mean()
## MA20 = MA20.item() if hasattr(MA20, 'item') else MA20  # ❌ WRONG! since MA20 must be full series

        EMA20 = df["Close"].ewm(span=20).mean()
        MA60 = df["Close"].rolling(window=60).mean()
        EMA60 = df["Close"].ewm(span=60).mean()
        MA120 = df["Close"].rolling(window=120).mean()
        EMA120 = df["Close"].ewm(span=120).mean()

        if cross_within_period(parameter1=EMA20, parameter2=MA20, begin=1, period=search_period):
            if cross_within_period(parameter1=EMA60, parameter2=MA60, begin=1, period=search_period):
                    if  cross_within_period(parameter1=EMA120, parameter2=MA120, begin=1, period=search_period):
                
                        closeP_above_MA = True
                        for j in range(search_period + 1):
                            close = df["Close"].iloc[-j]
                            close = close.item() if hasattr(close, 'item') else close

                            # Get scalar values for comparison
                            ema20_val = EMA20.iloc[-j]
                            ema20_val = ema20_val.item() if hasattr(ema20_val, 'item') else ema20_val
                            
                                
                            ma20_val = MA20.iloc[-j]
                            ma20_val = ma20_val.item() if hasattr(ma20_val, 'item') else ma20_val



                            ema60_val = EMA60.iloc[-j]
                            ema60_val = ema60_val.item() if hasattr(ema60_val, 'item') else ema60_val
                                
                            ma60_val = MA60.iloc[-j]
                            ma60_val = ma60_val.item() if hasattr(ma60_val, 'item') else ma60_val
                                
                            ema120_val = EMA120.iloc[-j]
                            ema120_val = ema120_val.item() if hasattr(ema120_val, 'item') else ema120_val
                            
                                
                            ma120_val = MA120.iloc[-j]
                            ma120_val = ma120_val.item() if hasattr(ma120_val, 'item') else ma120_val

                            
                            if (float(close) < float(ema20_val) or 
                                float(close) < float(ma20_val) or 
                                float(close) < float(ema60_val) or 
                                float(close) < float(ma60_val) or
                                float(close) < float(ema120_val) or
                                float(close) < float(ma120_val)):
                                closeP_above_MA = False
                                break

                        if closeP_above_MA:
                            MA_upward_trend.append(stock)
    if len(MA_upward_trend) == 0:
        MA_upward_trend.append("No triple MA crossed stock were found")
    print(f"Triple_MA_upward_trend: {MA_upward_trend}")
    return MA_upward_trend