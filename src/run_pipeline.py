"""Top-level runner: aggregate -> train -> export.

Run this from a scheduler (Windows Task Scheduler, cron, Airflow) to retrain weekly.
"""
import os
from src import data_pipeline, modeling, export_tableau


def run_full_pipeline(connection_string: str = None, source_table: str = "sales_transactions"):
    engine = connection_string or None
    agg = data_pipeline.aggregate_sales(engine, source_table=source_table, out_csv="output/aggregated_sales.csv")
    model_path, forecast_path = modeling.train_and_forecast(agg, periods=52, model_out="output/sarimax_model.pkl", forecast_out="output/forecast.csv")
    export_tableau.publish_csv_to_output(forecast_path, dest_name="forecast_for_tableau.csv")
    export_tableau.publish_csv_to_output(agg, dest_name="aggregated_for_tableau.csv")
    print("Pipeline complete. Files in output/ and output/tableau/")


if __name__ == "__main__":
    run_full_pipeline()
