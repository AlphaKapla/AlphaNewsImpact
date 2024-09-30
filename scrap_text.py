from bs4 import BeautifulSoup
import requests

def get_content(url, selector, time_selector):
    response = requests.get(url)
    response.raise_for_status() 

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all elements within the specified main selector
    elements = soup.select(selector)
    all_texts = [element.get_text() for element in elements]

    # Find the time element using the time_selector
    time_element = soup.select_one(time_selector)  # select_one as we expect only one time element
    time = time_element.text.strip() if time_element else None

    return all_texts, time

# Example usage (unchanged except for the additional time_selector)
url = 'https://www.businesswire.com/news/home/20240926554709/en/Large-Deals-Workforce-Management-Leadership-Drive-UKG-Third-Quarter-Fiscal-2024-Results' 
url2 = 'https://www.businesswire.com/news/home/20240926721611/en/Accenture-Reports-Fourth-Quarter-and-Full-Year-Fiscal-2024-Results'
selector = '#bw-news-view > article > div > div.bw-release-story > p, \
            #bw-news-view > article > div > div.bw-release-story > ul > li'
time_selector = '#bw-news-view > article > div > div.bw-release-timestamp > time'

all_texts, time = get_content(url2, selector, time_selector)

# Print the extracted content, including the time text
for text in all_texts:
    print(text)

print(time)

