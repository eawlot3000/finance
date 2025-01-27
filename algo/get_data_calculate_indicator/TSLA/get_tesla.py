#!/usr/bin/env python3
import requests

# Configuration
API_KEY = "VIBBPSYNEUTGVC3H"
BASE_URL = "https://www.alphavantage.co/query"
SYMBOL = "TSLA"
INTERVAL = "1min"  # Time interval between two consecutive data points in the time series
OUTPUT_SIZE = "full"  # Fetch the full data for the specified month
DATATYPE = "csv"

# here you can specify the full month you want to fetch the data for
MONTH = "2024-06"  # Specify the month in YYYY-MM format

# API request parameters
params = {
  "function": "TIME_SERIES_INTRADAY",
  "symbol": SYMBOL,
  "interval": INTERVAL,
  "month": MONTH,  # Specify the month
  "outputsize": OUTPUT_SIZE,
  "datatype": DATATYPE,
  "apikey": API_KEY,
  "extended_hours": "false"  # Only fetch data for regular trading hours
}

# Fetch the data
response = requests.get(BASE_URL, params=params)

# Check if the request was successful
if response.status_code == 200:
  # Save the CSV data to a file
  filename = f"{SYMBOL}_regular_hours_{MONTH}.csv"
  with open(filename, "wb") as file:
    file.write(response.content)
  print(f"Data saved to {filename}")
else:
  print(f"Failed to fetch data: {response.status_code} - {response.text}")
