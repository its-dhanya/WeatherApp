import requests
from dotenv import load_dotenv
import os
from dataclasses import dataclass
from typing import Optional, Tuple

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('API_KEY')

@dataclass
class WeatherData:
    main: str
    description: str
    icon: str
    temperature: float

def get_lat_lon(city_name: str, state_code: str, country_code: str, API_key: str) -> Optional[Tuple[float, float]]:
    """
    Fetch latitude and longitude for the given city, state, and country.
    """
    try:
        response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct',
                                params={'q': f'{city_name},{state_code},{country_code}', 'appid': API_key})
        response.raise_for_status()  # Raise an error for bad HTTP status codes
        data = response.json()
        if not data:
            raise ValueError(f"Location not found for {city_name}, {state_code}, {country_code}")
        lat, lon = data[0].get('lat'), data[0].get('lon')
        if lat is None or lon is None:
            raise ValueError(f"Latitude and Longitude not available for {city_name}, {state_code}, {country_code}")
        return lat, lon
    except requests.RequestException as e:
        print(f"Error fetching location data: {e}")
    except ValueError as ve:
        print(ve)
    return None

def get_current_weather(lat: float, lon: float, API_key: str) -> Optional[WeatherData]:
    """
    Fetch current weather data for the given latitude and longitude.
    """
    if lat is None or lon is None:
        print("Invalid latitude and longitude.")
        return None

    try:
        response = requests.get(f'https://api.openweathermap.org/data/2.5/weather',
                                params={'lat': lat, 'lon': lon, 'appid': API_key, 'units': 'metric'})
        response.raise_for_status()
        data = response.json()

        if 'weather' not in data or 'main' not in data:
            raise ValueError("Invalid weather data received.")

        weather = WeatherData(
            main=data['weather'][0].get('main', 'N/A'),
            description=data['weather'][0].get('description', 'N/A'),
            icon=data['weather'][0].get('icon', 'N/A'),
            temperature=float(data['main'].get('temp', 0))  # Default to 0 if temp is missing
        )
        return weather
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
    except ValueError as ve:
        print(ve)
    return None

def main(city_name: str, state_name: str, country_name: str) -> Optional[WeatherData]:
    """
    Main function to fetch weather data for a given city, state, and country.
    """
    lat_lon = get_lat_lon(city_name, state_name, country_name, api_key)
    if lat_lon:
        lat, lon = lat_lon
        return get_current_weather(lat, lon, api_key)
    else:
        print(f"Failed to get location data for {city_name}, {state_name}, {country_name}.")
    return None

if __name__ == "__main__":
    city_name = 'Toronto'
    state_name = 'ON'
    country_name = 'Canada'
    weather_data = main(city_name, state_name, country_name)
    
    if weather_data:
        print(weather_data)
    else:
        print("Failed to fetch weather data.")
