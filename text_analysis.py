import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason
import json
import pandas as pd  
import requests
import asyncio
from pyppeteer.launcher import launch

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

#json_data = read_json_file("IdealCase/Q4results_Linear.json")
#json_data = read_json_file("sources_simple.json")
json_data = read_json_file("scraped_data.json")
df = pd.DataFrame(json_data)
df = df.astype(str)

text_concat = ""
for index, row in df.iterrows():
  text_concat = text_concat + "inputs: " + df.inputs[index] + "\n" + "outputs: " + df.outputs[index] + "\n"

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

generate()
