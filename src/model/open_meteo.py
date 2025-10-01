from datetime import datetime
from typing import NotRequired, TypedDict

from dateutil.parser import parse


class OpenMeteoValues(TypedDict):
    shortwave_radiation: list[float]
    direct_radiation: list[float]
    diffuse_radiation: list[float]
    direct_normal_irradiance: list[float]
    global_tilted_irradiance: list[float]
    terrestrial_radiation: list[float]
    weather_code: list[float]
    cloud_cover: list[float]
    cloud_cover_low: list[float]
    cloud_cover_mid: list[float]
    cloud_cover_high: list[float]
    visibility: list[float]
    precipitation: list[float]


class OpenMeteoTimeSeries(OpenMeteoValues):
    time: list[str]


class OpenMeteoForecastData(TypedDict):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: int
    hourly_units: dict[str, str]
    hourly: OpenMeteoTimeSeries
    daily_units: NotRequired[dict[str, str]]
    daily: NotRequired[OpenMeteoTimeSeries]


class OpenMeteoForecast:
    """Multi-day weather forecast from the OpenMeteo API"""

    def __init__(
        self, lat: float, lon: float, days: list[datetime], vals: OpenMeteoValues
    ):
        assert lat >= -90 and lat <= 90, "Latitude must be within [-90, 90]"
        assert lon >= -180 and lon <= 180, "Longitude must be within [-180, 180]"
        assert "daylight_duration" in vals, "Value data must contain daylight duration"
        assert "sunshine_duration" in vals, "Value data must contain sunshine duration"
        assert len(days) > 0, "No dates in time series"
        assert len(days) == len(vals["daylight_duration"]), "Wrong number of days"
        assert len(days) == len(vals["sunshine_duration"]), "Wrong number of days"

        self.lat = lat
        self.lon = lon
        self.days = days
        self.daylight_dur = vals["daylight_duration"]
        self.sunshine_dur = vals["sunshine_duration"]

    @staticmethod
    def fromjson(data: OpenMeteoForecastData):
        days = [parse(d) for d in data["daily"]["time"]]
        return OpenMeteoForecast(
            data["latitude"], data["longitude"], days, data["daily"]
        )

    def __repr__(self):
        return f"OpenMeteoForecast ({self.lat}, {self.lon}) [{len(self.days)} day{'s'[: len(self.days) ^ 1]}]"
