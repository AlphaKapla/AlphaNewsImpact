import asyncio
from stock_price import StockPrice 
from scrap_text import *
from historic_price import *

## unit tests to use with pytest

def test_stock_price():
    app = StockPrice("GWRE",)
    app.connect('127.0.0.1', 7496, 123)
    app.run()
    assert app.last_price != 0 

def test_scrap_text():
    url2 = 'https://www.businesswire.com/news/home/20240926721611/en/Accenture-Reports-Fourth-Quarter-and-Full-Year-Fiscal-2024-Results'
    stock, time, text = scrape_text_with_requests(url2)
    assert "The impact of the business optimization costs and investment gain on diluted earnings per share are presented" in text 
    assert time == "September 26, 2024 06:39 AM Eastern Daylight Time"
    assert stock == "ACN"

def test_historic_price1():
    stock = "GWRE"
    time = "September 05, 2024 04:15 PM Eastern Daylight Time"
    historicpriceApp = HistoricPrice(stock, transform_datetime_to_IBformat(time), False)
    historicpriceApp.connect('127.0.0.1', 7496, 123)
    historicpriceApp.run()
    historicpriceApp.historical_data
    historicpriceApp.plot_data(1)
    assert abs(historicpriceApp.getmaxover5() - 5.364548494983285) < 0.0001
    assert abs(historicpriceApp.getminover5() - -1.3377926421404682) < 0.0001

def test_historic_price2():
    stock = "ACN"
    time = "September 26, 2024 06:39 AM Eastern Daylight Time"
    historicpriceApp = HistoricPrice(stock, transform_datetime_to_IBformat(time), False)
    historicpriceApp.connect('127.0.0.1', 7496, 123)
    historicpriceApp.run()
    historicpriceApp.historical_data
    historicpriceApp.plot_data(1)
    assert abs(historicpriceApp.getmaxover5() - 6.470622727805791) < 0.0001
    assert abs(historicpriceApp.getminover5() - 0.0) < 0.0001

def test_historic_price3():
    stock = "CHCO"
    time = "September 25, 2024 07:01 PM Eastern Daylight Time"
    historicpriceApp = HistoricPrice(stock, transform_datetime_to_IBformat(time), False)
    historicpriceApp.connect('127.0.0.1', 7496, 123)
    historicpriceApp.run()
    historicpriceApp.historical_data
    historicpriceApp.plot_data(1)
    assert abs(historicpriceApp.getmaxover5() - 0.39407178959992606) < 0.0001
    assert abs(historicpriceApp.getminover5() + 1.1393814786258873) < 0.0001

def test_historic_price4():
    stock = "ACI"
    time = "October 15, 2024 08:30 AM Eastern Daylight Time"
    historicpriceApp = HistoricPrice(stock, transform_datetime_to_IBformat(time), False)
    historicpriceApp.connect('127.0.0.1', 7496, 123)
    historicpriceApp.run()
    historicpriceApp.historical_data
    historicpriceApp.plot_data(1)
    assert abs(historicpriceApp.getmaxover5() - 0.161812297734634) < 0.0001
    assert abs(historicpriceApp.getminover5() + 1.8338727076591146) < 0.0001

