
import requests
import schedule
import time
import sqlite3
from datetime import datetime

# Configuration
API_KEY = "your_openweathermap_api_key"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
CITIES = ["Delhi", "Mumbai", "Chennai", "Bangalore", "Kolkata", "Hyderabad"]
ALERT_THRESHOLD_TEMP = 35
ALERT_CONSECUTIVE_THRESHOLD = 2
alert_log = {city: 0 for city in CITIES}

# Database setup
conn = sqlite3.connect("weather_data.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS daily_summary (
                    date TEXT PRIMARY KEY,
                    avg_temp REAL,
                    max_temp REAL,
                    min_temp REAL,
                    dominant_condition TEXT
                 )''')
conn.commit()

def kelvin_to_celsius(temp_k):
    return temp_k - 273.15

def fetch_weather(city):
    params = {"q": city, "appid": API_KEY}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return {
            "city": city,
            "temp": kelvin_to_celsius(data["main"]["temp"]),
            "feels_like": kelvin_to_celsius(data["main"]["feels_like"]),
            "condition": data["weather"][0]["main"],
            "timestamp": data["dt"]
        }
    return None

def calculate_daily_summary(city_data):
    temperatures = [entry["temp"] for entry in city_data]
    conditions = [entry["condition"] for entry in city_data]
    avg_temp = sum(temperatures) / len(temperatures)
    max_temp = max(temperatures)
    min_temp = min(temperatures)
    dominant_condition = max(set(conditions), key=conditions.count)

    date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT OR REPLACE INTO daily_summary VALUES (?, ?, ?, ?, ?)",
                   (date, avg_temp, max_temp, min_temp, dominant_condition))
    conn.commit()

def check_alert_conditions(city, temp, condition):
    if temp > ALERT_THRESHOLD_TEMP:
        alert_log[city] += 1
        if alert_log[city] >= ALERT_CONSECUTIVE_THRESHOLD:
            print(f"ALERT! City: {city}, Temp: {temp}°C, Condition: {condition}")
            alert_log[city] = 0
    else:
        alert_log[city] = 0

def process_weather_data():
    daily_data = {city: [] for city in CITIES}
    for city in CITIES:
        weather_data = fetch_weather(city)
        if weather_data:
            print(f"City: {weather_data['city']}, Temp: {weather_data['temp']:.2f}°C, Condition: {weather_data['condition']}")
            daily_data[city].append(weather_data)
            check_alert_conditions(city, weather_data["temp"], weather_data["condition"])
    
    for city, data in daily_data.items():
        if data:
            calculate_daily_summary(data)

schedule.every(5).minutes.do(process_weather_data)

print("Starting the weather monitoring system...")
while True:
    schedule.run_pending()
    time.sleep(1)
