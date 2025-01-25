#!/usr/bin/env python3
""" ERROR:
[*********************100%***********************]  1 of 1 completed

1 Failed download:
['TSLA']: YFPricesMissingError('$%ticker%: possibly delisted; no price data found  (1m 2024-12-22 00:00:00 -> 2025-01-21 00:00:00) (Yahoo error = "1m data not availa
ble for startTime=1734843600 and endTime=1737435600. Only 8 days worth of 1m granularity data are allowed to be fetched per request.")')
MACD data saved to tesla_macd_data.csv

[Process exited 0]
"""




import pandas as pd
import datetime
import yfinance as yf

def fetch_1min_data_in_batches(ticker, start_date, end_date):
    all_data = []
    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + datetime.timedelta(days=8), end_date)
        print(f"Fetching data from {current_start} to {current_end}")
        data = yf.download(ticker, start=current_start, end=current_end, interval="1m")
        if not data.empty:
            all_data.append(data)
        current_start = current_end
    if all_data:
        return pd.concat(all_data)
    else:
        return pd.DataFrame()

# Define the ticker and date range
ticker = "TSLA"
end_date = datetime.datetime(2025, 1, 21)
start_date = end_date - datetime.timedelta(days=30)

# Fetch the data in batches
data = fetch_1min_data_in_batches(ticker, start_date, end_date)

if data.empty:
    print("No data was fetched. Check your ticker or API restrictions.")
else:
    # Calculate MACD components
    short_window = 12
    long_window = 26
    signal_window = 9

    # Calculate the EMA (Exponential Moving Average)
    data['EMA12'] = data['Close'].ewm(span=short_window, adjust=False).mean()
    data['EMA26'] = data['Close'].ewm(span=long_window, adjust=False).mean()

    # Calculate MACD Line and Signal Line
    data['MACD_Line'] = data['EMA12'] - data['EMA26']
    data['Signal_Line'] = data['MACD_Line'].ewm(span=signal_window, adjust=False).mean()

    # Calculate the Histogram
    data['Histogram'] = data['MACD_Line'] - data['Signal_Line']

    # Save to CSV
    csv_file = "tesla_macd_data.csv"
    data.to_csv(csv_file)

    print(f"MACD data saved to {csv_file}")

