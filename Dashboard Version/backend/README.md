# 🧩 Grocery Sales Dashboard — Backend

> **Part of Approach 2 (Code)** — Full-stack web dashboard backend built with FastAPI, SQLAlchemy, and PostgreSQL.  
> 📁 Location: `Dashboard Version/backend/`

This document provides a comprehensive overview of the backend architecture, from the directory structure down to each module's purpose, design rationale, and contribution to the overall system. It is intended to serve as a reference for the final project report and to facilitate understanding of the development process and technical decisions.

---

## 📑 Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Directory Structure](#2-directory-structure)
3. [Layer-by-Layer Breakdown](#3-layer-by-layer-breakdown)
   - [3.1 Core Layer](#31-core-layer)
   - [3.2 Models Layer (SQLAlchemy ORM)](#32-models-layer-sqlalchemy-orm)
   - [3.3 Repositories Layer (Data Access)](#33-repositories-layer-data-access)
   - [3.4 Services Layer (Business Logic)](#34-services-layer-business-logic)
   - [3.5 Schemas Layer (Pydantic Validation)](#35-schemas-layer-pydantic-validation)
   - [3.6 API Layer (FastAPI Routers)](#36-api-layer-fastapi-routers)
   - [3.7 ETL Layer (Data Pipeline)](#37-etl-layer-data-pipeline)
   - [3.8 Utils Layer](#38-utils-layer)
4. [Data Model](#4-data-model)
5. [ETL Pipeline](#5-etl-pipeline)
6. [Analytical Insights Summary](#6-analytical-insights-summary)
7. [API Endpoints Reference](#7-api-endpoints-reference)
8. [Local Setup](#8-local-setup)
9. [Configuration & Environment](#9-configuration--environment)
10. [Technical Decisions & Rationale](#10-technical-decisions--rationale)
11. [Testing & Validation](#11-testing--validation)
12. [Future Improvements](#12-future-improvements)

---

## 1. Architecture Overview

The backend follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     FASTAPI (API Layer)                      │
│  dashboard │ sales │ products │ customers │ employees       │
│  basket │ filters │ insights                                 │
├─────────────────────────────────────────────────────────────┤
│                   SERVICES (Business Logic)                  │
│  DashboardService │ ProductService │ CustomerService         │
│  EmployeeService │ BasketService                              │
├─────────────────────────────────────────────────────────────┤
│               REPOSITORIES (Data Access)                     │
│  DashboardRepository (single repository for all queries)     │
├─────────────────────────────────────────────────────────────┤
│              SQLALCHEMY MODELS (ORM Layer)                   │
│  DimCategory │ DimProduct │ DimCustomer │ DimEmployee        │
│  DimDate │ FactSales                                         │
├─────────────────────────────────────────────────────────────┤
│                    POSTGRESQL DATABASE                       │
│  Tables │ Materialized Views │ Indexes │ Constraints         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     ETL PIPELINE (Sidecar)                    │
│  Extractor → Transformer → Validator → Loader → Sync        │
│  Reads CSV files → Cleans & enriches → Loads to PostgreSQL   │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

| Principle | Application |
|-----------|-------------|
| **Separation of Concerns** | Each layer (API → Service → Repository → Model) has a single responsibility |
| **Dependency Injection** | Database sessions are injected via FastAPI's `Depends()` |
| **Caching** | In-memory cache decorator for expensive aggregated queries |
| **Materialized Views** | Pre-computed aggregations for sub-second dashboard loads |
| **Optimized Bulk Loading** | Uses PostgreSQL `COPY` for large tables (>100K rows), ~10-50x faster than INSERT |
| **Pydantic Validation** | Strict input/output schemas with automatic OpenAPI documentation |

---

## 2. Directory Structure

```
backend/
├── .env                           # Environment variables (DB credentials, cache TTL)
├── .env.example                   # Example environment file
├── .gitignore
├── requirements.txt               # Python dependencies
├── run_pipeline.py                # Quick script to run the ETL pipeline
├── ANALYSIS_INSIGHTS.md           # Detailed analytical insights from the data
├── ETL_PIPELINE.md                # Full ETL pipeline documentation
├── README.md                      # This file
│
├── alembic/                       # Database migration directory (currently empty)
│
├── scripts/
│   ├── load_all_data.py           # Standalone CSV-to-PostgreSQL loader
│   ├── analyze_data.py            # Data analysis script
│   └── data/                      # CSV data files for import
│       ├── dim_category.csv
│       ├── dim_customer.csv
│       ├── dim_employee.csv
│       ├── dim_product.csv
│       └── fact_sales.csv
│
└── app/
    ├── __init__.py
    ├── main.py                    # FastAPI application entry point
    │
    ├── core/
    │   ├── __init__.py
    │   ├── config.py              # Pydantic-settings configuration
    │   └── database.py            # SQLAlchemy engine & session management
    │
    ├── models/
    │   ├── __init__.py
    │   ├── dim_category.py        # Category dimension
    │   ├── dim_customer.py        # Customer dimension
    │   ├── dim_date.py            # Date dimension
    │   ├── dim_employee.py        # Employee dimension
    │   ├── dim_product.py         # Product dimension
    │   └── fact_sales.py          # Sales fact table
    │
    ├── schemas/
    │   ├── __init__.py
    │   ├── analytics.py           # Advanced analytics schemas
    │   ├── basket.py              # Basket analysis schemas
    │   ├── customer.py            # Customer schemas
    │   ├── dashboard.py           # Dashboard & KPI schemas
    │   ├── employee.py            # Employee schemas
    │   ├── filters.py             # Filter options schema
    │   └── product.py             # Product schemas
    │
    ├── repositories/
    │   ├── __init__.py
    │   └── dashboard_repository.py # Single repository for all queries
    │
    ├── services/
    │   ├── __init__.py
    │   ├── dashboard_service.py   # Dashboard KPIs & summary
    │   ├── product_service.py     # Product analytics
    │   ├── customer_service.py    # Customer analytics
    │   ├── employee_service.py    # Employee analytics
    │   └── basket_service.py      # Market basket analysis
    │
    ├── api/
    │   ├── __init__.py
    │   ├── dashboard.py           # GET /api/dashboard/summary
    │   ├── sales.py               # GET /api/sales/*
    │   ├── products.py            # GET /api/products/*
    │   ├── customers.py           # GET /api/customers/*
    │   ├── employees.py           # GET /api/employees/*
    │   ├── basket.py              # GET /api/basket/analysis
    │   ├── filters.py             # GET /api/filters/
    │   └── insights.py            # GET /api/insights/*
    │
    ├── etl/
    │   ├── __init__.py
    │   ├── pipeline.py            # ETL orchestrator
    │   ├── extractor.py           # CSV reading & validation
    │   ├── transformer.py         # Data cleaning & enrichment
    │   ├── validator.py           # Business rules validation engine
    │   ├── loader.py              # PostgreSQL bulk loading (COPY/INSERT)
    │   └── sync.py                # Database health & integrity checks
    │
    └── utils/
        ├── __init__.py
        ├── cache.py               # In-memory caching decorator
        └── helpers.py             # Formatting & serialization utilities
```

---

## 3. Layer-by-Layer Breakdown

### 3.1 Core Layer

**Files**: `core/config.py`, `core/database.py`

#### `core/config.py` — Application Configuration

```python
class Settings(BaseSettings):
    APP_NAME: str = "Grocery Sales Dashboard API"
    APP_VERSION: str = "1.0.0"
    POSTGRES_USER / PASSWORD / HOST / PORT / DB
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
```

**Purpose**: Centralizes all configuration using `pydantic-settings`. Reads from environment variables and a `.env` file.

**Key design decisions**:
- **`@property` for `DATABASE_URL`**: Computes the connection string dynamically from individual components, avoiding hardcoded URLs.
- **Separate sync/async URLs**: Provides both `DATABASE_URL` (for SQLAlchemy sync) and `DATABASE_URL_ASYNC` (for future async migration).
- **`.env` file support**: Uses `pydantic-settings` to load a `.env` file, keeping secrets out of code.
- **Typed settings**: All settings are type-annotated, ensuring validation at startup.

#### `core/database.py` — Database Engine & Sessions

```python
engine = create_engine(settings.DATABASE_URL, pool_size=20, ...)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():  # FastAPI dependency
    db = SessionLocal()
    yield db
    db.close()
```

**Purpose**: Creates the SQLAlchemy engine and provides a session dependency for FastAPI.

**Key design decisions**:
- **Connection pool of 20**: Handles concurrent dashboard requests without creating new connections each time.
- **`pool_pre_ping=True**: Tests connections before use, preventing stale connection errors.
- **`pool_recycle=3600`**: Recycles connections after 1 hour to avoid PostgreSQL timeouts.
- **Generator-based session**: The `get_db()` function uses `yield` to allow FastAPI's dependency injection to manage session lifecycle — the session is automatically closed when the request ends, even if an exception occurs.

---

### 3.2 Models Layer (SQLAlchemy ORM)

**Folder**: `models/`

Six models representing the **star schema**:

| Model | Table | Type | Key Fields |
|-------|-------|------|------------|
| `DimCategory` | `dim_category` | Dimension | `categoryid` (PK), `categoryname` |
| `DimProduct` | `dim_product` | Dimension | `productid` (PK), `productname`, `price`, `categoryid` (FK→dim_category), `class`, `resistant`, `isallergic`, `vitalitydays`, `categoryname` |
| `DimCustomer` | `dim_customer` | Dimension | `customerid` (PK), name fields, `city`, `country`, `countrycode` |
| `DimEmployee` | `dim_employee` | Dimension | `employeeid` (PK), name fields, `birthdate`, `gender`, `hiredate`, `city` |
| `DimDate` | `dim_date` | Dimension | `date_key` (PK), `year`, `quarter`, `month`, `day`, `day_of_week`, `is_weekend` |
| `FactSales` | `fact_sales` | Fact | `salesid` (PK), `employeeid` (FK), `customerid` (FK), `productid` (FK), `date` (FK), `quantity`, `discount`, `totalprice` |

**Design rationale**:
- **Star schema**: Chosen for analytical queries — denormalized dimensions allow fast aggregations without complex joins.
- **FK constraints**: Enforce referential integrity at the database level, preventing orphan records.
- **`categoryname` in `dim_product`**: Denormalized from `dim_category` to avoid a join in every product query — a common data warehouse optimization.
- **`Date` as FK in `fact_sales`**: Links to `dim_date` for time-intelligence calculations (YoY, MoM, YTD).

---

### 3.3 Repositories Layer (Data Access)

**File**: `repositories/dashboard_repository.py`

**Purpose**: Single repository class that encapsulates **all database queries** — from simple lookups to complex analytical aggregations.

**Key design decisions**:

1. **Single repository pattern**: Instead of one repository per entity, a single `DashboardRepository` handles all queries. This is intentional:
   - Analytical dashboards often need data from multiple tables in a single request (e.g., KPIs + time series + categories).
   - Avoids circular dependencies between repositories.
   - Simplifies transaction management.

2. **Materialized view optimization**: Heavy aggregations query pre-built materialized views instead of raw fact tables:

   ```python
   # Uses mv_daily_sales (pre-aggregated, ~99.9% fewer rows than fact_sales)
   def get_all_kpis(self, start_date=None, end_date=None):
       query = "SELECT ... FROM mv_daily_sales WHERE ..."
   ```

3. **Dynamic filter application**: Helper methods `_apply_date_filter()` and `_apply_filters()` add WHERE clauses dynamically based on user-provided filters, preventing SQL injection via parameterized queries.

4. **Fallback strategy**: If materialized views return no results (e.g., with date filters outside their range), the repository falls back to querying `fact_sales` directly.

**Queries implemented**:
- `get_all_kpis()` — Single query returning all 6 KPIs (revenue, quantity, transactions, avg basket, customers, products)
- `get_monthly_revenue()` — Time series with YoY comparison
- `get_sales_by_category()` — Category breakdown with percentages
- `get_price_distribution()` — Price range buckets
- `get_price_volume_matrix()` — Scatter plot data
- `get_customer_segments()` — VIP/Regular/Occasional segmentation
- `get_basket_rules()` — Market basket association rules (support, confidence, lift)
- `get_filter_options()` — Dynamic filter values for the frontend
- `get_revenue_concentration()` / `get_revenue_by_day_of_week()` / etc. — Advanced insights

---

### 3.4 Services Layer (Business Logic)

**Folder**: `services/`

Five service classes that **orchestrate business logic**:

| Service | File | Responsibility |
|---------|------|----------------|
| `DashboardService` | `dashboard_service.py` | Builds the complete dashboard summary: KPIs, time series, category breakdown, monthly seasonality, top products |
| `ProductService` | `product_service.py` | Product detail, product listing with revenue rank, price distribution buckets, price-volume scatter matrix |
| `CustomerService` | `customer_service.py` | Customer segmentation (VIP/Regular/Occasional), top customers, activity over time |
| `EmployeeService` | `employee_service.py` | Top employees, performance by age group, performance by seniority |
| `BasketService` | `basket_service.py` | Market basket analysis: association rules filtered by support/lift, top rules, scatter matrix data |

**Design rationale**:
- **Thin services**: Each service is a thin layer that calls the repository, transforms raw data into Pydantic schemas, and applies caching.
- **Caching decorator**: The `@cached()` decorator (from `utils/cache.py`) caches expensive method results for `CACHE_TTL_SECONDS` (default 5 minutes). Cache keys include method arguments so different filters are cached independently.
- **Decimal precision**: All monetary values use Python's `Decimal` type to avoid floating-point rounding errors.
- **Error handling**: Services return `None` for not-found entities (e.g., `ProductService.get_product_detail()`), which the API layer converts to HTTP 404.

**Example flow** — `DashboardService.get_dashboard_summary()`:

```
1. Check cache → miss
2. Call repo.get_all_kpis() → single query → 6 KPIs
3. Call repo.get_monthly_revenue() → time series data
4. Call repo.get_sales_by_category() → category breakdown
5. Build Pydantic response models
6. Store in cache → return
```

---

### 3.5 Schemas Layer (Pydantic Validation)

**Folder**: `schemas/`

Seven schema modules defining **request/response models**:

| Schema File | Key Models |
|-------------|------------|
| `dashboard.py` | `DashboardSummary`, `KPICard`, `SalesOverTime`, `SalesByCategory`, `SalesByMonth`, `TopProduct` |
| `product.py` | `ProductDetail`, `ProductList`, `PriceDistribution`, `ProductPerformance` |
| `customer.py` | `CustomerSegments`, `TopCustomer`, `CustomerActivity` |
| `employee.py` | `TopEmployee`, `EmployeePerformanceByAge`, `EmployeePerformanceBySeniority` |
| `basket.py` | `BasketAnalysisResult`, `BasketRule` |
| `analytics.py` | `RevenueConcentration`, `DayOfWeekRevenue`, `MomGrowth`, `RFMSegment`, `GeographicDistribution`, `EmployeeParity` |
| `filters.py` | `FilterOptions` |

**Design rationale**:
- **Strict typing**: All fields are type-annotated with `str`, `int`, `Decimal`, `Optional`, etc.
- **Automatic OpenAPI**: FastAPI generates interactive API docs from these schemas at `/api/docs`.
- **Validation**: Pydantic validates incoming query parameters and outgoing responses at runtime.
- **`Decimal` for currency**: Avoids floating-point precision issues common in financial applications.
- **Optional fields**: Fields like `percentage`, `trend`, and `yoy_growth` are optional (`Optional[Decimal]`) since they may not be available for all data points.

---

### 3.6 API Layer (FastAPI Routers)

**Folder**: `api/`

Eight router modules defining **HTTP endpoints**:

| Router | Prefix | Endpoints | Purpose |
|--------|--------|-----------|---------|
| `dashboard.py` | `/api/dashboard` | `GET /summary` | Complete dashboard data with KPIs and charts |
| `sales.py` | `/api/sales` | `GET /over-time`, `/by-category`, `/monthly` | Sales-specific analytics |
| `products.py` | `/api/products` | `GET /`, `/{id}`, `/analytics/price-distribution`, `/analytics/price-volume-matrix` | Product analytics |
| `customers.py` | `/api/customers` | `GET /segments`, `/top`, `/activity`, `/{id}` | Customer analytics |
| `employees.py` | `/api/employees` | `GET /top`, `/performance/by-age`, `/performance/by-seniority`, `/{id}` | Employee analytics |
| `basket.py` | `/api/basket` | `GET /analysis` | Market basket analysis |
| `filters.py` | `/api/filters` | `GET /` | Dynamic filter options |
| `insights.py` | `/api/insights` | `GET /revenue-concentration`, `/revenue-by-day`, `/month-over-month`, `/sales-by-resistance`, `/rfm-segments`, `/geographic-distribution`, `/employee-parity` | Advanced analytical insights |

**Design rationale**:
- **RESTful naming**: Resources are plural (`/products`, `/customers`), IDs are path parameters (`/{id}`), and actions are query parameters.
- **Dependency injection**: Each endpoint receives a DB session via `Depends(get_db)` — FastAPI handles session lifecycle automatically.
- **Query parameters for filtering**: `start_date`, `end_date`, `category`, `product`, `employee` are passed as query parameters, not in the path.
- **CORS enabled**: The app allows all origins (`*`) since the frontend runs on a different port during development.
- **Swagger/OpenAPI**: Docs are served at `/api/docs` (Swagger UI) and `/api/redoc` (ReDoc).

**Endpoint example** — `GET /api/basket/analysis`:

```python
@router.get("/analysis", response_model=BasketAnalysisResult)
def get_basket_analysis(
    min_support: float = Query(0.01, ge=0.001, le=1.0),
    min_lift: float = Query(1.5, ge=1.0),
    limit: int = Query(50, ge=1, le=200),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    service = BasketService(db)
    return service.get_basket_analysis(min_support, min_lift, limit, start_date, end_date)
```

---

### 3.7 ETL Layer (Data Pipeline)

**Folder**: `etl/`

Six modules forming a **complete ETL pipeline** that mirrors the Apache Hop pipeline from Approach 1:

| Module | File | Responsibility |
|--------|------|----------------|
| `pipeline.py` | `pipeline.py` | Orchestrator — coordinates extract, transform, validate, load steps |
| `extractor.py` | `extractor.py` | Reads CSV files, validates existence and structure |
| `transformer.py` | `transformer.py` | Data cleaning, column standardization, enrichment, date generation |
| `validator.py` | `validator.py` | Business rules engine — type-safe validation rules per table |
| `loader.py` | `loader.py` | PostgreSQL loading — uses COPY for large tables, INSERT for small |
| `sync.py` | `sync.py` | Database health checks, schema verification, referential integrity |

#### Pipeline Flow

```
DataExtractor.extract()
    ↓ (raw DataFrames)
TransformPipeline (transformer.py)
    ├── clean_sales_dates()     → Parse dates, drop nulls, split date/time
    ├── standardize_columns()   → Rename to snake_case
    ├── enrich_products()       → Join category names
    ├── enrich_customers()      → Join city/country names
    ├── enrich_employees()      → Join city names
    ├── generate_dim_date()     → Generate date dimension from range
    └── clean_fact_sales()      → Final fact table cleanup
    ↓ (cleaned DataFrames)
DataValidator (validator.py)
    ├── Check PK uniqueness
    ├── Check NOT NULL constraints
    ├── Check positive prices/quantities
    ├── Check FK referential integrity
    └── Report violations
    ↓ (validated DataFrames)
Loader (loader.py)
    ├── load_dataframe(dim_category)   → INSERT (11 rows)
    ├── load_dataframe(dim_product)    → INSERT (~450 rows)
    ├── load_dataframe(dim_customer)   → INSERT (~100K rows)
    ├── load_dataframe(dim_employee)   → INSERT (~50 rows)
    ├── load_dataframe(dim_date)       → INSERT (~130 rows)
    └── load_dataframe(fact_sales)     → COPY (~6.7M rows, ~10-50x faster)
    ↓
DatabaseSynchronizer (sync.py)
    └── refresh_materialized_views()   → 5 views refreshed
```

#### Key Design Decisions

**Loading strategy**: The loader uses **two different methods** depending on table size:

| Table | Rows | Method | Why |
|-------|------|--------|-----|
| `dim_category` | 11 | `INSERT` (multi-row) | Small dataset, not worth COPY overhead |
| `dim_product` | ~450 | `INSERT` (multi-row) | Small dataset |
| `dim_customer` | ~100K | `INSERT` (multi-row) | Under 100K threshold |
| `dim_employee` | ~50 | `INSERT` (multi-row) | Small dataset |
| `dim_date` | ~130 | `INSERT` (multi-row) | Generated, not from CSV |
| `fact_sales` | **~6.7M** | **`COPY` (bulk)** | **10-50x faster** than INSERT for large tables |

The threshold is set at **100K rows** (`COPY_THRESHOLD = 100_000`). Tables above this use PostgreSQL's `COPY FROM` via an in-memory CSV buffer (`StringIO`).

**Validation engine**: The `DataValidator` uses a **rule-based architecture**:

```python
class ValidationRule:
    def __init__(self, name, description, severity, check_fn):
        # name: unique identifier (e.g., "pk_unique")
        # description: human-readable explanation
        # severity: HIGH / MEDIUM / LOW
        # check_fn: callable that returns list of violations
```

Each table has its own set of rules registered in `_register_all_rules()`. Rules are categorized by severity — HIGH rules (PK violations, nulls in critical columns) block the pipeline, while MEDIUM/LOW rules generate warnings.

**Date dimension generation**: The `generate_dim_date()` function creates a complete date dimension covering the full sales date range, with derived columns:

| Column | Derivation | Purpose |
|--------|------------|---------|
| `year` | `date.year` | Year-level grouping |
| `quarter` | `(month-1)//3+1` | Quarterly reporting |
| `month` | `date.month` | Monthly analysis |
| `month_name` | `strftime('%B')` | Display labels |
| `day_of_week` | `isoweekday()` | Weekday analysis |
| `is_weekend` | `weekday() >= 5` | Weekend vs weekday filtering |

---

### 3.8 Utils Layer

**Folder**: `utils/`

| File | Purpose |
|------|---------|
| `cache.py` | In-memory caching decorator with TTL support |
| `helpers.py` | Formatting utilities (currency, percentage, date serialization) |

#### `cache.py` — In-Memory Caching

```python
@cached(ttl=300)  # Cache for 5 minutes
def expensive_method(self, arg1, arg2):
    ...
```

**Design rationale**:
- **Deterministic cache keys**: Built from `MD5(prefix:args:kwargs)` — ensures different method arguments produce different cache entries.
- **TTL-based expiration**: Entries expire after `CACHE_TTL_SECONDS` (configurable via `.env`).
- **Zero-config**: If `CACHE_TTL_SECONDS = 0`, caching is disabled entirely — useful for development.
- **Production-ready note**: The module header explicitly notes that swapping to Redis is straightforward — the decorator interface remains the same.

#### `helpers.py` — Formatting Utilities

Simple utility functions for consistent formatting:
- `decimal_to_float()` — Safe Decimal → float conversion
- `serialize_datetime()` — Datetime → ISO string
- `format_currency()` — `€1,234.56` formatting
- `format_percentage()` — `12.34%` formatting

---

## 4. Data Model

### Star Schema Diagram

```
┌─────────────────┐     ┌──────────────────────────────────┐
│   dim_category   │     │          dim_product              │
│─────────────────│     │──────────────────────────────────│
│ categoryid (PK) ├─────┤ productid (PK)                    │
│ categoryname    │     │ productname                       │
└─────────────────┘     │ price                             │
                        │ categoryid (FK → dim_category)    │
┌─────────────────┐     │ class / resistant / isallergic    │
│   dim_customer   │     │ categoryname (denormalized)       │
│─────────────────│     └──────────────┬───────────────────┘
│ customerid (PK) │                    │
│ firstname       │                    │
│ lastname        │                    │
│ city / country  │                    │
└────────┬────────┘                    │
         │                             │
         ▼                             ▼
┌──────────────────────────────────────────────────────────┐
│                     fact_sales                            │
│──────────────────────────────────────────────────────────│
│ salesid (PK)                                              │
│ employeeid (FK → dim_employee)                            │
│ customerid (FK → dim_customer)                            │
│ productid  (FK → dim_product)                             │
│ date       (FK → dim_date)                                │
│ quantity / discount / totalprice                          │
│ transactionnumber / time                                  │
└──────────────────────────────────────────────────────────┘
         ▲                             ▲
         │                             │
┌────────┴────────┐     ┌──────────────┴───────────────────┐
│   dim_employee   │     │          dim_date                 │
│─────────────────│     │──────────────────────────────────│
│ employeeid (PK) │     │ date_key (PK)                     │
│ firstname       │     │ year / quarter / month / day      │
│ lastname        │     │ day_of_week / is_weekend          │
│ birthdate       │     │ month_name / week_of_year         │
│ hiredate / city │     └──────────────────────────────────┘
└─────────────────┘
```

### Materialized Views

Five pre-computed views for **sub-second dashboard performance**:

| View | Aggregation Level | Purpose |
|------|-------------------|---------|
| `mv_daily_sales` | Day + product + employee + customer | Base KPI queries, time series, filters |
| `mv_monthly_sales` | Month + category + gender + country | Monthly trends, YoY comparison |
| `mv_customer_segmentation` | Customer-level with segment labels | Customer dashboard |
| `mv_top_products` | Product-level with revenue/volume ranking | Top products chart |
| `mv_employee_performance` | Employee-level with revenue/transaction metrics | Employee dashboard |

These views are refreshed after every ETL run via `refresh_materialized_views()`.

---

## 5. ETL Pipeline

See [`ETL_PIPELINE.md`](ETL_PIPELINE.md) for the complete ETL documentation.

### Quick Start

```bash
cd backend
python run_pipeline.py
```

Or with explicit parameters:

```python
from app.etl.pipeline import ETLPipeline

pipeline = ETLPipeline(
    database_url="postgresql://user:pass@localhost:5432/grocery_sales",
    dataset_path="scripts/data"
)
metrics = pipeline.run(reset=True)
print(metrics)
# {'dim_category': 11, 'dim_product': 452, 'dim_customer': 98759,
#  'dim_employee': 23, 'dim_date': 129, 'fact_sales': 6690599}
```

### Data Sources

| File | Rows | Description |
|------|------|-------------|
| `categories.csv` | 11 | Product category reference |
| `products.csv` | ~450 | Products with category FK |
| `customers.csv` | ~100K | Customers with city/country FK |
| `employees.csv` | ~50 | Employees with city FK |
| `cities.csv` | ~1K | City reference for enrichment |
| `countries.csv` | ~100 | Country reference for enrichment |
| `sales.csv` | ~6.7M | Transaction-level sales facts |

### Key Business Rules Applied

| Rule | Description |
|------|-------------|
| **Date cleaning** | Parse `SalesDate`, floor to seconds, drop ~67K null-date rows (~1%) |
| **Column standardization** | Rename all columns to lowercase snake_case |
| **Dimension enrichment** | Join city/country names into customer/employee dimensions |
| **Product enrichment** | Denormalize category name into product dimension |
| **Date generation** | Generate `dim_date` covering full sales date range |
| **FK load order** | Load dimensions in FK dependency order: category → product → customer → employee → date → fact_sales |
| **Bulk loading** | Use `COPY` for fact_sales (~6.7M rows), `INSERT` for small dimensions |

---

## 6. Analytical Insights Summary

> Full details in [`ANALYSIS_INSIGHTS.md`](ANALYSIS_INSIGHTS.md)

### Executive KPIs

| KPI | Value | Note |
|-----|-------|------|
| **Total Revenue** | €4,421,743,593.52 | Computed as `qty × price` (`TotalPrice` is 0 in source) |
| **Total Quantity** | 87,003,547 units | ~20M units/month |
| **Total Transactions** | 6,690,599 | ~1.55M/month |
| **Average Basket** | €660.89 | Per transaction |
| **Active Customers** | 98,759 | Unique buyers |
| **Active Employees** | 23 | Sales staff |
| **Products** | 452 | All have at least 1 sale ✅ |

### Key Business Insights

| Domain | Insight |
|--------|---------|
| **Categories** | Balanced diversification — top category (Confections) = 12.9%, bottom = 6.9% |
| **Customers** | 90% are VIP (89K customers generating 98.7% of revenue) |
| **Employees** | Remarkably uniform — top 5 each generate ~€193M (only 0.5% spread) |
| **Products** | No dead stock — all 452 products have been sold |
| **Pricing** | 52% of products priced €50–100 (premium strategy) |
| **Peak days** | Weekdays (Mon–Wed) outperform weekends by ~5.5% |
| **Top 10 products** | Tightly clustered (€18.6M–€19.3M) — no single product dominates |

### Data Quality

| Issue | Impact | Resolution |
|-------|--------|------------|
| `TotalPrice = 0` in CSV | Revenue must be computed | `qty × price` |
| 67,526 null dates (~1%) | Rows excluded | Acceptable loss |
| Microsecond precision | Truncated to seconds | Acceptable granularity |
| No orphan records ✅ | Foreign keys satisfied | Data integrity intact |

---

## 7. API Endpoints Reference

| Method | Endpoint | Description | Query Parameters |
|--------|----------|-------------|-----------------|
| `GET` | `/api/health` | Health check | — |
| `GET` | `/api/dashboard/summary` | Complete dashboard data | `start_date`, `end_date` |
| `GET` | `/api/sales/over-time` | Revenue time series | `start_date`, `end_date`, `category` |
| `GET` | `/api/sales/by-category` | Sales by category | `start_date`, `end_date`, `product` |
| `GET` | `/api/sales/monthly` | Monthly sales | `start_date`, `end_date`, `category`, `employee` |
| `GET` | `/api/products/` | All products with revenue rank | `start_date`, `end_date` |
| `GET` | `/api/products/{id}` | Product detail | — |
| `GET` | `/api/products/analytics/price-distribution` | Price range buckets | `start_date`, `end_date` |
| `GET` | `/api/products/analytics/price-volume-matrix` | Price vs volume scatter | `start_date`, `end_date` |
| `GET` | `/api/customers/segments` | Customer segments | `start_date`, `end_date` |
| `GET` | `/api/customers/top` | Top customers | `limit`, `start_date`, `end_date` |
| `GET` | `/api/customers/activity` | Customer activity over time | `start_date`, `end_date` |
| `GET` | `/api/customers/{id}` | Customer detail | — |
| `GET` | `/api/employees/top` | Top employees | `limit`, `start_date`, `end_date` |
| `GET` | `/api/employees/performance/by-age` | Performance by age group | `start_date`, `end_date` |
| `GET` | `/api/employees/performance/by-seniority` | Performance by seniority | `start_date`, `end_date` |
| `GET` | `/api/employees/{id}` | Employee detail | — |
| `GET` | `/api/basket/analysis` | Market basket analysis | `min_support`, `min_lift`, `limit`, `start_date`, `end_date` |
| `GET` | `/api/filters/` | Dynamic filter options | — |
| `GET` | `/api/insights/revenue-concentration` | Revenue concentration (Herfindahl index) | — |
| `GET` | `/api/insights/revenue-by-day` | Revenue by day of week | — |
| `GET` | `/api/insights/month-over-month` | Month-over-month growth | — |
| `GET` | `/api/insights/sales-by-resistance` | Sales by product resistance level | — |
| `GET` | `/api/insights/rfm-segments` | RFM customer segments | — |
| `GET` | `/api/insights/geographic-distribution` | Geographic revenue distribution | — |
| `GET` | `/api/insights/employee-parity` | Employee performance parity analysis | — |

> Interactive API documentation is available at `/api/docs` (Swagger UI) when the server is running.

---

## 8. Local Setup

### Prerequisites

- **Python**: 3.12 or 3.13 (not 3.14 — some wheels may not be available)
- **PostgreSQL**: 16+ installed and running
- **Bun**: (for the frontend — optional if only running the backend)

### Step 1: Database Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create the database
sudo -u postgres psql -c "CREATE DATABASE grocery_sales;"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"

# Execute the schema
sudo -u postgres psql -d grocery_sales -f ../database/schema.sql
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (wheels only to avoid compilation issues)
pip install --only-binary :all: -r requirements.txt

# If that fails for your Python version, install pandas/numpy first:
# pip install --only-binary :all: pandas numpy
# pip install -r requirements.txt

# Create .env file (optional — defaults work for local dev)
cp .env.example .env
```

### Step 3: Load Data

```bash
cd backend
source .venv/bin/activate
python scripts/load_all_data.py
```

Or run the full ETL pipeline:

```bash
cd backend
source .venv/bin/activate
python scripts/run_pipeline.py
```

### Step 4: Start the Server

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Verify

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/api/docs |
| ReDoc Docs | http://localhost:8000/api/redoc |
| Health Check | http://localhost:8000/api/health |

```bash
curl http://localhost:8000/api/health
# {"status": "healthy", "app": "Grocery Sales Dashboard API", "version": "1.0.0"}
```

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `psycopg2` install fails | Install `libpq-dev` (`sudo apt install libpq-dev`) |
| `pandas` no wheel for Python 3.14 | Use Python 3.12 or 3.13 instead |
| Port 8000 already in use | Change port: `--port 8001` |
| Database connection refused | Ensure PostgreSQL is running: `sudo systemctl start postgresql` |
| Alembic folder empty | Migrations are handled via the schema SQL file directly |

---

## 9. Configuration & Environment

### `.env` File

```ini
APP_NAME=Grocery Sales Dashboard API
APP_VERSION=1.0.0
DEBUG=false

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=grocery_sales

CACHE_TTL_SECONDS=300
```

### Dependencies (`requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | ≥0.115.0 | Web framework for REST API |
| `uvicorn` | ≥0.30.0 | ASGI server |
| `sqlalchemy` | ≥2.0.0 | ORM for database interaction |
| `psycopg2-binary` | ≥2.9.0 | PostgreSQL adapter |
| `alembic` | ≥1.13.0 | Database migrations |
| `pydantic` | ≥2.9.0 | Data validation & settings |
| `pydantic-settings` | ≥2.5.0 | Settings management |
| `python-dateutil` | ≥2.9.0 | Date parsing utilities |
| `pandas` | ≥2.2.0 | Data manipulation (ETL) |
| `numpy` | ≥1.26.0 | Numerical computing (ETL) |
| `python-dotenv` | ≥1.0.0 | .env file loading |
| `httpx` | ≥0.27.0 | HTTP client (testing) |

---

## 10. Technical Decisions & Rationale

### Why FastAPI over Flask/Django?

| Factor | FastAPI | Flask | Django |
|--------|---------|-------|--------|
| Performance | ⚡ Async-native | Synchronous | Synchronous |
| Auto-docs | ✅ Built-in (Swagger + ReDoc) | ❌ Manual | ❌ Manual |
| Validation | ✅ Pydantic | ❌ Manual | ❌ DRF |
| Type hints | ✅ First-class | ❌ Basic | ❌ Basic |
| Project size | Lightweight | Lightweight | Heavy |

FastAPI was chosen for its **automatic OpenAPI documentation**, **Pydantic validation**, and **async support** — ideal for a data API that serves a frontend dashboard.

### Why a single repository instead of one per entity?

1. **Analytical queries cross multiple tables**: A single dashboard summary query touches 5+ tables and materialized views. Splitting across repositories would require coordination.
2. **Simpler dependency graph**: No circular imports between repositories.
3. **Co-located filter logic**: Date and dimension filters are applied consistently across all queries.

### Why materialized views over query-time aggregations?

| Approach | Query Time | Data Freshness | Complexity |
|----------|------------|----------------|------------|
| Materialized Views | **~50ms** | Stale until refresh | Medium |
| Query-time aggregation | **~5-10s** (on 6.7M rows) | Always fresh | Low |

The dashboard targets **interactive sub-second response times**. Pre-computing aggregations via materialized views was the only viable approach for the 6.7M-row fact table.

### Why `COPY` for large tables and `INSERT` for small?

PostgreSQL's `COPY` is **10-50x faster** than `INSERT` for bulk loading because it bypasses the query planner, triggers, and foreign key checks. However, `COPY` has overhead (creating an in-memory buffer, starting a raw connection). For small tables (<100K rows), `INSERT` is simpler and fast enough.

### Why `Decimal` instead of `float` for monetary values?

Floating-point arithmetic introduces rounding errors:

```python
>>> 0.1 + 0.2
0.30000000000000004  # ❌
>>> Decimal('0.1') + Decimal('0.2')
Decimal('0.30')       # ✅
```

For a dashboard reporting €4.4 billion in revenue, float precision would cause visible errors in KPIs and percentages.

### Why in-memory cache instead of Redis?

**Simplicity**. For a single-server deployment, an in-memory dictionary cache with TTL is sufficient. The cache interface is designed so that swapping to Redis requires changing only the `_cache_store` implementation — the decorator API remains unchanged.

---

## 11. Testing & Validation

### ETL Validation

The `DataValidator` engine checks:

| Check | Severity | Tables |
|-------|----------|--------|
| PK uniqueness | HIGH | All dimensions |
| NOT NULL constraints | HIGH | All tables |
| Positive prices/quantities | HIGH | Products, sales |
| FK referential integrity | HIGH | fact_sales |
| Column count vs schema | MEDIUM | All tables |
| Date range consistency | MEDIUM | fact_sales vs dim_date |

### Database Synchronization

The `DatabaseSynchronizer` verifies:

- All expected tables exist
- Row counts meet minimum thresholds
- Foreign key relationships are intact
- No schema drift (missing columns, type mismatches)

### API Testing

API endpoints can be tested via:

```bash
# Health check
curl http://localhost:8000/api/health

# Dashboard summary
curl http://localhost:8000/api/dashboard/summary

# Basket analysis with custom thresholds
curl "http://localhost:8000/api/basket/analysis?min_support=0.01&min_lift=1.5&limit=20"
```

---

## 12. Future Improvements

| Area | Improvement | Impact |
|------|-------------|--------|
| **Performance** | Replace in-memory cache with Redis | Distributed caching, persistent across restarts |
| **Performance** | Add composite indexes on `mv_daily_sales` | Faster filtered queries |
| **Scalability** | Migrate to async SQLAlchemy | Handle more concurrent requests |
| **Data Quality** | Add automated data quality reports | Proactive issue detection |
| **ETL** | Support incremental loads (CDC) | Handle daily data updates without full reload |
| **API** | Add pagination for large result sets | Better UX for `/products/` and `/customers/top` |
| **API** | Add export endpoints (CSV, Excel) | Direct data download for analysts |
| **Security** | Add authentication (JWT/OAuth2) | Production deployment requirement |
| **Monitoring** | Add Prometheus metrics & structured logging | Operational visibility |
| **Documentation** | Add Postman collection | Easier API exploration |

---

> **Project**: Grocery Sales BI Dashboard — Approach 2 (Code)  
> **Backend**: FastAPI + SQLAlchemy + PostgreSQL  
> **Documentation updated**: June 2026
