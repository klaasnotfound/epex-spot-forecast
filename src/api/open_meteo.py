import requests

from src.model.open_meteo import OpenMeteoForecast, OpenMeteoForecastData
from src.util.geo import LatLon


def get_forecast(lat: float, lon: float) -> OpenMeteoForecast:
    """Fetch OpenMeteo weather forecast for a given location."""

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=daylight_duration,sunshine_duration"
    res = requests.get(url)
    data: OpenMeteoForecastData = res.json()
    forecast = OpenMeteoForecast.fromjson(data)

    return forecast


def get_forecasts(locs: list[LatLon]) -> list[OpenMeteoForecast]:
    """Fetch OpenMeteo weather forecasts for several locations."""

    lats = ",".join(map(str, [loc.lat for loc in locs]))
    lons = ",".join(map(str, [loc.lon for loc in locs]))
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&daily=daylight_duration,sunshine_duration"
    res = requests.get(url)
    res.raise_for_status()
    data: list[OpenMeteoForecastData] = res.json()

    forecasts = [OpenMeteoForecast.fromjson(d) for d in data]

    return forecasts
