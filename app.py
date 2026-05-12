from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # loads your API key from .env

app = Flask(__name__)

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

def get_weather(city):
    # Current weather
    current_url = f"{BASE_URL}/weather?q={city}&appid={API_KEY}&units=metric"
    current_response = requests.get(current_url)
    
    # 5-day forecast
    forecast_url = f"{BASE_URL}/forecast?q={city}&appid={API_KEY}&units=metric"
    forecast_response = requests.get(forecast_url)
    
    if current_response.status_code != 200:
        return None, None, current_response.json().get("message", "City not found")
    
    current_data = current_response.json()
    forecast_data = forecast_response.json()
    
    # Extract what we need from the JSON
    weather = {
        "city": current_data["name"],
        "country": current_data["sys"]["country"],
        "temp": round(current_data["main"]["temp"]),
        "feels_like": round(current_data["main"]["feels_like"]),
        "humidity": current_data["main"]["humidity"],
        "wind_speed": round(current_data["wind"]["speed"] * 3.6, 1),  # m/s → km/h
        "description": current_data["weather"][0]["description"].title(),
        "icon": current_data["weather"][0]["icon"],
    }
    
    # Get one forecast per day (API gives every 3 hours, we take noon readings)
    forecast = []
    seen_dates = set()
    for item in forecast_data["list"]:
        date = item["dt_txt"].split(" ")[0]
        time = item["dt_txt"].split(" ")[1]
        if date not in seen_dates and time == "12:00:00":
            forecast.append({
                "date": date,
                "temp_max": round(item["main"]["temp_max"]),
                "temp_min": round(item["main"]["temp_min"]),
                "description": item["weather"][0]["description"].title(),
                "icon": item["weather"][0]["icon"],
            })
            seen_dates.add(date)
        if len(forecast) == 5:
            break
    
    return weather, forecast, None

@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    forecast = None
    error = None
    city = ""
    
    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if city:
            weather, forecast, error = get_weather(city)
    
    return render_template("index.html", weather=weather, forecast=forecast, error=error, city=city)

if __name__ == "__main__":
    app.run(debug=True)