import pytest
from dateutil.parser import parse

from src.model.open_meteo import OpenMeteoForecastData, OpenMeteoForecastDataPoint
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
        merge_forecasts(forecasts[:2], [1.0])
    with pytest.raises(AssertionError):
        merge_forecasts([forecasts[0], forecasts[2]])

    # Works as expected
    fc = merge_forecasts(forecasts[:2])
    assert (fc[0].lat, fc[0].lon, fc[0].elev) == (50, 12, 86.5)
    assert fc[0].ts.isoformat()[:10] == "2025-09-17"
    assert getattr(fc[0], "global_tilted_irradiance_wm2") == 16

    # Applies weights correctly
    fc = merge_forecasts(forecasts[:2], [3, 1])
    assert (fc[0].lat, fc[0].lon, fc[0].elev) == (49, 11.5, 54.75)
    assert fc[0].ts.isoformat()[:10] == "2025-09-17"
    assert round(getattr(fc[0], "temperature_2m_degc"), 2) == 15.23
    assert round(getattr(fc[0], "global_tilted_irradiance_wm2"), 2) == 10.1

    # Works for longer forecasts
    fc = merge_forecasts(forecasts[2:4], [1, 9])
    assert (fc[1].lat, fc[1].lon, fc[1].elev) == (48.2, 10.9, 27.3)
    assert [dp.ts.isoformat()[:16] for dp in fc] == [
        "2025-09-17T00:00",
        "2025-09-17T01:00",
    ]
    assert [round(getattr(dp, "terrestrial_radiation_wm2"), 1) for dp in fc] == [
        16.7,
        155.3,
    ]

    # Rejects non-overlapping forecasts
    with pytest.raises(AssertionError):
        merge_forecasts(forecasts[3:])


fc_data_1: OpenMeteoForecastData = {
    "temperature_2m_degc": 15.9,
    "shortwave_radiation_wm2": 0,
    "direct_radiation_wm2": 0,
    "diffuse_radiation_wm2": 0,
    "direct_normal_irradiance_wm2": 0,
    "global_tilted_irradiance_wm2": 4.2,
    "terrestrial_radiation_wm2": 0,
    "wind_speed_10m_kmh": 2.0,
    "wind_speed_80m_kmh": 4.7,
    "wind_speed_120m_kmh": 6.3,
    "cloud_cover_perc": 100,
    "cloud_cover_low_perc": 0,
    "cloud_cover_mid_perc": 48,
    "cloud_cover_high_perc": 100,
    "visibility_m": 24140,
    "precipitation_mm": 0,
}

fc_data_2: OpenMeteoForecastData = {
    "temperature_2m_degc": 13.2,
    "shortwave_radiation_wm2": 111,
    "direct_radiation_wm2": 10,
    "diffuse_radiation_wm2": 74,
    "direct_normal_irradiance_wm2": 8.3,
    "global_tilted_irradiance_wm2": 27.8,
    "terrestrial_radiation_wm2": 167.2,
    "wind_speed_10m_kmh": 0.8,
    "wind_speed_80m_kmh": 2.3,
    "wind_speed_120m_kmh": 4.1,
    "cloud_cover_perc": 80,
    "cloud_cover_low_perc": 5,
    "cloud_cover_mid_perc": 72,
    "cloud_cover_high_perc": 80,
    "visibility_m": 16768,
    "precipitation_mm": 0.9,
}

fc_data_3: OpenMeteoForecastData = {
    "temperature_2m_degc": 20.1,
    "shortwave_radiation_wm2": 0,
    "direct_radiation_wm2": 0,
    "diffuse_radiation_wm2": 0,
    "direct_normal_irradiance_wm2": 0,
    "global_tilted_irradiance_wm2": 0,
    "terrestrial_radiation_wm2": 48.6,
    "wind_speed_10m_kmh": 0,
    "wind_speed_80m_kmh": 0,
    "wind_speed_120m_kmh": 0,
    "cloud_cover_perc": 80,
    "cloud_cover_low_perc": 5,
    "cloud_cover_mid_perc": 72,
    "cloud_cover_high_perc": 80,
    "visibility_m": 16768,
    "precipitation_mm": 0.9,
}


@pytest.fixture
def forecasts() -> list[list[OpenMeteoForecastDataPoint]]:
    return [
        [
            OpenMeteoForecastDataPoint(
                parse("2025-09-17T00:00"), 48, 11, 23, fc_data_1
            ),
        ],
        [
            OpenMeteoForecastDataPoint(
                parse("2025-09-17T00:00"), 52, 13, 150, fc_data_2
            ),
        ],
        [
            OpenMeteoForecastDataPoint(
                parse("2025-09-17T00:00"), 50, 10, 66, fc_data_2
            ),
            OpenMeteoForecastDataPoint(
                parse("2025-09-17T01:00"), 50, 10, 66, fc_data_3
            ),
        ],
        [
            OpenMeteoForecastDataPoint(
                parse("2025-09-17T00:00"), 48, 11, 23, fc_data_1
            ),
            OpenMeteoForecastDataPoint(
                parse("2025-09-17T01:00"), 48, 11, 23, fc_data_2
            ),
        ],
        [
            OpenMeteoForecastDataPoint(
                parse("2025-09-17T00:00"), 48, 11, 23, fc_data_1
            ),
            OpenMeteoForecastDataPoint(
                parse("2025-09-18T00:00"), 48, 11, 23, fc_data_2
            ),
        ],
    ]
