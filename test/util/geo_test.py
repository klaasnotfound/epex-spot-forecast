import pytest
from dateutil.parser import parse

from src.model.open_meteo import OpenMeteoForecast, OpenMeteoValues
from src.util.geo import get_german_states, merge_forecasts


def test_get_german_states():
    states = get_german_states()
    assert len(states) == 16
    for state in states:
        assert len(state.name) == 2
        assert state.lat > 47
        assert state.lat < 55
        assert state.lon > 4
        assert state.lon < 16


def test_merge_forecasts(forecasts):
    # Rejects invalid values
    with pytest.raises(AssertionError):
        merge_forecasts([forecasts[0]])
    with pytest.raises(AssertionError):
        merge_forecasts([forecasts[0], forecasts[1]], [1.0])

    # Works as expected
    fc = merge_forecasts(forecasts[:2])
    assert (fc.lat, fc.lon) == (48.5, 11.5)
    assert [d.isoformat()[:10] for d in fc.times] == ["2025-09-17"]
    assert getattr(fc, "global_tilted_irradiance") == [9.0]

    # Applies weights correctly
    fc = merge_forecasts(forecasts[:2], [3, 1])
    assert (fc.lat, fc.lon) == (48.25, 11.25)
    assert [d.isoformat()[:10] for d in fc.times] == ["2025-09-17"]
    assert getattr(fc, "temperature_2m") == [1.25]
    assert getattr(fc, "global_tilted_irradiance") == [7.5]

    # Works for longer forecasts
    fc = merge_forecasts(forecasts[2:4], [1, 9])
    assert (round(fc.lat, 1), round(fc.lon, 1)) == (48.9, 11.9)
    assert [d.isoformat()[:16] for d in fc.times] == [
        "2025-09-18T00:00",
        "2025-09-18T00:01",
    ]
    assert [round(v, 1) for v in getattr(fc, "terrestrial_radiation")] == [13.3, 14.3]
    assert [round(v, 1) for v in getattr(fc, "cloud_cover_mid")] == [22.7, 23.7]

    # Rejects non-overlapping forecasts
    with pytest.raises(AssertionError):
        merge_forecasts(forecasts[-2:])


vals_1: OpenMeteoValues = {
    "temperature_2m": [1],
    "shortwave_radiation": [2],
    "direct_radiation": [3],
    "diffuse_radiation": [4],
    "direct_normal_irradiance": [5],
    "global_tilted_irradiance": [6],
    "terrestrial_radiation": [7],
    "weather_code": [8],
    "cloud_cover": [9],
    "cloud_cover_low": [10],
    "cloud_cover_mid": [11],
    "cloud_cover_high": [12],
    "visibility": [13],
    "precipitation": [14],
}

vals_2: OpenMeteoValues = {
    "temperature_2m": [2],
    "shortwave_radiation": [4],
    "direct_radiation": [6],
    "diffuse_radiation": [8],
    "direct_normal_irradiance": [10],
    "global_tilted_irradiance": [12],
    "terrestrial_radiation": [14],
    "weather_code": [16],
    "cloud_cover": [18],
    "cloud_cover_low": [20],
    "cloud_cover_mid": [24],
    "cloud_cover_high": [26],
    "visibility": [28],
    "precipitation": [30],
}

vals_3: OpenMeteoValues = {
    "temperature_2m": [1, 2],
    "shortwave_radiation": [2, 3],
    "direct_radiation": [3, 4],
    "diffuse_radiation": [4, 5],
    "direct_normal_irradiance": [5, 6],
    "global_tilted_irradiance": [6, 7],
    "terrestrial_radiation": [7, 8],
    "weather_code": [8, 9],
    "cloud_cover": [9, 10],
    "cloud_cover_low": [10, 11],
    "cloud_cover_mid": [11, 12],
    "cloud_cover_high": [12, 13],
    "visibility": [13, 14],
    "precipitation": [14, 15],
}

vals_4: OpenMeteoValues = {
    "temperature_2m": [2, 3],
    "shortwave_radiation": [4, 5],
    "direct_radiation": [6, 7],
    "diffuse_radiation": [8, 9],
    "direct_normal_irradiance": [10, 11],
    "global_tilted_irradiance": [12, 13],
    "terrestrial_radiation": [14, 15],
    "weather_code": [16, 17],
    "cloud_cover": [18, 19],
    "cloud_cover_low": [20, 21],
    "cloud_cover_mid": [24, 25],
    "cloud_cover_high": [26, 27],
    "visibility": [28, 29],
    "precipitation": [30, 31],
}


@pytest.fixture
def forecasts():
    return [
        OpenMeteoForecast(48, 11, [parse("2025-09-17")], vals_1),
        OpenMeteoForecast(49, 12, [parse("2025-09-17")], vals_2),
        OpenMeteoForecast(
            48, 11, [parse("2025-09-18T00:00"), parse("2025-09-18T00:01")], vals_3
        ),
        OpenMeteoForecast(
            49, 12, [parse("2025-09-18T00:00"), parse("2025-09-18T00:01")], vals_4
        ),
        OpenMeteoForecast(
            50, 13, [parse("2025-09-18T17:00"), parse("2025-09-18T18:00")], vals_4
        ),
    ]
