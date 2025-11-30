<p align="center">
  <img width="128" align="center" src="data/assets/ic-epex-fc.png" alt="EPEX Spot Forecast Logo">
</p>

<h1 align="center">EPEX Spot Forecast</h1>

<p align="center">
  <img src="https://img.shields.io/badge/%F0%9F%90%8D_Python-gray" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-ee4c2c?logo=pytorch&logoColor=white">
  <img src="https://img.shields.io/badge/%F0%9F%A6%86_DuckDB-gray" alt="DuckDB">
  <a href="https://github.com/klaasnotfound/epex-spot-forecast/actions">
  <img src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/klaasnotfound/38460a88beb57dcb08dc3a4ad0abba35/raw/covbadge.json" alt="Test coverage" />
  </a>
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

_Note_: Both APIs provide generous free tiers for non-commercial use and data for different geographic regions. Here, we focus on Germany alone.

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

_Note_: Both download scripts provide a `reset` parameter, which - when `True` - will drop the corresponding table from the database prior to downloading. Fetching the weather data may take a while and you may see some slowdown due to rate limiting. As long as you use the data non-commercially and stay below the 10k requests/day limit, you are within the limits of OpenMeteo's free tier and should be fine.

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

which will give you something like:

![Screenshot of DuckDB SQL tabel output](/data/assets/img-duckdb-ui-agg-data.png)

## Prediction

### Objective

Our objective is to predict the intraday electricity prices of the next day, i.e. the hourly price parties are willing to pay for electricity on short notice. It's important to understand that the day-ahead auction price already represents a _very good guess_ of what electricity will realistically cost during a given time on the next day. Until noon each day, market participants can enter their bid for one-hour intervals on the next day¹. These bids factor in all information available at that time, including knowledge about the weather forecast, next-day generation capacity and the bidders' individual urgency to procure the requested load. Bids are aggregated and the final price is calculated automatically by [the intersection of supply and demand curves](https://en.wikipedia.org/wiki/European_Power_Exchange#Day-ahead_markets).

¹ <small>Technically, bids can be for 15-minute intervals, but we'll stick to a 1-hour resolution for this analysis.</small>

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

## Results

### Baseline

The average absolute difference between the day-ahead price and the intraday price for the test period is `12.78 EUR`. That is to say: If you used yesterday's day-ahead price as the predictor, you would miss the intraday price by an average of `12.78 EUR`. These misses vary wildly - sometimes they're too high, sometimes too low, with a standard deviation of `33.99 EUR`. As an example, here are three days from March 2025:

![Plot of the intraday price for two days in March 2025, overlayed with the previous day's day-ahead price](/data/assets/img-price-pred-01.png)

### Blended Price

The predictions from the trained long short-term memory model (as well as the gated recurrent unit model) capture the general intraday price movements well, but fail to be more accurate than the day-ahead price from the previous day. Here are 7 days from March 2025:

![Plot of the intraday price for two days in March 2025, overlayed with the previous day's day-ahead price and the price predicted by an LSTM](/data/assets/img-price-pred-02.png)

A possible reason for this is that the electricity price is not just influenced by "regular" weather-induced supply and demand, but also by bulk bids from individual market participants with over- or undersupply (e.g. when charging/discharging pumped hydro storage). These factors are known to the bidding parties and influence the day-ahead auction price but are not visible in the weather forecast or previous-day market data.

Visual inspection of the data revealed something interesting: More often than not, the predicted prices and the day-ahead prices seemed to be on opposite sides of the intraday price. The day-ahead auction (DAA) price was generally "more correct", but the question was whether "blending in" a bit of the model prediction would yield an improved estimate. Defining the blended price as

$$p_{blend} = \gamma \cdot p_{pred} + (1-\gamma) \cdot p_{daa}$$

and iterating over different $\gamma \in [0, 1]$ confirmed this assumption: A blend factor of $\gamma$ = `0.2` yielded maximum improvement (and this remained stable across different configurations and runs of the LSTM and GRU models). The model performance presented in the following is therefore not evaluted on the predicted price but on the _blended price_ (with $\gamma$ = `0.2` ).

<details>
<summary>
<h3>LSTM</h3>
</summary>

The performance of different LSTM configurations (differing in the `num_layers` and `hidden_size`), averaged over 5 runs, is:

| # Layers | Hidden Size | # Params | Ø Diff Pred. (EUR) | Ø Diff Blended (EUR) | Improvement (EUR) |
| -------- | ----------- | -------- | ------------------ | -------------------- | ----------------- |
| 2        | 64          | 58161    | 20.73              | 12.03                | 0.75              |
| `3`      | `64`        | `91441`  | `20.85`            | `11.91`              | `0.88`            |
| 4        | 64          | 124721   | 20.82              | 12.05                | 0.73              |
| 2        | 96          | 125633   | 20.99              | 11.94                | 0.84              |
| 3        | 96          | 200129   | 20.79              | 11.97                | 0.81              |
| 4        | 96          | 274625   | 20.98              | 12.06                | 0.73              |
| 2        | 128         | 218705   | 20.93              | 12.07                | 0.71              |
| 3        | 128         | 350801   | 21.17              | 12.10                | 0.68              |
| 4        | 128         | 482897   | 20.53              | 12.00                | 0.78              |
| 2        | 192         | 481649   | 20.78              | 12.01                | 0.77              |
| 3        | 192         | 778097   | 21.05              | 12.04                | 0.74              |
| 4        | 192         | 1074545  | 21.38              | 12.08                | 0.70              |
| 2        | 256         | 846993   | 20.67              | 11.99                | 0.79              |
| 3        | 256         | 1373329  | 21.26              | 12.01                | 0.77              |
| 4        | 256         | 1899665  | 21.40              | 12.10                | 0.69              |
| 2        | 384         | 1884881  | 20.69              | 12.00                | 0.79              |
| 3        | 384         | 3067601  | 21.22              | 12.11                | 0.67              |
| 4        | 384         | 4250321  | 21.43              | 12.09                | 0.69              |

The best performance was achieved by a 3-layer LSTM with 64 hidden units per layer. On average, the blended predictions are `0.88 EUR` better than the day-ahead auction price. What's more is that the standard deviation of the absolute differences (between blended and intraday price) is `13.44 EUR` (a `20.54 EUR` improvement over the day-ahead difference standard deviation). In other words, the blended predictions tend to over- and undershoot the intraday price way less than the day-ahead auction price.

</details>

<details>
<summary>
<h3>GRU</h3>
</summary>

Training the GRU model took significantly longer than the LSTM model and yielded basically the same results.

| # Layers | Hidden Size | # Params | Ø Diff Pred. (EUR) | Ø Diff Blended (EUR) | Improvement (EUR) |
| -------- | ----------- | -------- | ------------------ | -------------------- | ----------------- |
| 2        | 64          | 44209    | 20.65              | 11.96                | 0.82              |
| 3        | 64          | 69169    | 20.74              | 11.96                | 0.82              |
| 4        | 64          | 94129    | 20.72              | 11.99                | 0.79              |
| 2        | 96          | 95489    | 20.39              | 11.94                | 0.84              |
| 3        | 96          | 151361   | 20.81              | 12.00                | 0.78              |
| 4        | 96          | 207233   | 20.78              | 11.92                | 0.86              |
| `2`      | `128`       | `166225` | `20.72`            | `11.91`              | `0.87`            |
| 3        | 128         | 265297   | 21.11              | 12.06                | 0.72              |
| 4        | 128         | 364369   | 20.91              | 12.00                | 0.78              |
| 2        | 192         | 366065   | 21.13              | 11.98                | 0.80              |
| 3        | 192         | 588401   | 21.13              | 12.03                | 0.75              |
| 4        | 192         | 810737   | 20.98              | 11.98                | 0.80              |
| 2        | 256         | 643729   | 21.57              | 12.03                | 0.75              |
| 3        | 256         | 1038481  | 21.24              | 12.10                | 0.68              |
| 4        | 256         | 1433233  | 21.13              | 11.91                | 0.87              |
| 2        | 384         | 1432529  | 21.71              | 12.15                | 0.63              |
| 3        | 384         | 2319569  | 21.77              | 12.14                | 0.64              |
| 4        | 384         | 3206609  | 21.40              | 12.08                | 0.70              |

The best performance was achieved by a 2-layer GRU with 128 hidden units per layer. On average, blended GRU price predictions were `0.87 EUR` closer to the intraday price than the day-ahead price, the standard deviation was `13.42 EUR` (an improvement of `20.56 EUR`). While the performance is comparable to the LSTM model, it definitely seems preferable to use the LSTM, which could be trained much faster and requires only half the number of parameters.

</details>
