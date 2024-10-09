from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import *
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime  # Import the datetime module
import pytz

class StockPrice(EWrapper, EClient):

    def __init__(self,stockname,newstime):
        EClient.__init__(self, self)
        self.historical_data = {}
        self.stock_name = stockname
        self.news_time  = newstime 

    def nextValidId(self, orderId: int):
        # Request historical data for AAPL
        self.reqHistoricalData(
            reqId=1,
            contract=self.create_contract(self.stock_name, "STK", "USD", "SMART"),
            endDateTime=self.news_time,
            #endDateTime="",
            durationStr="1 D",  # Last day
            barSizeSetting="1 min",  # 1-minute bars
            whatToShow="TRADES",
            useRTH=0,  # Include data outside regular trading hours (1 for regular hour trading market)
            formatDate=1,  # Format date as YYYYMMDD
            keepUpToDate=False,
            chartOptions=None,
        )

    def create_contract(self, symbol, secType, currency, exchange):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = secType
        contract.currency = currency
        contract.exchange = exchange
        return contract

    def historicalData(self, reqId: int, bar: BarData):
        # Store historical data in a dictionary
        symbol = self.historical_data.setdefault(reqId, {}).setdefault("symbol", self.stock_name)
        self.historical_data[reqId].setdefault("data", []).append({
            "date": bar.date,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume
        })

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        self.write_to_csv(reqId)
        self.disconnect()

    def error(self, reqId, errorCode, errorString):
        print(f"Error: reqId:{reqId} errorCode:{errorCode} errorString:{errorString}")

    def write_to_csv(self, reqId):
        # Write historical data to a CSV file
        with open('historical_data.csv', 'w', newline='') as csvfile:
            fieldnames = ['date', 'open', 'high', 'low', 'close', 'volume']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for data_point in self.historical_data[reqId]["data"]:
                writer.writerow(data_point)

    def plot_data(self, reqId):
        # Plot the historical data with adjusted x-axis ticks and normalized prices
        data = self.historical_data[reqId]["data"]
        dates = [mdates.datestr2num(d["date"]) for d in data]  # Convert dates to numbers since GMT
        close_prices = [d["close"] for d in data]

        # Find the index of the close price closest to 1 PM
        target_time = datetime.datetime(2024, 10, 1, 13, 00, tzinfo=pytz.timezone('GMT')).timestamp() #transform 
        closest_index = min(range(len(dates)), key=lambda i: abs(dates[i]*86400 - target_time))
        normalization_price = close_prices[closest_index]

        # Normalize close prices to percentage change from the normalization price
        normalized_prices = [(price - normalization_price) / normalization_price * 100 for price in close_prices]

        plt.plot(dates, normalized_prices)
        plt.xlabel("Time")
        plt.ylabel("Close Price Change (%)")  # Update y-axis label
        date_str = mdates.num2date(dates[0]).strftime('%Y-%m-%d')
        plt.title(self.stock_name + " Historical Data - " + date_str)  # Add date to title
        plt.axvline(x=dates[closest_index], color='red', linestyle='--', label='Target Time (1 PM)')

        # Set x-axis locator and formatter for hourly ticks
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Format as HH:MM

        plt.xticks(rotation=45)
        plt.show()

def main():
    app = StockPrice("UNFI","20241001 15:00:00 US/Eastern")
    app.connect('127.0.0.1', 7496, 123)
    app.run()
    print("Historical data:", app.historical_data)
    print("Ploting data:",app.plot_data(1)) # Plot the data with reqId 1

if __name__ == '__main__':
    main()
