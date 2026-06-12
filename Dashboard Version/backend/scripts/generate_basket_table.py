#!/usr/bin/env python3
"""
Generate basket_analysis_results.csv with raw decimal values + SQL for DB loading.

This script re-computes the basket analysis from groceries_long.csv and
exports a complete CSV with both raw (decimal) and percentage columns,
plus the CREATE TABLE and COPY SQL statements.

Usage:
    python scripts/generate_basket_table.py [--load]
"""

import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "..", "..")  # Bi/ directory
GROCERIES_CSV = os.path.join(DATA_DIR, "groceries_long.csv")
OUTPUT_CSV = os.path.join(DATA_DIR, "basket_analysis_results.csv")


def clean_product_name(name):
    name = str(name).strip()
    name = re.sub(r'[#`]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def main():
    print("=" * 60)
    print("🛒 Basket Analysis — CSV + SQL Generator")
    print("=" * 60)

    # ── 1. Load data ──
    print(f"\n📂 Loading {GROCERIES_CSV}...")
    df = pd.read_csv(GROCERIES_CSV)
    df['product_name'] = df['product_name'].apply(clean_product_name)
    df = df[df['product_name'] != ''].copy()
    print(f"   Rows: {len(df):,}")
    print(f"   Unique baskets: {df['transaction_id'].nunique():,}")
    print(f"   Unique products: {df['product_name'].nunique():,}")

    # ── 2. Generate product pairs ──
    print("\n🔄 Generating product pairs...")
    transactions = df.groupby('transaction_id')['product_name'].apply(list).to_dict()
    pair_counts = defaultdict(int)

    for trans_id, products in transactions.items():
        unique_products = sorted(set(products))
        for a, b in combinations(unique_products, 2):
            pair_counts[(a, b)] += 1

    print(f"   Total unique pairs: {len(pair_counts):,}")

    # ── 3. Compute metrics ──
    print("\n📊 Computing Support, Confidence, Lift...")
    product_counts = df['product_name'].value_counts()
    n_transactions = df['transaction_id'].nunique()

    basket_data = []
    for (a, b), count in pair_counts.items():
        support = count / n_transactions
        count_p1 = product_counts.get(a, 0)
        count_p2 = product_counts.get(b, 0)
        confidence_p1 = count / count_p1 if count_p1 > 0 else 0
        confidence_p2 = count / count_p2 if count_p2 > 0 else 0
        support_a = count_p1 / n_transactions
        support_b = count_p2 / n_transactions
        lift = support / (support_a * support_b) if support_a * support_b > 0 else 0

        basket_data.append({
            'Product1': a,
            'Product2': b,
            'Basket': f"{a} → {b}",
            # Raw decimal values
            'Support': round(support, 8),
            'Confidence_P1': round(confidence_p1, 8),
            'Confidence_P2': round(confidence_p2, 8),
            'Lift': round(lift, 4),
            # Percentage values for display
            'Support_Pct': round(support * 100, 4),
            'Confidence_P1_Pct': round(confidence_p1 * 100, 4),
            'Confidence_P2_Pct': round(confidence_p2 * 100, 4),
            # Transaction count
            'NbTransactions': count,
        })

    basket_df = pd.DataFrame(basket_data)
    print(f"   Computed: {len(basket_df):,} association rules")

    # Stats
    print(f"\n📈 Statistics:")
    print(f"   Lift range: {basket_df['Lift'].min():.4f} — {basket_df['Lift'].max():.4f}")
    print(f"   Support range: {basket_df['Support'].min():.8f} — {basket_df['Support'].max():.8f}")
    print(f"   Confidence range: {basket_df['Confidence_P1'].min():.6f} — {basket_df['Confidence_P1'].max():.6f}")
    print(f"   Rules with Lift > 0.3: {(basket_df['Lift'] > 0.3).sum():,}")
    print(f"   Rules with Lift > 0.2: {(basket_df['Lift'] > 0.2).sum():,}")
    print(f"   Rules with Lift > 0.15: {(basket_df['Lift'] > 0.15).sum():,}")

    # ── 4. Export CSV ──
    print(f"\n💾 Exporting to {OUTPUT_CSV}...")
    # Columns for the final CSV (matching DB table)
    export_df = basket_df[[
        'Product1', 'Product2', 'Basket', 'Support', 'Confidence_P1',
        'Confidence_P2', 'Lift', 'Support_Pct', 'Confidence_P1_Pct',
        'Confidence_P2_Pct', 'NbTransactions'
    ]].copy()
    export_df.to_csv(OUTPUT_CSV, index=False)
    print(f"   ✓ Exported {len(export_df):,} rows")

    # ── 5. Generate CREATE TABLE SQL ──
    sql = """
-- ==========================================
-- BASKET ANALYSIS RESULTS (Pre-computed)
-- Generated from basket_analysis_results.csv
-- Contains 75,020 association rules with
-- Support, Confidence, and Lift metrics.
-- ==========================================
DROP TABLE IF EXISTS basket_analysis_results CASCADE;

CREATE TABLE basket_analysis_results (
    id SERIAL PRIMARY KEY,
    product1 VARCHAR(200) NOT NULL,
    product2 VARCHAR(200) NOT NULL,
    basket_label VARCHAR(500) NOT NULL,
    support NUMERIC(12,8) NOT NULL,
    confidence_p1 NUMERIC(12,8) NOT NULL,
    confidence_p2 NUMERIC(12,8) NOT NULL,
    lift NUMERIC(8,4) NOT NULL,
    support_pct NUMERIC(10,4) NOT NULL DEFAULT 0,
    confidence_p1_pct NUMERIC(10,4) NOT NULL DEFAULT 0,
    confidence_p2_pct NUMERIC(10,4) NOT NULL DEFAULT 0,
    nb_transactions INTEGER NOT NULL DEFAULT 0
);

-- Indexes for fast filtering
CREATE INDEX idx_bar_support ON basket_analysis_results(support DESC);
CREATE INDEX idx_bar_lift ON basket_analysis_results(lift DESC);
CREATE INDEX idx_bar_product1 ON basket_analysis_results(product1);
CREATE INDEX idx_bar_product2 ON basket_analysis_results(product2);
CREATE INDEX idx_bar_basket_label ON basket_analysis_results(basket_label);

-- Grant access
ALTER TABLE basket_analysis_results OWNER TO postgres;
"""
    sql_path = os.path.join(PROJECT_ROOT, "scripts", "create_basket_table.sql")
    with open(sql_path, 'w') as f:
        f.write(sql.strip() + "\n")
    print(f"   ✓ SQL created at {sql_path}")

    # ── 6. Generate COPY SQL for loading ──
    copy_sql = f"""-- Load basket_analysis_results.csv into PostgreSQL
-- Run from the Bi/ directory (where the CSV is located)

COPY basket_analysis_results(product1, product2, basket_label, support, confidence_p1, confidence_p2, lift, support_pct, confidence_p1_pct, confidence_p2_pct, nb_transactions)
FROM '{OUTPUT_CSV}'
DELIMITER ','
CSV HEADER;
"""
    copy_path = os.path.join(PROJECT_ROOT, "scripts", "load_basket_table.sql")
    with open(copy_path, 'w') as f:
        f.write(copy_sql.strip() + "\n")
    print(f"   ✓ COPY SQL created at {copy_path}")

    print(f"\n{'='*60}")
    print("✅ Done! Next steps:")
    print(f"   1. Run: psql -d grocery_db -f scripts/create_basket_table.sql")
    print(f"   2. Run: psql -d grocery_db -f scripts/load_basket_table.sql")
    print(f"   3. Update backend to query basket_analysis_results table")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
