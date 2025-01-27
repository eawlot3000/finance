# o1 model, but just had exactly the same result (maybe algorithm same as well)
# https://chatgpt.com/c/6796f68c-0bc4-8002-a337-1742f11be572


import pandas as pd

def main():
  # Load data
  file_path = './TSLA/TSLA_regular_hours_interval_1min_2023-12_2025-01_with_indicators.csv'
  df = pd.read_csv(file_path)

  # Reverse so the oldest row is first; confirm your CSV isn't already in ascending order
  df = df.iloc[::-1].reset_index(drop=True)

  # Convert 'timestamp' to datetime
  df['timestamp'] = pd.to_datetime(df['timestamp'], format='%m/%d/%Y %H:%M')

  # Calculate rolling mean for ATR (as in your original code)
  atr_window = 14
  df['ATR_mean'] = df['ATR_14'].rolling(window=atr_window).mean()

  # Define signals (original logic)
  df['Signal'] = df.apply(generate_signals, axis=1)

  # Print how many signals were generated
  print("Signal Counts:")
  print("BUY  :", (df['Signal'] == 'BUY').sum())
  print("SELL :", (df['Signal'] == 'SELL').sum())
  print("HOLD :", (df['Signal'] == 'HOLD').sum(), "\n")

  # Backtest
  df = backtest_portfolio(df, initial_balance=10000)

  # Analyze the results
  monthly_summary = analyze_portfolio(df, initial_balance=10000)

  # Save results
  df.to_csv('trading_results_with_signals.csv', index=False)
  monthly_summary.to_csv('monthly_performance_summary.csv', index=True)

def generate_signals(row):
  """
  Original signal logic:
    BUY if MACD histogram > 0, RSI < 30, and ATR_14 > ATR_mean
    SELL if MACD histogram < 0 and RSI > 70
    otherwise HOLD
  """
  if (row['MACD_histogram'] > 0
      and row['RSI_14'] < 30
      and row['ATR_14'] > row['ATR_mean']):
    return 'BUY'
  elif (row['MACD_histogram'] < 0
        and row['RSI_14'] > 70):
    return 'SELL'
  else:
    return 'HOLD'

def backtest_portfolio(df, initial_balance=10000):
  """
  Backtesting logic to calculate portfolio performance,
  the same way as your original code.
  """
  balance = initial_balance
  position = 0
  df['Portfolio_Value'] = float(initial_balance)

  for i, row in df.iterrows():
    if row['Signal'] == 'BUY' and balance > 0:
      # Buy as many shares as possible
      position = balance / row['close']
      balance = 0
    elif row['Signal'] == 'SELL' and position > 0:
      # Sell all shares
      balance = position * row['close']
      position = 0

    # Update portfolio value on each row
    df.at[i, 'Portfolio_Value'] = balance if balance > 0 else position * row['close']

  return df

def analyze_portfolio(df, initial_balance=10000):
  """
  Analyze portfolio performance:
    - Start/End date
    - Total trading days
    - Duration in months
    - Monthly income and growth rate
    - Total ROI and average monthly/yearly ROI
  """
  # Extract unique trading dates
  df['Trading_Date'] = df['timestamp'].dt.date
  unique_trading_days = df['Trading_Date'].nunique()

  # Start & end date
  trading_start_date = df['Trading_Date'].iloc[0]
  trading_end_date = df['Trading_Date'].iloc[-1]

  # Total months over the trading period
  total_months = (
    (trading_end_date.year - trading_start_date.year) * 12
    + (trading_end_date.month - trading_start_date.month)
    + 1
  )

  # Group by month
  df['Month'] = df['timestamp'].dt.to_period('M')
  monthly_summary = df.groupby('Month').agg(
    Monthly_End_Value=('Portfolio_Value', 'last')
  )

  # Calculate monthly income/growth
  monthly_summary['Monthly_Income'] = monthly_summary['Monthly_End_Value'].diff().fillna(0)
  monthly_summary['Monthly_Growth_Rate'] = (
    monthly_summary['Monthly_Income'] 
    / monthly_summary['Monthly_End_Value'].shift(1).fillna(initial_balance)
  )

  # Final calculations
  final_value = df['Portfolio_Value'].iloc[-1]
  total_profit = final_value - initial_balance
  total_roi = total_profit / initial_balance

  avg_monthly_roi = total_roi / total_months
  avg_yearly_roi = avg_monthly_roi * 12

  # Print summary
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

  print("\n================================")
  print("Monthly Performance:\n")
  print(monthly_summary)

  return monthly_summary

if __name__ == '__main__':
  main()

