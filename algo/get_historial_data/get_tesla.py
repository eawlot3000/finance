#!/usr/bin/env python3
import requests

# Configuration
API_KEY = "VIBBPSYNEUTGVC3H"
BASE_URL = "https://www.alphavantage.co/query"
SYMBOL = "TSLA"
INTERVAL = "1min"
OUTPUT_SIZE = "full"  # Fetch the most recent 30 days of intraday data
DATATYPE = "csv"

# API request parameters
params = {
  "function": "TIME_SERIES_INTRADAY",
  "symbol": SYMBOL,
  "interval": INTERVAL,
  "outputsize": OUTPUT_SIZE,
  "datatype": DATATYPE,
  "apikey": API_KEY,
}

# Fetch the data
response = requests.get(BASE_URL, params=params)

# Check if the request was successful
if response.status_code == 200:
  # Save the CSV data to a file
  filename = f"{SYMBOL}_last_30_days.csv"
  with open(filename, "wb") as file:
    file.write(response.content)
  print(f"Data saved to {filename}")
else:
  print(f"Failed to fetch data: {response.status_code} - {response.text}")

