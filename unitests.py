from stock_price import StockPrice 
from scrap_text import *

def test_stock_price():
    app = StockPrice("GWRE")
    app.connect('127.0.0.1', 7496, 123)
    app.run()
    assert app.last_price != 0 

def test_scrap_text():
    url2 = 'https://www.businesswire.com/news/home/20240926721611/en/Accenture-Reports-Fourth-Quarter-and-Full-Year-Fiscal-2024-Results'
    stock, time, text = scrape_text_with_requests(url2)
    assert "The impact of the business optimization costs and investment gain on diluted earnings per share are presented" in text 
    assert time == "September 26, 2024 06:39 AM Eastern Daylight Time"
    assert stock == "ACN"
