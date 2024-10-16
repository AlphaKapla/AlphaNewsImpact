from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.ticktype import TickTypeEnum
from ibapi.common import *

class StockPrice(EWrapper, EClient):
    def __init__(self, sname: str):
        EClient.__init__(self, self)
        self.last_price = 0
        self.stock_name = sname
        
    def symbolSamples(self, reqId: int, contractDescriptions: ListOfContractDescription):
        super().symbolSamples(reqId, contractDescriptions)
        print("Symbol Samples. Request Id: ", reqId) 
        for contractDescription in contractDescriptions:
            derivSecTypes = ""
            for derivSecType in contractDescription.derivativeSecTypes:
                derivSecTypes += " "
                derivSecTypes += derivSecType
            print("Contract: conId:%s, symbol:%s, secType:%s primExchange:%s, "
                  "currency:%s, derivativeSecTypes:%s" % (
                contractDescription.contract.conId,
                contractDescription.contract.symbol,
                contractDescription.contract.secType,
                contractDescription.contract.primaryExchange,
                contractDescription.contract.currency, derivSecTypes))
            self.disconnect() 

    def nextValidId(self, orderId:int):    
        self.reqMarketDataType(MarketDataTypeEnum.REALTIME) 
        contract = Contract()
        contract.symbol = self.stock_name
        contract.secType = "STK"
        contract.currency = "USD"
        contract.exchange = "SMART"
        self.reqMktData(1, contract, "", False, False, None)

    def error(self, reqId: int, errorCode: int, errorString: str, advancedOrderRejectJson: str = ""):  # Add the extra argument
        print('Info: ', reqId, ' ', errorCode, ' ', errorString)

    def tickPrice(self, reqId: int, tickType: int, price: float, attrib: TickAttrib):
        print('Tick Price. Ticker Id:', reqId, 'tickType:', TickTypeEnum.to_str(tickType), 
              'Price:', price)
        if tickType == TickTypeEnum.LAST or tickType == TickTypeEnum.DELAYED_LAST:
            self.last_price = price
            print("disconnecting")
            self.disconnect() 

def main():
    app = StockPrice("GWRE")  # Pass the stock name here
    app.connect('127.0.0.1', 7496, 123)
    app.run() 
    print("app.last_price:", app.last_price) 

if __name__ == '__main__':
    main()
