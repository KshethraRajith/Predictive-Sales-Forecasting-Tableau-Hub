"""Create synthetic aggregated data, run batch forecasts, and produce Tableau CSVs.

Usage: python scripts/run_demo.py
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime

def make_synthetic_aggregated(out_csv: str = "output/aggregated_sales.csv"):
    periods = 156  # 3 years weekly
    start = pd.to_datetime("2019-01-07")
    dates = pd.date_range(start=start, periods=periods, freq='W')

    regions = ['north', 'south']
    products = ['widgets', 'gadgets']

    rows = []
    for r in regions:
        for p in products:
            base = 200 if r == 'north' else 150
            season_amp = 30 if p == 'widgets' else 20
            noise_scale = 5
            for i, d in enumerate(dates):
                seasonal = season_amp * np.sin(2 * np.pi * (i % 52) / 52)
                trend = 0.1 * i
                sales = max(0, base + seasonal + trend + np.random.normal(scale=noise_scale))
                rows.append({
                    'date': d.strftime('%Y-%m-%d'),
                    'region': r,
                    'product_category': p,
                    'sales': round(float(sales), 2),
                    'transactions': int(max(1, sales // 20))
                })

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    return out_csv


def run_demo():
    print("Generating synthetic aggregated CSV...")
    agg = make_synthetic_aggregated()
    print("Running batch forecasts (this may take a minute)...")
    import sys
    from pathlib import Path
    # ensure repo root is on sys.path so `src` package imports work when running from scripts/
    repo_root = str(Path(__file__).resolve().parents[1])
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.batch_forecast import batch_forecast
    outs = batch_forecast(aggregated_csv=agg, periods=12)
    print("Demo complete. Outputs:")
    for f in outs:
        print(" -", f)


if __name__ == '__main__':
    run_demo()
