from flask import Flask, render_template, redirect, url_for, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import json

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

@app.route("/")
def index(error=None):
    return render_template("index.html", search_url=url_for("search_location"), error=error)

@app.route("/search_location", methods=["POST"])
def search_location():
    post_code = request.form["post_code"]
    country_code = request.form["country_code"]
    return redirect(url_for("weather", country_code=country_code, post_code=post_code))

@app.route("/weather/<country_code>/<post_code>")
def weather(country_code:str, post_code:int):
    location_response = get_location_data(country_code, post_code)
    if location_response.status_code != 200:
        return redirect(url_for("error", error_type="LocationNotFound"))
    
    location_data = location_response.json()
    print(location_data)
    current_weather_data = get_current_weather_data(location_data)
    return render_template("weather.html", current_data=current_weather_data)


def get_location_data(country_code:str, post_code:int):
    url = f"http://api.openweathermap.org/geo/1.0/zip?zip={post_code},{country_code}&appid={API_KEY}"
    response = requests.get(url)
    return response


def get_current_weather_data(location_data):
    lat = location_data["lat"]
    lon = location_data["lon"]
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    response = requests.get(url)
    current_weather_data = response.json()

    tz_offset = current_weather_data["timezone"]

    utc_time = datetime.fromtimestamp(current_weather_data["dt"], tz=timezone.utc)
    city_timezone = timezone(timedelta(seconds=tz_offset))

    local_time = utc_time.astimezone(city_timezone)

    sunrise_utc = datetime.fromtimestamp(current_weather_data["sys"]["sunrise"], tz=timezone.utc)
    sunset_utc = datetime.fromtimestamp(current_weather_data["sys"]["sunset"], tz=timezone.utc)
    sunrise_local = sunrise_utc.astimezone(city_timezone)
    sunset_local = sunset_utc.astimezone(city_timezone)

    current_weather_data["local_time"] = local_time.strftime("%H:%M")
    current_weather_data["sunrise_time"] = sunrise_local.strftime("%H:%M")
    current_weather_data["sunset_time"] = sunset_local.strftime("%H:%M")
    return current_weather_data






@app.route("/error/<error_type>")
def error(error_type):
    return render_template("error.html", error_type=error_type)