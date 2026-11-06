"""City search and weather data from Open-Meteo."""

import math
from dataclasses import dataclass
from datetime import date, datetime

import requests


class WeatherError(Exception):
    """A problem the app can explain to the user."""


@dataclass(frozen=True)
class City:
    name: str
    latitude: float
    longitude: float
    country: str = ""
    region: str = ""

    @property
    def label(self):
        return ", ".join(
            dict.fromkeys(p for p in (self.name, self.region, self.country) if p)
        )


@dataclass(frozen=True)
class ForecastDay:
    date: date
    code: int
    low: float
    high: float
    rain_chance: float


@dataclass(frozen=True)
class Weather:
    city: City
    time: datetime
    timezone: str
    temperature: float
    feels_like: float
    humidity: float
    wind: float
    code: int
    forecast: list[ForecastDay]


def condition(code):
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Freezing fog",
        51: "Light drizzle",
        53: "Drizzle",
        55: "Heavy drizzle",
        56: "Freezing drizzle",
        57: "Freezing drizzle",
        61: "Light rain",
        63: "Rain",
        65: "Heavy rain",
        66: "Freezing rain",
        67: "Freezing rain",
        71: "Light snow",
        73: "Snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Light showers",
        81: "Showers",
        82: "Heavy showers",
        85: "Snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with hail",
    }
    return descriptions.get(code, "Conditions unavailable")


class WeatherClient:
    def _get(self, url, params):
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except ValueError as error:
            raise WeatherError(
                "The weather service sent an unreadable response. Please try again."
            ) from error
        except requests.RequestException as error:
            raise WeatherError(
                "Couldn't connect to the weather service. Check your connection and try again."
            ) from error

    def search_cities(self, query):
        data = self._get(
            "https://geocoding-api.open-meteo.com/v1/search",
            {"name": query.strip(), "count": 5, "language": "en", "format": "json"},
        )
        try:
            return [
                City(
                    item["name"],
                    self._number(item["latitude"]),
                    self._number(item["longitude"]),
                    item.get("country", ""),
                    item.get("admin1", ""),
                )
                for item in data.get("results", [])
            ]
        except (AttributeError, KeyError, TypeError, ValueError) as error:
            raise WeatherError(
                "The city results are incomplete. Please try another search."
            ) from error

    @staticmethod
    def _number(value):
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError("Missing or invalid measurement")
        return value

    def get_weather(self, city):
        data = self._get(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": city.latitude,
                "longitude": city.longitude,
                "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
                "daily": "weather_code,temperature_2m_min,temperature_2m_max,precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": 3,
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
            },
        )
        return self.parse_weather(city, data)

    def parse_weather(self, city, data):
        try:
            current, daily = data["current"], data["daily"]
            forecast = [
                ForecastDay(
                    date.fromisoformat(daily["time"][i]),
                    self._number(daily["weather_code"][i]),
                    self._number(daily["temperature_2m_min"][i]),
                    self._number(daily["temperature_2m_max"][i]),
                    self._number(daily["precipitation_probability_max"][i]),
                )
                for i in range(3)
            ]
            return Weather(
                city,
                datetime.fromisoformat(current["time"]),
                data["timezone"],
                self._number(current["temperature_2m"]),
                self._number(current["apparent_temperature"]),
                self._number(current["relative_humidity_2m"]),
                self._number(current["wind_speed_10m"]),
                self._number(current["weather_code"]),
                forecast,
            )
        except (KeyError, TypeError, ValueError, IndexError) as error:
            raise WeatherError(
                "Some weather readings are missing. Please refresh in a moment."
            ) from error
