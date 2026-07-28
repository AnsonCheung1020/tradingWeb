from django.shortcuts import render
import pandas as pd
import datetime as dt
import yfinance as yf
import talib
import os
import numpy as np

def stock_screener_view(request):
    if request.method == 'POST':
        csvfilename = os.path.join(os.path.dirname(__file__), 'data/3B_Total.csv')
        stocklist = pd.read_csv(csvfilename, engine="python", encoding="ISO-8859-1")
        yf.pdr_override()
        start = dt.datetime.now() - dt.timedelta(days=200)
        now = dt.datetime.now()

        def get_suffix(stock_symbol):
            if '=' in stock_symbol:
                parts = stock_symbol.split('=')
                return parts[-1]

            elif '.' in stock_symbol:
                parts = stock_symbol.split('.')
                return parts[-1]

            return None

        def enough_amount(data, i, stock_symbol):
            amount = data['Volume'].iloc[-i] * data['Close'].iloc[-i]
            suffix = get_suffix(stock_symbol)

            threshold = 1e7  # this local variable is necessary to be here otherwise -> UnboundLocalError: local variable 'threshold' referenced before assignment -> or you can define as global outside
            if suffix == 'T':
                threshold = 1.4e9

            elif suffix == 'L':
                threshold = 7.8e6

            elif suffix == 'T0':
                threshold = 1.34e7

            elif suffix == 'SI':
                threshold = 1.34e7

            elif suffix == 'HK':
                threshold = 1.25e6

            elif suffix == 'X' or suffix == 'F':
                threshold = 0

            if amount > threshold:
                return True 

            else:
                return False

        def calculate_ma_slope(data, ma_window, bar_number):
            ma = data.rolling(ma_window).mean()
            ma_slope = (ma[-1] - ma[-bar_number]) / (bar_number - 1)  # y2-y1/x2-x1
            return ma, ma_slope

        def calculate_hma(data, period):  # Hull Moving average
            wma_right_half_period = data.rolling(window=int(period / 2)).mean() * 2
            wma_full_period = data.rolling(window=period).mean()
            raw_hma = wma_right_half_period - wma_full_period
            return raw_hma.rolling(window=int(np.sqrt(period))).mean()  # smooth the raw HMA with another WMA, this one with the square root of the specified number of periods.

        def peak_trough_peak_hma(data, begin, end, peak_allowance, peak_trough_ratio):  # stage 2 analysis
            data['HMA3'] = calculate_hma(data['Close'], 3)
            if end <= begin:  # begin has to be lower than the end for the trough
                return False, None
            right_peak = data['HMA3'].iloc[-begin]  # begin is the more recent index such that we loop from begin to end (right to left ) -> right peak here is the RHS
            for i in range(begin + 3, end):
                left_peak = data['HMA3'].iloc[-i]  # at least 3 days from the RHS
                for j in range(i - 1, begin + 3, -1):
                    trough = data['HMA3'].iloc[-j]
                    if (1 - peak_allowance) * left_peak <= right_peak <= (1 + peak_allowance) * left_peak and peak_trough_ratio <= left_peak / trough:  # deeper trough better -> stronger momentum when break out
                        return True, -i  # for consistency
            return False, None

        cupAndHandle = []
        for i in range(len(stocklist)):
            stock = str(stocklist.iloc[i]['Symbol'])
            print(f"processing stock {i + 1}/{len(stocklist)}: {stock}")
            try:
                df = yf.download(stock, start, now)  # returning a data frame but need to specify to column so as to be useful

            except Exception as e:
                print(f"Error processing {stock}: {e}")
                continue
            if len(df) < 110:
                print(f"not enough data for {stock}, skip it")
                continue
            if not enough_amount(df, 2, stock):
                print(f"turnover too low for {stock}, skip it")
                continue

            ma60, ma60_slope = calculate_ma_slope(df['Close'], 60, 3)
            if ma60_slope < 0:
                print(f"downward trend for {stock}, skip")
                continue  # to check whether the stock with cup and handle is in the upward trend -> CNH with upward trend is better : 1. the trend is your fd 2. to avoid 蟹貨
            # finding stock with the handle

            ptp1, ptp_index1 = peak_trough_peak_hma(data=df, begin=2, end=15, peak_allowance=0.01, peak_trough_ratio=1.05)
            if not ptp1:
                continue
            else:
                print(f"inner rim index@ {ptp_index1}; handle length = {ptp_index1 - 2}")

            # find stock with cup after handle
            ptp2, ptp_index2 = peak_trough_peak_hma(data=df, begin=ptp_index1, end=100, peak_allowance=0.01, peak_trough_ratio=1.3)
            if ptp2:
                print(f"outer rim index at {ptp_index2}; cup width {ptp_index2 - ptp_index1}")
                cupAndHandle.append(stock)
                print(f"cup and handle pattern detected at {ptp_index2} for {stock}")
            else:
                print(f"handle found at {ptp_index1}, but no cup found for {stock}")
        if len(cupAndHandle) == 0:
            print("No cup and handle pattern detected")
        print(f"Cup and handle _HMA: {cupAndHandle}")
        return render(request, 'cup_and_h/cup_and_h.html', {'cupAndHandle': cupAndHandle})
    else:
        return render(request, 'cup_and_h/cup_and_h.html')