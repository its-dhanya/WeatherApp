from flask import Flask, request, render_template, jsonify
import requests
import os
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('API_KEY')

app = Flask(__name__)

@dataclass
class WeatherData:
    main: str
    description: str
    icon: str
    temperature: int

def get_lat_lon(city_name: str, state_code: str, country_code: str, API_key: str):
    """
    Fetch latitude and longitude for the given city, state, and country.
    """
    try:
        response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},{country_code}&appid={API_key}')
        response.raise_for_status()
        data = response.json()
        if not data:
            raise ValueError(f"Location not found for {city_name}, {state_code}, {country_code}")
        lat, lon = data[0].get('lat'), data[0].get('lon')
        if lat is None or lon is None:
            raise ValueError(f"Latitude and Longitude not available for {city_name}, {state_code}, {country_code}")
        return lat, lon
    except requests.RequestException as e:
        print(f"Error fetching location data: {e}")
        return None, None
    except ValueError as ve:
        print(ve)
        return None, None

def get_current_weather(lat: float, lon: float, API_key: str):
    """
    Fetch current weather data for the given latitude and longitude.
    """
    if lat is None or lon is None:
        print("Invalid latitude and longitude.")
        return None

    try:
        response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&units=metric')
        response.raise_for_status()
        data = response.json()

        if 'weather' not in data or 'main' not in data:
            raise ValueError("Invalid weather data received.")

        weather = WeatherData(
            main=data['weather'][0].get('main', 'N/A'),
            description=data['weather'][0].get('description', 'N/A'),
            icon=data['weather'][0].get('icon', 'N/A'),
            temperature=int(data['main'].get('temp', 0))  # Default to 0 if temp is missing
        )
        return weather
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
    except ValueError as ve:
        print(ve)
        return None

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city_name = request.form.get('cityName')
        state_name = request.form.get('stateName')
        country_name = request.form.get('countryName')

        # Basic validation
        if not city_name or not state_name or not country_name:
            error = "All fields are required."
            return render_template('index.html', error=error)

        # Validate state abbreviation
        if len(state_name) != 2 or not state_name.isalpha():
            error = "State abbreviation must be exactly 2 letters."
            return render_template('index.html', error=error)

        # Fetch weather data
        lat, lon = get_lat_lon(city_name, state_name, country_name, api_key)
        if lat is not None and lon is not None:
            weather_data = get_current_weather(lat, lon, api_key)
            if weather_data:
                return render_template('index.html', data=weather_data)
            else:
                error = "Could not retrieve weather data."
                return render_template('index.html', error=error)
        else:
            error = "Invalid location information provided."
            return render_template('index.html', error=error)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
