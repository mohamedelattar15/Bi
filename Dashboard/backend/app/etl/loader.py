"""
ETL — Load Module

Handles inserting transformed DataFrames into PostgreSQL tables.
Respects foreign key order: dimensions first, then facts.
"""

import pandas as pd
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session

# Maximum parameters per PostgreSQL statement (safety margin)
MAX_PARAMS = 60000


def _chunk_size(num_columns: int) -> int:
    """Calculate safe chunk size based on column count."""
    return min(5000, MAX_PARAMS // num_columns)


def load_dataframe(df: pd.DataFrame, table: str, engine: Engine,
                   chunksize: int | None = None) -> int:
    """
    Load a DataFrame into a PostgreSQL table.

    Args:
        df: DataFrame to insert
        table: Target table name
        engine: SQLAlchemy engine
        chunksize: Rows per INSERT chunk (auto-calculated if None)

    Returns:
        Number of rows inserted
    """
    if df.empty:
        print(f"  ⚠️  No data to insert into {table}")
        return 0

    if chunksize is None:
        chunksize = _chunk_size(len(df.columns))

    df.to_sql(
        table,
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=chunksize,
    )
    return len(df)


def refresh_materialized_views(engine: Engine) -> None:
    """Refresh all analytical materialized views in order."""
    views = [
        "mv_daily_sales",
        "mv_monthly_sales",
        "mv_customer_segmentation",
        "mv_top_products",
        "mv_employee_performance",
    ]
    with engine.begin() as conn:
        for view in views:
            print(f"  Refreshing {view}...")
            conn.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
    print("  ✅ All materialized views refreshed")


def truncate_tables(engine: Engine, tables: list[str]) -> None:
    """Truncate tables in reverse dependency order."""
    with engine.begin() as conn:
        for table in tables:
            conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
            print(f"  Truncated {table}")
