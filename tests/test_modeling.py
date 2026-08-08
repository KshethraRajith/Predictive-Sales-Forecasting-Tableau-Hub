import os
import numpy as np
import pandas as pd
from src import modeling


def test_train_and_forecast_smoke(tmp_path):
    # create synthetic weekly series for 3 years
    periods = 156
    dates = pd.date_range(start="2018-01-01", periods=periods, freq='W')
    week = np.arange(periods)
    sales = 200 + 20 * np.sin(2 * np.pi * week / 52) + np.random.normal(scale=2, size=periods)

    df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'region': ['north'] * periods,
        'product_category': ['widgets'] * periods,
        'sales': sales,
        'transactions': [10] * periods,
    })

    agg_file = tmp_path / 'agg.csv'
    df.to_csv(agg_file, index=False)

    model_out = tmp_path / 'model.pkl'
    forecast_out = tmp_path / 'forecast.csv'

    modeling.train_and_forecast(str(agg_file), region='north', product_category='widgets', periods=4, model_out=str(model_out), forecast_out=str(forecast_out))

    assert os.path.exists(forecast_out)
    out = pd.read_csv(forecast_out)
    assert 'forecast' in out.columns
    assert len(out) == 4
