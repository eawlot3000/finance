#!/usr/bin/env python3





import pandas as pd

def main():
  # 1. 读取数据
  file_path = './TSLA/TSLA_regular_hours_interval_1min_2023-12_2025-01_with_indicators.csv'
  df = pd.read_csv(file_path)

  # 2. 数据顺序处理：确保最早日期在顶部
  df = df.iloc[::-1].reset_index(drop=True)

  # 3. 时间戳转换
  df['timestamp'] = pd.to_datetime(df['timestamp'], format='%m/%d/%Y %H:%M')

  # 4. 计算 ATR 滚动均值
  atr_window = 14
  df['ATR_mean'] = df['ATR_14'].rolling(window=atr_window).mean()

  # 5. 生成交易信号（此处保留“更激进的BUY”逻辑为例，也可替换回原逻辑）
  df[['Signal', 'Reason']] = df.apply(
    lambda row: pd.Series(generate_signals_more_aggressive(row)),
    axis=1
  )

  # 6. 打印统计信息（便于了解多少 BUY / SELL / HOLD）
  print("Signal Counts:")
  print("BUY  :", (df['Signal'] == 'BUY').sum())
  print("SELL :", (df['Signal'] == 'SELL').sum())
  print("HOLD :", (df['Signal'] == 'HOLD').sum(), "\n")

  # 7. 回测
  df = backtest_portfolio(df, initial_balance=10000)

  # 8. 分析结果
  monthly_summary = analyze_portfolio(df, initial_balance=10000)

  # 9. 存盘
  df.to_csv('trading_results_with_signals.csv', index=False)
  monthly_summary.to_csv('monthly_performance_summary.csv', index=True)

def generate_signals_more_aggressive(row):
  """
  更激进的买入逻辑 + 原本的卖出逻辑不变。

  逻辑示例：
  - BUY:
      * MACD_histogram > -0.1 (比 0 更宽松)
      * RSI_14 < 45 (比 < 30 更宽松)
      * ATR_14 > 0.8 * ATR_mean (比 > ATR_mean 更宽松)
  - SELL:
      * MACD_histogram < 0
      * RSI_14 > 70
    与原逻辑相同
  - HOLD:
      否则不动作

  返回值: (signal, reason)
  """
  macd = row['MACD_histogram']
  rsi = row['RSI_14']
  atr = row['ATR_14']
  atr_mean = row['ATR_mean']

  # 更激进的买入条件
  buy_cond = (
    (macd > -0.1) and
    (rsi < 45) and
    (atr > 0.8 * atr_mean)
  )

  # 卖出条件（不变）
  sell_cond = (
    (macd < 0) and
    (rsi > 70)
  )

  if buy_cond:
    reason = (
      f"Buy: MACD_hist={macd:.2f} > -0.1, "
      f"RSI={rsi:.2f} < 45, "
      f"ATR_14={atr:.2f} > 0.8*ATR_mean={0.8*atr_mean:.2f}"
    )
    return ('BUY', reason)
  elif sell_cond:
    reason = (
      f"Sell: MACD_hist={macd:.2f} < 0, "
      f"RSI={rsi:.2f} > 70"
    )
    return ('SELL', reason)
  else:
    reason = (
      f"Hold: MACD_hist={macd:.2f}, "
      f"RSI={rsi:.2f}, "
      f"ATR_14={atr:.2f}, "
      f"ATR_mean={atr_mean:.2f}"
    )
    return ('HOLD', reason)

def backtest_portfolio(df, initial_balance=10000):
  """
  回测逻辑：
    - balance 现金余额
    - position 持有的股票数量
    - 仅在 (signal == 'BUY' and balance>0) 或 (signal == 'SELL' and position>0) 时打印交易信息
    - 通过记录上一次买入的金额 last_buy_cost 来计算卖出时的单次交易收益
  """
  balance = initial_balance
  position = 0
  df['Portfolio_Value'] = float(initial_balance)

  # 记录上次买入时实际花费的现金
  # 当下一次 SELL 时，可计算单次交易盈利:  (本次卖出所得 - last_buy_cost)
  last_buy_cost = 0.0  

  # 交易编号，从 0 开始
  transaction_count = 0

  for i, row in df.iterrows():
    current_signal = row['Signal']
    reason = row['Reason']
    timestamp = row['timestamp']
    close_price = row['close']

    # (1) BUY 信号 && balance > 0 才能实际买入
    if current_signal == 'BUY' and balance > 0:
      # 打印交易信息
      print("="*60)
      print(f"Transaction Index: {transaction_count}")
      print(f"DataFrame Row Index: {i}")
      print(f"Time: {timestamp}")
      print(f"Close Price: {close_price:.4f}")
      print(f"Signal: {current_signal}")
      print(f"Reason: {reason}")
      print(f"Current Balance (Before Buy): {balance:.2f}")
      print(f"Current Position (shares): {position:.4f}")

      # 用全部余额买入
      position = balance / close_price
      last_buy_cost = balance  # 记录此次买入花费
      balance = 0.0

      transaction_count += 1  # 更新交易次数

      print(f"Bought {position:.4f} shares. New Balance = {balance:.2f}")
      print(f"----")

    # (2) SELL 信号 && position > 0 才能实际卖出
    elif current_signal == 'SELL' and position > 0:
      print("="*60)
      print(f"Transaction Index: {transaction_count}")
      print(f"DataFrame Row Index: {i}")
      print(f"Time: {timestamp}")
      print(f"Close Price: {close_price:.4f}")
      print(f"Signal: {current_signal}")
      print(f"Reason: {reason}")
      print(f"Current Balance (Before Sell): {balance:.2f}")
      print(f"Current Position (shares): {position:.4f}")

      # 全部卖出
      sell_amount = position * close_price
      balance = sell_amount
      position = 0.0

      # 计算本次交易盈利
      profit = sell_amount - last_buy_cost
      # 避免除零
      roi_per_trade = profit / last_buy_cost if last_buy_cost != 0 else 0.0

      transaction_count += 1

      print(f"Sold all shares for {sell_amount:.2f} USD.")
      print(f"Trade Profit: {profit:.2f}, ROI: {roi_per_trade:.2%}")
      print(f"New Balance: {balance:.2f}")
      print(f"----")

      # 卖出后，将 last_buy_cost 归零，以便下次买入重新计算
      last_buy_cost = 0.0

    # 无论是否交易，都要更新当下的组合价值
    portfolio_value = balance if balance > 0 else position * close_price
    df.at[i, 'Portfolio_Value'] = portfolio_value

  return df

def analyze_portfolio(df, initial_balance=10000):
  """
  分析:
    - 起止日期
    - 交易天数
    - 持续月数
    - 每月末的组合价值、月度收益、月度增长率
    - 总收益率ROI，月度/年度平均ROI
  """
  df['Trading_Date'] = df['timestamp'].dt.date
  unique_trading_days = df['Trading_Date'].nunique()

  # 起止日期
  trading_start_date = df['Trading_Date'].iloc[0]
  trading_end_date = df['Trading_Date'].iloc[-1]

  # 总月数
  total_months = (
    (trading_end_date.year - trading_start_date.year) * 12
    + (trading_end_date.month - trading_start_date.month)
    + 1
  )

  # 按月分组
  df['Month'] = df['timestamp'].dt.to_period('M')
  monthly_summary = df.groupby('Month').agg(
    Monthly_End_Value=('Portfolio_Value', 'last')
  )

  # 计算月度收益、月度增长率
  monthly_summary['Monthly_Income'] = monthly_summary['Monthly_End_Value'].diff().fillna(0)
  monthly_summary['Monthly_Growth_Rate'] = (
    monthly_summary['Monthly_Income'] 
    / monthly_summary['Monthly_End_Value'].shift(1).fillna(initial_balance)
  )

  # 总收益
  final_value = df['Portfolio_Value'].iloc[-1]
  total_profit = final_value - initial_balance
  total_roi = total_profit / initial_balance if initial_balance != 0 else 0

  avg_monthly_roi = total_roi / total_months
  avg_yearly_roi = avg_monthly_roi * 12

  # 打印结果
  print("\nPortfolio Analysis Summary:\n")
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

