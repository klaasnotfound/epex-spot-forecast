import calendar
import time
from datetime import datetime
from typing import TypedDict

from dateutil.parser import parse
from duckdb import DuckDBPyConnection
from duckdb.typing import DuckDBPyType


class ApiForecastValues(TypedDict):
    temperature_2m: list[float]
    shortwave_radiation: list[float]
    direct_radiation: list[float]
    diffuse_radiation: list[float]
    direct_normal_irradiance: list[float]
    global_tilted_irradiance: list[float]
    terrestrial_radiation: list[float]
    cloud_cover: list[float]
    cloud_cover_low: list[float]
    cloud_cover_mid: list[float]
    cloud_cover_high: list[float]
    visibility: list[float]
    precipitation: list[float]


class ApiTimeSeries(ApiForecastValues):
    time: list[str]


class ApiForecastData(TypedDict):
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: int
    timezone: str
    timezone_abbreviation: str
    elevation: int
    hourly_units: dict[str, str]
    hourly: ApiTimeSeries


class OpenMeteoForecastData(TypedDict):
    temperature_2m_degc: float
    shortwave_radiation_wm2: float
    direct_radiation_wm2: float
    diffuse_radiation_wm2: float
    direct_normal_irradiance_wm2: float
    global_tilted_irradiance_wm2: float
    terrestrial_radiation_wm2: float
    cloud_cover_perc: float
    cloud_cover_low_perc: float
    cloud_cover_mid_perc: float
    cloud_cover_high_perc: float
    visibility_m: float
    precipitation_mm: float


ZERO_FC_DATA = OpenMeteoForecastData(
    temperature_2m_degc=0,
    shortwave_radiation_wm2=0,
    direct_radiation_wm2=0,
    diffuse_radiation_wm2=0,
    direct_normal_irradiance_wm2=0,
    global_tilted_irradiance_wm2=0,
    terrestrial_radiation_wm2=0,
    cloud_cover_perc=0,
    cloud_cover_low_perc=0,
    cloud_cover_mid_perc=0,
    cloud_cover_high_perc=0,
    visibility_m=0,
    precipitation_mm=0,
)


class OpenMeteoForecastDataPoint:
    """Weather forecast data point (e.g. hourly) from the OpenMeteo API"""

    def __init__(
        self,
        ts: datetime,
        lat: float,
        lon: float,
        elev: float,
        vals: OpenMeteoForecastData,
    ):
        assert lat >= -90 and lat <= 90, "Latitude must be within [-90, 90]"
        assert lon >= -180 and lon <= 180, "Longitude must be within [-180, 180]"

        self.ts = ts
        self.lat = lat
        self.lon = lon
        self.elev = elev
        for attr in OpenMeteoForecastData.__annotations__:
            setattr(self, attr, vals[attr])

    def __repr__(self):
        return (
            f"ForecastData: ({self.ts.isoformat()[:16]}) [{self.lat}, {self.lon}]@{round(self.elev)}m "
            + f"{getattr(self, 'temperature_2m_degc'):.1f}°C"
        )

    @staticmethod
    def init_table(con: DuckDBPyConnection):
        col_str = ", ".join(
            [
                f"{k} {DuckDBPyType(v)}"
                for k, v in OpenMeteoForecastData.__annotations__.items()
            ]
        )
        stmt = f"""
        CREATE OR REPLACE TABLE open_meteo_hourly (
            ts TIMESTAMP_MS,
            lat DOUBLE,
            lon DOUBLE,
            elev_m DOUBLE,
            {col_str},
            PRIMARY KEY (ts, lat, lon)
        );
        """
        con.execute(stmt)

    @staticmethod
    def upsert_many(data: list["OpenMeteoForecastDataPoint"], con: DuckDBPyConnection):
        val_str = (
            "("
            + "), (".join(
                [
                    f"make_timestamp_ms({round(calendar.timegm(time.localtime(d.ts.timestamp())) * 1e3)}), "
                    + f"{d.lat:.6f}, {d.lon:.6f}, {d.elev},"
                    + ", ".join(
                        [
                            f"{getattr(d, k)}"
                            for k in OpenMeteoForecastData.__annotations__
                        ]
                    ).replace("None", "NULL")
                    for d in data
                ]
            )
            + ")"
        )
        stmt = f"""
        INSERT OR IGNORE INTO open_meteo_hourly VALUES
        {val_str};
        """
        con.execute(stmt)

    @staticmethod
    def fromjson(data: ApiForecastData) -> list["OpenMeteoForecastDataPoint"]:
        data_points: list["OpenMeteoForecastDataPoint"] = []
        lat = data["latitude"]
        lon = data["longitude"]
        elev = data["elevation"]
        hourly = data["hourly"]
        for idx, time_str in enumerate(hourly["time"]):
            ts = parse(time_str)
            vals: dict[str, float] = {}
            for k in OpenMeteoForecastData.__annotations__:
                attr = "_".join(k.split("_")[:-1])
                vals[k] = hourly[attr][idx]
            data_points.append(
                OpenMeteoForecastDataPoint(
                    ts, lat, lon, elev, OpenMeteoForecastData(**vals)
                )
            )

        return data_points
