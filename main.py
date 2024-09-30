import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason
import json
import pandas as pd  
import requests
import asyncio
from pyppeteer.launcher import launch


def scrape_webpage(url):
    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP errors

    soup = BeautifulSoup(response.content, 'html.parser')
    return extracted_data

def read_json_file(file_path):
  try:
    with open(file_path, 'r') as file:
      data = json.load(file)
    return data
  except FileNotFoundError: 

    print(f"Error: File '{file_path}' not found.")
    return None
  except json.JSONDecodeError:
    print(f"Error: Invalid JSON format in '{file_path}'.") 
    return None

def generate():
  vertexai.init(project="gen-lang-client-0984550043", location="us-central1")
  model = GenerativeModel(
    "gemini-pro-experimental",
    system_instruction=[textsi_1]
  )
  responses = model.generate_content(
      [text_concat,textinput],
      generation_config=generation_config,
      safety_settings=safety_settings,
      stream=True,
  )

  for response in responses:
    print(response.text, end="")

json_data = read_json_file("IdealCase/Q4results_Linear.json")
df = pd.DataFrame(json_data)
df = df.astype(str)

text_concat = ""
for index, row in df.iterrows():
  text_concat = text_concat + "inputs: " + df.inputs[index] + "\n" + "outputs: " + df.outputs[index] + "\n"

#breakpoint()

text1 = """input: Bowlero Reports Fourth Quarter and Full Year Results for Fiscal Year 2024
September 05, 2024 04:05 PM Eastern Daylight Time
RICHMOND, Va.--(BUSINESS WIRE)--Bowlero Corp. (NYSE: BOWL) (“Bowlero” or the “Company”), one of the world’s premier operators of location-based entertainment, today provided financial results for the fourth quarter and full year of fiscal year 2024, which ended on June 30, 2024.

Quarter Highlights:

Revenue increased 18.6% to $283.9 million versus fourth quarter fiscal year 2023
Revenue excluding Service Fee Revenue increased 20.2% to $282.9 million versus fourth quarter fiscal year 2023
Same Store Revenue increased 6.9% to $242.5 million versus fourth quarter fiscal year 2023
Net loss of $62.2 million versus net income of $146.2 million in fourth quarter fiscal year 2023
Adjusted EBITDA of $83.4 million versus $64.5 million in fourth quarter fiscal year 2023
Added two locations through acquisitions during the quarter
Fiscal Year Highlights:

Revenue increased 9.1% to $1,154.6 million versus the prior year
Revenue excluding Service Fee Revenue increased 10.7% to $1,149.2 million versus the prior year
Same Store Revenue was flat at $985.9 million versus the prior year
Net loss of $83.6 million versus prior year net income of $82.0 million
Adjusted EBITDA of $361.5 million versus prior year of $354.3 million
Added 25 locations during the fiscal year, 22 through acquisitions and three new builds
Total locations in operation as of June 30, 2024 was 352, plus the Raging Waves waterpark
“We ended fiscal year 2024 on a high note with a superior same-store-sales comp and total growth. Our proven ability to deploy capital across our portfolio and operate acquired assets more efficiently while investing in our people and brand showed results with Adjusted EBITDA growing 29%+ year-over-year in the quarter,” said Thomas Shannon, Founder, Chairman, and CEO. “Season Pass sales across our portfolio hit a record $11 million and helped drive consumer traffic. We also saw an increase in customer satisfaction from the ancillary benefits of the passes, including in arcade play and food promotions. The enormous success of the Summer Pass has compelled us to offer a Fall Season Pass for October and November prior to the holiday and winter push.”

“Bowlero’s primary strength is its ability to optimize assets through efficiencies, analytics and now scale, resulting in class-leading returns on invested capital. This year, we acquired 22 locations, including the flagship Lucky Strike locations and the 60-acre Raging Waves waterpark in Yorkville, Illinois. The initial results of these acquisitions have been outstanding, including record profitability at Lucky Strike and double digit year-over-year revenue growth at Raging Waves. We expect to achieve returns similar to our successes with the acquisitions of centers from AMF, Brunswick, Bowl America, and 40+ independents. Recently, economic factors have increased M&A opportunities, and we expect to continue executing our playbook of buying assets at attractive prices and systemically improving them. We are offsetting slight weakness in the consumer with what we believe are market share gains in the location-based entertainment sector. We expect low to mid single-digit positive same-store-sales comp in the upcoming year.”

output: the score is +10.4"""
text2 = """
input: Guidewire Announces Fourth Quarter and Fiscal Year 2024 Financial Results
September 05, 2024 04:15 PM Eastern Daylight Time
SAN MATEO, Calif.--(BUSINESS WIRE)--Guidewire (NYSE: GWRE) today announced its financial results for the fiscal quarter and year ended July 31, 2024.

“We enter the new fiscal year positioned well to continue accelerating modernization programs in the P&C industry and delivering increasing value to P&C insurers\' drive for greater agility and innovation.”
Post this
“We finished the year with record fourth quarter sales activity and fully ramped ARR growth of 19%,” said Mike Rosenbaum, chief executive officer, Guidewire. “We enter the new fiscal year positioned well to continue accelerating modernization programs in the P&C industry and delivering increasing value to P&C insurers\' drive for greater agility and innovation.”

“The fourth quarter capped off a tremendous year and strong financial results,” said Jeff Cooper, chief financial officer, Guidewire. “The combination of fully ramped ARR growth and 20% cash flow from operations as a percent of revenue demonstrates the power and durability of our model.”
output: the score is +5.3"""
textinput="Q4 results: 30%"
textsi_1 = """You are an expert financial analyst in big companies, specialized in stock equities. Your response should be short without any details. You should reply by a score range from -15 to +15, estimating the sentiment of financial report released that user gives you. A score of +20 being an extremely positive feeling, -20 extremely negative, and 0 is neutral."""

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.7,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
]


#url = "https://www.businesswire.com/portal/site/home/template.PAGE/search/?searchType=news&searchTerm=Fiscal%20%222024%20Results%22%20-Announces%20-Announce&searchPage=1"
#data = scrape_webpage(url)
#print(data)
#generate()