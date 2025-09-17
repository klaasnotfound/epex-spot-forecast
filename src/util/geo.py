import json
import os
from typing import NamedTuple

from src.model.forecast import Location
from src.model.geo import BBox, GeoJsonBB
from src.model.open_meteo import OpenMeteoForecast
from src.util.math import normalize

data_dir = os.path.normpath(f"{__file__}/../../../data")
bbox_filepath = f"{data_dir}/geo/german-states-bbox.json"


LatLon = NamedTuple("LatLon", [("lat", float), ("lon", float)])


def get_german_states() -> list[Location]:
    """Return a list of forecast locations, one for every German state."""

    states: list[Location] = []
    with open(bbox_filepath) as f:
        data: dict[str, GeoJsonBB] = json.load(f)
        for key in data:
            bb = BBox.fromjson(data[key])
            states.append(Location(key, bb.lat_cnt, bb.lon_cnt, bb.weight))

    return states


def merge_forecasts(
    forecasts: list[OpenMeteoForecast], weights: list[float] | None = None
) -> OpenMeteoForecast:
    """Merges several OpenMeteo forecasts into one, using optional weights."""

    w = weights or [1.0 for x in forecasts]
    w = normalize(w)

    assert len(forecasts) > 1, "Merging requires at least 2 forecasts"
    assert len(forecasts) == len(w), "Number of forecasts and weights must match"

    mlat = 0.0
    mlon = 0.0
    days = forecasts[0].days
    daySet = set(days)
    dld = [0.0 for x in forecasts[0].daylight_dur]
    ssd = [0.0 for x in forecasts[0].sunshine_dur]

    for fcidx, fc in enumerate(forecasts):
        mlat += fc.lat * w[fcidx]
        mlon += fc.lon * w[fcidx]
        for didx, d in enumerate(fc.days):
            assert d in daySet, "Forecasts have mismatching days"
            dld[didx] += fc.daylight_dur[didx] * w[fcidx]
            ssd[didx] += fc.sunshine_dur[didx] * w[fcidx]

    return OpenMeteoForecast(
        mlat,
        mlon,
        days,
        {
            "daylight_duration": dld,
            "sunshine_duration": ssd,
        },
    )
