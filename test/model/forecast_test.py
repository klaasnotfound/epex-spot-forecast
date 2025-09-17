import pytest

from src.model.forecast import Location


def test_init():
    # Rejects invalid values
    with pytest.raises(AssertionError):
        Location("", 0, 0)
    with pytest.raises(AssertionError):
        Location("Neverland", -100, 0)
    with pytest.raises(AssertionError):
        Location("Neverland", 100, 0)
    with pytest.raises(AssertionError):
        Location("Neverland", 0, -200)
    with pytest.raises(AssertionError):
        Location("Neverland", 0, 200)

    # Works as expected
    loc = Location("Bavaria", 48.60359999365066, 11.477256502649954, 26.8)
    assert loc.name == "Bavaria"
    assert loc.lat == 48.60359999365066
    assert loc.lon == 11.477256502649954
    assert loc.weight == 26.8


def test_repr():
    loc = Location("Bavaria", 48.60359999365066, 11.477256502649954, 26.8)
    assert f"{loc}" == "ForecastLocation 'Bavaria' (48.603600, 11.477257) W: 26.80"
