"""Time-series modeling utilities.

Uses statsmodels' SARIMAX to produce point forecasts and confidence intervals.
"""
from typing import Optional
import pandas as pd
import numpy as np
import os
import pickle
from statsmodels.tsa.statespace.sarimax import SARIMAX


def train_and_forecast(aggregated_csv: str, region: Optional[str] = None, product_category: Optional[str] = None,
                       date_col: str = "date", target_col: str = "sales",
                       periods: int = 52, freq: str = "W", model_out: str = "output/sarimax_model.pkl",
                       forecast_out: str = "output/forecast.csv"):
    df = pd.read_csv(aggregated_csv, parse_dates=[date_col])
    if region:
        df = df[df.region == region]
    if product_category:
        df = df[df.product_category == product_category]

    # Aggregate to a single series (sum across groups if not provided)
    series = df.groupby(date_col)[target_col].sum().sort_index()
    series.index = pd.DatetimeIndex(series.index)
    series = series.asfreq(freq, fill_value=0)

    # Simple SARIMAX default parameters. Adjust after diagnostics.
    seasonal_period = 52  # weekly seasonality yearly
    model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(1, 1, 1, seasonal_period), enforce_stationarity=False, enforce_invertibility=False)
    res = model.fit(disp=False)

    # Forecast with confidence intervals
    pred = res.get_forecast(steps=periods)
    point = pred.predicted_mean
    conf = pred.conf_int(alpha=0.05)

    forecast_index = pd.date_range(start=series.index[-1] + pd.to_timedelta(1, unit=freq.lower()), periods=periods, freq=freq)
    out = pd.DataFrame({"date": forecast_index, "forecast": point.values, "lower_95": conf.iloc[:, 0].values, "upper_95": conf.iloc[:, 1].values})

    os.makedirs(os.path.dirname(forecast_out), exist_ok=True)
    out.to_csv(forecast_out, index=False)

    # Save model
    os.makedirs(os.path.dirname(model_out), exist_ok=True)
    with open(model_out, "wb") as f:
        pickle.dump(res, f)

    return model_out, forecast_out


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregated", default="output/aggregated_sales.csv")
    parser.add_argument("--periods", type=int, default=52)
    args = parser.parse_args()
    print("Training model and writing forecast to output/forecast.csv...")
    train_and_forecast(args.aggregated, periods=args.periods)
