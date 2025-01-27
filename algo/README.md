# THE AUTOMATD STOCK TRADING PROJECT.


## Workflow Summary:
* `file0.py` pull the data of tickers from Alpha Vantage API and create ticker.csv file, must contains columns: Date, Open, High, Low, Close, Volume
* `file1.py` use python ibkr api, to get the real-time streaming data, during normal trading hours
* `file1.py` write these real-time data into each ticker.csv file, fill new rows constantly for each new data (Date, Open, High, Low, Close, Volume)
* `file2.py` a dedicated python file to calcuate the indicators (MACD/SMA/EMA/RSI/ATR/VWAP), and write the indicators into the same ticker.csv file (created new headers)
* `file3`, `the MOST IMPORTANT ONE` pure algorithmic trading / dedicated python file to make the trading decision (need to implement the logic more!!! like stop loss, take profit, etc.) MUST DO BEFORE deploy in the real world trading: **Backtesting**:
   - Use historical data to test the algorithm’s performance and refine the logic. (draw signal and graphs)



## Steps details:
### 1. to get the historial data, by stocks. and save it into .csv file.
* https://www.alphavantage.co/documentation/#time-series-data


### 2. create a new dir for a specific stock, with the ticker name, ie "TSLA", and in each folder, you need to have the following files ""TICKER.csv"":
* "TICKER.csv" - the stock price data that has the following columns:
    * "Date" - the date of the stock price
    * "Open" - the opening price of the stock
    * "High" - the highest price of the stock
    * "Low" - the lowest price of the stock
    * "Close" - the closing price of the stock
    * "Volume" - the volume of the stock

### 3. 
