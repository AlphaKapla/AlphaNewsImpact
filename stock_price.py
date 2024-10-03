from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum
from ibapi.common import *

class StockPrice(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        # here you can add variables to the TestApp class, just use self.var in the class
        self.last = 0;
        
    # ib suggests waiting for this response to know that you have a connection
    def nextValidId(self, orderId:int):    
        self.reqMarketDataType(MarketDataTypeEnum.REALTIME) # or DELAYED
        contract = Contract()
        contract.symbol = "AAPL"
        contract.secType = "STK"
        contract.currency = "USD"
        contract.exchange = "SMART"
        self.reqMktData(1, contract, "", False, False, None)

    def error(self, reqId, errorCode, errorString):
        print('Info: ', reqId, ' ', errorCode, ' ', errorString)

    def tickPrice(self, reqId, tickType, price, attrib):
            print('Tick Price. Ticker Id:', reqId, 'tickType:', TickTypeEnum.to_str(tickType), 
            'Price:', price)
            if tickType == TickTypeEnum.LAST or tickType == TickTypeEnum.DELAYED_LAST :
                self.last = price;
                print("disconnecting")
                self.disconnect() # just for testing, normally the program would do something

def main():
    app = StockPrice()
    app.connect('127.0.0.1', 7496, 123)
    app.run() # this blocks the program until disconnect()
    print("app.last:", app.last) # now you refer to the variable by class.var

if __name__ == '__main__':
    main()