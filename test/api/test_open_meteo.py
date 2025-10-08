import pytest

from src.api.open_meteo import get_forecast, get_forecasts
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
    assert [d.isoformat()[:16] for d in fcs[0].times[:2]] == [
        "2025-10-08T00:00",
        "2025-10-08T01:00",
    ]
    assert [d.isoformat()[:16] for d in fcs[1].times[:2]] == [
        "2025-10-08T00:00",
        "2025-10-08T01:00",
    ]
    assert [d.isoformat()[:16] for d in fcs[2].times[:2]] == [
        "2025-10-08T00:00",
        "2025-10-08T01:00",
    ]
    assert (fcs[0].lat, fcs[0].lon) == (48.66, 9)
    assert (fcs[1].lat, fcs[1].lon) == (48.92, 11.4)
    assert (fcs[2].lat, fcs[2].lon) == (52.5, 13.419998)
