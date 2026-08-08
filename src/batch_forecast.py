"""Batch forecasting runner.

Generates forecasts per (region, product_category) group found in the aggregated CSV.
Writes forecasts into `output/tableau/` with distinct filenames.
"""
import pandas as pd
import os
import re
from src import modeling, export_tableau


def _safe_name(s: str) -> str:
    if s is None:
        return "all"
    s = str(s)
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def batch_forecast(aggregated_csv: str = "output/aggregated_sales.csv", periods: int = 52):
    df = pd.read_csv(aggregated_csv, parse_dates=["date"]) if os.path.exists(aggregated_csv) else None
    if df is None or df.empty:
        raise FileNotFoundError(f"Aggregated CSV not found or empty: {aggregated_csv}")

    groups = df.groupby(["region", "product_category"]).size().reset_index().iloc[:, :2]

    outputs = []
    for _, row in groups.iterrows():
        region = row[0]
        product = row[1]
        rname = _safe_name(region)
        pname = _safe_name(product)
        suffix = f"{rname}_{pname}"
        model_out = f"output/models/sarimax_{suffix}.pkl"
        forecast_out = f"output/forecasts/forecast_{suffix}.csv"

        print(f"Training forecast for region={region} product={product} -> {forecast_out}")
        try:
            modeling.train_and_forecast(aggregated_csv, region=region, product_category=product, periods=periods, model_out=model_out, forecast_out=forecast_out)
            dest = export_tableau.publish_csv_to_output(forecast_out, dest_name=f"forecast_{suffix}.csv")
            outputs.append(dest)
        except Exception as e:
            print(f"Failed for {region}/{product}: {e}")

    return outputs


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--aggregated", default="output/aggregated_sales.csv")
    parser.add_argument("--periods", type=int, default=52)
    args = parser.parse_args()
    outs = batch_forecast(args.aggregated, periods=args.periods)
    print("Wrote:", outs)
