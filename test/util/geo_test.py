import math

import pytest
from dateutil.parser import parse

from src.model.open_meteo import OpenMeteoForecast
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
    assert [d.isoformat()[:10] for d in fc.days] == ["2025-09-17"]
    assert fc.daylight_dur == [1.5]
    assert fc.sunshine_dur == [4.5]

    # Applies weights correctly
    fc = merge_forecasts(forecasts[:2], [3, 1])
    assert (fc.lat, fc.lon) == (48.25, 11.25)
    assert [d.isoformat()[:10] for d in fc.days] == ["2025-09-17"]
    assert fc.daylight_dur == [1.25]
    assert fc.sunshine_dur == [4.25]

    # Works for longer forecasts
    fc = merge_forecasts(forecasts[2:4], [1, 9])
    assert (round(fc.lat, 1), round(fc.lon, 1)) == (48.9, 11.9)
    assert [d.isoformat()[:10] for d in fc.days] == ["2025-09-18", "2025-09-19"]
    assert [round(v, 1) for v in fc.daylight_dur] == [2.8, 3.8]
    assert [round(v, 1) for v in fc.sunshine_dur] == [11.8, 12.8]

    # Rejects non-overlapping forecasts
    with pytest.raises(AssertionError):
        merge_forecasts(forecasts[-2:])


@pytest.fixture
def forecasts():
    return [
        OpenMeteoForecast(48, 11, [parse("2025-09-17")], {"daylight_duration": [1], "sunshine_duration": [4]}),
        OpenMeteoForecast(49, 12, [parse("2025-09-17")], {"daylight_duration": [2], "sunshine_duration": [5]}),
        OpenMeteoForecast(
            48,
            11,
            [parse("2025-09-18"), parse("2025-09-19")],
            {"daylight_duration": [1, 2], "sunshine_duration": [10, 11]},
        ),
        OpenMeteoForecast(
            49,
            12,
            [parse("2025-09-18"), parse("2025-09-19")],
            {"daylight_duration": [3, 4], "sunshine_duration": [12, 13]},
        ),
        OpenMeteoForecast(
            50,
            13,
            [parse("2025-09-20"), parse("2025-09-21")],
            {"daylight_duration": [3, 4], "sunshine_duration": [12, 13]},
        ),
    ]
