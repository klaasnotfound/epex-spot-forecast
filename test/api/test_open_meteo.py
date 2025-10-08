import pytest
from dateutil.parser import parse

from src.api.open_meteo import (
    get_forecast,
    get_forecasts,
    get_historical_forecast,
    get_historical_forecasts,
)
from src.util.geo import LatLon


@pytest.mark.vcr
def test_get_forecast():
    fc = get_forecast(52.52, 13.41)
    assert (fc[0].lat, fc[0].lon, fc[0].elev) == (52.52, 13.419998, 38)
    assert [dp.ts.isoformat()[:16] for dp in fc[:2]] == [
        "2025-10-08T00:00",
        "2025-10-08T01:00",
    ]
    assert [getattr(dp, "global_tilted_irradiance_wm2") for dp in fc[6:10]] == [
        0.9,
        5.6,
        14.2,
        46.6,
    ]
    assert [getattr(dp, "precipitation_mm") for dp in fc[:3]] == [0.10, 0.00, 0.00]


@pytest.mark.vcr
def test_get_forecasts():
    fc = get_forecasts(
        [
            LatLon(48.662587, 9.00161),
            LatLon(48.917408, 11.4061),
            LatLon(52.505774, 13.4244),
        ]
    )
    assert len(fc) == 3 * 7 * 24
    assert [dp.ts.isoformat()[:16] for dp in fc[:2]] == [
        "2025-10-08T00:00",
        "2025-10-08T01:00",
    ]
    assert (fc[0].lat, fc[0].lon, fc[0].elev) == (48.66, 9, 483)
    assert (fc[168].lat, fc[168].lon, fc[168].elev) == (48.92, 11.4, 450)
    assert (fc[336].lat, fc[336].lon, fc[336].elev) == (52.5, 13.419998, 41)


@pytest.mark.vcr
def test_get_historical_forecast():
    fc = get_historical_forecast(52.52, 13.41, parse("2023-01-01"), parse("2023-01-10"))
    assert (fc[0].lat, fc[0].lon, fc[0].elev) == (52.52, 13.419998, 38)
    assert [dp.ts.isoformat()[:16] for dp in fc[:2]] == [
        "2023-01-01T00:00",
        "2023-01-01T01:00",
    ]
    assert [getattr(dp, "temperature_2m_degc") for dp in fc[:2]] == [15.9, 15.6]
    assert [getattr(dp, "cloud_cover_mid_perc") for dp in fc[:2]] == [48, 0]


@pytest.mark.vcr
def test_get_historical_forecasts():
    fc = get_historical_forecasts(
        [
            LatLon(48.662587, 9.00161),
            LatLon(48.917408, 11.4061),
            LatLon(52.505774, 13.4244),
        ],
        parse("2023-01-01"),
        parse("2023-01-10"),
    )
    assert len(fc) == 3 * 10 * 24
    assert [dp.ts.isoformat()[:16] for dp in fc[:2]] == [
        "2023-01-01T00:00",
        "2023-01-01T01:00",
    ]
    assert (fc[0].lat, fc[0].lon, fc[0].elev) == (48.66, 9, 483)
    assert (fc[240].lat, fc[240].lon, fc[240].elev) == (48.92, 11.4, 450)
    assert (fc[480].lat, fc[480].lon, fc[480].elev) == (52.5, 13.419998, 41)
    assert [getattr(dp, "temperature_2m_degc") for dp in fc[:2]] == [11.7, 11.4]
    assert [getattr(dp, "temperature_2m_degc") for dp in fc[240:242]] == [9.3, 9.3]
    assert [getattr(dp, "temperature_2m_degc") for dp in fc[480:482]] == [16.0, 15.7]
