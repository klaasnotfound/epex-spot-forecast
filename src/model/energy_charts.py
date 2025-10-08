import calendar
import time
from typing import NotRequired, TypedDict

from duckdb import DuckDBPyConnection
from duckdb.typing import DuckDBPyType


class ApiI18nName(TypedDict):
    en: str
    de: str
    fr: str
    it: str
    es: str


class ApiMarketData(TypedDict):
    name: ApiI18nName | list[ApiI18nName]
    data: list[float]
    xAxisValues: NotRequired[list[int]]


class EpexMarketData(TypedDict):
    pumped_hydro_cons_kw: float
    x_border_trading_kw: float
    non_ren_prod_kw: float
    ren_prod_kw: float
    load_kw: float
    daa_price_eurmwh: float
    idc_av_price_eurmwh: float
    idc_low_price_eurmwh: float
    idc_high_price_eurmwh: float


class EpexMarketDataPoint:
    """EPEX spot market price with associated power production info"""

    def __init__(self, ts: int, vals: EpexMarketData):
        assert ts > 0, "Timestamp must be > 0"

        self.ts = ts
        for attr in EpexMarketData.__annotations__:
            setattr(self, attr, vals[attr])

    def __repr__(self):
        return (
            f"EpexData: ({self.ts}) {getattr(self, 'idc_av_price_eurmwh'):.2f} EUR/MWh"
        )

    @staticmethod
    def init_table(con: DuckDBPyConnection):
        col_str = ", ".join(
            [
                f"{k} {DuckDBPyType(v)}"
                for k, v in EpexMarketData.__annotations__.items()
            ]
        )
        stmt = f"""
        CREATE OR REPLACE TABLE epex_market (
            ts TIMESTAMP_MS PRIMARY KEY,
            {col_str}
        );
        """
        con.execute(stmt)

    @staticmethod
    def upsert_many(data: list["EpexMarketDataPoint"], con: DuckDBPyConnection):
        val_str = (
            "("
            + "), (".join(
                [
                    f"make_timestamp_ms({round(calendar.timegm(time.localtime(d.ts / 1e3)) * 1e3)}), "
                    + ", ".join(
                        [f"{getattr(d, k)}" for k in EpexMarketData.__annotations__]
                    ).replace("None", "NULL")
                    for d in data
                ]
            )
            + ")"
        )
        stmt = f"""
        INSERT OR IGNORE INTO epex_market VALUES
        {val_str};
        """
        con.execute(stmt)
