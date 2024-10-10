from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import *
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime  # Import the datetime module
import pytz

# reqhistoricaldata has 15 min delay compare to stock_price.py due to my Market Data Subscriptions with Interactive Broker
# How to check and update your subscriptions:
# 1. Log in to Account Management: Go to the Interactive Brokers Account Management website.
# 2. Navigate to Market Data Subscriptions: Find the section for managing your market data subscriptions. 
# The exact location might vary depending on your account type.
# 3. Check for the Instrument: Look for the specific instrument (stock, futures, etc.) 
# for which you're requesting historical data.
# 4. Subscription Status: Check if you have a real-time subscription for that instrument. 
# If you only have a delayed subscription or no subscription, that's the reason for the 15-minute delay.
# 5. Upgrade Subscription: If necessary, upgrade your subscription to real-time for that instrument. 
# This might involve additional fees.

class TimeChecker(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        self.reqCurrentTime()  # Request the current time

    def currentTime(self, time: int):
        # This method is called when the server sends the time
        print("IB time:", datetime.datetime.fromtimestamp(time)) 
        self.disconnect()

    def error(self, reqId, errorCode, errorString):
        print(f"Error: reqId:{reqId} errorCode:{errorCode} errorString:{errorString}")

class StockPrice(EWrapper, EClient):

    def __init__(self,stockname,newstime):
        EClient.__init__(self, self)
        self.historical_data = {}
        self.stock_name = stockname
        self.news_time  = newstime #  
        self.maxover5   = 0 # pourcentage of evolution max over 5h after news release
        self.minover5   = 0 # pourcentage de variation min over 5h after news release

    def add_10h_to_datetime_str(self,datetime_str):
      """
      Adds 10 hours to a datetime string in the format 'YYYYMMDD HH:MM:SS US/TimeZone',
      keeping the original time zone string.
    
      Args:
        datetime_str: The datetime string.
    
      Returns:
        A new datetime string with 10 hours added, preserving the original time zone string.
      """
      try:
        # Split the string to extract the date, time, and time zone information
        datetime_part, tz_part = datetime_str.rsplit(' ', 1)
    
        # Create a datetime object
        datetime_object = datetime.datetime.strptime(datetime_part, '%Y%m%d %H:%M:%S')
    
        # Get the time zone object
        tz_object = pytz.timezone(tz_part)
    
        # Make the datetime object aware of the time zone
        datetime_object = tz_object.localize(datetime_object)
    
        # Add 10 hours
        new_datetime_object = datetime_object + datetime.timedelta(hours=10)
    
        # Format the new datetime object back into a string with the original time zone
        new_datetime_str = new_datetime_object.strftime('%Y%m%d %H:%M:%S ') + tz_part
        return new_datetime_str
    
      except ValueError:
        return "Invalid datetime format"

    def nextValidId(self, orderId: int):
        # Request historical data for AAPL
        self.reqMarketDataType(MarketDataTypeEnum.REALTIME) # or DELAYED
        self.reqHistoricalData(
            reqId=1,
            contract=self.create_contract(self.stock_name, "STK", "USD", "SMART"),
            endDateTime=self.add_10h_to_datetime_str(self.news_time),
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

    def get_target_time_gmt(self):
        try:
            # Split the string to extract the date, time, and time zone information
            datetime_part, tz_part = self.news_time.rsplit(' ', 1)
        
            # Create a datetime object with the specified time zone
            datetime_object = datetime.datetime.strptime(datetime_part, '%Y%m%d %H:%M:%S')
        
            # Get the time zone object
            tz_object = pytz.timezone(tz_part)
        
            # Make the datetime object aware of the time zone
            datetime_object = tz_object.localize(datetime_object)

            # Convert to GMT time zone
            gmt_datetime_object = datetime_object.astimezone(pytz.timezone('GMT'))
        
            # Get the timestamp in seconds since epoch GMT
            target_time_gmt = gmt_datetime_object.timestamp()

            return target_time_gmt
    
        except ValueError:
            return "Invalid datetime format"


    def plot_data(self, reqId):
        # Plot the historical data with adjusted x-axis ticks and normalized prices
        data = self.historical_data[reqId]["data"]
        #dates = [mdates.datestr2num(d["date"])+3600.0/86400.0 for d in data]  
        dates = [mdates.datestr2num(d["date"])+3600.0/86400.0 for d in data]  # Convert dates(GMT+2) to second since epoch GMT
        close_prices = [d["close"] for d in data]

        # Find the index of the close price closest to 1 PM
        #target_time = datetime.datetime(2024, 10, 1, 13, 00, tzinfo=pytz.timezone('GMT')).timestamp() #transform 
        target_time = self.get_target_time_gmt()+3600*2 # from GMT to GMT+2
        closest_index = min(range(len(dates)), key=lambda i: abs(dates[i]*86400 - target_time))

        # Calculate the index for 5 hours after the target time
        index_5h_after_target = min(closest_index + 5 * 60, len(dates) - 1)  # 5 hours * 60 minutes/hour
        
        # Normalize close prices to percentage change from the normalization price
        normalization_price = close_prices[closest_index]
        normalized_prices = [(price - normalization_price) / normalization_price * 100 for price in close_prices]

        # Compute the max price over the 5 hours after the target time
        self.maxover5 = max(normalized_prices[closest_index:index_5h_after_target + 1])
        # Compute the min price over the 5 hours after the target time
        self.minover5 = min(normalized_prices[closest_index:index_5h_after_target + 1])

        # Print the max and Min price
        print(f"Max price over 5 hours after target time: {self.maxover5}")
        print(f"Min price over 5 hours after target time: {self.minover5}")

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

def transform_datetime_to_IBformat(datetime_str):
  """
  Transforms a datetime string from the format "Month DD, YYYY HH:MM PM" 
  to "YYYYMMDD HH:MM:SS US/Eastern" ! US/Eastern is hardcoded for now

  Args:
    datetime_str: The datetime string in the original format.

  Returns:
    The transformed datetime string in the desired format.
  """
  try:
    if "Eastern Daylight Time" not in datetime_str:
      raise ValueError(f"Substring 'Eastern Daylight Time' not found in '{datetime_str}', cannot manage other time zone conversion for now")
    
    # Re-combine the parts
    extracted_str = datetime_str.replace(" Eastern Daylight Time","")

    # Parse the modified string into a datetime object
    datetime_object = datetime.datetime.strptime(extracted_str, "%B %d, %Y %I:%M %p")

    # Format the datetime object into the desired output format
    transformed_str = datetime_object.strftime("%Y%m%d %H:%M:%S US/Eastern")
    return transformed_str

  except ValueError as e:
    print(f"Error: {e}")
    return None


def main():
    mytime="September 04, 2024 07:00 AM Eastern Daylight Time"
    #mytime="October 07, 2024 09:00 AM Eastern Daylight Time"
    #mytime="October 09, 2024 09:48 PM Eastern Daylight Time"
    mystock="CIEN"
    app = StockPrice(mystock,transform_datetime_to_IBformat(mytime))
    app.connect('127.0.0.1', 7496, 123)
    app.run()
    print("Historical data:", app.historical_data)
    print("Ploting data:",app.plot_data(1)) # Plot the data with reqId 1
#    app2 = TimeChecker()
#    print("running")
#    app2.connect('127.0.0.1', 7496, 123)
#    app2.run()

if __name__ == '__main__':
    main()
