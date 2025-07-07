
import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
from dateutil.parser import parse as parse_date

from langchain_together import ChatTogether
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool, StructuredTool

from langchain.agents import create_react_agent

load_dotenv()

def get_current_weather(location: str) -> str:
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return json.dumps({"error": "OpenWeatherMap API key is not set."})
     
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric",
        "lang": "en"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        processed_data = {
            "location": data["name"],
            "temperature": f"{data['main']['temp']}°C",
            "feels_like": f"{data['main']['feels_like']}°C",
            "conditions": data['weather'][0]['description'],
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{data['wind']['speed']} m/s"
        }
        return json.dumps(processed_data, ensure_ascii=False)

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return json.dumps({"error": f"City not found: {location}"})
        else:
            return json.dumps({"error": f"An HTTP error occurred: {http_err}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

def get_weather_forecast(json_str: str) -> str:
    information = json.loads(json_str)
    location = information["location"]
    date_str = information["date"]

    api_key = os.environ.get("WEATHERAPI_API_KEY")
    if not api_key:
        return json.dumps({"error": "API key for WeatherAPI.com is not set."})

    try:
        today = date.today()
        target_date = parse_date(date_str, default=datetime.combine(today, datetime.min.time())).date()
    except (ValueError, TypeError):
        return json.dumps({"error": f"Failed to parse the date: '{date_str}'. Use YYYY-MM-DD format or words like 'tomorrow'."})

    fourteen_days_from_now = today + timedelta(days=14)

    if target_date < today:
        return json.dumps({"error": "Cannot check the weather for a past date."})
    if target_date > fourteen_days_from_now:
        return json.dumps({"error": f"The forecast is only available for 14 days ahead. The date '{target_date}' is too far in the future."})

    base_url = "https://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": api_key,
        "q": location,
        "dt": target_date.strftime('%Y-%m-%d'),
        "lang": "en"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
         
        forecast_day_data = data["forecast"]["forecastday"][0]
        day_info = forecast_day_data["day"]
         
        wind_kph = day_info['maxwind_kph']
        wind_ms = round(wind_kph / 3.6, 2)

        processed_data = {
            "location": f"{data['location']['name']}, {data['location']['country']}",
            "date": forecast_day_data['date'],
            "avg_temperature": f"{day_info['avgtemp_c']}°C",
            "min_temperature": f"{day_info['mintemp_c']}°C",
            "max_temperature": f"{day_info['maxtemp_c']}°C",
            "conditions": day_info['condition']['text'],
            "humidity": f"{day_info['avghumidity']}%",
            "chance_of_rain": f"{day_info.get('daily_chance_of_rain', 'N/A')}%",
            "max_wind_speed": f"{wind_ms} m/s"
        }
         
        return json.dumps(processed_data, ensure_ascii=False)

    except requests.exceptions.HTTPError as http_err:
        return json.dumps({"error": f"HTTP error from WeatherAPI.com: {http_err}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})


current_weather_tool = Tool(
    name="current_weather_checker",
    description="Use this tool to check the CURRENT weather in a given city. Returns a JSON with detailed weather information for now.",
    func=get_current_weather
)

forecast_weather_tool = StructuredTool.from_function(
    func=get_weather_forecast,
    name="weather_forecast_checker",
    description="Use this tool to check the weather FORECAST in a given city for a specific day. The forecast is available up to 14 days in the future. Function has two  different parameters location and date."
)