from typing import TypedDict


class GeoJsonBB(TypedDict):
    minLat: float
    maxLat: float
    minLon: float
    maxLon: float


class BBox:
    """A geographic bounding box delimited by southwest (min) and northeast (max) geo coordinates"""

    def __init__(self, min_lat: float, min_lon: float, max_lat: float, max_lon: float):
        assert min_lat >= -90 and min_lat <= 90, "Latitude must be within [-90, 90]"
        assert max_lat >= -90 and max_lat <= 90, "Latitude must be within [-90, 90]"
        assert min_lon >= -180 and min_lon <= 180, "Longitude must be within [-180, 180]"
        assert max_lon >= -180 and max_lon <= 180, "Longitude must be within [-180, 180]"
        assert max_lat > min_lat, "Max latitude must be greater than min latitude"
        assert max_lon > min_lon, "Max longitude must be greater than min longitude"

        self.min_lat = min_lat
        self.min_lon = min_lon
        self.max_lat = max_lat
        self.max_lon = max_lon
        self.lat_cnt = (max_lat + min_lat) / 2
        self.lon_cnt = (max_lon + min_lon) / 2

    def __repr__(self):
        return f"GeoBoundingBox ({self.min_lat}, {self.min_lon}) - ({self.max_lat}, {self.max_lon})"

    @property
    def weight(self):
        """Weighted area of this bounding box (in [0, 1e6])"""

        return (self.max_lon - self.min_lon) / 0.36 * (self.max_lat - self.min_lat) / 0.18

    @staticmethod
    def fromjson(data: GeoJsonBB):
        """Create a bounding box from GeoJSON data (has to contain { "minLat": ...} values')."""

        return BBox(data["minLat"], data["minLon"], data["maxLat"], data["maxLon"])
