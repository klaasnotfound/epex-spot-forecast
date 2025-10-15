import src.util.log as log
from src.model.open_meteo import OpenMeteoForecastData, OpenMeteoForecastDataPoint
from src.util.db import get_db_connection
from src.util.geo import get_german_states, merge_forecasts

TBL_NAME = "open_meteo_agg_hourly"


def aggregate_forecasts():
    states = get_german_states()
    log.msg(f"Aggregate forecasts for {len(states)} German states")

    log.info(f"Init DB table '{TBL_NAME}'")
    con = get_db_connection()
    OpenMeteoForecastDataPoint.init_table(con, TBL_NAME)

    [(start, end)] = con.sql(
        "SELECT MIN(ts), MAX(ts) FROM open_meteo_hourly"
    ).fetchall()
    start_year = max(2022, start.year)  # We have None values before 2022
    end_year = end.year
    for year in range(start_year, end_year + 1):
        log.info(f"Merging forecasts in {year}")
        forecasts: list[list[OpenMeteoForecastDataPoint]] = []
        for state in states:
            stmt = f"""
                SELECT *
                FROM open_meteo_hourly
                WHERE ts >= '{year}-01-01' AND ts < '{year + 1}-01-01'
                  AND lat >= {(state.lat - 0.1):6f} AND lat <= {(state.lat + 0.1):6f}
                  AND lon >= {(state.lon - 0.1):6f} AND lon <= {(state.lon + 0.1):6f}
                ORDER BY ts
            """
            res = con.sql(stmt).fetchall()
            points: list[OpenMeteoForecastDataPoint] = []
            for row in res:
                (ts, lat, lon, elev, *vals) = row
                d = OpenMeteoForecastData(
                    **dict(zip(OpenMeteoForecastData.__annotations__.keys(), vals))
                )
                dp = OpenMeteoForecastDataPoint(ts, lat, lon, elev, d)
                points.append(dp)
            forecasts.append(points)
        merged = merge_forecasts(forecasts, [s.weight for s in states])
        OpenMeteoForecastDataPoint.upsert_many(merged, con, TBL_NAME)

    log.success("Done")


if __name__ == "__main__":
    aggregate_forecasts()
