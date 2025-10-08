from datetime import datetime

import requests

from src.model.open_meteo import (
    OpenMeteoForecast,
    OpenMeteoForecastData,
    OpenMeteoValues,
)
from src.util.geo import LatLon

HOURLY_ATTRS = ",".join(OpenMeteoValues.__annotations__.keys())


def get_forecast(lat: float, lon: float) -> OpenMeteoForecast:
    """Fetch OpenMeteo weather forecast for a given location."""

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={HOURLY_ATTRS}&tilt=35"
    res = requests.get(url)
    data: OpenMeteoForecastData = res.json()
    forecast = OpenMeteoForecast.fromjson(data)

    return forecast


def get_forecasts(locs: list[LatLon]) -> list[OpenMeteoForecast]:
    """Fetch OpenMeteo weather forecasts for several locations."""

    lats = ",".join(map(str, [loc.lat for loc in locs]))
    lons = ",".join(map(str, [loc.lon for loc in locs]))
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly={HOURLY_ATTRS}&tilt=35"
    res = requests.get(url)
    res.raise_for_status()
    data: list[OpenMeteoForecastData] = res.json()

    forecasts = [OpenMeteoForecast.fromjson(d) for d in data]

    return forecasts


def get_historical_forecast(
    lat: float, lon: float, start: datetime, end: datetime
) -> OpenMeteoForecast:
    """Fetch historic OpenMeteo weather forecast for a given location and time range."""

    sd = start.isoformat()[:10]
    ed = end.isoformat()[:10]
    url = f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={sd}&end_date={ed}&hourly={HOURLY_ATTRS}&tilt=35"
    res = requests.get(url)
    data: OpenMeteoForecastData = res.json()
    forecast = OpenMeteoForecast.fromjson(data)

    return forecast


def get_historical_forecasts(
    locs: list[LatLon], start: datetime, end: datetime
) -> list[OpenMeteoForecast]:
    """Fetch OpenMeteo weather forecasts for several locations and a given time range."""

    lats = ",".join(map(str, [loc.lat for loc in locs]))
    lons = ",".join(map(str, [loc.lon for loc in locs]))
    sd = start.isoformat()[:10]
    ed = end.isoformat()[:10]
    url = f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&start_date={sd}&end_date={ed}&hourly={HOURLY_ATTRS}&tilt=35"
    res = requests.get(url)
    res.raise_for_status()
    data: list[OpenMeteoForecastData] = res.json()

    forecasts = [OpenMeteoForecast.fromjson(d) for d in data]

    return forecasts
