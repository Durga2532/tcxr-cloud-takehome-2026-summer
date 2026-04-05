import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
print("API KEY loaded:", API_KEY)
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

params = {
    "zip": "94203,us",
    "appid": API_KEY,
    "units": "imperial"
}

response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    data = response.json()
    print("City:", data["city"]["name"])
    print("First forecast entry:", data["list"][0])
else:
    print("Error:", response.status_code, response.json()["message"])