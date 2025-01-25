#!/usr/bin/env python3
import threading
import time
from flask import Flask, render_template, jsonify
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

# Flask app
app = Flask(__name__)

# Global variables for storing data
account_data = {}
portfolio_data = []
total_unrealized_pnl = 0.0
total_daily_pnl = 0.0
refresh_count = 0

# IBKR API App
class IBKRApp(EWrapper, EClient):
  def __init__(self):
    EClient.__init__(self, self)

  def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
    global account_data
    if account not in account_data:
      account_data[account] = {}
    account_data[account][tag] = (value, currency)

  def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float,
                      averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
    global portfolio_data, total_unrealized_pnl
    portfolio_data.append({
      "symbol": contract.symbol,
      "secType": contract.secType,
      "position": position,
      "marketPrice": round(marketPrice, 2),
      "marketValue": round(marketValue, 2),
      "averageCost": round(averageCost, 2),
      "unrealizedPNL": round(unrealizedPNL, 2),
      "realizedPNL": round(realizedPNL, 2),
      "accountName": accountName
    })
    total_unrealized_pnl += unrealizedPNL

  def dailyPnL(self, reqId: int, dailyPnL: float):
    global total_daily_pnl
    total_daily_pnl += dailyPnL


def run_loop(app):
  app.run()

# Start IBKR API connection

def start_ibkr():
  global app_ibkr
  app_ibkr = IBKRApp()
  app_ibkr.connect("127.0.0.1", 7496, clientId=1)

  api_thread = threading.Thread(target=run_loop, args=(app_ibkr,))
  api_thread.start()

  time.sleep(1)  # Allow connection to establish

  while True:
    global portfolio_data, account_data, refresh_count, total_unrealized_pnl, total_daily_pnl

    portfolio_data.clear()  # Clear previous portfolio data
    total_unrealized_pnl = 0.0
    total_daily_pnl = 0.0

    app_ibkr.reqAccountSummary(9001, "All", "NetLiquidation,TotalCashValue,EquityWithLoanValue")
    app_ibkr.reqAccountUpdates(True, "U19929135")

    time.sleep(5)  # Wait to gather data

    app_ibkr.cancelAccountSummary(9001)
    app_ibkr.reqAccountUpdates(False, "U19929135")

    refresh_count += 1
    print(f"Data updated successfully {refresh_count} times.")
    time.sleep(30)  # Update every 30 seconds

# Flask routes
@app.route("/")
def home():
  global account_data, portfolio_data, refresh_count, total_unrealized_pnl, total_daily_pnl
  return render_template("index.html", account_data=account_data, portfolio_data=portfolio_data, 
                         refresh_count=refresh_count, total_unrealized_pnl=round(total_unrealized_pnl, 2), 
                         total_daily_pnl=round(total_daily_pnl, 2))

@app.route("/refresh_count")
def get_refresh_count():
  global refresh_count
  return jsonify({"refresh_count": refresh_count})

# Start Flask in a separate thread
def start_flask():
  app.run(debug=True, use_reloader=False, port=5001)

if __name__ == "__main__":
  # Start IBKR API and Flask app in separate threads
  threading.Thread(target=start_ibkr).start()
  threading.Thread(target=start_flask).start()

