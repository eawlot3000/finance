#!/usr/bin/env python3

# it works
# this code will display in termianl about your holding and account balance

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time

class IBKRApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.account_data = {}
        self.portfolio_data = []

    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        if account not in self.account_data:
            self.account_data[account] = {}
        self.account_data[account][tag] = (value, currency)

    def accountSummaryEnd(self, reqId: int):
        print("Account summary received:")
        for account, data in self.account_data.items():
            print(f"Account: {account}")
            for tag, (value, currency) in data.items():
                print(f"  {tag}: {value} {currency}")

    def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, marketValue: float,
                        averageCost: float, unrealizedPNL: float, realizedPNL: float, accountName: str):
        self.portfolio_data.append({
            "symbol": contract.symbol,
            "secType": contract.secType,
            "position": position,
            "marketPrice": marketPrice,
            "marketValue": marketValue,
            "averageCost": averageCost,
            "unrealizedPNL": unrealizedPNL,
            "realizedPNL": realizedPNL,
            "accountName": accountName
        })

    def accountDownloadEnd(self, accountName: str):
        print(f"Portfolio data for account {accountName}:")
        for item in self.portfolio_data:
            print(item)

    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=None):
        print(f"Error. ReqId: {reqId}, Code: {errorCode}, Msg: {errorString}")
        if advancedOrderRejectJson:
            print(f"Advanced Order Reject JSON: {advancedOrderRejectJson}")

def run_loop(app):
    app.run()

if __name__ == "__main__":
    app = IBKRApp()
    app.connect("127.0.0.1", 7496, clientId=1)

    api_thread = threading.Thread(target=run_loop, args=(app,))
    api_thread.start()

    time.sleep(1)  # Allow connection to establish

    # Request account summary for all accounts
    app.reqAccountSummary(9001, "All", "NetLiquidation,TotalCashValue,EquityWithLoanValue")

    # Request portfolio updates for your account ID
    app.reqAccountUpdates(True, "U19929135")

    time.sleep(5)  # Allow data to be fetched

    # Stop account summary (if you no longer need updates)
    app.cancelAccountSummary(9001)

    # Keep portfolio updates running if needed (comment out the next line to keep it active)
    # app.reqAccountUpdates(False, "U19929135")

    time.sleep(1)  # Allow cancellations to complete

    app.disconnect()

