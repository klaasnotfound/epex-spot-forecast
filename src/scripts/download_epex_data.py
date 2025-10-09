from datetime import datetime

import src.util.log as log
from src.api.energy_charts import get_weekly_market_data
from src.model.energy_charts import EpexMarketDataPoint
from src.util.db import get_db_connection


def download_data(reset=False, year=datetime.now().year):
    log.msg("Download EPEX spot data")

    con = get_db_connection()
    if reset:
        EpexMarketDataPoint.init_table(con)
    curr_year = datetime.now().year
    curr_week = datetime.now().isocalendar().week
    to_week = curr_week if year == curr_year else 53
    weeks = range(1, to_week)
    for week in weeks:
        data = get_weekly_market_data(year, week)
        EpexMarketDataPoint.upsert_many(data, con)
        log.info(f"{year}-{week:02d}: {len(data)} data points", " ✓")

    log.success("Done")


if __name__ == "__main__":
    for year in range(2015, 2025):
        log.msg(f"--- YEAR: {year} ---")
        download_data(year=year)
        log.msg("")
