"""
ETL — Load Module

Handles inserting transformed DataFrames into PostgreSQL tables.
Respects foreign key order: dimensions first, then facts.
Uses COPY for large tables (>100K rows) — dramatically faster than multi-row INSERT.
"""

import io
import pandas as pd
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session

# Threshold: use COPY for tables bigger than this
COPY_THRESHOLD = 100_000


def load_dataframe(df: pd.DataFrame, table: str, engine: Engine,
                   chunksize: int | None = None) -> int:
    """
    Load a DataFrame into a PostgreSQL table.

    Uses COPY for large tables (>100K rows), multi-row INSERT for small ones.
    COPY is ~10-50x faster for bulk loading.

    Args:
        df: DataFrame to insert
        table: Target table name
        engine: SQLAlchemy engine
        chunksize: Ignored for COPY, used only for INSERT fallback

    Returns:
        Number of rows inserted
    """
    if df.empty:
        print(f"  ⚠️  No data to insert into {table}")
        return 0

    if len(df) > COPY_THRESHOLD:
        _copy_from_buffer(df, table, engine)
    else:
        # Fallback to multi-row INSERT for small tables
        df.to_sql(
            table,
            engine,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=chunksize or 5000,
        )

    return len(df)


def _copy_from_buffer(df: pd.DataFrame, table: str, engine: Engine) -> None:
    """
    Bulk-load a DataFrame using PostgreSQL COPY.
    Writes the DataFrame to an in-memory CSV buffer and pipes it via COPY.
    """
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False, sep="\t", na_rep="\\N")
    buffer.seek(0)

    conn = engine.raw_connection()
    try:
        with conn.cursor() as cursor:
            cursor.copy_from(buffer, table, sep="\t", null="\\N")
        conn.commit()
        print(f"  📦 Bulk-loaded {len(df):,} rows into {table} via COPY")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


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
