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


class HistoricPrice(EWrapper, EClient):
    def __init__(self, stockname, newstime, boolshow):
        EClient.__init__(self, self)
        self.historical_data = {}
        self.stock_name = stockname
        self.news_time = newstime 
        self.maxover5 = 0  # pourcentage of evolution max over 5h after news release
        self.minover5 = 0  # pourcentage de variation min over 5h after news release
        self.boolplot: bool = boolshow  # not show graph, 1 show graph

    def getmaxover5(self) -> float:
        return self.maxover5
    
    def getminover5(self) -> float:
        return self.minover5

    def add_10h_to_datetime_str(self, datetime_str):
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

        # Check if the time is between 4h and 7h
        hour = new_datetime_object.hour
        if 4 <= hour < 7:
            new_datetime_object += datetime.timedelta(hours=10)  # Add 4 more hours to avoid IB API crash
    
        # Format the new datetime object back into a string with the original time zone
        new_datetime_str = new_datetime_object.strftime('%Y%m%d %H:%M:%S ') + tz_part
        print("my time plus 10h:",new_datetime_str)
        return new_datetime_str
    
      except ValueError:
        return "Invalid datetime format"

    def nextValidId(self, orderId: int):
        # Request historical data for AAPL
        # Warning if endDateTime is between 4h00 and 7h00 of the morning it doesn't work -> adding firewall
        self.reqMarketDataType(MarketDataTypeEnum.REALTIME) # or DELAYED
        self.reqHistoricalData(
            reqId=1,
            contract=self.create_contract(self.stock_name, "STK", "USD", "SMART"),
            endDateTime=self.add_10h_to_datetime_str(self.news_time),
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

    def get_news_time(self):
        try:
            # Split the string to extract the date, time, and time zone information
            date_part, time_part, tz_part = self.news_time.rsplit(' ', 2)  # Split into 3 parts
            tz_part = tz_part.replace("Daylight ", "")  # Remove "Daylight"
            tz_part = tz_part.replace("Standard ", "")  # Remove "Standard"

            # Re-combine the parts
            datetime_str = f"{date_part} {time_part} {tz_part}"

            # Create a datetime object with the specified time zone
            datetime_object = datetime.datetime.strptime(f"{date_part} {time_part}",'%Y%m%d %H:%M:%S')

            # Make the datetime object aware of the time zone
            # tz_object = pytz.timezone('US/Eastern')  # Use the correct time zone name
            tz_object = pytz.timezone('GMT')  # Use the correct time zone name
            datetime_object = tz_object.localize(datetime_object)

            # Get the timestamp in seconds since epoch UTC
            target_time = datetime_object.timestamp()

            return target_time

        except ValueError:
            return "Invalid datetime format"

    def timestamp_to_datetime_string(self, timestamp):
        datetime_object = datetime.datetime.fromtimestamp(timestamp)
        datetime_string = datetime_object.strftime('%Y-%m-%d %H:%M:%S')  # convert in local time
        return datetime_string


    def get_local_timezone(self):
        """
        Automatically detects the local time zone.

        Returns:
            A pytz timezone object representing the local time zone.
        """
        try:
            # Get the local time zone abbreviation
            local_timezone_abbr = datetime.datetime.now(datetime.timezone.utc).astimezone().tzname()

            # Map abbreviations to full time zone names (this is not exhaustive)
            timezone_map = {
                "BST": "Europe/London",
                "GMT": "Europe/London",
                "CET": "Europe/Paris",
                "CEST": "Europe/Paris",
                "EET": "Europe/Athens",
                "EEST": "Europe/Athens",
                "MSK": "Europe/Moscow",
                "MSD": "Europe/Moscow",
                "IST": "Asia/Kolkata",
                "JST": "Asia/Tokyo",
                "KST": "Asia/Seoul",
                "AEST": "Australia/Sydney",
                "AEDT": "Australia/Sydney",
                "EST": "America/New_York",
                "EDT": "America/New_York",
                "CST": "America/Chicago",
                "CDT": "America/Chicago",
                "MST": "America/Denver",
                "MDT": "America/Denver",
                "PST": "America/Los_Angeles",
                "PDT": "America/Los_Angeles"
            }

            # Get the full time zone name from the map
            local_timezone_name = timezone_map.get(local_timezone_abbr)
            if local_timezone_name:
                local_timezone = pytz.timezone(local_timezone_name)
                return local_timezone
            else:
                print(f"Unknown time zone abbreviation: {local_timezone_abbr}")
                return None

        except Exception as e:
            print(f"Could not determine the local time zone: {e}")
            return None


    def plot_data(self, reqId):
        # Plot the historical data with adjusted x-axis ticks and normalized prices
        data = self.historical_data[reqId]["data"]
        # ! mdates.datestr2num does not take into account local time, consider dates and time in UTC
        # adding timezone to add offset hour compare to UTC
        offset_hours = datetime.datetime.now(self.get_local_timezone()).utcoffset().total_seconds()/3600.0
        dates = [mdates.datestr2num(d["date"])-offset_hours/24.0 - 5/24.0 for d in data] 
        print('offset hours =',offset_hours)
        close_prices = [d["close"] for d in data]
        # Find the index of the close price to target
        target_time = self.get_news_time()
        print("target_time :", self.timestamp_to_datetime_string(target_time))
        closest_index = min(range(len(dates)), key=lambda i: abs(dates[i]*86400 - target_time))
        print("data[0]['date'] extracted from IB at my time zone :", data[0]['date'])
        print("tmin after conversion to NY time :", self.timestamp_to_datetime_string(dates[0]*86400))
        print("data[end]['date'] extracted from IB at my time zone :",data[len(dates)-1]['date'])
        print("tmax after conversion to NY time :", self.timestamp_to_datetime_string(dates[len(dates)-1]*86400))

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

        # Create a DateFormatter with the local time zone
        # formatter = mdates.DateFormatter('%Y-%m-%d %H:%M:%S', tz=pytz.timezone('Europe/Paris'))

        # Set the formatter for the x-axis
        # plt.gca().xaxis.set_major_formatter(formatter)
        plt.plot(dates, normalized_prices)
        plt.xlabel("Time")
        plt.ylabel("Close Price Change (%)")  # Update y-axis label
        date_str = mdates.num2date(dates[0]).strftime('%Y-%m-%d')
        plt.title(self.stock_name + " Historical Data - " + date_str)  # Add date to title
        plt.axvline(x=dates[closest_index]+offset_hours/24, color='red', linestyle='--', label='Target Time')
        plt.axhline(y=0, color='red', linestyle='--', label='Target Time')

        # Add gray shadow for out-of-market hours
        # Get the date from the first date in the dates list
        date_obj = mdates.num2date(dates[0])
        date_str = date_obj.strftime('%Y-%m-%d')

        # Calculate the start and end times for market hours
        market_open_time = datetime.datetime(date_obj.year, date_obj.month, date_obj.day, 9, 30)
        market_close_time = datetime.datetime(date_obj.year, date_obj.month, date_obj.day, 16, 0)

        # Convert market times to numerical values for plotting
        market_open_num = mdates.date2num(market_open_time)
        market_close_num = mdates.date2num(market_close_time)
        plt.axvspan(dates[0], market_open_num, color='gray', alpha=0.2)  # Before market open
        plt.axvspan(market_close_num, dates[-1], color='gray', alpha=0.2)  # After market close


        # Set x-axis locator and formatter for hourly ticks
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        plt.xticks(rotation=45)
        if self.boolplot:
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
            if "Eastern Standard Time" not in datetime_str:
                raise ValueError(f"Substring 'Eastern Daylight or Standard Time' not found in '{datetime_str}', cannot manage other time zone conversion for now")

        # Re-combine the parts
        extracted_str = datetime_str.replace(" Eastern Daylight Time","")
        extracted_str = extracted_str.replace(" Eastern Standard Time","")

        # Parse the modified string into a datetime object
        datetime_object = datetime.datetime.strptime(extracted_str, "%B %d, %Y %I:%M %p")

        # Format the datetime object into the desired output format
        transformed_str = datetime_object.strftime("%Y%m%d %H:%M:%S US/Eastern")
        return transformed_str

    except ValueError as e:
        print(f"Error: {e}")
        return None


def main():
    
    ## Example 1: 
    mystock = "GWRE"
    mytime = "September 05, 2024 04:15 PM Eastern Daylight Time"
    # Max price over 5 hours after target time: 5.364548494983285
    # Min price over 5 hours after target time: -1.3377926421404682

    ## Example 2:
    # mystock = "ACN"
    # mytime = "September 26, 2024 06:39 AM Eastern Daylight Time"
    # Max price over 5 hours after target time: 6.470622727805791
    # Min price over 5 hours after target time: 0.0

    ## Example 3: 
    # mystock = "CHCO"
    # mytime = "September 25, 2024 07:01 PM Eastern Daylight Time"
    # Max price over 5 hours after target time:Max price over 5 hours after target time: 0.39407178959992606
    # Min price over 5 hours after target time: -1.1393814786258873

    ## Example 4:
    # mystock = "ACI"
    # mytime = "October 15, 2024 08:30 AM Eastern Daylight Time"
    # Max price over 5 hours after target time: 0.161812297734634
    # Min price over 5 hours after target time: -1.8338727076591146

    ## Example 6:
    # mystock = "KIND"
    # mytime  = "November 06, 2024 04:05 PM Eastern Standard Time"

    #mystock = "CRI"
    #mytime = "October 25, 2024 06:11 AM Eastern Daylight Time"

    app = HistoricPrice(mystock, transform_datetime_to_IBformat(mytime), True)
    app.connect('127.0.0.1', 7496, 123)
    app.run()
    print("Historical data:", app.historical_data)
    print("Ploting data:", app.plot_data(1))  # Plot the data with reqId 1
    print("mon min egal =",app.getminover5())
    print("mon max egal =",app.getmaxover5())
#    app2 = TimeChecker()
#    print("running")
#    app2.connect('127.0.0.1', 7496, 123)
#    app2.run()


if __name__ == '__main__':
    main()
