import json
import os
from typing import NamedTuple

from src.model.forecast import Location
from src.model.geo import BBox, GeoJsonBB
from src.model.open_meteo import (
    ZERO_FC_DATA,
    OpenMeteoForecastData,
    OpenMeteoForecastDataPoint,
)
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
    forecasts: list[list[OpenMeteoForecastDataPoint]],
    weights: list[float] | None = None,
) -> list[OpenMeteoForecastDataPoint]:
    """Merges several OpenMeteo forecasts into one, using optional weights."""

    w = weights or [1.0 for x in forecasts]
    w = normalize(w)

    assert len(forecasts) > 1, "Merging requires at least 2 forecasts"
    assert len(forecasts) == len(w), "Number of forecasts and weights must match"
    for fc in forecasts[1:]:
        assert len(fc) == len(forecasts[0]), "Forecasts have different lengths"

    merged: list[OpenMeteoForecastDataPoint] = [
        OpenMeteoForecastDataPoint(dp.ts, 0, 0, 0, ZERO_FC_DATA) for dp in forecasts[0]
    ]
    for fcidx, fc in enumerate(forecasts):
        for dpidx, dp in enumerate(merged):
            assert dp.ts == fc[dpidx].ts
            dp.lat += fc[dpidx].lat * w[fcidx]
            dp.lon += fc[dpidx].lon * w[fcidx]
            dp.elev += fc[dpidx].elev * w[fcidx]
            for k in OpenMeteoForecastData.__annotations__:
                v = getattr(dp, k)
                setattr(dp, k, v + getattr(fc[dpidx], k) * w[fcidx])

    return merged
