from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import pandas as pd
import datetime as dt
import yfinance as yf
import json
import os
import threading
## track the screener process by threading and terminate the process freely
terminate_flag = False
screener_thread = None
results = []


# remark in python if you want to modify the global variable values you need to state them as global in the function

def wedge_screener_view(request):
    global terminate_flag, screener_thread, results
    if request.method == 'POST':
        terminate_flag = False
        results=[]
        #def separate function handle the capbaility of threading
        if screener_thread and screener_thread.is_alive():
            terminate_flag = True
            screener_thread.join()
        def screener_logic():
            try:
                _run_screener_logic(request)
            except Exception as e:
                print (f"error in running screener logic:{str(e)}")
        screener_thread = threading.Thread(target=screener_logic)
        screener_thread.start()

        return JsonResponse({'status': 'started', 'message': 'Screener started. Use /check_status to get results.'})
    return render(request, 'wedges/wedges.html')

def check_status(request):
    global screener_thread, results
    return JsonResponse({
        'status': 'running' if screener_thread and screener_thread.is_alive() else 'completed',
        'results': results
    })



def terminate_screener(request):
    global terminate_flag, screener_thread
    if screener_thread and screener_thread.is_alive(): #.is_alive() is to check whether the thread is still running ffla
        terminate_flag = True 
        screener_thread.join()
        return JsonResponse({'status':'screener terminated'})
    return JsonResponse({'status':'no screener is running'})


def _run_screener_logic (request):
    global terminate_flag, results
    terminate_flag = False
    csvfilename = os.path.join(os.path.dirname(__file__), 'data/new_stocklist2.csv')
    stocklist = pd.read_csv(csvfilename, engine = "python", encoding ="utf-8-sig")
    start= dt.datetime.now()-dt.timedelta(days=200)
    now=dt.datetime.now()
    #green candle
    def green_candle(date,i):
        close_curr = date['Close'].iloc[-i]
        close_prev = date['Close'].iloc[-i-1]
        close_curr = close_curr.item() if hasattr(close_curr, 'item') else close_curr
        close_prev = close_prev.item() if hasattr(close_prev, 'item') else close_prev
        return (float(close_curr) > float(close_prev))

    def red_candle(date,i):
        close_curr = date['Close'].iloc[-i]
        close_prev = date['Close'].iloc[-i-1]
        close_curr = close_curr.item() if hasattr(close_curr, 'item') else close_curr
        close_prev = close_prev.item() if hasattr(close_prev, 'item') else close_prev
        return (float(close_curr) < float(close_prev))

    #find maximum High between [start, end]
    def find_max_high(date, start, end):
        return (date['High'].iloc[-start:-end-1:-1].max())
        # find the max bewteen -2 to end , when the step is negatve, the stop index should be less than start index and using reverse order is more readable

    # find minimum low between  [start, end]
    def find_min_low(date, start, end):
        return (date['Low'].iloc[-start:-end-1:-1].min())

    # check if there is formation of upward wedge -> max_high is a green candle
    def wedges(date, start, end, max_high):
        if start <= 1: # start must >= 2
            return False
        
        # count the number of peaks between start to end
        peak_count = 0
        for i in range(-start,-end-1,-1):
            if 1.01*max_high >= date['High'].iloc[i] >= 0.99*max_high: # range of peak : [0.99 to 1.01]
                peak_count += 1
        
        # Check breakout condition after counting all peaks
        close_val = date['Close'].iloc[-1]
        close_val = close_val.item() if hasattr(close_val, 'item') else close_val
        
        if peak_count >= 3 and float(close_val) > 1.005 * max_high: # break up from peak after 3+ peaks
            return True
        return False

    # remark: [0.995,1.005] as the effective range of wedge formation by consolidation consideration
    
    # check if there is formation of downward wedge 向下契型,第四次破底 -> min_low is a red candle
    'not used in this case'
    def downward_wedge(data, start, end, min_low):
        if start <=1:
            return False
        else:
            low_count =0
            for i in range(-start,-end-1,-1):
                if 1.005*min_low >= data['Low'].iloc[i]>=0.995*min_low:
                    low_count +=1
                
                    if low_count >=4 and data['Close'].iloc[-1]<0.995*min_low:
                        return True

            return False

    # calculate MA (SMA)
    def calculate_ma_slope(data, ma_window, bar_number):
        ma = data['Close'].rolling(ma_window).mean()
        ma_slope = float(ma[-1]-ma[-bar_number])/(bar_number-1)
        return ma, ma_slope

    def volume_increase_ladder3(data,i):
        return (float(data['Volume'].iloc[-i-2]) < float(data['Volume'].iloc[-i-1]) < float(data['Volume'].iloc[-i]))

    def volume_decrease_ladder3(data,i):
        return (data['Volume'].iloc[-i-2]> data['Volume'].iloc[-i-1] > data['Volume'].iloc[-i])

    # we extract the suffix after dot
    def get_suffix (stock_symbol):
        parts = stock_symbol.split('.')
        return parts[-1] if len(parts) > 1 else None

    def enough_amount (data,i, stock_symbol):
        amount = data['Volume'].iloc[-i]* data['Close'].iloc[-i]
        suffix = get_suffix(stock_symbol)

        #define different threshold based on suffix (different markets)
        threshold = 1e7 # default for US market
        if suffix == 'T': # Toyko market
            threshold = 1.4e9
        elif suffix == 'L': # london stock
            threshold = 7.8e6
        elif suffix == 'TO': # Toronto stock
            threshold = 1.34e7
        elif suffix == 'SI' : # Singapore Tock exhange
            threshold = 1.34e7
        elif suffix == 'HK' : # HK exchange
            threshold = 1.25e6
        # Check if the turnover > threshold
        
        return amount > threshold
    def calculate_RSI(data, window=14):
        delta = data['Close'].diff() # calculate the difference between the current and previous day's closing price
        gain = (delta.where(delta>0,0)).rolling(window=window).mean()
        loss = (-delta.where(delta<0,0)).rolling(window=window).mean()
        rs = gain/loss
        rsi = 100 - 100/(1+rs)
        return rsi


    def calculate_MACD(data, long_window=26, short_window=12, signal_EMA = 9):
        short_ema= data['Close'].ewm(span=short_window, adjust=False).mean()
        long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
        macd = short_ema - long_ema
        signal = macd.ewm(span=signal_EMA, adjust=False).mean()
        return macd, signal

    #obtain the last 120 days volume
    def is_volume_surge(data):
        avg_volume = data['Volume'].iloc[-120:].mean()
        return data['Volume'].iloc[-1] > 1.5* avg_volume

    def is_uptrend(data):
        ma20 = data['Close'].rolling(window=20).mean()
        ma50 = data['Close'].rolling(window=50).mean()
        return (float(ma20.iloc[-1]) > float(ma50.iloc[-1]) and float(ma20.iloc[-1]) > float(ma20.iloc[-2]) and float(ma50.iloc[-1]) > float(ma50.iloc[-2]))
                
            
    breakupList =[]
    reverseList=[]
    reboundList=[]
    breakdownList=[]

    break_factor =1.005
    # 1.005 is typically used to define a threshold or multiplier for significant price movement or breaks in techncial analysis. It represents a small % increase above the key level of resistance or support to confirm breakup or breakdown
    begin_ =3
    end_ =120 # length of the window
    # squeezing pattern (uptrend raising wedge)
    for i in range (len(stocklist)):
        if terminate_flag:
            print("Termination flag set. Exiting screener logic.")
            return
        stock = str(stocklist.iloc[i]["Symbol"]) # str() to convert the symbol to string
        print(f"{i+1}/{len(stocklist)}{stock}")

        try:
            df=yf.download(stock, start, now, auto_adjust = True) # return as pandas Dataframe
        except (KeyError, IndexError) as e:
            print(f"Error:{str(e)}")
            continue

        if len(df) <120:
            print(df)
            continue
        
        #check turnover
        if not enough_amount(df,2,stock):
            continue
        df['RSI'] = calculate_RSI(df)
        df['MACD'], df['Signal'] = calculate_MACD(df)
        max_h = find_max_high(df, start=2, end=end_)
        min_h = find_min_low(df, start=2, end=end_)

        processed = False
        for length in range(begin_,end_,1):
            if terminate_flag:
                print("Termination flag set. Exiting screener logic.")
                return
            if processed:
                break
            
            if wedges(df, start=2, end=length, max_high=max_h):
                # Safe extraction of values
                close_val = df['Close'].iloc[-1]
                close_val = close_val.item() if hasattr(close_val, 'item') else close_val
                
                rsi_val = df['RSI'].iloc[-1]
                rsi_val = rsi_val.item() if hasattr(rsi_val, 'item') else rsi_val
                
                macd_val = df['MACD'].iloc[-1]
                macd_val = macd_val.item() if hasattr(macd_val, 'item') else macd_val
                
                signal_val = df['Signal'].iloc[-1]
                signal_val = signal_val.item() if hasattr(signal_val, 'item') else signal_val
                
                if (green_candle(df,1) and float(close_val) > break_factor*max_h
                and ((float(rsi_val) < 70) or (float(rsi_val) >= 70 and is_uptrend(df)))
                and (float(macd_val) > float(signal_val))): #valid breakout
                    if stock not in breakupList:
                        breakupList.append(stock)
                        processed = True
    if len(breakupList) == 0:
        breakupList.append("No upward wedge breakout stock detected")
    print (f"Results:{breakupList}")
    results = breakupList























