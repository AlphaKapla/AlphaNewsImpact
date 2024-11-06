import asyncio
from scrap_last_news import scrap
from scrap_text import *
from historic_price import *
import os

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


# DataBase completion
urls = [
        'http://www.businesswire.com/news/home/20240925645735/en/City-Holding-Company-Increases-Quarterly-Dividend-On-Common-Shares',
        'https://www.businesswire.com/news/home/20240926721611/en/Accenture-Reports-Fourth-Quarter-and-Full-Year-Fiscal-2024-Results',
        'https://www.businesswire.com/news/home/20240926554709/en/Large-Deals-Workforce-Management-Leadership-Drive-UKG-Third-Quarter-Fiscal-2024-Results',
        'https://www.businesswire.com/news/home/20240926721611/en/Accenture-Reports-Fourth-Quarter-and-Full-Year-Fiscal-2024-Results',
        'https://www.businesswire.com/news/home/20241015517655/en/Albertsons-Companies-Inc.-Reports-Second-Quarter-Fiscal-2024-Results'
        'https://www.businesswire.com/news/home/20241106589586/en/Nextdoor-Reports-Third-Quarter-2024-Results'
        'https://www.businesswire.com/news/home/20241106827708/en/HubSpot-Reports-Q3-2024-Results'
        'https://www.businesswire.com/news/home/20241106893388/en/Centuri-Reports-Third-Quarter-2024-Results-Reiterates-2024-Guidance' #need to be checked before
        ]
for url in urls:
    print("scrapping url :",url)
    stock, time, text = scrape_text_with_requests(url)
    if stock is not None:
        print("my stock is :", stock)
        print("my time is :", time)
        historicpriceApp = HistoricPrice(stock, transform_datetime_to_IBformat(time), False)
        historicpriceApp.connect('127.0.0.1', 7496, 123)
        historicpriceApp.run()
        historicpriceApp.historical_data
        historicpriceApp.plot_data(1)
        if text:
            if os.path.exists("scraped_data.json"):
                save_text_to_json(text, historicpriceApp.getmaxover5(), append=True)  # Save the data to JSON
            else:
                save_text_to_json(text, historicpriceApp.getmaxover5(), append=False)  # Save the data to JSON
        else:
            print(f"text empty")


if __name__ == "__main__":
    asyncio.run(main())  # Run the main function
