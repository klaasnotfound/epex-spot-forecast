from typing import NotRequired, TypedDict, Union

from duckdb import DuckDBPyConnection
from duckdb.typing import DuckDBPyType

from src.model.persistable import Persistable


class ApiI18nName(TypedDict):
    en: str
    de: str
    fr: str
    it: str
    es: str


class ApiMarketData(TypedDict):
    name: Union[ApiI18nName, list[ApiI18nName]]
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
    idc_id3_price_eurmwh: float
    idc_id1_price_eurmwh: float


class EpexMarketDataPoint(Persistable):
    """EPEX spot market price with associated power production info"""

    def __init__(self, ts: int, vals: EpexMarketData):
        assert ts > 0, "Timestamp must be > 0"

        self.ts = ts
        attrs = EpexMarketData.__annotations__
        for attr in attrs:
            setattr(self, attr, vals[attr])

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
            ts TIMESTAMP_S,
            {col_str}
        );
        """
        con.execute(stmt)

    def __repr__(self):
        return f"EpexData: ({self.ts}) {self.idc_av_price_eurmwh:.2f} EUR/MWh"
