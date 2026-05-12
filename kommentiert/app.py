from flask import Flask, render_template, redirect, url_for, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# api key laden
load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

# index seite, bei url "/"
@app.route("/")
def index():
    return render_template("index.html", search_url=url_for("search_location"))

# der app.route decorator sorgt daf+r, dass die Funktion bei einer bestimmten url endung ausgeführt wird
@app.route("/search_location", methods=["POST"])
def search_location():
    post_code = request.form["post_code"]
    country_code = request.form["country_code"]
    # holt daten aus dem request und leitet dann passend weiter
    return redirect(url_for("weather", country_code=country_code, post_code=post_code))


@app.route("/weather/<country_code>/<post_code>")
# country und post code werden von search location weiter gegeben und dann hier weiterverwendet
def weather(country_code:str, post_code:int):
    # holt die Wetterdaten von der API
    location_response = get_location_data(country_code, post_code)
    if location_response.status_code != 200:
        # wenn es einen Ort nicht gibt
        return redirect(url_for("error", error_type="LocationNotFound"))
    
    location_data = location_response.json()
    # print(location_data)
    current_weather_data = get_current_weather_data(location_data)
    # gibt die Wetterdaten and das Template weiter, wo sie mit Hilfe von Jinja eingbaut werden
    return render_template("weather.html", current_data=current_weather_data)


def get_location_data(country_code:str, post_code:int):
    # holt die Koordinaten eines Ortes mit Hilfe des Ländercodes und der Postleitzahl, indem die url für den API call angepasst wird
    url = f"http://api.openweathermap.org/geo/1.0/zip?zip={post_code},{country_code}&appid={API_KEY}"
    response = requests.get(url)
    return response


def get_current_weather_data(location_data):
    lat = location_data["lat"]
    lon = location_data["lon"]
    # holt die tatsächlichen Wetterdaten, indem die URL für den API call angepasst wird
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    response = requests.get(url)
    current_weather_data = response.json()

    # passt die Zeiten den Zeitzonen entsprechend an unsere Zeitzone an
    tz_offset = current_weather_data["timezone"]

    utc_time = datetime.fromtimestamp(current_weather_data["dt"], tz=timezone.utc)
    city_timezone = timezone(timedelta(seconds=tz_offset))
    local_time = utc_time.astimezone(city_timezone)

    # lädt die Zeit von den Wetterdaten
    sunrise_utc = datetime.fromtimestamp(current_weather_data["sys"]["sunrise"], tz=timezone.utc)
    sunset_utc = datetime.fromtimestamp(current_weather_data["sys"]["sunset"], tz=timezone.utc)
    sunrise_local = sunrise_utc.astimezone(city_timezone)
    sunset_local = sunset_utc.astimezone(city_timezone)

    # macht den Timestamp zu einem darstellbaren string
    current_weather_data["local_time"] = local_time.strftime("%H:%M")
    current_weather_data["sunrise_time"] = sunrise_local.strftime("%H:%M")
    current_weather_data["sunset_time"] = sunset_local.strftime("%H:%M")
    return current_weather_data

# falls etwas schief geht, z.B. ungültige Location
@app.route("/error/<error_type>")
def error(error_type):
    return render_template("error.html", error_type=error_type)