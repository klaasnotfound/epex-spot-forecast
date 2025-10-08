import json
import os
from typing import NamedTuple

from src.model.forecast import Location
from src.model.geo import BBox, GeoJsonBB
from src.model.open_meteo import OpenMeteoForecast, OpenMeteoValues
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
    times = forecasts[0].times
    hourSet = set(times)
    vals: dict[str, list[float]] = {}
    for k in OpenMeteoValues.__annotations__:
        vals[k] = [0.0 for x in getattr(forecasts[0], k)]

    for fcidx, fc in enumerate(forecasts):
        mlat += fc.lat * w[fcidx]
        mlon += fc.lon * w[fcidx]
        for didx, d in enumerate(fc.times):
            assert d in hourSet, "Forecasts have mismatching hours"
            for k in OpenMeteoValues.__annotations__:
                vals[k][didx] += getattr(fc, k)[didx] * w[fcidx]

    return OpenMeteoForecast(mlat, mlon, times, OpenMeteoValues(**vals))
