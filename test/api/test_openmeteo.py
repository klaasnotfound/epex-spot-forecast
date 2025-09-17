import pytest

from src.api.open_meteo import get_forecast, get_forecasts
from src.util.geo import LatLon


@pytest.mark.vcr
def test_get_forecast():
    fc = get_forecast(52.52, 13.41)
    assert (fc.lat, fc.lon) == (52.52, 13.419998)
    assert [d.isoformat()[:10] for d in fc.days[:2]] == ["2025-09-17", "2025-09-18"]
    assert fc.daylight_dur[:2] == [45132.20, 44888.03]
    assert fc.sunshine_dur[:2] == [29070.21, 0.00]


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
    assert [d.isoformat()[:10] for d in fcs[0].days[:2]] == ["2025-09-17", "2025-09-18"]
    assert [d.isoformat()[:10] for d in fcs[1].days[:2]] == ["2025-09-17", "2025-09-18"]
    assert [d.isoformat()[:10] for d in fcs[2].days[:2]] == ["2025-09-17", "2025-09-18"]
    assert (fcs[0].lat, fcs[0].lon) == (48.66, 9)
    assert (fcs[1].lat, fcs[1].lon) == (48.92, 11.4)
    assert (fcs[2].lat, fcs[2].lon) == (52.5, 13.419998)
