import asyncio 
from pyppeteer import launch
from bs4 import BeautifulSoup

async def scrap():

  #--------------------------
  # pyppeter basic launch
  #--------------------------

  browser = await launch(headless=True)
  page = await browser.newPage()
  urlMGA = "https://www.businesswire.com/portal/site/home/template.PAGE/search/?searchType=news&searchTerm=Fiscal%20%222024%20Results%22%20-Announces%20-Announce&searchPage=1"
  await page.goto(urlMGA)
  selectorPath = '#bw-group-all > div > div > div.bw-search-results > section > ul > li > h3' ;
  # wait for javascript from the webpage to run
  await page.waitForSelector(selectorPath)
  # return webpage content
  html = await page.content()
  await browser.close()
  # close pyppeter 

  #------------------------------------------
  # begin html parsing with BeautifulSoup
  #------------------------------------------

  soup = BeautifulSoup(html, 'html.parser')
  title = soup.find_all('a',href=True)
  # Find all <h3> tags
  h3_tags = soup.find_all('h3')
  # List to store the URLs
  urls = []

  # Iterate through each <h3> tag
  for h3_tag in h3_tags:
  # Find all anchor tags <a> within the current <h3>
    anchor_tags = h3_tag.find_all('a')

  # Iterate through each anchor tag and extract the URL
    for anchor_tag in anchor_tags:
      url = anchor_tag.get('href')  # Get the 'href' attribute value (the URL)
      if url:
        urls.append(url)  # Add the URL to the list

  return(urls)

# Creates a new event loop & runs your main() coroutine until it completes and then closes the loop 
ulrs = asyncio.run(scrap())
print(ulrs)

