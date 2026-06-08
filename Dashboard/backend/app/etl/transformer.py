"""
ETL — Transform Module

Applies all data cleaning, enrichment, and transformation rules
that were previously implemented in:
  - Power BI Data_Preprocessing notebooks
  - Apache Hop dimension pipeline
  - Pandas fusion script (grocery_sales_fusion.ipynb)

Each transformation is a pure function for testability.
"""

import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import Optional


# ──────────────────────────────────────────────
# 1. DATE CLEANING (ref: notebook step 0.1)
# ──────────────────────────────────────────────

def clean_sales_dates(df: pd.DataFrame,
                      date_col: str = "SalesDate") -> pd.DataFrame:
    """
    Parse SalesDate, remove nulls, split into date/time.

    Business Rules:
    - Floor to seconds (remove milliseconds)
    - Drop rows with null/NaT dates (~1% of data)
    - Extract .date and .time columns

    Ref: grocery_sales_fusion.ipynb §0.1
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[date_col] = df[date_col].dt.floor("S")

    rows_before = len(df)
    df = df.dropna(subset=[date_col])
    rows_after = len(df)

    if rows_before > rows_after:
        print(f"  ⚠️  Dropped {rows_before - rows_after:,} rows with null dates")

    df["date"] = df[date_col].dt.date
    df["time"] = df[date_col].dt.strftime("%H:%M:%S")
    return df


# ──────────────────────────────────────────────
# 2. COLUMN STANDARDIZATION
# ──────────────────────────────────────────────

def standardize_columns(df: pd.DataFrame,
                        mapping: dict[str, str]) -> pd.DataFrame:
    """
    Rename columns from source names to target snake_case names.

    Args:
        df: Source DataFrame
        mapping: Dict of {source_name: target_name}

    Returns:
        DataFrame with renamed columns
    """
    return df.rename(columns=mapping)


# ──────────────────────────────────────────────
# 3. DIMENSION ENRICHMENT
# ──────────────────────────────────────────────

def enrich_products(products: pd.DataFrame,
                    categories: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich products with denormalized category name.

    Ref: Apache Hop dim_product branch
    """
    cat_map = dict(zip(categories["CategoryID"], categories["CategoryName"]))
    products = products.copy()
    products["categoryname"] = products["CategoryID"].map(cat_map)
    return products


def enrich_customers(customers: pd.DataFrame,
                     cities: pd.DataFrame,
                     countries: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich customers with city and country information.

    Ref: Apache Hop dim_customer branch, notebook step 1
    """
    df = customers.merge(cities, on="CityID", how="left")
    df = df.merge(countries, on="CountryID", how="left")
    return df


def enrich_employees(employees: pd.DataFrame,
                     cities: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich employees with city name.

    Ref: Apache Hop dim_employee branch
    """
    city_map = dict(zip(cities["CityID"], cities["CityName"]))
    employees = employees.copy()
    employees["City"] = employees["CityID"].map(city_map)
    return employees


# ──────────────────────────────────────────────
# 4. DIM_DATE GENERATION
# ──────────────────────────────────────────────

def generate_dim_date(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate dim_date table from min/max sales date.

    Ref: Notebook step 2 (Year, Month, Quarter, DayOfWeek extraction)

    Returns:
        DataFrame with columns: date_key, year, quarter, month, month_name,
        day, day_of_week, day_name, week_of_year, is_weekend
    """
    min_date = sales_df["date"].min()
    max_date = sales_df["date"].max()

    records = []
    current = min_date
    while current <= max_date:
        records.append({
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

    return pd.DataFrame(records)


# ──────────────────────────────────────────────
# 5. FACT TABLE TRANSFORMATIONS
# ──────────────────────────────────────────────

def prepare_fact_sales(sales: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare fact_sales DataFrame with standardized columns.

    Transformations:
    - Rename columns to snake_case
    - Parse and clean dates
    - Select final column set
    """
    df = sales.rename(columns={
        "SalesID": "salesid",
        "SalesPersonID": "employeeid",
        "CustomerID": "customerid",
        "ProductID": "productid",
        "Quantity": "quantity",
        "Discount": "discount",
        "TotalPrice": "totalprice",
        "TransactionNumber": "transactionnumber",
    })

    df = clean_sales_dates(df, "SalesDate")

    return df[["salesid", "employeeid", "customerid", "productid",
               "date", "quantity", "discount", "totalprice",
               "transactionnumber", "time"]]


def prepare_dim_categories(categories: pd.DataFrame) -> pd.DataFrame:
    """Standardize categories for dim_category load."""
    df = categories.rename(columns={
        "CategoryID": "categoryid",
        "CategoryName": "categoryname",
    })
    return df[["categoryid", "categoryname"]]


def prepare_dim_products(products: pd.DataFrame,
                         categories: pd.DataFrame) -> pd.DataFrame:
    """Standardize and enrich products for dim_product load."""
    df = enrich_products(products, categories)
    df = df.rename(columns={
        "ProductID": "productid",
        "ProductName": "productname",
        "Price": "price",
        "CategoryID": "categoryid",
        "Class": "class",
        "ModifyDate": "modifydate",
        "Resistant": "resistant",
        "IsAllergic": "isallergic",
        "VitalityDays": "vitalitydays",
    })
    df["modifydate"] = pd.to_datetime(df["modifydate"],
                                      errors="coerce").dt.date
    return df[["productid", "productname", "price", "categoryid",
               "class", "modifydate", "resistant", "isallergic",
               "vitalitydays", "categoryname"]]


def prepare_dim_customers(customers: pd.DataFrame,
                          cities: pd.DataFrame,
                          countries: pd.DataFrame) -> pd.DataFrame:
    """Standardize and enrich customers for dim_customer load."""
    df = enrich_customers(customers, cities, countries)
    df = df.rename(columns={
        "CustomerID": "customerid",
        "FirstName": "customerfirstname",
        "MiddleInitial": "middleinitial",
        "LastName": "customerlastname",
        "Address": "address",
        "CityID": "cityid",
        "CityName": "city",
        "Zipcode": "zipcode",
        "CountryID": "countryid",
        "CountryName": "country",
        "CountryCode": "countrycode",
    })
    df["zipcode"] = df["Zipcode"].astype(str)

    # Fix renamed columns from merge
    if "CountryID" in df.columns:
        df = df.rename(columns={"CountryID": "countryid"})
    if "CityID" in df.columns:
        df = df.rename(columns={"CityID": "cityid"})

    return df[["customerid", "customerfirstname", "middleinitial",
               "customerlastname", "address", "cityid", "city",
               "zipcode", "countryid", "country", "countrycode"]]


def prepare_dim_employees(employees: pd.DataFrame,
                          cities: pd.DataFrame) -> pd.DataFrame:
    """Standardize and enrich employees for dim_employee load."""
    df = enrich_employees(employees, cities)
    df = df.rename(columns={
        "EmployeeID": "employeeid",
        "FirstName": "employeefirstname",
        "MiddleInitial": "middleinitial",
        "LastName": "employeelastname",
        "BirthDate": "birthdate",
        "Gender": "gender",
        "HireDate": "hiredate",
        "CityID": "cityid",
        "City": "city",
    })
    df["birthdate"] = pd.to_datetime(df["birthdate"],
                                     errors="coerce").dt.date
    df["hiredate"] = pd.to_datetime(df["hiredate"],
                                    errors="coerce").dt.date

    # Fix renamed column
    if "City" not in df.columns and "city" in df.columns:
        pass  # already renamed
    elif "City" not in df.columns and "City" in df.columns:
        pass  # already present from enrichment

    return df[["employeeid", "employeefirstname", "employeelastname",
               "birthdate", "gender", "hiredate", "city", "cityid"]]
