"""
Clean script to load all CSV data into PostgreSQL.
Loads dimensions first, then fact_sales in 5000-row chunks.

Usage:
    python scripts/load_all_data.py

The script truncates all tables first, so it's safe to re-run.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import create_engine, text

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts", "data"
)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/grocery_sales",
)

CHUNK_SIZE = 5000


def main():
    start = time.time()
    print("=" * 60)
    print("  🚀 Loading all data into PostgreSQL")
    print("=" * 60)
    print(f"\n🔗 Database: {DATABASE_URL}")
    print(f"📂 Dataset:  {DATASET_PATH}")

    engine = create_engine(DATABASE_URL)

    # ── Step 1: Reset all tables ──
    print("\n── Step 1: Resetting all tables ──")
    tables_to_truncate = [
        "fact_sales", "dim_date", "dim_employee",
        "dim_customer", "dim_product", "dim_category"
    ]
    with engine.begin() as conn:
        for table in tables_to_truncate:
            conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
            print(f"  Truncated {table}")
    print("  ✅ Database reset complete")

    # ── Step 2: Load dimension tables ──
    print("\n── Step 2: Loading dimension tables ──")

    # dim_category
    df = pd.read_csv(os.path.join(DATASET_PATH, "dim_category.csv"))
    df.to_sql("dim_category", engine, if_exists="append", index=False, method="multi")
    print(f"  ✅ dim_category: {len(df):,} rows")

    # dim_product
    df = pd.read_csv(os.path.join(DATASET_PATH, "dim_product.csv"))
    df.to_sql("dim_product", engine, if_exists="append", index=False, method="multi")
    print(f"  ✅ dim_product: {len(df):,} rows")

    # dim_customer
    df = pd.read_csv(os.path.join(DATASET_PATH, "dim_customer.csv"))
    df.to_sql("dim_customer", engine, if_exists="append", index=False,
              method="multi", chunksize=5000)
    print(f"  ✅ dim_customer: {len(df):,} rows")

    # dim_employee
    df = pd.read_csv(os.path.join(DATASET_PATH, "dim_employee.csv"))
    df.to_sql("dim_employee", engine, if_exists="append", index=False, method="multi")
    print(f"  ✅ dim_employee: {len(df):,} rows")

    # ── Step 3: Generate and load dim_date ──
    print("\n── Step 3: Generating dim_date from fact_sales dates ──")

    # Read just the date column from fact_sales to get the date range
    fact_dates = pd.read_csv(
        os.path.join(DATASET_PATH, "fact_sales.csv"),
        usecols=["date"]
    )
    fact_dates["date"] = pd.to_datetime(fact_dates["date"], errors="coerce")
    min_date = fact_dates["date"].min().date()
    max_date = fact_dates["date"].max().date()

    from datetime import timedelta
    date_rows = []
    current = min_date
    while current <= max_date:
        date_rows.append({
            "date_key": current,
            "year": current.year,
            "quarter": (current.month - 1) // 3 + 1,
            "month": current.month,
            "month_name": current.strftime("%B"),
            "day": current.day,
            "day_of_week": current.isoweekday(),
            "day_name": current.strftime("%A"),
            "week_of_year": current.isocalendar()[1],
            "is_weekend": current.weekday() >= 5,
        })
        current += timedelta(days=1)

    dim_date = pd.DataFrame(date_rows)
    dim_date.to_sql("dim_date", engine, if_exists="append", index=False,
                    method="multi", chunksize=5000)
    print(f"  ✅ dim_date: {len(dim_date):,} rows ({min_date} to {max_date})")

    # ── Step 4: Load fact_sales using fast COPY in batches ──
    print("\n── Step 4: Loading fact_sales (using PostgreSQL COPY in batches) ──")

    # Load products for price lookup
    prod_prices = pd.read_csv(
        os.path.join(DATASET_PATH, "dim_product.csv"),
        usecols=["productid", "price"]
    )
    price_map = dict(zip(prod_prices["productid"], prod_prices["price"]))

    total_rows = 0
    chunk_start = time.time()
    COPY_BATCH_SIZE = 500_000

    import io

    def copy_dataframe_to_table(df: pd.DataFrame, table: str, engine) -> int:
        """Bulk-load a DataFrame using PostgreSQL COPY (tab-separated)."""
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, header=False, sep="\t", na_rep="\\N")
        buffer.seek(0)
        conn = engine.raw_connection()
        try:
            with conn.cursor() as cursor:
                cursor.copy_from(buffer, table, sep="\t", null="\\N")
            conn.commit()
            return len(df)
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    for chunk in pd.read_csv(
        os.path.join(DATASET_PATH, "fact_sales.csv"),
        chunksize=COPY_BATCH_SIZE
    ):
        # Compute totalprice = quantity * price
        chunk["price"] = chunk["productid"].map(price_map).fillna(0)
        chunk["totalprice"] = chunk["quantity"] * chunk["price"]
        chunk = chunk.drop(columns=["price"])

        # Ensure column order matches DB schema
        chunk = chunk[[
            "salesid", "employeeid", "customerid", "productid",
            "date", "quantity", "discount", "totalprice",
            "transactionnumber", "time"
        ]]

        copy_dataframe_to_table(chunk, "fact_sales", engine)
        total_rows += len(chunk)

        elapsed = time.time() - chunk_start
        rate = total_rows / elapsed if elapsed > 0 else 0
        print(f"  📊 {total_rows:,} / 6,690,599 rows loaded ({rate:,.0f} rows/sec)")

    elapsed = time.time() - chunk_start
    print(f"\n  ✅ fact_sales: {total_rows:,} rows loaded in {elapsed:.1f}s")

    # ── Step 5: Refresh materialized views ──
    print("\n── Step 5: Refreshing materialized views ──")
    mviews = [
        "mv_daily_sales", "mv_monthly_sales",
        "mv_customer_segmentation", "mv_top_products",
        "mv_employee_performance",
    ]
    with engine.begin() as conn:
        for view in mviews:
            try:
                conn.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
                print(f"  ✅ Refreshed {view}")
            except Exception as e:
                print(f"  ⚠️  Could not refresh {view}: {e}")

    # ── Summary ──
    total_elapsed = time.time() - start
    print("\n" + "=" * 60)
    print(f"  ✅ ALL DATA LOADED — {total_elapsed:.1f}s")
    print("=" * 60)

    # Final row count verification
    with engine.connect() as conn:
        for tbl in ["dim_category", "dim_product", "dim_customer",
                     "dim_employee", "dim_date", "fact_sales"]:
            result = conn.execute(text(f"SELECT count(*) FROM {tbl}"))
            print(f"     {tbl}: {result.scalar():,} rows")


if __name__ == "__main__":
    main()
