# Predictive Sales Forecasting & Tableau Hub

Overview
- Process historical transaction logs (SQL) and train weekly time-series forecasting models (Python).
- Produce forecasts with 95% confidence bands and export CSVs for Tableau storyboards.

Quick start
1. Create a `.env` file at the repo root with `DATABASE_URL` pointing to your DB.
2. Create a Python venv and install requirements:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Running the pipeline
- To run once (local):

```bash
python -m src.run_pipeline
```

Files of interest
- [src/data_pipeline.py](src/data_pipeline.py) — SQL aggregation helper (writes `output/aggregated_sales.csv`).
- [src/modeling.py](src/modeling.py) — SARIMAX training and forecasting (writes `output/forecast.csv`).
- [src/export_tableau.py](src/export_tableau.py) — copies CSVs to `output/tableau/` for Tableau.
- [src/run_pipeline.py](src/run_pipeline.py) — pipeline wrapper to run all steps.

Tableau integration
- Point Tableau at `output/tableau/aggregated_for_tableau.csv` and `output/tableau/forecast_for_tableau.csv`.
- Build a storyboard with a map/geo sheet (use `region`) plus a timeline sheet that uses `date`.

Scheduling / automation
- Windows Task Scheduler: create a task to run the `python -m src.run_pipeline` command weekly.
- Or use `cron` on Linux/macOS for weekly execution.

Next steps and recommendations
- Tune SARIMAX parameters per series with diagnostics and AIC/BIC.
- Add regional/product-level models and ensemble predictions.
- Consider publishing .hyper extracts using the Tableau Hyper API for performance.
