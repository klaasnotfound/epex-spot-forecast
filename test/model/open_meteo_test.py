import duckdb
import pytest
from dateutil.parser import parse

from src.model.open_meteo import OpenMeteoForecastData, OpenMeteoForecastDataPoint


def test_init(fc_data_1: OpenMeteoForecastData):
    # Rejects invalid values
    with pytest.raises(AssertionError):
        OpenMeteoForecastDataPoint(parse("2023-01-01"), -100, 0, 0, fc_data_1)
    with pytest.raises(AssertionError):
        OpenMeteoForecastDataPoint(parse("2023-01-01"), 100, 0, 0, fc_data_1)
    with pytest.raises(AssertionError):
        OpenMeteoForecastDataPoint(parse("2023-01-01"), 0, -200, 0, fc_data_1)
    with pytest.raises(AssertionError):
        OpenMeteoForecastDataPoint(parse("2023-01-01"), 0, 200, 0, fc_data_1)

    # Works as expected
    dp = OpenMeteoForecastDataPoint(parse("2023-01-01"), 1, 2, 3, fc_data_1)
    assert (dp.lat, dp.lon, dp.elev) == (1, 2, 3)
    assert dp.ts.isoformat()[:10] == "2023-01-01"
    assert getattr(dp, "cloud_cover_mid_perc") == 48
    assert getattr(dp, "visibility_m") == 24140


def test_repr(fc_data_1: OpenMeteoForecastData):
    dp = OpenMeteoForecastDataPoint(parse("2023-01-01"), 52.5, 13.4, 38, fc_data_1)
    assert f"{dp}" == "ForecastData: (2023-01-01T00:00) [52.5, 13.4]@38m 15.9°C"


def test_init_table():
    con = duckdb.connect(":memory:")
    OpenMeteoForecastDataPoint.init_table(con)
    assert "open_meteo_hourly" in f"{con.sql('SHOW ALL TABLES')}"
    assert [(0,)] == con.sql("SELECT count(*) FROM open_meteo_hourly").fetchall()


def test_upsert_many(fc_data_1, fc_data_2):
    con = duckdb.connect(":memory:")
    OpenMeteoForecastDataPoint.init_table(con)
    assert [(0,)] == con.sql("SELECT count(*) FROM open_meteo_hourly").fetchall()
    dp1 = OpenMeteoForecastDataPoint(parse("2023-01-01T00:00"), 52, 13, 38, fc_data_1)
    dp2 = OpenMeteoForecastDataPoint(parse("2023-01-01T01:00"), 52, 13, 38, fc_data_2)
    OpenMeteoForecastDataPoint.upsert_many([dp1, dp2], con)
    assert [(2,)] == con.sql("SELECT count(*) FROM open_meteo_hourly").fetchall()


def test_fromjson(json_data):
    dps = OpenMeteoForecastDataPoint.fromjson(json_data)
    assert (dps[0].lat, dps[0].lon) == (52.52, 13.419998)
    assert dps[15].ts.isoformat()[:16] == "2023-01-01T15:00"
    assert getattr(dps[25], "visibility_m") == 16240
    assert getattr(dps[30], "precipitation_mm") == 0.4


@pytest.fixture
def fc_data_1() -> OpenMeteoForecastData:
    return {
        "temperature_2m_degc": 15.9,
        "shortwave_radiation_wm2": 0,
        "direct_radiation_wm2": 0,
        "diffuse_radiation_wm2": 0,
        "direct_normal_irradiance_wm2": 0,
        "global_tilted_irradiance_wm2": 0,
        "terrestrial_radiation_wm2": 0,
        "cloud_cover_perc": 100,
        "cloud_cover_low_perc": 0,
        "cloud_cover_mid_perc": 48,
        "cloud_cover_high_perc": 100,
        "visibility_m": 24140,
        "precipitation_mm": 0,
    }


@pytest.fixture
def fc_data_2() -> OpenMeteoForecastData:
    return {
        "temperature_2m_degc": 15.6,
        "shortwave_radiation_wm2": 0,
        "direct_radiation_wm2": 0,
        "diffuse_radiation_wm2": 0,
        "direct_normal_irradiance_wm2": 0,
        "global_tilted_irradiance_wm2": 0,
        "terrestrial_radiation_wm2": 0,
        "cloud_cover_perc": 99,
        "cloud_cover_low_perc": 29,
        "cloud_cover_mid_perc": 0,
        "cloud_cover_high_perc": 97,
        "visibility_m": 24140,
        "precipitation_mm": 0,
    }


# fmt: off
@pytest.fixture
def json_data():
    return {
        "latitude": 52.52,
        "longitude": 13.419998,
        "generationtime_ms": 1.08981132507324,
        "utc_offset_seconds": 0,
        "timezone": "GMT",
        "timezone_abbreviation": "GMT",
        "elevation": 38,
        "hourly_units": {
            "time": "iso8601",
            "temperature_2m": "°C",
            "shortwave_radiation": "W/m²",
            "direct_radiation": "W/m²",
            "diffuse_radiation": "W/m²",
            "direct_normal_irradiance": "W/m²",
            "global_tilted_irradiance": "W/m²",
            "terrestrial_radiation": "W/m²",
            "cloud_cover": "%",
            "cloud_cover_low": "%",
            "cloud_cover_mid": "%",
            "cloud_cover_high": "%",
            "visibility": "m",
            "precipitation": "mm"
        },
        "hourly": {
            "time": [
            "2023-01-01T00:00", "2023-01-01T01:00", "2023-01-01T02:00", "2023-01-01T03:00", "2023-01-01T04:00", "2023-01-01T05:00", "2023-01-01T06:00", "2023-01-01T07:00", "2023-01-01T08:00", "2023-01-01T09:00", "2023-01-01T10:00", "2023-01-01T11:00", "2023-01-01T12:00", "2023-01-01T13:00", "2023-01-01T14:00", "2023-01-01T15:00", "2023-01-01T16:00", "2023-01-01T17:00", "2023-01-01T18:00", "2023-01-01T19:00", "2023-01-01T20:00", "2023-01-01T21:00", "2023-01-01T22:00", "2023-01-01T23:00", "2023-01-02T00:00", "2023-01-02T01:00", "2023-01-02T02:00", "2023-01-02T03:00", "2023-01-02T04:00", "2023-01-02T05:00", "2023-01-02T06:00", "2023-01-02T07:00", "2023-01-02T08:00", "2023-01-02T09:00", "2023-01-02T10:00", "2023-01-02T11:00", "2023-01-02T12:00", "2023-01-02T13:00", "2023-01-02T14:00", "2023-01-02T15:00", "2023-01-02T16:00", "2023-01-02T17:00", "2023-01-02T18:00", "2023-01-02T19:00", "2023-01-02T20:00", "2023-01-02T21:00", "2023-01-02T22:00", "2023-01-02T23:00"
            ],
            "temperature_2m": [15.9, 15.6, 15.3, 15.4, 15.2, 15, 15, 14.5, 14.5, 14.8, 14.9, 15.2, 15.8, 15.7, 15.3, 14.7, 13.8, 12.9, 12.1, 11.9, 11.7, 11.5, 11.5, 11.5, 11.5, 11.4, 11.4, 11.8, 12.1, 12.2, 12.6, 12.6, 12.6, 13.7, 14, 14.2, 14.5, 14.4, 14.2, 14.7, 13.9, 12.6, 12, 11.3, 10.7, 10.2, 9.8, 9.5],
            "shortwave_radiation": [0, 0, 0, 0, 0, 0, 0, 0, 6, 30, 50, 76, 111, 95, 44, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 28, 60, 60, 42, 50, 52, 14, 0, 0, 0, 0, 0, 0, 0, 0],
            "direct_radiation": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 12, 10, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "diffuse_radiation": [0, 0, 0, 0, 0, 0, 0, 0, 6, 30, 50, 74, 99, 85, 43, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 28, 56, 60, 42, 49, 49, 14, 0, 0, 0, 0, 0, 0, 0, 0],
            "direct_normal_irradiance": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8.3, 48.7, 46.6, 6.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20.3, 0, 0, 4.6, 20.1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "global_tilted_irradiance": [0, 0, 0, 0, 0, 0, 0, 0, 5.6, 27.8, 46.4, 74.9, 128.9, 111.9, 44, 14.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4.6, 26, 65.8, 55.7, 39, 48.7, 57.6, 13, 0, 0, 0, 0, 0, 0, 0, 0],
            "terrestrial_radiation": [0, 0, 0, 0, 0, 0, 0, 0, 39.8, 167.2, 277.8, 339.6, 348.3, 303.5, 208.1, 68.7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 40.2, 168.2, 279.2, 341.4, 350.6, 306.1, 211.1, 71.9, 0, 0, 0, 0, 0, 0, 0, 0],
            "cloud_cover": [100, 99, 100, 100, 9, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 98, 99, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 97, 100, 95, 100, 99, 100, 100, 100, 100, 100, 100, 100, 100, 93, 100, 100, 99, 100, 86],
            "cloud_cover_low": [0, 29, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 60, 100, 40, 44, 11, 0, 0, 0, 0, 0, 23, 32, 29, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 24, 79, 73, 60, 66, 81, 86, 81, 97, 71],
            "cloud_cover_mid": [48, 0, 0, 0, 0, 4, 98, 82, 100, 87, 85, 97, 50, 100, 30, 84, 77, 77, 82, 82, 98, 100, 93, 97, 100, 100, 100, 94, 74, 97, 100, 83, 100, 80, 100, 100, 100, 100, 86, 98, 100, 100, 78, 97, 100, 93, 100, 62],
            "cloud_cover_high": [100, 97, 100, 100, 9, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 88, 93, 100, 100, 100, 100, 100, 100, 95, 49, 100, 100, 63, 35, 79, 100, 93, 100, 100, 100, 100, 100, 100, 0, 0, 0, 0, 0, 0, 34, 0],
            "visibility": [24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 16240, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 23580, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140, 24140],
            "precipitation": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.1, 0, 0.1, 0, 0, 0, 0, 0.1, 0.4, 0, 0.1, 0.2, 0.1, 0, 0.2, 0.1, 0.2, 0, 0, 0, 0.1, 0, 0.1, 0.2, 0.1, 0]
        }
    }
# fmt: on
