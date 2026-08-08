"""Data ingestion and SQL aggregation helpers.

Functions:
- aggregate_sales: runs a SQL aggregation query and saves grouped CSV for modeling.
"""
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

def get_engine(conn_string: Optional[str] = None):
    """Return a SQLAlchemy engine. If conn_string is None, read from ENV: DATABASE_URL."""
    if conn_string is None:
        conn_string = os.getenv("DATABASE_URL")
    if conn_string is None:
        raise ValueError("DATABASE_URL not provided")
    return create_engine(conn_string)


def aggregate_sales(engine, source_table: str, start_date: Optional[str] = None, end_date: Optional[str] = None, out_csv: str = "output/aggregated_sales.csv"):
    """Aggregate historical sales into weekly totals with geography and product groups.

    Parameters
    - engine: SQLAlchemy engine or connection string
    - source_table: table name or subquery to pull raw transactions
    - start_date/end_date: optional filters in YYYY-MM-DD
    - out_csv: path to write aggregated CSV
    """
    if not hasattr(engine, "execute"):
        engine = get_engine(engine)

    date_filter = ""
    if start_date:
        date_filter += f" AND transaction_date >= '{start_date}'"
    if end_date:
        date_filter += f" AND transaction_date <= '{end_date}'"

    # Example aggregation query; adapt fields to your schema
    query = f"""
    SELECT
      CAST(transaction_date AS DATE) as date,
      region,
      product_category,
      SUM(amount) as sales,
      COUNT(*) as transactions
    FROM {source_table}
    WHERE 1=1 {date_filter}
    GROUP BY CAST(transaction_date AS DATE), region, product_category
    ORDER BY date
    """

    df = pd.read_sql_query(query, engine)

    # Convert to weekly aggregated time series for modeling: week starting on Monday
    df["date"] = pd.to_datetime(df["date"]).dt.to_period("W").apply(lambda r: r.start_time)
    grouped = df.groupby(["date", "region", "product_category"]).agg({"sales": "sum", "transactions": "sum"}).reset_index()

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    grouped.to_csv(out_csv, index=False)
    return out_csv


if __name__ == "__main__":
    # simple local test runner (requires DATABASE_URL in env)
    engine = get_engine()
    print("Aggregating to output/aggregated_sales.csv...")
    aggregate_sales(engine, source_table="sales_transactions", out_csv="output/aggregated_sales.csv")
