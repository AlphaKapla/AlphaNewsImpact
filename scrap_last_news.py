import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import hashlib


async def scrap(url):
    # pyppeter basic launch
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.goto(url)
    selectorPath = '#bw-group-all > div > div > div.bw-search-results > section > ul > li > h3'
    # wait for javascript from the webpage to run
    await page.waitForSelector(selectorPath)
    # return webpage content
    html = await page.content()
    # begin html parsing with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # Find all <h3> tags & and first for hashing
    h3_tags_all = soup.find_all('h3')
    h3_tags_first = soup.find('h3')
    currentHash = hashlib.sha224(h3_tags_first.getText().encode('utf-8')).hexdigest()
    # List to store the URLs
    urls = []
    # Iterate through each <h3> tag
    for h3_tag in h3_tags_all:
        # Find all anchor tags <a> within the current <h3>
        anchor_tags = h3_tag.find_all('a')
        # Iterate through each anchor tag and extract the URL
        for anchor_tag in anchor_tags:
            url = anchor_tag.get('href')  # Get the 'href' attribute value (the URL)
            if url:
                urls.append(url)  # Add the URL to the list
    i = 1
    while i < 1:
        print("waiting 30s ...")
        await asyncio.sleep(30)  # Wait for 30 seconds
        print("reload :", i)
        await page.reload(wait_until='networkidle')  # Reload the page
        # Example: Extract text content using a text selector
        await page.waitForSelector(selectorPath)
        new_html = await page.content()
        soup = BeautifulSoup(new_html, 'html.parser')
        # Find first <h3> tags for hashing
        h3_tags_first = soup.find('h3')
        newHash = hashlib.sha224(h3_tags_first.getText().encode('utf-8')).hexdigest()
        i = i+1
        if newHash != currentHash:
            print("###############################################")
            print("New hash:", newHash)
            print("###############################################")
            # Reset list to store the URLs
            urls = []
            # Find all <h3> tags
            h3_tags_all = soup.find_all('h3')
            # Iterate through each <h3> tag
            for h3_tag in h3_tags_all:
                # Find all anchor tags <a> within the current <h3>
                anchor_tags = h3_tag.find_all('a')
                # Iterate through each anchor tag and extract the URL
                for anchor_tag in anchor_tags:
                    url = anchor_tag.get('href')  # Get the 'href' attribute value (the URL)
                    if url:
                        urls.append(url)  # Add the URL to the list
            currentHash = newHash  # Update the current hash
    await browser.close()
    return urls


if __name__ == "__main__":
    # Creates a new event loop & runs your main() coroutine until it completes and then closes the loop
    url_base = "https://www.businesswire.com/portal/site/home/template.PAGE/search/?searchType=news&searchTerm=Fiscal%20%222024%20Results%22%20-Announces%20-Announce&searchPage=1"
    urls = asyncio.run(scrap(url_base))
    for url in urls:
        print(url)
