#!/usr/bin/env python3

# ========== ========== ========== ========== ==========
# BEFORE you run this file:
# Fill in SYMBOL, START_MONTH, and END_MONTH
# Example: 
#   SYMBOL = "TSLA"
#   START_MONTH = "2023-12"
#   END_MONTH   = "2024-06"
# ========== ========== ========== ========== ==========

# This script will query Alpha Vantage's TIME_SERIES_INTRADAY endpoint
# with month=YYYY-MM, as per the new documentation that supports
# fetching specific months of historical intraday data.



import requests
import os

# Configuration
API_KEY = "VIBBPSYNEUTGVC3H"  # Your Alpha Vantage key
BASE_URL = "https://www.alphavantage.co/query"
INTERVAL = "1min"        # 1min, 5min, 15min, 30min, or 60min
SYMBOL = "TSLA"              # Leave blank if not ready to run
START_MONTH = "2023-12"  # e.g. "YYYY-MM"
END_MONTH   = "2024-05"  # e.g. "YYYY-MM"

# Display the command details and confirm with the user
confirmation_message = (
  f"You are about to fetch intraday data (1-min) from Alpha Vantage for '{SYMBOL}'\n"
  f"from {START_MONTH} through {END_MONTH} (regular hours only), in CSV format.\n\n"
  f"Is this correct and ready to proceed? (y to proceed, any other key to quit): "
)
confirmation = input(confirmation_message).strip().lower()
if confirmation != "y":
  print("Operation canceled.")
  exit()

def fetch_and_save_data(symbol, month, filename):
  """
  Fetch intraday 1-minute data for 'symbol' and 'month' (YYYY-MM),
  saving the CSV data to 'filename'.
  
  This uses the documented month parameter in TIME_SERIES_INTRADAY.
  """
  params = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": symbol,
    "interval": INTERVAL,
    "apikey": API_KEY,
    "datatype": "csv",
    # Per the docs you shared:
    #   adjusted=false => unadjusted (as-traded) prices
    #   extended_hours=false => no pre/post market data
    #   month=YYYY-MM => fetch the entire intraday data for this month
    "adjusted": "false",
    "extended_hours": "false",
    "month": month,
    # Optionally specify outputsize=full, but by specifying 'month=YYYY-MM',
    # the docs say the API should return the *full* intraday data for that month anyway.
    "outputsize": "full"
  }

  response = requests.get(BASE_URL, params=params)
  if response.status_code == 200:
    # If you want each month in its own standalone CSV file, just write in "wb" mode:
    with open(filename, "wb") as file:
      file.write(response.content)
    print(f"Data for month {month} saved to {filename}")
  else:
    print(f"Failed to fetch data for {month}: {response.status_code} - {response.text}")

def months_in_range(start_str, end_str):
  """
  Generates a list of YYYY-MM strings from start_str to end_str inclusive.
  Example: start_str='2023-12', end_str='2024-02'
  yields '2023-12', '2024-01', '2024-02'.
  """
  start_year, start_mon = map(int, start_str.split('-'))
  end_year, end_mon = map(int, end_str.split('-'))

  year = start_year
  month = start_mon

  while (year < end_year) or (year == end_year and month <= end_mon):
    yield f"{year}-{month:02d}"
    month += 1
    if month == 13:
      month = 1
      year += 1

# Specify the output directory
OUTPUT_DIR = "./TSLA/past_multiple_months"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fetch data for each month from START_MONTH to END_MONTH inclusive
for m in months_in_range(START_MONTH, END_MONTH):
  filename = os.path.join(OUTPUT_DIR, f"{SYMBOL}_regular_hours_interval_{INTERVAL}_{m}.csv")
  fetch_and_save_data(SYMBOL, m, filename)

