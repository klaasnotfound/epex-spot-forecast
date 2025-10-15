import pytest

from src.model.geo import BBox


def test_init():
    # Rejects invalid values
    with pytest.raises(AssertionError):
        BBox(-100, 0, 0, 0)
    with pytest.raises(AssertionError):
        BBox(100, 0, 0, 0)
    with pytest.raises(AssertionError):
        BBox(0, -200, 0, 0)
    with pytest.raises(AssertionError):
        BBox(0, 200, 0, 0)
    with pytest.raises(AssertionError):
        BBox(0, 0, -100, 0)
    with pytest.raises(AssertionError):
        BBox(0, 0, 100, 0)
    with pytest.raises(AssertionError):
        BBox(0, 0, 0, -200)
    with pytest.raises(AssertionError):
        BBox(0, 0, 0, 200)
    with pytest.raises(AssertionError):
        BBox(45, 0, -45, 0)
    with pytest.raises(AssertionError):
        BBox(-10, 45, 10, -45)
    with pytest.raises(AssertionError):
        BBox(0, 0, 0, 0)

    # Works as expected
    bb = BBox(-90, -90, 90, 90)
    assert (bb.lon_cnt, bb.lat_cnt) == (0, 0)
    assert bb.weight == 5e5


def test_repr():
    bb = BBox(-90, -90, 90, 90)
    assert f"{bb}" == "GeoBoundingBox (-90, -90) - (90, 90)"


def test_fromjson(json_data):
    bb = BBox.fromjson(json_data)
    assert bb.min_lat == 47.2703623267
    assert bb.max_lon == 13.8350427083


@pytest.fixture
def json_data():
    return {
        "minLat": 47.2703623267,
        "maxLat": 50.5644529365,
        "minLon": 8.9771580802,
        "maxLon": 13.8350427083,
    }
