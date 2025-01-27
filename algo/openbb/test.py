#!/usr/bin/env python3

from openbb import obb
obb.user.preferences.output_type = "dataframe"
start_date: "2025-01-01" # Start date to get data from with
interval: 1 # Interval (in minutes) to get data—that is, 1, 5, 15, 30, 60, or 1,440
end_date: "2025-01-25" # End date to get data from with
data = obb.equity.price.historical("SPY", provider="yfinance")
# print(data)


balance_sheet = obb.equity.fundamental.metrics(
  "AAPL,MSFT",
  provider="yfinance"
)

print(balance_sheet)
