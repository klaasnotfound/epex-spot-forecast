import pytest
from dateutil.parser import parse

from src.model.open_meteo import OpenMeteoForecast


def test_init():
    # Rejects invalid values
    with pytest.raises(AssertionError):
        OpenMeteoForecast(
            -100, 0, [], {"daylight_duration": [], "sunshine_duration": []}
        )
    with pytest.raises(AssertionError):
        OpenMeteoForecast(
            100, 0, [], {"daylight_duration": [], "sunshine_duration": []}
        )
    with pytest.raises(AssertionError):
        OpenMeteoForecast(
            0, -200, [], {"daylight_duration": [], "sunshine_duration": []}
        )
    with pytest.raises(AssertionError):
        OpenMeteoForecast(
            0, 200, [], {"daylight_duration": [], "sunshine_duration": []}
        )
    with pytest.raises(AssertionError):
        OpenMeteoForecast(0, 0, [], {"sunshine_duration": []})
    with pytest.raises(AssertionError):
        OpenMeteoForecast(0, 0, [], {"daylight_duration": []})
    with pytest.raises(AssertionError):
        OpenMeteoForecast(0, 0, [], {"daylight_duration": [], "sunshine_duration": []})
    with pytest.raises(AssertionError):
        OpenMeteoForecast(
            0,
            0,
            [parse("2025-09-17")],
            {"daylight_duration": [], "sunshine_duration": []},
        )
    with pytest.raises(AssertionError):
        OpenMeteoForecast(
            0,
            0,
            [parse("2025-09-17")],
            {"daylight_duration": [1], "sunshine_duration": []},
        )

    # Works as expected
    fc = OpenMeteoForecast(
        0,
        0,
        [
            parse("2025-09-17"),
            parse("2025-09-18"),
            parse("2025-09-19"),
        ],
        {"daylight_duration": [1, 2, 3], "sunshine_duration": [4, 5, 6]},
    )
    assert (fc.lat, fc.lon) == (0, 0)
    assert [d.isoformat()[:10] for d in fc.days] == [
        "2025-09-17",
        "2025-09-18",
        "2025-09-19",
    ]
    assert fc.daylight_dur == [1, 2, 3]
    assert fc.sunshine_dur == [4, 5, 6]


def test_repr():
    fc = OpenMeteoForecast(
        45,
        30,
        [parse("2025-09-19")],
        {"daylight_duration": [1], "sunshine_duration": [4]},
    )
    assert f"{fc}" == "OpenMeteoForecast (45, 30) [1 day]"
    fc = OpenMeteoForecast(
        45,
        30,
        [parse("2025-09-19"), parse("2025-09-20")],
        {"daylight_duration": [1, 2], "sunshine_duration": [4, 5]},
    )
    assert f"{fc}" == "OpenMeteoForecast (45, 30) [2 days]"


def test_fromjson(json_data):
    fc = OpenMeteoForecast.fromjson(json_data)
    assert (fc.lat, fc.lon) == (52.52, 13.419998)
    assert [d.isoformat()[:10] for d in fc.days[:2]] == ["2025-09-16", "2025-09-17"]
    assert fc.daylight_dur[:2] == [45397.04, 45152.57]
    assert fc.sunshine_dur[:2] == [8741.57, 30228.32]


@pytest.fixture
def json_data():
    return {
        "latitude": 52.52,
        "longitude": 13.419998,
        "generationtime_ms": 0.10371208190918,
        "utc_offset_seconds": 7200,
        "timezone": "Europe/Berlin",
        "timezone_abbreviation": "GMT+2",
        "elevation": 38,
        "daily_units": {
            "time": "iso8601",
            "daylight_duration": "s",
            "sunshine_duration": "s",
        },
        "daily": {
            "time": [
                "2025-09-16",
                "2025-09-17",
                "2025-09-18",
                "2025-09-19",
                "2025-09-20",
                "2025-09-21",
                "2025-09-22",
            ],
            "daylight_duration": [
                45397.04,
                45152.57,
                44908.36,
                44664.55,
                44421.27,
                44178.66,
                43936.83,
            ],
            "sunshine_duration": [
                8741.57,
                30228.32,
                134.59,
                36776.93,
                37313.67,
                38041.49,
                21572.05,
            ],
        },
    }
