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
    assert (fc.lat, fc.lon) == (52.52, 13.419998)
    assert [d.isoformat()[:16] for d in fc.times[:2]] == [
        "2025-10-08T00:00",
        "2025-10-08T01:00",
    ]
    assert getattr(fc, "global_tilted_irradiance")[5:10] == [0.0, 0.9, 5.6, 14.2, 46.6]
    assert getattr(fc, "precipitation")[:5] == [0.10, 0.00, 0.00, 0.00, 0.00]


@pytest.mark.vcr
def test_get_forecasts():
    fcs = get_forecasts(
        [
            LatLon(48.662587, 9.00161),
            LatLon(48.917408, 11.4061),
            LatLon(52.505774, 13.4244),
        ]
    )
    assert len(fcs) == 3
    for fcidx in range(0, 3):
        assert [d.isoformat()[:16] for d in fcs[fcidx].times[:2]] == [
            "2025-10-08T00:00",
            "2025-10-08T01:00",
        ]
    assert (fcs[0].lat, fcs[0].lon) == (48.66, 9)
    assert (fcs[1].lat, fcs[1].lon) == (48.92, 11.4)
    assert (fcs[2].lat, fcs[2].lon) == (52.5, 13.419998)


@pytest.mark.vcr
def test_get_historical_forecast():
    fc = get_historical_forecast(52.52, 13.41, parse("2023-01-01"), parse("2023-01-10"))
    assert (fc.lat, fc.lon) == (52.52, 13.419998)
    assert [d.isoformat()[:16] for d in fc.times[:2]] == [
        "2023-01-01T00:00",
        "2023-01-01T01:00",
    ]
    assert getattr(fc, "temperature_2m")[:5] == [15.9, 15.6, 15.3, 15.4, 15.2]
    assert getattr(fc, "cloud_cover_mid")[:7] == [48, 0, 0, 0, 0, 4, 98]


@pytest.mark.vcr
def test_get_historical_forecasts():
    fcs = get_historical_forecasts(
        [
            LatLon(48.662587, 9.00161),
            LatLon(48.917408, 11.4061),
            LatLon(52.505774, 13.4244),
        ],
        parse("2023-01-01"),
        parse("2023-01-10"),
    )
    assert len(fcs) == 3
    for fcidx in range(0, 3):
        assert [d.isoformat()[:16] for d in fcs[fcidx].times[:2]] == [
            "2023-01-01T00:00",
            "2023-01-01T01:00",
        ]
    assert (fcs[0].lat, fcs[0].lon) == (48.66, 9)
    assert (fcs[1].lat, fcs[1].lon) == (48.92, 11.4)
    assert (fcs[2].lat, fcs[2].lon) == (52.5, 13.419998)
    assert getattr(fcs[0], "temperature_2m")[:5] == [11.7, 11.4, 11.3, 11.2, 11.0]
    assert getattr(fcs[1], "temperature_2m")[:5] == [9.3, 9.3, 8.9, 7.7, 7.8]
    assert getattr(fcs[2], "temperature_2m")[:5] == [16.0, 15.7, 15.4, 15.5, 15.2]
