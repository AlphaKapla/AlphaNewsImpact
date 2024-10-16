import asyncio
from scrap_last_news import scrap
from scrap_text import *

async def main():  # Define an async function
    url_base = "https://www.businesswire.com/portal/site/home/template.PAGE/search/?searchType=news&searchTerm=Fiscal%20%222024%20Results%22%20-Announces%20-Announce&searchPage=1"
    print("scrapping web ...")
    urls = await scrap(url_base)  # Use await to call scrap()

    for url in urls: 
        print(url)
        stock, time, text = scrape_text_with_requests(url)  # Use await to call scrap_text()
        print(stock)
        print(time)
        print(text)
        # ... do something with stock, time, and text ...

if __name__ == "__main__":
    asyncio.run(main())  # Run the main function
