from datetime import date
from typing import NotRequired, TypedDict

import requests

from src.model.energy_charts import ApiMarketData, EpexMarketData, EpexMarketDataPoint


def get_weekly_market_data(year: int, week: int) -> list[EpexMarketDataPoint]:
    """Fetch weekly EPEX spot market data from energy-charts.info"""

    cur_year = date.today().year
    assert year >= 1990 and year <= cur_year, f"Year must be in [{1990}, {cur_year}]"
    assert week >= 1 and week <= 52, "Week must be in [1, 52]"

    url = f"https://energy-charts.info/charts/price_spot_market/data/de/week_{year}_{week:02d}.json"
    res = requests.get(url)
    res.raise_for_status()
    data: list[ApiMarketData] = res.json()

    class TimeSeriesRef(TypedDict):
        q: str
        d: NotRequired[ApiMarketData]

    time_series: dict[str, TimeSeriesRef] = {
        "phc": {"q": "pumped storage"},
        "xbt": {"q": "Cross border"},
        "nrp": {"q": "Non-Renewable"},
        "rp": {"q": "Renewable"},
        "l": {"q": "Load"},
        "dap": {"q": "Day Ahead"},
        "ida": {"q": "Intraday Continuous Average"},
        "idl": {"q": "Intraday Continuous Low"},
        "idh": {"q": "Intraday Continuous High"},
        "id3": {"q": "Intraday Continuous ID3"},
        "id1": {"q": "Intraday Continuous ID1"},
    }
    times: list[int] = []

    for d in data:
        if "xAxisValues" in d:
            times = d["xAxisValues"]
        name = d["name"][0]["en"] if isinstance(d["name"], list) else d["name"]["en"]
        for key in time_series:
            if time_series[key]["q"] in name:
                time_series[key]["d"] = d["data"]

    assert len(times) > 0, "Data is missing time axis"
    for k in time_series:
        assert len(time_series[k]["d"]) == len(times), (
            "Y and X values have different dimensions"
        )

    wmd: list[EpexMarketDataPoint] = []
    for idx, t in enumerate(times):
        wmd.append(
            EpexMarketDataPoint(
                t,
                EpexMarketData(
                    pumped_hydro_cons_kw=time_series["phc"]["d"][idx],
                    x_border_trading_kw=time_series["xbt"]["d"][idx],
                    non_ren_prod_kw=time_series["nrp"]["d"][idx],
                    ren_prod_kw=time_series["rp"]["d"][idx],
                    load_kw=time_series["l"]["d"][idx],
                    daa_price_eurmwh=time_series["dap"]["d"][idx],
                    idc_av_price_eurmwh=time_series["ida"]["d"][idx],
                    idc_low_price_eurmwh=time_series["idl"]["d"][idx],
                    idc_high_price_eurmwh=time_series["idh"]["d"][idx],
                    idc_id3_price_eurmwh=time_series["id3"]["d"][idx],
                    idc_id1_price_eurmwh=time_series["id1"]["d"][idx],
                ),
            )
        )

    return wmd
