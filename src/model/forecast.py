class Location:
    def __init__(self, name: str, lat: float, lon: float, weight=1.0):
        assert len(name) > 0, "Name must not be empty"
        assert lat >= -90 and lat <= 90, "Latitude must be within [-90, 90]"
        assert lon >= -180 and lon <= 180, "Longitude must be within [-180, 180]"
        assert weight > 0, "Weight must be > 0"

        self.name = name
        self.lat = lat
        self.lon = lon
        self.weight = weight

    def __repr__(self):
        return f"ForecastLocation '{self.name}' ({self.lat:.6f}, {self.lon:.6f}) W: {self.weight:.2f}"
