import duckdb
import pytest

from src.model.energy_charts import EpexMarketData, EpexMarketDataPoint


def test_init(em_data_1):
    # Rejects invalid values
    with pytest.raises(AssertionError):
        EpexMarketDataPoint(-4, em_data_1)

    # Works as expected
    dp = EpexMarketDataPoint(1757887200000, vals=em_data_1)
    assert dp.ts == 1757887200000
    assert round(getattr(dp, "ren_prod_kw"), 1) == 34853.0
    assert round(getattr(dp, "idc_av_price_eurmwh"), 1) == 25.5


def test_repr(em_data_1):
    mdp = EpexMarketDataPoint(1757887200000, vals=em_data_1)
    assert f"{mdp}" == "EpexData: (1757887200000) 25.46 EUR/MWh"


def test_init_table():
    con = duckdb.connect(":memory:")
    EpexMarketDataPoint.init_table(con)
    assert "epex_market" in f"{con.sql('SHOW ALL TABLES')}"
    assert [(0,)] == con.sql("SELECT count(*) FROM epex_market").fetchall()


def test_upsert_many(em_data_1, em_data_2):
    con = duckdb.connect(":memory:")
    EpexMarketDataPoint.init_table(con)
    assert [(0,)] == con.sql("SELECT count(*) FROM epex_market").fetchall()
    dp1 = EpexMarketDataPoint(1757887200000, vals=em_data_1)
    dp2 = EpexMarketDataPoint(1757890800000, vals=em_data_2)
    EpexMarketDataPoint.upsert_many([dp1, dp2], con)
    stmt = "SELECT count(*) FROM epex_market WHERE ts >= '2025-09-15'"
    assert [(2,)] == con.sql(stmt).fetchall()


@pytest.fixture
def em_data_1() -> EpexMarketData:
    return {
        "pumped_hydro_cons_kw": -2308.715000442213,
        "x_border_trading_kw": 1598.17975,
        "non_ren_prod_kw": 6688.0012926017225,
        "ren_prod_kw": 34852.981094802555,
        "load_kw": 40733.5475,
        "daa_price_eurmwh": 20.0,
        "idc_av_price_eurmwh": 25.46,
        "idc_low_price_eurmwh": -4.05,
        "idc_high_price_eurmwh": 41.89,
    }


@pytest.fixture
def em_data_2() -> EpexMarketData:
    return {
        "pumped_hydro_cons_kw": -2858.682500547554,
        "x_border_trading_kw": -1485.3804999999998,
        "non_ren_prod_kw": 6299.789802914948,
        "ren_prod_kw": 37540.08954645315,
        "load_kw": 39468.7825,
        "daa_price_eurmwh": 3.87,
        "idc_av_price_eurmwh": 16.76,
        "idc_low_price_eurmwh": 2.27,
        "idc_high_price_eurmwh": 64.57,
    }
