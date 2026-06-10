"""
ETL — Pipeline Orchestrator

Coordinates the full ETL workflow:
  1. Extract raw CSV data
  2. Transform and enrich each table
  3. Load dimensions (FK order: category → product → customer → employee → date)
  4. Load fact_sales
  5. Refresh materialized views

Usage:
    from app.etl.pipeline import ETLPipeline
    pipeline = ETLPipeline()
    pipeline.run(reset=True)
"""

import os
import time

import pandas as pd
from sqlalchemy import Engine, create_engine

from app.etl.extractor import DataExtractor
from app.etl.transformer import generate_dim_date
from app.etl.loader import load_dataframe, refresh_materialized_views, truncate_tables
from app.etl.sync import DatabaseSynchronizer

# Default dataset path relative to this file
DEFAULT_DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "scripts", "data"
)
DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/grocery_sales"


class ETLPipeline:
    """
    Full ETL pipeline for the Grocery Sales Data Warehouse.

    Load order (FK dependency order):
      1. dim_category     (no dependencies)
      2. dim_product      (depends on dim_category via categoryid)
      3. dim_customer     (no FK dependencies on other dims)
      4. dim_employee     (no FK dependencies on other dims)
      5. dim_date         (no dependencies)
      6. fact_sales       (depends on all dims)
    """

    DIM_LOAD_ORDER = [
        ("dim_category", "categories.csv"),
        ("dim_product", "products.csv"),
        ("dim_customer", "customers.csv"),
        ("dim_employee", "employees.csv"),
        ("dim_date", None),  # generated, not from CSV
    ]

    def __init__(self, database_url: str = DEFAULT_DATABASE_URL,
                 dataset_path: str = DEFAULT_DATASET_PATH):
        self.database_url = database_url
        self.dataset_path = dataset_path
        self.engine: Engine | None = None
        self.extractor = DataExtractor(dataset_path)
        self.sync = DatabaseSynchronizer(database_url)
        self.metrics: dict[str, int] = {}

    def run(self, reset: bool = False) -> dict[str, int]:
        """
        Execute the full ETL pipeline.

        Args:
            reset: If True, truncate all tables before loading

        Returns:
            Dict mapping table_name -> rows_inserted
        """
        start_time = time.time()
        print("=" * 60)
        print("  🔄 ETL Pipeline — Grocery Sales Data Warehouse")
        print("=" * 60)

        self.engine = create_engine(self.database_url)
        print(f"\n🔗 Database: {self.database_url}")
        print(f"📂 Dataset:  {self.dataset_path}")

        # Step 0: Reset if requested
        if reset:
            self._reset_database()

        # Step 1: Extract & Transform dimensions + facts
        print("\n── Step 1: Extract & Transform ──")
        datasets = self._extract_all()

        # Step 2: Validate source data
        print("\n── Step 2: Validate ──")
        self._validate_all(datasets)

        # Step 3: Load dimensions
        print("\n── Step 3: Load Dimensions ──")
        self._load_dimensions(datasets)

        # Step 4: Load fact table
        print("\n── Step 4: Load Fact Table ──")
        self._load_facts(datasets)

        # Step 5: Refresh materialized views
        print("\n── Step 5: Refresh Materialized Views ──")
        refresh_materialized_views(self.engine)

        # Step 6: Sync validation
        print("\n── Step 6: Verify Sync ──")
        self.sync.verify_sync(self.engine)

        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print(f"  ✅ ETL Complete — {elapsed:.1f}s")
        for table, count in self.metrics.items():
            print(f"     {table}: {count:,} rows")
        print("=" * 60)

        return self.metrics

    def _reset_database(self) -> None:
        """Truncate all tables in reverse dependency order."""
        print("\n🔄 Resetting database...")
        truncate_tables(self.engine, [
            "fact_sales",
            "dim_date",
            "dim_employee",
            "dim_customer",
            "dim_product",
            "dim_category",
        ])
        print("  ✅ Database reset")

    def _extract_all(self) -> dict:
        """Extract pre-transformed CSV files (ready to load)."""
        return {
            "dim_category": self.extractor.extract("dim_category.csv"),
            "dim_product": self.extractor.extract("dim_product.csv"),
            "dim_customer": self.extractor.extract("dim_customer.csv"),
            "dim_employee": self.extractor.extract("dim_employee.csv"),
            "fact_sales": self.extractor.extract("fact_sales.csv"),
        }

    def _validate_all(self, datasets: dict) -> None:
        """Log loaded rows for each pre-transformed dataset."""
        for name, df in datasets.items():
            print(f"  ✅ {name}: {len(df):,} rows — pre-transformed")

    def _load_dimensions(self, datasets: dict) -> None:
        """Load pre-transformed dimension tables directly."""
        # ── dim_category (pre-transformed) ──
        self.metrics["dim_category"] = load_dataframe(
            datasets["dim_category"], "dim_category", self.engine
        )
        print(f"  ✅ dim_category: {self.metrics['dim_category']:,} rows")

        # ── dim_product (pre-transformed) ──
        self.metrics["dim_product"] = load_dataframe(
            datasets["dim_product"], "dim_product", self.engine
        )
        print(f"  ✅ dim_product: {self.metrics['dim_product']:,} rows")

        # ── dim_customer (pre-transformed) ──
        self.metrics["dim_customer"] = load_dataframe(
            datasets["dim_customer"], "dim_customer", self.engine
        )
        print(f"  ✅ dim_customer: {self.metrics['dim_customer']:,} rows")

        # ── dim_employee (pre-transformed) ──
        self.metrics["dim_employee"] = load_dataframe(
            datasets["dim_employee"], "dim_employee", self.engine
        )
        print(f"  ✅ dim_employee: {self.metrics['dim_employee']:,} rows")

        # ── dim_date (generated from fact_sales dates) ──
        fact_for_dates = datasets["fact_sales"].copy()
        fact_for_dates["date"] = pd.to_datetime(
            fact_for_dates["date"], errors="coerce"
        ).dt.date
        df = generate_dim_date(fact_for_dates)
        self.metrics["dim_date"] = load_dataframe(df, "dim_date", self.engine)
        print(f"  ✅ dim_date: {self.metrics['dim_date']:,} rows")

    def _load_facts(self, datasets: dict) -> None:
        """Load fact_sales with pre-computed totalprice (quantity * price)."""
        fact = datasets["fact_sales"].copy()
        prod = datasets["dim_product"][["productid", "price"]]
        fact = fact.merge(prod, on="productid", how="left")
        fact["totalprice"] = fact["quantity"] * fact["price"].fillna(0)
        fact = fact.drop(columns=["price"])
        # Match DB column order: salesid, employeeid, customerid, productid,
        # date, quantity, discount, totalprice, transactionnumber, time
        fact = fact[["salesid", "employeeid", "customerid", "productid",
                     "date", "quantity", "discount", "totalprice",
                     "transactionnumber", "time"]]

        self.metrics["fact_sales"] = load_dataframe(fact, "fact_sales", self.engine)
        print(f"  ✅ fact_sales: {self.metrics['fact_sales']:,} rows")


# Convenience function
def run_etl(reset: bool = False) -> dict[str, int]:
    """Run the full ETL pipeline."""
    pipeline = ETLPipeline()
    return pipeline.run(reset=reset)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run ETL Pipeline")
    parser.add_argument("--reset", action="store_true",
                        help="Truncate tables before loading")
    args = parser.parse_args()
    run_etl(reset=args.reset)
