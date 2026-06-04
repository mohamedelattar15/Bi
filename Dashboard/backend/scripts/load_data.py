"""
Script to load grocery sales CSV data into PostgreSQL.
Uses the star schema: dim_category, dim_product, dim_customer, dim_employee, dim_date, fact_sales

Usage:
    python scripts/load_data.py

Prerequisites:
    - PostgreSQL running with 'grocery_sales' database
    - schema.sql already executed
    - CSV files in ../dataset/ directory
"""

import pandas as pd
from sqlalchemy import create_engine, text
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "dataset")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/grocery_sales",
)


def load_csv(filename: str) -> pd.DataFrame:
    path = os.path.join(DATASET_PATH, filename)
    print(f"  Loading {path}...")
    return pd.read_csv(path)


def create_dim_date(engine) -> None:
    """Populate dim_date table with date range from sales data."""
    print("\n📅 Creating dim_date...")

    # Find date range from sales data
    sales = load_csv("sales.csv")
    sales["SalesDate"] = pd.to_datetime(sales["SalesDate"], errors="coerce")
    min_date = sales["SalesDate"].min().date()
    max_date = sales["SalesDate"].max().date()

    print(f"  Date range: {min_date} to {max_date}")

    # Generate all dates
    dates = []
    current = min_date
    while current <= max_date:
        dates.append({
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

    df_dates = pd.DataFrame(dates)
    df_dates.to_sql("dim_date", engine, if_exists="append", index=False, method="multi")
    print(f"  ✅ Inserted {len(df_dates)} dates")


def load_dim_categories(engine) -> None:
    """Load categories CSV into dim_category."""
    print("\n📂 Loading dim_category...")
    df = load_csv("categories.csv")
    df.columns = ["categoryid", "categoryname"]
    df.to_sql("dim_category", engine, if_exists="append", index=False, method="multi")
    print(f"  ✅ Inserted {len(df)} categories")


def load_dim_products(engine) -> None:
    """Load products CSV into dim_product."""
    print("\n📦 Loading dim_product...")
    df = load_csv("products.csv")
    df = df.rename(columns={
        "ProductID": "productid",
        "ProductName": "productname",
        "Price": "price",
        "CategoryID": "categoryid",
        "Class": "class_",
        "ModifyDate": "modifydate",
        "Resistant": "resistant",
        "IsAllergic": "isallergic",
        "VitalityDays": "vitalitydays",
    })
    df["modifydate"] = pd.to_datetime(df["modifydate"], errors="coerce").dt.date

    # Add category name denormalized
    categories = pd.read_csv(os.path.join(DATASET_PATH, "categories.csv"))
    cat_map = dict(zip(categories["CategoryID"], categories["CategoryName"]))
    df["categoryname"] = df["categoryid"].map(cat_map)

    df.to_sql("dim_product", engine, if_exists="append", index=False, method="multi")
    print(f"  ✅ Inserted {len(df)} products")


def load_dim_customers(engine) -> None:
    """Load customers CSV into dim_customer."""
    print("\n👤 Loading dim_customer...")
    df = load_csv("customers.csv")
    cities = pd.read_csv(os.path.join(DATASET_PATH, "cities.csv"))
    countries = pd.read_csv(os.path.join(DATASET_PATH, "countries.csv"))

    df = df.rename(columns={
        "CustomerID": "customerid",
        "FirstName": "customerfirstname",
        "MiddleInitial": "middleinitial",
        "LastName": "customerlastname",
        "CityID": "cityid",
        "Address": "address",
    })

    # Join city and country info
    df = df.merge(cities, on="CityID", how="left")
    df = df.merge(countries, on="CountryID", how="left")
    df = df.rename(columns={
        "CityName": "city",
        "CountryName": "country",
        "CountryCode": "countrycode",
    })

    df["zipcode"] = df["Zipcode"].astype(str)
    df = df[["customerid", "customerfirstname", "middleinitial", "customerlastname",
             "address", "cityid", "city", "zipcode", "countryid", "country", "countrycode"]]

    df.to_sql("dim_customer", engine, if_exists="append", index=False, method="multi", chunksize=5000)
    print(f"  ✅ Inserted {len(df)} customers")


def load_dim_employees(engine) -> None:
    """Load employees CSV into dim_employee."""
    print("\n👔 Loading dim_employee...")
    df = load_csv("employees.csv")
    cities = pd.read_csv(os.path.join(DATASET_PATH, "cities.csv"))

    df = df.rename(columns={
        "EmployeeID": "employeeid",
        "FirstName": "employeefirstname",
        "MiddleInitial": "middleinitial",
        "LastName": "employeelastname",
        "BirthDate": "birthdate",
        "Gender": "gender",
        "HireDate": "hiredate",
        "CityID": "cityid",
    })

    df["birthdate"] = pd.to_datetime(df["birthdate"], errors="coerce").dt.date
    df["hiredate"] = pd.to_datetime(df["hiredate"], errors="coerce").dt.date

    # Add city name
    city_map = dict(zip(cities["CityID"], cities["CityName"]))
    df["city"] = df["cityid"].map(city_map)

    df = df[["employeeid", "employeefirstname", "employeelastname",
             "birthdate", "gender", "hiredate", "city", "cityid"]]

    df.to_sql("dim_employee", engine, if_exists="append", index=False, method="multi")
    print(f"  ✅ Inserted {len(df)} employees")


def load_fact_sales(engine) -> None:
    """Load sales CSV into fact_sales (the main fact table)."""
    print("\n📊 Loading fact_sales (~6.7M rows - this may take a while)...")
    df = load_csv("sales.csv")

    df = df.rename(columns={
        "SalesID": "salesid",
        "SalesPersonID": "employeeid",
        "CustomerID": "customerid",
        "ProductID": "productid",
        "Quantity": "quantity",
        "Discount": "discount",
        "TotalPrice": "totalprice",
        "TransactionNumber": "transactionnumber",
    })

    # Parse date
    df["SalesDate"] = pd.to_datetime(df["SalesDate"], errors="coerce")
    df = df.dropna(subset=["SalesDate"])
    df["date"] = df["SalesDate"].dt.date
    df["time"] = df["SalesDate"].dt.time.astype(str)

    df = df[["salesid", "employeeid", "customerid", "productid", "date",
             "quantity", "discount", "totalprice", "transactionnumber", "time"]]

    # Insert in chunks for large dataset
    chunksize = 50000
    for i in range(0, len(df), chunksize):
        chunk = df.iloc[i : i + chunksize]
        chunk.to_sql("fact_sales", engine, if_exists="append", index=False, method="multi")
        print(f"  Progress: {min(i + chunksize, len(df)):,} / {len(df):,} rows")

    print(f"  ✅ Inserted {len(df):,} sales records")


def refresh_materialized_views(engine) -> None:
    """Refresh all materialized views."""
    print("\n🔄 Refreshing materialized views...")
    views = [
        "mv_daily_sales",
        "mv_monthly_sales",
        "mv_customer_segmentation",
        "mv_top_products",
        "mv_employee_performance",
    ]
    with engine.connect() as conn:
        for view in views:
            print(f"  Refreshing {view}...")
            conn.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
        conn.commit()
    print("  ✅ All materialized views refreshed")


def main():
    print("=" * 60)
    print("  Grocery Sales Data Loader")
    print("=" * 60)

    engine = create_engine(DATABASE_URL)

    print(f"\n🔗 Connected to: {DATABASE_URL}")

    # Load in order
    load_dim_categories(engine)
    load_dim_products(engine)
    load_dim_customers(engine)
    load_dim_employees(engine)
    create_dim_date(engine)
    load_fact_sales(engine)

    # Refresh materialized views
    refresh_materialized_views(engine)

    print("\n" + "=" * 60)
    print("  ✅ Data loading complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
