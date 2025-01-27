#!/usr/bin/env python3
import pandas as pd
import ta
import os

def round_numeric_columns(df, decimal_places=2):
  """
  将 DataFrame 中的所有数值列(除时间列外)保留到小数点后 decimal_places 位。
  """
  numeric_cols = df.select_dtypes(include=['float', 'int']).columns
  for col in numeric_cols:
    df[col] = df[col].round(decimal_places)
  return df

def calculate_indicators(file_path):
  """
  读取 CSV (不会修改原文件)，计算多个技术指标并将结果输出到新的 CSV 文件。
  最终还会将所有数值列(除了 timestamp)保留小数点后两位。
  指标包括:
    - MACD_line, MACD_signal, MACD_histogram (默认参数, 无 window_sign)
    - SMA_50
    - EMA_200
    - RSI_14
    - ATR_14
    - VWAP
  """
  try:
    # 1. 确认文件是否存在
    if not os.path.exists(file_path):
      raise FileNotFoundError(f"File not found: {file_path}")

    # 2. 读取 CSV，解析日期列
    df = pd.read_csv(file_path, parse_dates=['timestamp'])

    # 3. 必列检测
    required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    for col in required_cols:
      if col not in df.columns:
        raise KeyError(f"Missing required column: {col}")

    # 4. 数值类型检测
    for col in ['open', 'high', 'low', 'close', 'volume']:
      if not pd.api.types.is_numeric_dtype(df[col]):
        raise TypeError(f"Column {col} must be numeric")

    # 5. 重置索引
    df = df.reset_index(drop=True)

    # 6. 内存中反转行顺序(把最早数据放在上)，便于正确计算滚动指标
    df_rev = df.iloc[::-1].copy()

    # 7. 计算各种指标 (在 df_rev 上做滚动计算)

    # 如果 ta.trend.macd_* 不支持 window_sign，你可以省略它
    df_rev['MACD_line'] = ta.trend.macd(df_rev['close'])
    df_rev['MACD_signal'] = ta.trend.macd_signal(df_rev['close'])
    df_rev['MACD_histogram'] = ta.trend.macd_diff(df_rev['close'])

    # SMA_50
    df_rev['SMA_50'] = ta.trend.sma_indicator(df_rev['close'], window=50)

    # EMA_200 # TODO: not accurate
    df_rev['EMA_200'] = ta.trend.ema_indicator(df_rev['close'], window=200)

    # # Calculate the hlc3 source price
    # df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3
    # # Reverse the source_price to match df_rev
    # source_price_rev = df.iloc[::-1]['hlc3']
    # # Calculate EMA on reversed source_price
    # df_rev['EMA_200'] = ta.trend.ema_indicator(source_price_rev, window=200)



    # RSI_14
    df_rev['RSI_14'] = ta.momentum.rsi(df_rev['close'], window=14)

    # ATR_14
    df_rev['ATR_14'] = ta.volatility.average_true_range(
      df_rev['high'],
      df_rev['low'],
      df_rev['close'],
      window=14
    )

    # VWAP
    df_rev['VWAP'] = ta.volume.volume_weighted_average_price(
      df_rev['high'],
      df_rev['low'],
      df_rev['close'],
      df_rev['volume']
    )

    # 8. 将 df_rev 再反转回原顺序（最新数据在上）
    df_final = df_rev.iloc[::-1].reset_index(drop=True)

    # 9. 将新指标列合并回原 df
    new_cols = [
      'MACD_line','MACD_signal','MACD_histogram',
      'SMA_50','EMA_200','RSI_14','ATR_14','VWAP'
    ]
    for col in new_cols:
      df[col] = df_final[col]

    # 10. 对所有数值列(非 timestamp)四舍五入到小数点后2位
    df = round_numeric_columns(df, decimal_places=2)

    # 11. 不覆盖原文件，而是新建 "_with_indicators" CSV
    base, ext = os.path.splitext(file_path)
    output_file = f"{base}_with_indicators{ext}"
    df.to_csv(output_file, index=False)

    print(f"Indicators calculated and saved to: {output_file}")

  except Exception as e:
    print(f"Error: {e}")

if __name__ == '__main__':
  # 使用时替换为你的CSV文件路径
  file_path = './TSLA/TSLA_regular_hours_interval_1min_2023-12_2025-01.csv'
  calculate_indicators(file_path)


