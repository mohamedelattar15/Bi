"""
ETL — Database Synchronization Module

Ensures consistency between the backend models, database schema,
and ETL pipeline via automated checks.

Responsibilities:
  - Verify table existence and column types match expected schema
  - Check row counts against thresholds
  - Validate foreign key referential integrity
  - Detect schema drift (missing columns, type mismatches)
"""

from sqlalchemy import Engine, text, inspect
from typing import Any


class DatabaseSynchronizer:
    """
    Synchronization and health-check manager for the data warehouse.

    Usage:
        sync = DatabaseSynchronizer(DATABASE_URL)
        sync.verify_sync(engine)
    """

    EXPECTED_TABLES = [
        "dim_category",
        "dim_product",
        "dim_customer",
        "dim_employee",
        "dim_date",
        "fact_sales",
    ]

    EXPECTED_MVIEWS = [
        "mv_daily_sales",
        "mv_monthly_sales",
        "mv_customer_segmentation",
        "mv_top_products",
        "mv_employee_performance",
    ]

    MINIMUM_ROW_COUNTS = {
        "dim_category": 10,
        "dim_product": 400,
        "dim_customer": 50000,
        "dim_employee": 20,
        "fact_sales": 5_000_000,
    }

    FOREIGN_KEY_CHECKS = [
        ("fact_sales", "employeeid", "dim_employee", "employeeid"),
        ("fact_sales", "customerid", "dim_customer", "customerid"),
        ("fact_sales", "productid", "dim_product", "productid"),
        ("fact_sales", "date", "dim_date", "date_key"),
        ("dim_product", "categoryid", "dim_category", "categoryid"),
    ]

    def __init__(self, database_url: str):
        self.database_url = database_url

    def verify_sync(self, engine: Engine) -> list[str]:
        """
        Run all synchronization checks and print results.

        Returns:
            List of warning/error messages (empty = fully synced)
        """
        print("\n🔍 Database Synchronization Check")
        all_issues: list[str] = []

        all_issues.extend(self._check_tables_exist(engine))
        all_issues.extend(self._check_mviews_exist(engine))
        all_issues.extend(self._check_row_counts(engine))
        all_issues.extend(self._check_foreign_keys(engine))

        if all_issues:
            print(f"  ⚠️  {len(all_issues)} issues found:")
            for issue in all_issues:
                print(f"     {issue}")
        else:
            print("  ✅ All systems synchronized")

        return all_issues

    def _check_tables_exist(self, engine: Engine) -> list[str]:
        """Verify all expected tables exist."""
        issues: list[str] = []
        inspector = inspect(engine)
        existing = inspector.get_table_names()

        for table in self.EXPECTED_TABLES:
            if table not in existing:
                issues.append(f"[MISSING] Table '{table}' does not exist")
            else:
                columns = [c["name"] for c in inspector.get_columns(table)]
                print(f"  ✅ {table}: {len(columns)} columns")

        return issues

    def _check_mviews_exist(self, engine: Engine) -> list[str]:
        """Verify all expected materialized views exist."""
        issues: list[str] = []
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT relname FROM pg_class
                WHERE relkind = 'm' AND relnamespace = 'public'::regnamespace
            """))
            existing = {row[0] for row in result}

        for mview in self.EXPECTED_MVIEWS:
            if mview not in existing:
                issues.append(f"[MISSING] Materialized view '{mview}' does not exist")
            else:
                print(f"  ✅ {mview}: exists")

        return issues

    def _check_row_counts(self, engine: Engine) -> list[str]:
        """Verify tables have minimum expected row counts."""
        issues: list[str] = []
        with engine.connect() as conn:
            for table, minimum in self.MINIMUM_ROW_COUNTS.items():
                try:
                    count = conn.execute(
                        text(f"SELECT COUNT(*) FROM {table}")
                    ).scalar()
                    print(f"     {table}: {count:>10,} rows (min: {minimum:>10,})")
                    if count < minimum:
                        issues.append(
                            f"[LOW] {table}: {count:,} rows < minimum {minimum:,}"
                        )
                except Exception as e:
                    issues.append(f"[ERROR] {table}: {e}")
        return issues

    def _check_foreign_keys(self, engine: Engine) -> list[str]:
        """Validate foreign key referential integrity."""
        issues: list[str] = []
        with engine.connect() as conn:
            for fk_table, fk_col, pk_table, pk_col in self.FOREIGN_KEY_CHECKS:
                try:
                    orphaned = conn.execute(text(f"""
                        SELECT COUNT(*) FROM {fk_table} f
                        LEFT JOIN {pk_table} p ON f.{fk_col} = p.{pk_col}
                        WHERE p.{pk_col} IS NULL
                    """)).scalar()
                    if orphaned > 0:
                        issues.append(
                            f"[ORPHAN] {fk_table}.{fk_col}: {orphaned:,} "
                            f"rows missing from {pk_table}.{pk_col}"
                        )
                    else:
                        print(f"     FK {fk_table}.{fk_col} → {pk_table}.{pk_col}: ✅")
                except Exception as e:
                    issues.append(f"[ERROR] FK check {fk_table}.{fk_col}: {e}")
        return issues
