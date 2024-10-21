import asyncio
from scrap_last_news import scrap
from scrap_text import *
from historic_price import *

async def main():  # Define an async function
    url_base = "https://www.businesswire.com/portal/site/home/template.PAGE/search/?searchType=news&searchTerm=Fiscal%20%222024%20Results%22%20-Announces%20-Announce&searchPage=1"
    print("scrapping web ...")
    urls = await scrap(url_base)  # Use await to call scrap()

"""     for url in urls: 
        print(url)
        stock, time, text = scrape_text_with_requests(url)  # Use await to call scrap_text()
        print(stock)
        print(time)
        print(text)
        # ... do something with stock, time, and text ... """


# Example usage
url3 = "http://www.businesswire.com/news/home/20240925645735/en/City-Holding-Company-Increases-Quarterly-Dividend-On-Common-Shares"
stock, time, text = scrape_text_with_requests(url3)
print("my stock is :", stock)
print("my time is :", time)

historicpriceApp = HistoricPrice(stock, transform_datetime_to_IBformat(time), False)
historicpriceApp.connect('127.0.0.1', 7496, 123)
historicpriceApp.run()
historicpriceApp.historical_data
historicpriceApp.plot_data(1)

if text:
    save_text_to_json(text, historicpriceApp.getmaxover5())  # Save the data to JSON
else:
    print(f"text empty")


if __name__ == "__main__":
    asyncio.run(main())  # Run the main function
