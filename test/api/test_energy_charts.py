import pytest

from src.api.energy_charts import get_weekly_market_data


@pytest.mark.vcr
def test_get_weekly_market_data():
    # Rejects invalid input
    with pytest.raises(AssertionError):
        get_weekly_market_data(-1999, 1)
    with pytest.raises(AssertionError):
        get_weekly_market_data(2026, 1)
    with pytest.raises(AssertionError):
        get_weekly_market_data(2024, -1)
    with pytest.raises(AssertionError):
        get_weekly_market_data(2024, 53)

    # Works as expected
    md = get_weekly_market_data(2024, 1)
    assert len(md) == 7 * 24
