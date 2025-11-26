<p align="center">
  <img width="128" align="center" src="data/assets/ic-epex-fc.png" alt="EPEX Spot Forecast Logo">
</p>

<h1 align="center">EPEX Spot Forecast</h1>

<p align="center">
  <img src="https://img.shields.io/badge/%F0%9F%90%8D_Python-gray" alt="Python">
  <img src="https://img.shields.io/badge/%F0%9F%A6%86_DuckDB-gray" alt="DuckDB">
  <img src="https://img.shields.io/badge/PyTorch-ee4c2c?logo=pytorch&logoColor=white">
  <img src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/klaasnotfound/38460a88beb57dcb08dc3a4ad0abba35/raw/covbadge.json" alt="Test coverage" />
</p>

## What

This repository showcases the prediction of next-day renewable electricity prices in Germany. It uses weather forecast and market data from publicly available sources.

## Why

The prediction of next-day electricity prices is, among others, relevant for the optimzation of battery energy storage systems (BESS), load balancing and profit maximization for solar power providers, from small home owners to utility-scale parks. Markets like the European power exchange spot market (EPEX Spot) provide an efficient mechanism to match short-term supply and demand, letting parties buy and sell electricity ad-hoc (intraday auction) or in advance (day-ahead auction).

## How

Unlike the stock market, where prices are driven by hidden signals and therefore hard to predict, renewable electricity output is strongly correlated with the amount of wind and sun available on a given day. This means that we should be able to use weather forecast data as a meaningful signal to predict renewable electricity prices.

## Data

### Sources

- EPEX Market data comes from the [energy-charts.info](https://energy-charts.info/) portal run by Fraunhofer ISE.
- Weather forecast data is sourced from the [OpenMeteo API](https://open-meteo.com/).

_Note_: Both APIs provide generous free tiers for non-commercial use and data for different geographic regions; we focus on Germany alone.

### Setup

If you would just like to see some prediction results, take a look at the `/notebooks` folder. To play around with the prediction yourself, you should clone this repository, load the Python virtual environment and install the dependencies:

```bash
git clone git@github.com:klaasnotfound/epex-spot-forecast.git
cd epex-spot-forecast
source venv/bin/activate
python3 -m pip install requirements.txt
```

### Scripts

Several scripts let you to download and merge data from the above sources. Data is stored in a local DuckDB, which is good for timeseries processing and translates seamlessly to Pandas dataframes. The scripts are executed with `python3 -m src.scripts.<script_name>`.

- `download_open_meteo_forecasts` - downloads hourly weather forecast data for a given year and all 16 German states. Edit the script at the bottom to download different years.
- `aggregate_forecasts` - merges all downloaded state forecasts into an average national forecast for Germany. This uses weights proportional to the installed wind and solar capacity in each state.
- `download_epex_data` - downloads hourly EPEX Spot market data for 2015 - 2025. You might not need that many years, edit the script at the bottom to your liking.

_Note_: Both download scripts provide a `reset` parameter, which - when `True` - will drop all data from the database prior to downloading. Fetching the weather data may take a while and you may see some slowdown due to rate limiting. As long as you use the data non-commercially and stay below 10k requests/day limit, you are within the limits of OpenMeteo's free tier and should be fine.

### Inspecting the data

DuckDB has a nice web-based UI viewer (which you have to [install separately](https://duckdb.org/docs/stable/core_extensions/ui)). To poke around the database you can invoke:

```bash
duckdb -ui
```

Once the web viewer is launched, go to "Attached dabases" and click on the "+" icon, then enter the absolute file path to the local DB, which will be something like `/<path_to_repo_parent>/epex-spot-forecast/data/db/local.db`. You can now browse tables and execute SQL queries. For example, to see all aggregated weather data from 2024 onward you would enter

```sql
SELECT *
FROM local.main.open_meteo_agg_hourly
WHERE open_meteo_agg_hourly.ts >= '2024-01-01'
ORDER BY open_meteo_agg_hourly.ts
```

which will give you something like this:

![Screenshot of DuckDB SQL tabel output](/data/assets//duckdb-ui-agg-data.png)

## Prediction

### Models

In the `/notebooks` folder, there are several Jupyter notebooks that walk you through the creation, training and evaluation of different prediction models:

- `lstm` - a long short-term memory ([LSTM](https://en.wikipedia.org/wiki/Long_short-term_memory)) model
- `gru` - a gated recurrent unit ([GRU](https://en.wikipedia.org/wiki/Gated_recurrent_unit)) model
- `chronos-2` - a 120M-parameter [foundation model](https://github.com/amazon-science/chronos-forecasting/) for one-shot time series forecasting developed by Amazon Science

### Features

The EPEX market data and the OpenMeteo weather data each contain several columns:

#### Market Data

| Column                  | Description                                        |
| ----------------------- | -------------------------------------------------- |
| `non_ren_prod_kw`       | Total non-renewable electricity production (in kW) |
| `ren_prod_kw`           | Total renewable electricity production (in kW)     |
| `load_kw`               | Load forecast (in kW)                              |
| `daa_price_eurmwh`      | Day-ahead auction price (in EUR/MWh)               |
| `idc_av_price_eurmwh`   | Intraday continuous average price (in EUR/MWh)     |
| `idc_low_price_eurmwh`  | Intraday continuous low price (in EUR/MWh)         |
| `idc_high_price_eurmwh` | Intraday continuous high price (in EUR/MWh)        |

#### Weather Forecast data

| Column                       | Description                                      |
| ---------------------------- | ------------------------------------------------ |
| temperature_2m_degc          | Air temperature 2m above ground (in °C)          |
| shortwave_radiation_wm2      | Shortwave solar radiation (in W/m²)              |
| direct_radiation_wm2         | Direct solar radiation (in W/m²)                 |
| diffuse_radiation_wm2        | Diffuse solar radiation (in W/m²)                |
| direct_normal_irradiance_wm2 | Direct solar normal irradiance (in W/m²)         |
| global_tilted_irradiance_wm2 | Global solar tilted irradiance (in W/m²)         |
| terrestrial_radiation_wm2    | Terrestrial solar radiation (in W/m²)            |
| cloud_cover_perc             | Total cloud cover as an area fraction (%)        |
| cloud_cover_low_perc         | Low level clouds and fog up to 3 km altitude (%) |
| cloud_cover_mid_perc         | Mid level clouds from 3 to 8 km altitude (%)     |
| cloud_cover_high_perc        | High level clouds from 8 km altitude (%)         |
| visibility_m                 | Viewing distance (in m)                          |
| wind_speed_10m_kmh           | Wind speed 10m above ground (in km/h)            |
| wind_speed_80m_kmh           | Wind speed 80m above ground (in km/h)            |
| wind_speed_120m_kmh          | Wind speed 120m above ground (in km/h)           |

_Note_: There are [many more variables available](https://open-meteo.com/en/docs) in the OpenMeteo API; these were the ones deemed to have a potential influence on solar and wind output. The global tilted irradiance is queried with an azimuth of 0° (facing south) and a tilt of of 35°, which is the recommended configuration for utility-scale solar farms in Germany.

### Miscellaneous

The day-ahead auction already presents a _very_ good guess of what electricity should realistically cost during a given time on the next day. Until noon each day, market participants can enter their bid for one-hour intervals on the next day¹. Market participants are aware of the weather forecast, too, and include this data along with their

¹ <small>Technically, bids can be for 15-minute intervals, but we'll stick to a 1-hour resolution for this analysis.</small>
