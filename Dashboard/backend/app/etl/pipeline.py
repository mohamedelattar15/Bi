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
from sqlalchemy import Engine, create_engine

from app.etl.extractor import DataExtractor
from app.etl.transformer import (
    prepare_dim_categories,
    prepare_dim_products,
    prepare_dim_customers,
    prepare_dim_employees,
    prepare_fact_sales,
    generate_dim_date,
)
from app.etl.loader import load_dataframe, refresh_materialized_views, truncate_tables
from app.etl.validator import DataValidator
from app.etl.sync import DatabaseSynchronizer

# Default dataset path relative to this file
DEFAULT_DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "scripts", "dataset"
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
        self.validator = DataValidator()
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
        """Extract all raw CSV files."""
        return {
            "categories": self.extractor.extract("categories.csv"),
            "products": self.extractor.extract("products.csv"),
            "customers": self.extractor.extract("customers.csv"),
            "employees": self.extractor.extract("employees.csv"),
            "cities": self.extractor.extract("cities.csv"),
            "countries": self.extractor.extract("countries.csv"),
            "sales": self.extractor.extract("sales.csv"),
        }

    def _validate_all(self, datasets: dict) -> None:
        """Validate all datasets against business rules."""
        rules = self.validator.get_all_rules()
        for name, df in datasets.items():
            issues = self.validator.validate(df, name)
            if issues:
                print(f"  📋 {name}: {len(issues)} validation issues")
                for issue in issues[:5]:  # show first 5
                    print(f"     {issue}")
            else:
                print(f"  ✅ {name}: {len(df):,} rows — valid")

    def _load_dimensions(self, datasets: dict) -> None:
        """Load all dimension tables in dependency order."""
        # ── dim_category ──
        df = prepare_dim_categories(datasets["categories"])
        self.metrics["dim_category"] = load_dataframe(df, "dim_category", self.engine)
        print(f"  ✅ dim_category: {self.metrics['dim_category']:,} rows")

        # ── dim_product (needs categories for enrichment) ──
        df = prepare_dim_products(datasets["products"], datasets["categories"])
        self.metrics["dim_product"] = load_dataframe(df, "dim_product", self.engine)
        print(f"  ✅ dim_product: {self.metrics['dim_product']:,} rows")

        # ── dim_customer (needs cities + countries) ──
        df = prepare_dim_customers(
            datasets["customers"], datasets["cities"], datasets["countries"]
        )
        self.metrics["dim_customer"] = load_dataframe(df, "dim_customer", self.engine)
        print(f"  ✅ dim_customer: {self.metrics['dim_customer']:,} rows")

        # ── dim_employee ──
        df = prepare_dim_employees(datasets["employees"], datasets["cities"])
        self.metrics["dim_employee"] = load_dataframe(df, "dim_employee", self.engine)
        print(f"  ✅ dim_employee: {self.metrics['dim_employee']:,} rows")

        # ── dim_date (generated from sales data) ──
        from app.etl.transformer import clean_sales_dates
        sales_for_dates = clean_sales_dates(datasets["sales"].copy())
        df = generate_dim_date(sales_for_dates)
        self.metrics["dim_date"] = load_dataframe(df, "dim_date", self.engine)
        print(f"  ✅ dim_date: {self.metrics['dim_date']:,} rows")

    def _load_facts(self, datasets: dict) -> None:
        """Load fact_sales table."""
        # Pass products for totalprice pre-computation (critical perf fix)
        df = prepare_fact_sales(datasets["sales"], datasets["products"])
        self.metrics["fact_sales"] = load_dataframe(df, "fact_sales", self.engine)
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
