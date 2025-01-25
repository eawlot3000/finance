#!/usr/bin/env python3
import pandas as pd
df = pd.read_csv("TSLA_last_30_days.csv")
df.tail()
print(df.tail())
print(type(df.tail()))


# Check if NA values are in data
df.isna().sum()
# print(type(df.isna().sum()))

# Engulfing pattern signals
import random
def Revsignal(df1):
  length = len(df1)
  high = list(df1['high'])
  low = list(df1['low'])
  close = list(df1['close'])
  open = list(df1['open'])
  signal = [0] * length
  bodydiff = [0] * length

  for row in range(1, length):
    bodydiff[row] = abs(open[row] - close[row])
    bodydiffmin = 0.003
    if (bodydiff[row] > bodydiffmin and bodydiff[row - 1] > bodydiffmin and
        open[row - 1] < close[row - 1] and
        open[row] > close[row] and
        (open[row] - close[row - 1]) >= +0e-5 and close[row] < open[row - 1]):
      signal[row] = 1
    elif (bodydiff[row] > bodydiffmin and bodydiff[row - 1] > bodydiffmin and
          open[row - 1] > close[row - 1] and
          open[row] < close[row] and
          (open[row] - close[row - 1]) <= -0e-5 and close[row] > open[row - 1]):
      signal[row] = 2
    else:
      signal[row] = 0
  return signal

df['signal1'] = Revsignal(df)
df[df['signal1'] == 1].count()


# Target
def mytarget(df1, barsfront):
  length = len(df1)
  high = list(df1['high'])
  low = list(df1['low'])
  close = list(df1['close'])
  open = list(df1['open'])
  trendcat = [None] * length
  
  piplim = 300e-5
  for line in range(0, length - 1 - barsfront):
    for i in range(1, barsfront + 1):
      if ((high[line + i] - max(close[line], open[line])) > piplim and 
          (min(close[line], open[line]) - low[line + i]) > piplim):
        trendcat[line] = 3  # no trend
      elif (min(close[line], open[line]) - low[line + i]) > piplim:
        trendcat[line] = 1  # -1 downtrend
        break
      elif (high[line + i] - max(close[line], open[line])) > piplim:
        trendcat[line] = 2  # uptrend
        break
      else:
        trendcat[line] = 0  # no clear trend  
  return trendcat

df['Trend'] = mytarget(df, 3)
# df.head(30)


import numpy as np
conditions = [(df['Trend'] == 1) & (df['signal1'] == 1), (df['Trend'] == 2) & (df['signal1'] == 2)]
values = [1, 2]
df['result'] = np.select(conditions, values)

trendId = 2
print(df[df['result'] == trendId].result.count() / df[df['signal1'] == trendId].signal1.count())
df[(df['Trend'] != trendId) & (df['signal1'] == trendId)]  # false positives


import pandas as pd
df = pd.read_csv("TSLA_last_30_days.csv")

dfpl = df[:]
print(dfpl.head())
print(len(dfpl))
import plotly.graph_objects as go
from datetime import datetime

fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['open'],
                high=dfpl['high'],
                low=dfpl['low'],
                close=dfpl['close'])])

fig.show()


"""

import csv

# Open the CSV file
with open('TSLA_last_30_days.csv', mode='r') as file:
  # Create a CSV reader
  csv_reader = csv.reader(file)
  
  # Extract the headers (first row)
  headers = next(csv_reader)
  
  # Initialize a dictionary to store data for each header
  data = {header: [] for header in headers}
  
  # Iterate through the rows and append data to the corresponding header
  for row in csv_reader:
    for header, value in zip(headers, row):
      data[header].append(value)
  
  # Print each header and its corresponding data
  for header in headers:
    print(f"{header}: {data[header]}")
"""

