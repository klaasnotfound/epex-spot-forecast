from calendar import monthrange
from datetime import datetime

from dateutil.parser import parse

import src.util.log as log
from src.api.open_meteo import get_historical_forecast
from src.model.open_meteo import OpenMeteoForecastDataPoint
from src.util.db import get_db_connection
from src.util.geo import get_german_states


def download_data(reset=False, year=datetime.now().year):
    log.msg("Download OpenMeteo weather forecasts")

    con = get_db_connection()
    if reset:
        OpenMeteoForecastDataPoint.init_table(con)

    states = get_german_states()

    curr_year = datetime.now().year
    curr_month = datetime.now().month
    to_month = curr_month if year == curr_year else 13
    months = range(1, to_month)
    for state in states:
        for month in months:
            num_days = monthrange(year, month)[1]
            start = parse(f"{year}-{month}-01")
            end = parse(f"{year}-{month}-{num_days}")
            stmt = f"""
                SELECT count(*)
                FROM open_meteo_hourly
                WHERE ts >= '{start.isoformat()[:10]}' AND ts <= '{end.isoformat()[:10]}'
                  AND lat >= {(state.lat - 0.1):6f} AND lat <= {(state.lat + 0.1):6f}
                  AND lon >= {(state.lon - 0.1):6f} AND lon <= {(state.lon + 0.1):6f}
            """
            res = con.sql(stmt).fetchall()
            if res[0][0] >= (num_days - 1) * 24:
                log.info(
                    f"{year}-{month:02d}: up to date",
                    " ✓",
                    f" → [{state.name}]",
                )
                continue
            data = get_historical_forecast(state.lat, state.lon, start, end)
            OpenMeteoForecastDataPoint.upsert_many(data, con)
            log.info(
                f"{year}-{month:02d}: {len(data)} data points",
                " ✓",
                f" → [{state.name}]",
            )

    log.success("Done")


if __name__ == "__main__":
    download_data(year=2021)
