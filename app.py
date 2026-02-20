from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html", search_url=url_for("search_location"))

@app.route("/search_location", methods=["POST"])
def search_location():
    plz = request.form["plz"]
    return redirect(url_for("weather", plz=plz))

@app.route("/weather/<plz>")
def weather(plz:int):
    return render_template("weather.html", plz=plz)

def get_weather_data(plz):
    pass