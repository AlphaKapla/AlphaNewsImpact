from stock_price import StockPrice 

def test_stock_price():
    app = StockPrice("GWRE")
    app.connect('127.0.0.1', 7496, 123)
    app.run()
    assert app.last_price != 0 
