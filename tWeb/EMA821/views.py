from django.shortcuts import render
from django.http import JsonResponse
from .forms import EMA821Form
import json 
from django.views.decorators.csrf import csrf_exempt
import numpy as np 
import pandas as pd
import datetime as dt
import yfinance as yf 
from pandas_datareader import data as pdr
import importlib.util
import os
# instead of render the result in django template directly, we can  can use Django's JsonResponse to return data to the frontend in JSON format.
def EMA821_view(request):
    ema821_gc = None
    if request.method == 'POST':
        form = EMA821Form(request.POST)
        if form.is_valid():
            search_period = form.cleaned_data['search_period']
            ema821_gc = run_stock_screener(search_period)
    
    else:
        form = EMA821Form()
    return render (request, 'EMA821/EMA821.html', {'form': form, 'ema821_gc': ema821_gc})

## remark latest yf version do not support datareader any more so no more yf.pdf_override()

def run_stock_screener(search_period):
    csvfilename = os.path.join(os.path.dirname(__file__),'data/new_stocklist2.csv')
    stocklist_df = pd.read_csv(csvfilename, engine="python", encoding="utf-8-sig")
    stocklist = stocklist_df['Symbol'].tolist()
    start= dt.datetime.now()-dt.timedelta(days=150) # timedelta : the date 150 days before 
    now=dt.datetime.now()
    def find_amount (data, i):
        try:
            volume = data['Volume'].iloc[-i]
            close = data['Close'].iloc[-i]
            # Ensure we get scalar values, not Series
            if hasattr(volume, 'item'):
                volume = volume.item()
            if hasattr(close, 'item'):
                close = close.item()
            return float(volume) * float(close)
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
    # check if the parameter is increasing during the period  --> index : top to bottem , top is the latest 
    def increasing (parameter, period):
        try:
            increase = True 
            for i in range (-period, 0):
                val_current = parameter.iloc[i]
                val_next = parameter.iloc[i+1]
                
                # Ensure scalar values
                if hasattr(val_current, 'item'):
                    val_current = val_current.item()
                if hasattr(val_next, 'item'):
                    val_next = val_next.item()
                    
                if float(val_current) >= float(val_next):   # largest is [0]
                    increase = False
                    break
            return increase
        except (IndexError, ValueError, TypeError):
            return False
    def cross_within_period (parameter1, parameter2, begin, period):
        index =0 
        for i in range(begin, begin+period+1):
            if cross(parameter1,parameter2, i):
                index=i
                break 
        return index
    ema821_gc=[]
    #iterate through each stock in the list 
    for i in range(len(stocklist)):
        stock= stocklist[i]
        print (f"{i+1}/ {len(stocklist)} {stock}") #maybe a f stirng with contain {}
        # Retry logic for downloading stock data
        df = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                df = yf.download(stock, start, now, auto_adjust=True)
                if df.empty:
                    raise ValueError("No data returned")
                break
            except Exception as e:
                print(f"Error retrieving data for {stock} on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    print(f"Failed to retrieve data for {stock} after {max_retries} attempts")
                    df = None
                    break
        
        # Skip if data download failed
        if df is None or df.empty:
            continue
        # check if there are enough data points to calculate the moving averages
        if len(df) <80:
            print (f"Not enough data points for {stock}")
            continue 
        #check turnover where the index is a random number to check that stock
        if find_amount(df, 2) < 2e7:
            print(f"Turnover of{stock} is too low ")
            continue
    
        #Check EMA60 slope >= 0 ewm :exponential moving windo 
        ema60 = df["Close"].ewm(span=60).mean()
        ema60_slope = (ema60.iloc[-1]-ema60.iloc[-3])/2
        if hasattr(ema60_slope, 'item'):
            ema60_slope = ema60_slope.item()
        if float(ema60_slope) < 0 : # check whether the ema is downward trend 
            #print(f"EMA60 of {stock} < 0 ")
            continue 
        # EMA8 GC EMA21
        # Calculate EMA 
        ema8 = df['Close'].ewm(span=8).mean()
        ema21 =df['Close'].ewm(span=21).mean()
        slope_ema21 = (ema21.iloc[-1]-ema21.iloc[-3])/2
        if hasattr(slope_ema21, 'item'):
            slope_ema21 = slope_ema21.item()
        slope_ema21 = float(slope_ema21)
        #check EMA gc
        if cross_within_period(parameter1=ema8, parameter2= ema21, begin=1, period = search_period)==0 and slope_ema21>= 0 : # increasing trend but no golden cross
            continue
        
        vea8 = df['Volume'].ewm(span=8).mean()
        vea21= df['Volume'].ewm(span=21).mean()
        vea8_21_index= cross_within_period(parameter1= vea8, parameter2= vea21, begin=1, period= search_period)
        if vea8_21_index == 0:
            continue
        
        #MACD GC (5,34,5)
        ema5 = df['Close'].ewm(span=5).mean()
        ema34 = df['Close'].ewm(span=34).mean()
        macd_line= ema5-ema34 # fast line
        signal_line= macd_line.ewm(span=5).mean()
        macd_diff= macd_line- signal_line # histogram 
        macd_index = cross_within_period (parameter1= macd_line, parameter2= signal_line, begin=1, period= search_period)
        
        # Safe extraction of scalar values for comparison
        close_val = df['Close'].iloc[-1]
        if hasattr(close_val, 'item'):
            close_val = close_val.item()
            
        ema60_val = ema60.iloc[-1]
        if hasattr(ema60_val, 'item'):
            ema60_val = ema60_val.item()
            
        signal_curr = signal_line.iloc[-1]
        if hasattr(signal_curr, 'item'):
            signal_curr = signal_curr.item()
            
        signal_prev = signal_line.iloc[-2]
        if hasattr(signal_prev, 'item'):
            signal_prev = signal_prev.item()
        
        if macd_index != 0 and float(close_val) > float(ema60_val) and float(signal_curr) > float(signal_prev) and float(signal_curr)>=0 : # increasing trend and green histo
            ema821_gc.append(stock)
    
    if len(ema821_gc) == 0:
        print("No EMA821 golden cross detected")
    print(f"ema821_gc: {ema821_gc}")
    return ema821_gc

''' if you do not explictly cast the data variable into a suitable one
You will get ValueError: The truth value of a Series is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all().'''