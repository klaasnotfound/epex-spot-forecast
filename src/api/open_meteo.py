from datetime import datetime

import requests

from src.model.open_meteo import (
    ApiForecastData,
    ApiForecastValues,
    OpenMeteoForecastDataPoint,
)
from src.util.geo import LatLon

HOURLY_ATTRS = ",".join(ApiForecastValues.__annotations__.keys())


def get_forecast(lat: float, lon: float) -> list[OpenMeteoForecastDataPoint]:
    """Fetch OpenMeteo weather forecast data for a given location."""

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly={HOURLY_ATTRS}&tilt=35"
    res = requests.get(url)
    data: ApiForecastData = res.json()
    forecast = OpenMeteoForecastDataPoint.fromjson(data)

    return forecast


def get_forecasts(locs: list[LatLon]) -> list[OpenMeteoForecastDataPoint]:
    """Fetch OpenMeteo weather forecasts for several locations."""

    lats = ",".join(map(str, [loc.lat for loc in locs]))
    lons = ",".join(map(str, [loc.lon for loc in locs]))
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&hourly={HOURLY_ATTRS}&tilt=35"
    res = requests.get(url)
    res.raise_for_status()
    data: list[ApiForecastData] = res.json()

    forecasts = [OpenMeteoForecastDataPoint.fromjson(d) for d in data]

    return [dp for fc in forecasts for dp in fc]


def get_historical_forecast(
    lat: float, lon: float, start: datetime, end: datetime
) -> list[OpenMeteoForecastDataPoint]:
    """Fetch historic OpenMeteo weather forecast for a given location and time range."""

    sd = start.isoformat()[:10]
    ed = end.isoformat()[:10]
    url = f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&start_date={sd}&end_date={ed}&hourly={HOURLY_ATTRS}&tilt=35"
    res = requests.get(url)
    data: ApiForecastData = res.json()
    forecast = OpenMeteoForecastDataPoint.fromjson(data)

    return forecast


def get_historical_forecasts(
    locs: list[LatLon], start: datetime, end: datetime
) -> list[OpenMeteoForecastDataPoint]:
    """Fetch OpenMeteo weather forecasts for several locations and a given time range."""

    lats = ",".join(map(str, [loc.lat for loc in locs]))
    lons = ",".join(map(str, [loc.lon for loc in locs]))
    sd = start.isoformat()[:10]
    ed = end.isoformat()[:10]
    url = f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={lats}&longitude={lons}&start_date={sd}&end_date={ed}&hourly={HOURLY_ATTRS}&tilt=35"
    res = requests.get(url)
    res.raise_for_status()
    data: list[ApiForecastData] = res.json()

    forecasts = [OpenMeteoForecastDataPoint.fromjson(d) for d in data]

    return [dp for fc in forecasts for dp in fc]
