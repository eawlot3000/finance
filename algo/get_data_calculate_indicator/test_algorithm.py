# by 4o
# 1/26/25
# https://chatgpt.com/c/6796dfe9-9ff4-8002-8dca-4d65a9e210e2


import pandas as pd

# Load data
file_path = './TSLA/TSLA_regular_hours_interval_1min_2023-12_2025-01_with_indicators.csv'
df = pd.read_csv(file_path)


# Reverse the DataFrame so that data is ordered from oldest to latest
df = df.iloc[::-1].reset_index(drop=True)


# Convert 'timestamp' column to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%m/%d/%Y %H:%M')

# Calculate rolling mean for ATR (for volatility detection)
atr_window = 14
df['ATR_mean'] = df['ATR_14'].rolling(window=atr_window).mean()

# Define trading signals
def generate_signals(row):
  if (row['MACD_histogram'] > 0 and 
      row['RSI_14'] < 30 and 
      row['ATR_14'] > row['ATR_mean']):
    return 'BUY'
  elif (row['MACD_histogram'] < 0 and 
        row['RSI_14'] > 70):
    return 'SELL'
  else:
    return 'HOLD'

# Apply the trading logic to the DataFrame
df['Signal'] = df.apply(generate_signals, axis=1)

# Backtesting the strategy
def backtest_portfolio(df, initial_balance=10000):
  """Backtesting logic to calculate portfolio performance."""
  balance = initial_balance
  position = 0
  df['Portfolio_Value'] = float(initial_balance)  # Explicitly set as float

  for i, row in df.iterrows():
    if row['Signal'] == 'BUY' and balance > 0:
      position = balance / row['close']  # Buy as many shares as possible
      balance = 0
    elif row['Signal'] == 'SELL' and position > 0:
      balance = position * row['close']  # Sell all shares
      position = 0
    # Update portfolio value
    df.at[i, 'Portfolio_Value'] = balance if balance > 0 else position * row['close']

  return df

# Run backtest
df = backtest_portfolio(df)

def analyze_portfolio(df, initial_balance=10000):
  """
  Analyze portfolio performance:
  - Start and end date
  - Total trading days (count only unique trading dates)
  - Total duration in months (based on trading days)
  - Monthly income and growth rate
  - Total ROI (Return on Investment)
  - Average monthly and yearly ROI
  """
  # Extract trading days
  df['Trading_Date'] = df['timestamp'].dt.date  # Extract unique trading dates
  unique_trading_days = df['Trading_Date'].nunique()  # Count unique trading days

  # Start and end date (based on unique trading dates)
  trading_start_date = df['Trading_Date'].iloc[0]
  trading_end_date = df['Trading_Date'].iloc[-1]

  # Total months (based on trading period)
  total_months = (trading_end_date.year - trading_start_date.year) * 12 + \
                 (trading_end_date.month - trading_start_date.month) + 1

  # Calculate monthly income
  df['Month'] = df['timestamp'].dt.to_period('M')  # Group by month
  monthly_summary = df.groupby('Month').agg(
    Monthly_End_Value=('Portfolio_Value', 'last'),  # Portfolio value at the end of each month
  )
  monthly_summary['Monthly_Income'] = monthly_summary['Monthly_End_Value'].diff().fillna(0)
  monthly_summary['Monthly_Growth_Rate'] = monthly_summary['Monthly_Income'] / monthly_summary['Monthly_End_Value'].shift(1).fillna(initial_balance)

  # Calculate total ROI
  final_value = df['Portfolio_Value'].iloc[-1]
  total_profit = final_value - initial_balance
  total_roi = total_profit / initial_balance

  # Average monthly and yearly ROI
  avg_monthly_roi = total_roi / total_months
  avg_yearly_roi = avg_monthly_roi * 12

  # Print results
  print("Portfolio Analysis Summary:\n")
  print(f"Trading Start Date: {trading_start_date}")
  print(f"Trading End Date: {trading_end_date}")
  print(f"Total Trading Days: {unique_trading_days} days")
  print(f"Total Duration: {total_months} months")
  print(f"Final Portfolio Value: ${final_value:.2f}")
  print(f"Total Profit: ${total_profit:.2f}")
  print(f"Total ROI: {total_roi:.2%}")
  print(f"Average Monthly ROI: {avg_monthly_roi:.2%}")
  print(f"Average Yearly ROI: {avg_yearly_roi:.2%}")

  # Print monthly details
  print("\n================================")
  print("Monthly Performance:\n")
  print(monthly_summary)

  return monthly_summary





# Analyze portfolio
monthly_summary = analyze_portfolio(df)

# Save results
df.to_csv('trading_results_with_signals.csv', index=False)
monthly_summary.to_csv('monthly_performance_summary.csv')
