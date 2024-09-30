import asyncio 
from pyppeteer import launch
from bs4 import BeautifulSoup
import requests

async def scrap_text(url):

    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.goto(url)
    await page.waitForSelector('#bw-news-view > div.bw-release-sidebars > div.bw-release-contact > h2')
    # return webpage content
    htmlpyp = await page.content()
    await browser.close()

    soup = BeautifulSoup(htmlpyp, 'html.parser')

    #--------------------------
    # Text
    #--------------------------

    elements = soup.findAll("div",class_="bw-release-story")
    all_texts = ""
    for element in elements:
        all_texts = all_texts + element.get_text()
    cleaned_text = all_texts.replace('\n\n',' ').replace(' ',' ')
    cleaned_text = ' '.join(cleaned_text.split())
    cleaned_text = cleaned_text.replace('  ', ';')

    #--------------------------
    # Time 
    #--------------------------

    timestamp_div = soup.find("div", class_="bw-release-timestamp")

    # Extract the text content of the time element
    time_element = timestamp_div.find("time")
    formatted_datetime = time_element.text.strip() 
    
    #--------------------------
    # Stock
    #--------------------------

    # Find the div with id "cic"
    cic_div = soup.find('div', id='cic')

    if (cic_div):
        # Find the first <a> tag within the div
        first_a_tag = cic_div.find('a')
        # Find the <span> tag within the first <a> tag
        span_tag = first_a_tag.find('span')
        stock = span_tag.get_text()
    else:
        stock='Not traded'

    return stock, formatted_datetime, cleaned_text

# Examples
url = 'https://www.businesswire.com/news/home/20240926554709/en/Large-Deals-Workforce-Management-Leadership-Drive-UKG-Third-Quarter-Fiscal-2024-Results' 
url2 = 'https://www.businesswire.com/news/home/20240926721611/en/Accenture-Reports-Fourth-Quarter-and-Full-Year-Fiscal-2024-Results'
url3 = 'http://www.businesswire.com/news/home/20240925645735/en/City-Holding-Company-Increases-Quarterly-Dividend-On-Common-Shares'

stock, time, text = asyncio.run(scrap_text(url))

print(stock)
print(time)
print(text)


