from datetime import datetime
from typing import TypedDict

from dateutil.parser import parse


class OpenMeteoValues(TypedDict):
    temperature_2m: list[float]
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


class OpenMeteoForecast:
    """Multi-day weather forecast from the OpenMeteo API"""

    def __init__(
        self, lat: float, lon: float, times: list[datetime], vals: OpenMeteoValues
    ):
        assert lat >= -90 and lat <= 90, "Latitude must be within [-90, 90]"
        assert lon >= -180 and lon <= 180, "Longitude must be within [-180, 180]"
        assert len(times) > 0, "No dates in time series"
        for k in OpenMeteoValues.__annotations__:
            assert k in vals, f"Value data must contain '{k}'"
            assert len(times) == len(vals[k]), "Wrong number of days"

        self.lat = lat
        self.lon = lon
        self.times = times
        for k in OpenMeteoValues.__annotations__:
            setattr(self, k, vals[k])

    @staticmethod
    def fromjson(data: OpenMeteoForecastData):
        times = [parse(d) for d in data["hourly"]["time"]]
        return OpenMeteoForecast(
            data["latitude"], data["longitude"], times, data["hourly"]
        )

    def __repr__(self):
        return f"OpenMeteoForecast ({self.lat}, {self.lon}) [{len(self.times)} hour{'s'[: len(self.times) ^ 1]}]"
