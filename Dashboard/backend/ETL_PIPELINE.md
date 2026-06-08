# 🔄 ETL Pipeline — Grocery Sales Data Warehouse

## 1. Overview

This document describes the complete ETL (Extract, Transform, Load) pipeline used to build the Grocery Sales Data Warehouse from raw CSV files into a star-schema PostgreSQL database.

### Source Systems

| Source | Format | Location | Records |
|--------|--------|----------|---------|
| `categories.csv` | CSV | `scripts/dataset/` | 11 rows |
| `products.csv` | CSV | `scripts/dataset/` | ~450 rows |
| `customers.csv` | CSV | `scripts/dataset/` | ~100,000 rows |
| `employees.csv` | CSV | `scripts/dataset/` | ~50 rows |
| `cities.csv` | CSV | `scripts/dataset/` | ~1,000 rows |
| `countries.csv` | CSV | `scripts/dataset/` | ~100 rows |
| `sales.csv` | CSV | `scripts/dataset/` | ~6,690,599 rows |

### Target Database

- **Engine**: PostgreSQL 16
- **Database**: `grocery_sales`
- **Schema**: `public` (star schema: 5 dimension tables + 1 fact table + 5 materialized views)

---

## 2. ETL Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          EXTRACT                                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │categories│ │ products │ │ customers│ │employees │ │  sales   │ │
│  │   .csv   │ │   .csv   │ │   .csv   │ │   .csv   │ │   .csv   │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
├───────┼────────────┼────────────┼────────────┼────────────┼───────┤
│                     TRANSFORM (Python pandas)                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ • Parse & coerce dates                                       │   │
│  │ • Remove rows with null SalesDate (~67K rows)                │   │
│  │ • Rename columns to lowercase snake_case                     │   │
│  │ • Sort & deduplicate dimension records                       │   │
│  │ • Enrich customers with city/country (joins)                 │   │
│  │ • Enrich products with category name (join)                  │   │
│  │ • Enrich employees with city name (join)                     │   │
│  │ • Generate dim_date from sales date range                    │   │
│  │ • Truncate time to HH:MM:SS format                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
├───────────────────────────────────────────────────────────────────┤
│                           LOAD                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │dim_cat.  │ │dim_prod. │ │dim_cust. │ │dim_emp.  │ │dim_date│ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                     fact_sales (~6.7M rows)                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
├───────────────────────────────────────────────────────────────────┤
│                      MATERIALIZED VIEWS                            │
│  • mv_daily_sales           • mv_monthly_sales                    │
│  • mv_customer_segmentation • mv_top_products                     │
│  • mv_employee_performance                                       │
└───────────────────────────────────────────────────────────────────┘
```

---

## 3. Step-by-Step Transformation Rules

### 3.1 Extract Phase — CSV Loading

All 7 CSV files are loaded using `pandas.read_csv()` with default settings (comma separator, header inference).

**Validation performed:**
- File existence check before read
- Column count match vs. expected schema
- Data type inference check

### 3.2 Transform Phase — Data Cleaning

#### 3.2.1 Date Cleaning (Step 0.1)

| Rule | Description | Rationale |
|------|-------------|-----------|
| `SalesDate` parsing | Convert to datetime with `errors='coerce'` | Handles malformed dates |
| Millisecond truncation | Floor to seconds via `.dt.floor('S')` | Aligns with fact_sales granularity |
| Null date removal | Drop rows where `SalesDate` is NaT | ~67,526 invalid rows removed |
| Date/Time split | Extract `.dt.date` and `.dt.time` | Enables date-only joins & time analysis |

**Assumption**: Rows with null `SalesDate` (~1% of total) are excluded from analysis. This is acceptable as it represents a small fraction of data.

#### 3.2.2 Column Standardization

All column names are converted to **lowercase snake_case** using explicit mapping:

| Source Column | Target Column | Table |
|--------------|---------------|-------|
| `SalesID` | `salesid` | fact_sales |
| `SalesPersonID` | `employeeid` | fact_sales |
| `CustomerID` | `customerid` | fact_sales, dim_customer |
| `ProductID` | `productid` | fact_sales, dim_product |
| `FirstName` (customers) | `customerfirstname` | dim_customer |
| `FirstName` (employees) | `employeefirstname` | dim_employee |
| `CityName` | `city` | dim_customer, dim_employee |
| `CountryName` | `country` | dim_customer |
| `TotalPrice` | `totalprice` | fact_sales |
| `Class` | `class` | dim_product |

**Business Logic**: Suffix disambiguation (`_x`/`_y`) is resolved by explicit rename — no automatic suffix deletion to avoid data loss.

### 3.3 Transform Phase — Data Enrichment

#### 3.3.1 Product Enrichment
- `dim_product.categoryname` is populated by joining `products.csv` → `categories.csv` on `CategoryID`
- This denormalizes the category name into the product dimension for faster queries

#### 3.3.2 Customer Enrichment
- `dim_customer.city`, `zipcode`, `countryid` are populated by joining `customers.csv` → `cities.csv` on `CityID`
- `dim_customer.country`, `countrycode` are populated by joining → `countries.csv` on `CountryID`
- Full name is generated as `TRIM(firstname || ' ' || COALESCE(middleinitial || ' ', '') || lastname)`

#### 3.3.3 Employee Enrichment
- `dim_employee.city` is populated by mapping `cityid` → `CityName` from `cities.csv`
- Full name is generated as `TRIM(firstname || ' ' || lastname)`

### 3.4 Transform Phase — Dimension Date Generation

The `dim_date` table is generated programmatically from the sales date range:

```python
min_date = sales['SalesDate'].min().date()
max_date = sales['SalesDate'].max().date()
# Generates all dates between min and max
```

**Derived columns:**
| Column | Derivation |
|--------|-----------|
| `year` | `date.year` |
| `quarter` | `(month - 1) // 3 + 1` |
| `month` | `date.month` |
| `month_name` | `date.strftime('%B')` |
| `day` | `date.day` |
| `day_of_week` | `date.isoweekday()` |
| `day_name` | `date.strftime('%A')` |
| `week_of_year` | `date.isocalendar()[1]` |
| `is_weekend` | `date.weekday() >= 5` |

**Business Rule**: The date dimension covers the complete range from first sale to last sale, enabling time-intelligence calculations (YTD, YoY, MoM).

### 3.5 Load Phase

#### 3.5.1 Dimension Loading

| Table | Strategy | Chunk Size | Uniqueness |
|-------|----------|------------|------------|
| `dim_category` | `method="multi"` INSERT | Single batch | PK constraint |
| `dim_product` | `method="multi"` INSERT | Single batch | PK constraint |
| `dim_customer` | `method="multi"` INSERT | Single batch | PK constraint |
| `dim_employee` | `method="multi"` INSERT | Single batch | PK constraint |
| `dim_date` | `method="multi"` INSERT | Single batch | PK constraint |

#### 3.5.2 Fact Table Loading

| Parameter | Value |
|-----------|-------|
| Table | `fact_sales` |
| Method | `method="multi"` INSERT |
| Chunk Size | 5,000 rows (to stay under PostgreSQL's 65,535 parameter limit) |
| Total Rows | ~6,690,599 |
| Expected Duration | ~10–20 min |

### 3.6 Materialized View Refresh

After data loading, 5 materialized views are refreshed (in order):

1. `mv_daily_sales` — Daily sales aggregations by product, employee, customer
2. `mv_monthly_sales` — Monthly aggregations by category, gender, country
3. `mv_customer_segmentation` — Customer segments (VIP, Regular, Occasional, New)
4. `mv_top_products` — Product ranking by revenue and volume
5. `mv_employee_performance` — Employee performance metrics

**Note**: These views use `REFRESH MATERIALIZED VIEW` (not CONCURRENTLY) for simplicity.

---

## 4. Business Rules & Data Validation

### 4.1 Constraint Checks

| Constraint | Table | Rule | Action on Violation |
|------------|-------|------|-------------------|
| PK Uniqueness | All dims | No duplicate IDs | Error — deduplicate source |
| `chk_quantity` | fact_sales | `quantity >= 0` | Reject row |
| `chk_totalprice` | fact_sales | `totalprice >= 0` | Reject row |
| `chk_discount` | fact_sales | `discount >= 0` | Reject row |
| `chk_quarter` | dim_date | `quarter BETWEEN 1 AND 4` | Error — fix generation |
| `chk_month` | dim_date | `month BETWEEN 1 AND 12` | Error — fix generation |
| FK `employeeid` | fact_sales | References `dim_employee` | Error — load employees first |
| FK `customerid` | fact_sales | References `dim_customer` | Error — load customers first |
| FK `productid` | fact_sales | References `dim_product` | Error — load products first |
| FK `date` | fact_sales | References `dim_date` | Error — generate dates first |

### 4.2 Data Quality Rules

| Rule | Check | Severity |
|------|-------|----------|
| Missing SalesDate | `dropna(subset=['SalesDate'])` | HIGH (~1% rows removed) |
| Negative Quantity | `quantity >= 0` | HIGH |
| Negative Price | `totalprice >= 0` | HIGH |
| Duplicate Transaction | `transactionnumber` uniqueness | MEDIUM |
| Invalid Foreign Key | FK constraints | HIGH |
| Date range consistency | fact_sales.date within dim_date range | MEDIUM |

### 4.3 Business Assumptions

1. **67,526 rows** with null `SalesDate` are excluded (~1%). These are considered corrupt and not recoverable.
2. **TotalPrice = 0** for many rows is valid — these may represent promotional or zero-value transactions.
3. All dimensions are loaded **before** the fact table to respect foreign key constraints.
4. The `dim_date` table covers the exact date range present in sales data.
5. Time values are truncated to `HH:MM:SS`; microsecond precision is discarded.

---

## 5. Apache Hop Pipeline Reference

The project also includes an Apache Hop pipeline (`Dimension_Pipeline.hpl`) that performs the same ETL using a visual tool:

### Pipeline Flow

```
CSV file input (grocery_sales_denormalized.csv)
├── Sort → Unique → Select → dim_category
├── Sort → Unique → Select → dim_product  
├── Sort → Unique → Select → dim_customer
├── Sort → Unique → Select → dim_employee
└── Select → Bulk Load → fact_sales
```

### Differences: Hop vs. Python Backend

| Aspect | Apache Hop | Python Backend |
|--------|------------|----------------|
| Source | Single denormalized CSV | 7 normalized CSVs |
| Date handling | Hop date mask `yyyy-MM-dd HH:mm:ss.SSS` | pandas `pd.to_datetime` |
| Deduplication | `Sort → Unique` transform | PK constraints + pandas |
| Fact loading | PostgreSQL Bulk Loader | SQLAlchemy `method="multi"` |
| Enrichment | Pre-joined in source CSV | Explicit joins in script |

---

## 6. Execution

### Run the Full ETL

```bash
cd Dashboard/backend
source .venv/bin/activate
python scripts/load_data.py --reset
```

### Run Without Reset (Append Only)

```bash
python scripts/load_data.py
```

### Refresh Materialized Views Only

```bash
python -c "
from sqlalchemy import create_engine, text
engine = create_engine('postgresql://postgres:postgres@localhost:5432/grocery_sales')
views = ['mv_daily_sales','mv_monthly_sales','mv_customer_segmentation','mv_top_products','mv_employee_performance']
for v in views:
    with engine.connect() as c:
        c.execute(text(f'REFRESH MATERIALIZED VIEW {v}'))
        c.commit()
    print(f'  Refreshed {v}')
"
```

---

## 7. Monitoring & Logging

| Metric | Expected | How to Monitor |
|--------|----------|----------------|
| Total fact rows | ~6,690,599 | `SELECT COUNT(*) FROM fact_sales` |
| Null SalesDate dropped | ~67,526 | Run count before/after drop |
| dim_date range | ~2017-01 to 2018-05 | `SELECT MIN(date), MAX(date) FROM fact_sales` |
| ETL duration | 10–20 min | Time the script execution |
| Materialized view refresh | ~2 min each | Check timestamps |

---

## 8. Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `UniqueViolation` | Duplicate PK in source | Use `--reset` or clean source data |
| `ForeignKeyViolation` | Missing dimension key | Ensure dimensions loaded before facts |
| `ParameterLimitExceeded` | Chunk too large (PostgreSQL 65K param limit) | Reduce `chunksize` (currently 5,000) |
| `FileNotFoundError` | CSV path incorrect | Check `DATASET_PATH` in script |
| `DataError` | Type mismatch or value truncation | Check column types and string lengths |
