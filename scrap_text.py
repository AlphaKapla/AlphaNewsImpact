from bs4 import BeautifulSoup
import requests

def get_content(url):
    response = requests.get(url)
    response.raise_for_status() 
    soup = BeautifulSoup(response.content, 'html.parser')

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

    return cleaned_text, formatted_datetime


# Examples
url = 'https://www.businesswire.com/news/home/20240926554709/en/Large-Deals-Workforce-Management-Leadership-Drive-UKG-Third-Quarter-Fiscal-2024-Results' 
url2 = 'https://www.businesswire.com/news/home/20240926721611/en/Accenture-Reports-Fourth-Quarter-and-Full-Year-Fiscal-2024-Results'
url3 = 'http://www.businesswire.com/news/home/20240925645735/en/City-Holding-Company-Increases-Quarterly-Dividend-On-Common-Shares'

text, time = get_content(url3)

print(text)
print(time)

