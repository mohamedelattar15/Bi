"""
AI dataset loader and preprocessing utilities.

This module centralises the PostgreSQL connection, the merge of
fact_sales and dim_product, and the daily aggregation logic.
"""

import pandas as pd
import psycopg2

DB_CONFIG = {
    "dbname": "grocery_db",
    "user": "postgres",
    "password": "2002",
    "host": "localhost",
    "port": 5432,
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def load_fact_product_tables():
    """Charge fact_sales et dim_product puis les fusionne par productid."""
    with get_connection() as conn:
        fact = pd.read_sql(
            "SELECT date, productid, customerid, quantity, discount FROM fact_sales",
            conn,
            parse_dates=["date"],
        )
        product = pd.read_sql(
            "SELECT productid, price FROM dim_product",
            conn,
        )

    fact["date"] = pd.to_datetime(fact["date"])
    merged = fact.merge(product, on="productid", how="left")

    if merged["price"].isna().any():
        missing = merged.loc[merged["price"].isna(), "productid"].unique()
        raise ValueError(
            f"Produit(s) manquant(s) dans dim_product pour productid(s)={missing.tolist()}"
        )

    return merged


def ensure_daily_index(df, date_col="date"):
    df = df.set_index(date_col).asfreq("D")
    for col in df.columns:
        df[col] = df[col].fillna(df[col].median())
    return df


def load_daily_revenue():
    """Charge le revenue journalier consolidé depuis les tables de ventes."""
    merged = load_fact_product_tables()
    merged["revenue"] = merged["price"] * merged["quantity"] - merged["discount"]

    daily = (
        merged.groupby("date", as_index=False)["revenue"]
        .sum()
        .rename(columns={"revenue": "revenue"})
    )
    daily = ensure_daily_index(daily)
    daily["revenue"] = daily["revenue"].astype(float)

    return daily


def load_daily_enriched_data():
    """Charge les métriques journalières enrichies pour le ML classique."""
    merged = load_fact_product_tables()
    merged["revenue"] = merged["price"] * merged["quantity"] - merged["discount"]

    daily = merged.groupby("date", as_index=False).agg(
        revenue=("revenue", "sum"),
        nb_transactions=("productid", "count"),
        total_qty=("quantity", "sum"),
        avg_discount=("discount", "mean"),
        nb_customers=("customerid", "nunique"),
        nb_products=("productid", "nunique"),
    )

    daily = ensure_daily_index(daily)
    daily = daily.astype({
        "revenue": float,
        "nb_transactions": float,
        "total_qty": float,
        "avg_discount": float,
        "nb_customers": float,
        "nb_products": float,
    })

    return daily
