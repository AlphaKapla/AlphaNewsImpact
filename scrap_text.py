import requests
from bs4 import BeautifulSoup
import re
import json

def extract_stock_symbol(text):
    """
    Extracts the stock symbol from a text string. 
    Looks for "NYSE:" or "NASDAQ:" followed by the symbol.
    Removes any non-alphanumeric characters from the end of the symbol.

    Args:
        text: The text string to search in.

    Returns:
        The cleaned stock symbol, or None if not found.
    """
    try:
        if "NYSE:" in text:
            stock = text.split("NYSE:")[1].split()[0]
        elif "NASDAQ:" in text:
            stock = text.split("NASDAQ:")[1].split()[0]
        else:
            stock = None

        if stock:
            stock = re.sub(r"\W+$", "", stock)  # Remove non-alphanumeric characters from the end

        return stock
    except IndexError:
        return None

def scrape_text_with_requests(url):
    """
    Scrapes text, time, and stock information from a Businesswire URL using the requests library.

    Args:
        url: The URL of the Businesswire article.

    Returns:
        A tuple containing the stock symbol, formatted datetime, and cleaned text.
    """
    try:
        response = requests.get(url, timeout=5)  # Set a timeout for the request

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            elements = soup.findAll("div", class_="bw-release-story")
            all_texts = ""
            for element in elements:
                all_texts = all_texts + element.get_text()
            cleaned_text = all_texts.replace("\n\n", " ").replace(" ", " ")
            cleaned_text = " ".join(cleaned_text.split())
            cleaned_text = cleaned_text.replace("  ", ";")
            timestamp_div = soup.find("div", class_="bw-release-timestamp")
            time_element = timestamp_div.find("time")
            formatted_datetime = time_element.text.strip()
            stock = extract_stock_symbol(cleaned_text)
            return stock, formatted_datetime, cleaned_text

        else:
            print(f"Failed to fetch {url}: Status code {response.status_code}")
            return None, None, None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching {url}: {e}")
        return None, None, None

def save_text_to_file(text, filename="scraped_text.txt"):
    """
    Saves the given text to a file.

    Args:
        text: The text to save.
        filename: The name of the file to save to.
    """
    try:
        with open(filename, "w") as file:
            file.write(text)
        print(f"Text saved to {filename}")
    except Exception as e:
        print(f"An error occurred while saving the text: {e}")

def save_text_to_json(text, maxover5, filename="scraped_data.json", append=False):
    """
    Saves the text and maxover5 to a JSON file.

    Args:
        text: The extracted text.
        maxover5: The calculated maxover5 value.
        filename: The name of the JSON file to save to.
        append: If True, appends the data to the existing file. 
                If False (default), overwrites the file.
    """
    try:
        if append:
            try:
                with open(filename, "r") as file:
                    data = json.load(file)  # Load existing data
            except FileNotFoundError:
                data = []  # If the file doesn't exist, start with an empty list
            data.append({"inputs": text, "outputs": "the score is " + str(maxover5)})  # Add new data
        else:
            data = [{"inputs": text, "outputs": "the score is " + str(maxover5)}]  # Create new data

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)  # Save the data to the JSON file
        print(f"Data saved to {filename}")

    except Exception as e:
        print(f"An error occurred while saving the data: {e}")

def main():
    # Examples
    url = 'https://www.businesswire.com/news/home/20240926554709/en/Large-Deals-Workforce-Management-Leadership-Drive-UKG-Third-Quarter-Fiscal-2024-Results' 
    url2 = 'https://www.businesswire.com/news/home/20240926721611/en/Accenture-Reports-Fourth-Quarter-and-Full-Year-Fiscal-2024-Results'
    url3 = 'http://www.businesswire.com/news/home/20240925645735/en/City-Holding-Company-Increases-Quarterly-Dividend-On-Common-Shares'
    url4 = 'https://www.businesswire.com/news/home/20241015517655/en/Albertsons-Companies-Inc.-Reports-Second-Quarter-Fiscal-2024-Results'  

    stock, time, text = scrape_text_with_requests(url2)

    print(stock)
    print(time)
    print(text)

    if text:
        save_text_to_file(text)
    else:
        print(f"Failed to scrape {url3}")

if __name__ == '__main__':
    main()
