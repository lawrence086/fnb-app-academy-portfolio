import copy
import unittest
from unittest.mock import patch

import requests
from weather import City, WeatherClient, WeatherError, condition


class WeatherTests(unittest.TestCase):
    def setUp(self):
        self.client = WeatherClient()
        self.city = City("Johannesburg", -26.2, 28.04, "South Africa", "Gauteng")
        self.data = {
            "timezone": "Africa/Johannesburg",
            "current": {
                "time": "2026-11-06T10:15",
                "temperature_2m": 24.5,
                "apparent_temperature": 25.1,
                "relative_humidity_2m": 50,
                "wind_speed_10m": 12.3,
                "weather_code": 2,
            },
            "daily": {
                "time": ["2026-11-06", "2026-11-07", "2026-11-08"],
                "weather_code": [2, 61, 0],
                "temperature_2m_min": [14, 15, 13],
                "temperature_2m_max": [26, 22, 28],
                "precipitation_probability_max": [10, 70, 0],
            },
        }

    def test_parse_current_and_forecast(self):
        weather = self.client.parse_weather(self.city, self.data)
        self.assertEqual(weather.temperature, 24.5)
        self.assertEqual(weather.time.hour, 10)
        self.assertEqual(weather.city.label, "Johannesburg, Gauteng, South Africa")
        self.assertEqual(weather.forecast[1].rain_chance, 70)
        self.assertEqual(weather.forecast[2].date.day, 8)

    def test_missing_readings_do_not_become_zero(self):
        for value in (None, "24", True, float("nan")):
            with self.subTest(value=value):
                data = copy.deepcopy(self.data)
                data["current"]["temperature_2m"] = value
                with self.assertRaises(WeatherError):
                    self.client.parse_weather(self.city, data)

    def test_incomplete_forecast_is_reported(self):
        self.data["daily"]["time"] = ["2026-11-06"]
        with self.assertRaises(WeatherError):
            self.client.parse_weather(self.city, self.data)

    @patch("weather.requests.get")
    def test_connection_error(self, get):
        get.side_effect = requests.ConnectionError("offline")
        with self.assertRaisesRegex(WeatherError, "connection"):
            self.client.get_weather(self.city)

    @patch("weather.requests.get")
    def test_http_error(self, get):
        get.return_value.raise_for_status.side_effect = requests.HTTPError("503")
        with self.assertRaises(WeatherError):
            self.client.get_weather(self.city)

    @patch("weather.requests.get")
    def test_bad_json(self, get):
        get.return_value.json.side_effect = requests.exceptions.JSONDecodeError(
            "not JSON", "oops", 0
        )
        with self.assertRaisesRegex(WeatherError, "unreadable"):
            self.client.get_weather(self.city)

    @patch("weather.requests.get")
    def test_search_allows_no_results_and_missing_optional_region(self, get):
        get.return_value.json.return_value = {}
        self.assertEqual(self.client.search_cities("unknown"), [])
        get.return_value.json.return_value = {
            "results": [{"name": "Paris", "latitude": 48.85, "longitude": 2.35}]
        }
        self.assertEqual(self.client.search_cities("Paris")[0].label, "Paris")

    @patch("weather.requests.get")
    def test_request_uses_three_days_and_explicit_units(self, get):
        get.return_value.json.return_value = self.data
        self.client.get_weather(self.city)
        params = get.call_args.kwargs["params"]
        self.assertEqual(params["forecast_days"], 3)
        self.assertEqual(params["timezone"], "auto")
        self.assertEqual(params["wind_speed_unit"], "kmh")
        self.assertEqual(get.call_args.kwargs["timeout"], 15)
        get.return_value.raise_for_status.assert_called_once()

    def test_unknown_code_has_a_fallback(self):
        self.assertEqual(condition(999), "Conditions unavailable")


if __name__ == "__main__":
    unittest.main()
