"""Analyze the grocery sales data for the analytical report."""

from sqlalchemy import create_engine, text
from datetime import datetime

engine = create_engine("postgresql://postgres:postgres@localhost:5432/grocery_sales")

print("=" * 70)
print("  GROCERY SALES DATA ANALYSIS")
print("=" * 70)

with engine.connect() as c:

    # ── 1. OVERALL KPIs ──
    print("\n## 1. OVERALL KPIs\n")

    qty = c.execute(text("SELECT SUM(quantity) FROM fact_sales")).scalar()
    txn = c.execute(text("SELECT COUNT(DISTINCT transactionnumber) FROM fact_sales")).scalar()
    cust = c.execute(text("SELECT COUNT(DISTINCT customerid) FROM fact_sales")).scalar()
    emp_count = c.execute(text("SELECT COUNT(DISTINCT employeeid) FROM fact_sales")).scalar()
    prod = c.execute(text("SELECT COUNT(*) FROM dim_product")).scalar()
    cat = c.execute(text("SELECT COUNT(*) FROM dim_category")).scalar()

    # Computed revenue
    rev = c.execute(text("""
        SELECT SUM(s.quantity * p.price) FROM fact_sales s
        JOIN dim_product p ON s.productid = p.productid
    """)).scalar()

    avg_basket = c.execute(text("""
        SELECT SUM(s.quantity * p.price) / NULLIF(COUNT(DISTINCT s.transactionnumber), 0)
        FROM fact_sales s JOIN dim_product p ON s.productid = p.productid
    """)).scalar()

    nosales = c.execute(text("""
        SELECT COUNT(*) FROM dim_product p
        LEFT JOIN fact_sales s ON p.productid = s.productid
        WHERE s.productid IS NULL
    """)).scalar()

    print(f"  💰 Total Revenue (computed):    {rev:>18,.2f}")
    print(f"  📦 Total Quantity Sold:         {qty:>18,}")
    print(f"  🧾 Total Transactions:          {txn:>18,}")
    print(f"  🛒 Average Basket Value:        {avg_basket:>18,.2f}")
    print(f"  👥 Active Customers:            {cust:>18,}")
    print(f"  👔 Active Employees:            {emp_count:>18,}")
    print(f"  📋 Total Products:              {prod:>18,}")
    print(f"  🏷️  Categories:                  {cat:>18,}")
    print(f"  ❌ Products with Zero Sales:    {nosales:>18,}")

    # ── 2. SALES ANALYSIS ──
    print("\n## 2. SALES ANALYSIS\n")

    print("### Revenue by Category\n")
    rows = c.execute(text("""
        SELECT p.categoryname,
               ROUND(SUM(s.quantity * p.price)::numeric, 2) as revenue,
               SUM(s.quantity) as quantity,
               COUNT(DISTINCT s.transactionnumber) as transactions,
               COUNT(DISTINCT s.customerid) as customers
        FROM fact_sales s
        JOIN dim_product p ON s.productid = p.productid
        GROUP BY p.categoryname
        ORDER BY revenue DESC
    """)).all()
    total_rev = sum(r.revenue for r in rows)
    print(f"  {'Category':20s} {'Revenue':>14s} {'%':>7s} {'Qty':>10s} {'Txns':>8s}")
    print("  " + "-" * 60)
    for r in rows:
        pct = r.revenue / total_rev * 100 if total_rev else 0
        print(f"  {r.categoryname:20s} {r.revenue:>14,.2f} {pct:>6.1f}% {r.quantity:>10,} {r.transactions:>8,}")

    print("\n### Monthly Revenue Trend\n")
    rows = c.execute(text("""
        SELECT d.year, d.month, d.month_name,
               ROUND(SUM(s.quantity * p.price)::numeric, 2) as revenue,
               SUM(s.quantity) as quantity,
               COUNT(DISTINCT s.transactionnumber) as transactions
        FROM fact_sales s
        JOIN dim_product p ON s.productid = p.productid
        JOIN dim_date d ON s.date = d.date_key
        GROUP BY d.year, d.month, d.month_name, d.quarter
        ORDER BY d.year, d.month
    """)).all()
    print(f"  {'Month':15s} {'Revenue':>14s} {'Qty':>10s} {'Txns':>8s}")
    print("  " + "-" * 50)
    for r in rows:
        print(f"  {r.year}-{r.month:02d} {r.month_name:8s} {r.revenue:>14,.2f} {r.quantity:>10,} {r.transactions:>8,}")

    print("\n### Top 10 Products by Revenue\n")
    rows = c.execute(text("""
        SELECT p.productname, p.categoryname,
               ROUND(SUM(s.quantity * p.price)::numeric, 2) as revenue,
               SUM(s.quantity) as quantity,
               COUNT(DISTINCT s.transactionnumber) as times_sold
        FROM fact_sales s
        JOIN dim_product p ON s.productid = p.productid
        GROUP BY p.productid, p.productname, p.categoryname
        ORDER BY revenue DESC
        LIMIT 10
    """)).all()
    print(f"  {'#':>3} {'Product':35s} {'Category':15s} {'Revenue':>14s} {'Qty':>8s} {'Sold':>6s}")
    print("  " + "-" * 85)
    for i, r in enumerate(rows, 1):
        print(f"  {i:3d} {r.productname:35s} {r.categoryname:15s} {r.revenue:>14,.2f} {r.quantity:>8,} {r.times_sold:>6,}")

    # ── 3. PRODUCT ANALYSIS ──
    print("\n## 3. PRODUCT ANALYSIS\n")

    avg_price = c.execute(text("SELECT AVG(price) FROM dim_product")).scalar()
    min_price = c.execute(text("SELECT MIN(price) FROM dim_product")).scalar()
    max_price = c.execute(text("SELECT MAX(price) FROM dim_product")).scalar()
    print(f"  Average Price: {avg_price:,.2f}")
    print(f"  Price Range: {min_price:,.2f} - {max_price:,.2f}")

    print("\n### Price Distribution\n")
    rows = c.execute(text("""
        SELECT CASE
            WHEN price < 10 THEN '0-10'
            WHEN price < 20 THEN '10-20'
            WHEN price < 30 THEN '20-30'
            WHEN price < 50 THEN '30-50'
            WHEN price < 100 THEN '50-100'
            ELSE '100+'
        END as range,
        COUNT(*) as products,
        ROUND(AVG(price)::numeric, 2) as avg_price
        FROM dim_product
        GROUP BY range ORDER BY MIN(price)
    """)).all()
    for r in rows:
        print(f"  {r.range:>8s}€: {r.products:>4d} products (avg {r.avg_price:>7.2f}€)")

    print("\n### Sales by Resistance\n")
    rows = c.execute(text("""
        SELECT p.resistant,
               COUNT(DISTINCT p.productid) as products,
               SUM(s.quantity) as quantity,
               ROUND(SUM(s.quantity * p.price)::numeric, 2) as revenue
        FROM dim_product p
        LEFT JOIN fact_sales s ON p.productid = s.productid
        GROUP BY p.resistant
        ORDER BY revenue DESC
    """)).all()
    for r in rows:
        print(f"  {r.resistant:15s} {r.products:>4d} products  {r.quantity:>10,} qty  {r.revenue:>14,.2f} rev")

    # ── 4. CUSTOMER ANALYSIS ──
    print("\n## 4. CUSTOMER ANALYSIS\n")

    segs = c.execute(text("""
        WITH cust_stats AS (
            SELECT customerid,
                   COUNT(DISTINCT transactionnumber) as freq,
                   SUM(quantity * p.price) as spent,
                   MIN(date) as first_purchase,
                   MAX(date) as last_purchase
            FROM fact_sales s
            JOIN dim_product p ON s.productid = p.productid
            GROUP BY customerid
        )
        SELECT CASE
            WHEN spent > 10000 AND freq > 5 THEN 'VIP'
            WHEN spent > 3000 THEN 'Regular'
            WHEN freq > 0 THEN 'Occasional'
            ELSE 'New'
        END as segment,
        COUNT(*) as customers,
        ROUND(AVG(spent)::numeric, 2) as avg_spent,
        ROUND(SUM(spent)::numeric, 2) as total_revenue
        FROM cust_stats
        GROUP BY segment ORDER BY total_revenue DESC
    """)).all()
    print(f"  {'Segment':15s} {'Customers':>10s} {'Avg Spent':>12s} {'Total Rev':>14s}")
    print("  " + "-" * 53)
    for r in segs:
        print(f"  {r.segment:15s} {r.customers:>10,} {r.avg_spent:>12,.2f} {r.total_revenue:>14,.2f}")

    print("\n### Top 10 Customers\n")
    rows = c.execute(text("""
        SELECT c.full_name, c.country,
               ROUND(SUM(s.quantity * p.price)::numeric, 2) as spent,
               COUNT(DISTINCT s.transactionnumber) as transactions
        FROM fact_sales s
        JOIN dim_customer c ON s.customerid = c.customerid
        JOIN dim_product p ON s.productid = p.productid
        GROUP BY c.customerid, c.full_name, c.country
        ORDER BY spent DESC
        LIMIT 10
    """)).all()
    for i, r in enumerate(rows, 1):
        print(f"  {i:2d}. {r.full_name:30s} {r.country:15s} {r.spent:>12,.2f} ({r.transactions:>4d} txns)")

    # ── 5. EMPLOYEE ANALYSIS ──
    print("\n## 5. EMPLOYEE ANALYSIS\n")

    print("### Top 5 Employees\n")
    rows = c.execute(text("""
        SELECT e.full_name, e.gender,
               ROUND(SUM(s.quantity * p.price)::numeric, 2) as revenue,
               COUNT(DISTINCT s.transactionnumber) as transactions,
               COUNT(DISTINCT s.customerid) as customers_served
        FROM fact_sales s
        JOIN dim_employee e ON s.employeeid = e.employeeid
        JOIN dim_product p ON s.productid = p.productid
        GROUP BY e.employeeid, e.full_name, e.gender
        ORDER BY revenue DESC
        LIMIT 5
    """)).all()
    for i, r in enumerate(rows, 1):
        print(f"  {i:2d}. {r.full_name:25s} {r.gender:8s} {r.revenue:>12,.2f}  ({r.transactions:>5d} txns, {r.customers_served:>5d} customers)")

    # ── 6. TIME INTELLIGENCE ──
    print("\n## 6. TIME INTELLIGENCE\n")

    # Day of week analysis
    rows = c.execute(text("""
        SELECT d.day_name, d.is_weekend,
               COUNT(DISTINCT s.transactionnumber) as transactions,
               ROUND(SUM(s.quantity * p.price)::numeric, 2) as revenue
        FROM fact_sales s
        JOIN dim_product p ON s.productid = p.productid
        JOIN dim_date d ON s.date = d.date_key
        GROUP BY d.day_name, d.is_weekend
        ORDER BY revenue DESC
    """)).all()
    print("  Revenue by Day of Week:")
    for r in rows:
        w = "📅" if not r.is_weekend else "🎉"
        print(f"  {w} {r.day_name:12s}  {r.revenue:>14,.2f}  ({r.transactions:>6,} txns)")

    # Date range
    dr = c.execute(text("SELECT MIN(date), MAX(date) FROM fact_sales")).first()
    print(f"\n  📆 Date Range: {dr[0]} to {dr[1]}")

print("\n" + "=" * 70)
print("  ANALYSIS COMPLETE")
print("=" * 70)
