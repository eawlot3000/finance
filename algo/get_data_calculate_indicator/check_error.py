#!/usr/bin/env python3
import pandas as pd

# TODO: change your different file paths here !!!
file_to_check = './TSLA/TSLA_regular_hours_interval_1min_2023-12_2025-01_with_indicators.csv'
df = pd.read_csv(file_to_check)




# Convert 'timeframe' to datetime (if it exists)
if 'timeframe' in df.columns:
    df['timeframe'] = pd.to_datetime(df['timeframe'], format='%m/%d/%Y %H:%M')

# Quick stats
print(df.describe())

# Exclude non-numeric columns for correlation matrix
numeric_df = df.select_dtypes(include=['float64', 'int64'])
print(numeric_df.corr())

