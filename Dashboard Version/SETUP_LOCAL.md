# 🚀 Local Setup (without Docker)

## Prerequisites

- **PostgreSQL** 16+ installed and running
- **Python** 3.12 or 3.13 (not 3.14 — some wheels may not be available)
- **Bun** (for the frontend) — install via `curl -fsSL https://bun.sh/install | bash`
- **Git** (to clone the repository)

---

## 1. Database — PostgreSQL

```bash
# Start PostgreSQL (if installed via systemd)
sudo systemctl start postgresql

# Create the database and user
sudo -u postgres psql -c "CREATE DATABASE grocery_sales;"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"

# Execute the schema (tables, views, indexes)
sudo -u postgres psql -d grocery_sales -f database/schema.sql
```

### Verify the schema

```bash
sudo -u postgres psql -d grocery_sales -c "\dt"
# Should show: dim_category, dim_product, dim_customer, dim_employee, dim_date, fact_sales
```

---

## 2. Backend — FastAPI

> ⚠️ **Important**: Use Python 3.12 or 3.13 (not 3.14).
> Check with `python3 --version`. If you have 3.14, use `python3.12` instead.

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (wheels only to avoid compilation issues)
pip install --only-binary :all: -r requirements.txt

# If that fails (no wheel for your Python version), install pandas/numpy first:
# pip install --only-binary :all: pandas numpy
pip install -r requirements.txt

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend runs at **http://localhost:8000**  
API Documentation: **http://localhost:8000/api/docs**

---

## 3. Import CSV Data

> **Note**: This step loads the pre-processed CSV files from `backend/scripts/data/` into PostgreSQL.

```bash
cd backend
source .venv/bin/activate

# Run the full ETL pipeline (truncates tables first, safe to re-run)
python scripts/load_all_data.py
```

### Alternative — Run the ETL Pipeline

```bash
cd backend
source .venv/bin/activate

# This runs extract → transform → validate → load via pandas
python scripts/run_pipeline.py
```

### After loading — Create materialized views for basket analysis

```bash
PGPASSWORD=postgres psql -h localhost -U postgres -d grocery_sales -c "
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_baskets AS
SELECT DISTINCT customerid, 
       CONCAT(customerid, '|', date) AS basket_id, 
       productid
FROM fact_sales;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_db ON mv_daily_baskets(customerid, basket_id, productid);
CREATE INDEX IF NOT EXISTS idx_mv_db_basket ON mv_daily_baskets(basket_id);
"
```

> 💡 **Tip**: This MV is used for basket preprocessing. The actual basket analysis is now pre-computed in the `basket_analysis_results` table.

### After loading — Load pre-computed basket analysis results

The basket analysis has been pre-computed using `Basket_Analysis.ipynb` and exported to `basket_analysis_results.csv`. Load it into the database:

```bash
PGPASSWORD=postgres psql -h localhost -U postgres -d grocery_sales -f 'Dashboard Version/backend/scripts/load_basket_table.sql'
```

This creates the `basket_analysis_results` table with **75,020 association rules** indexed by support and lift for fast queries.

---

## 4. Frontend — Next.js

```bash
cd frontend

# Install dependencies
bun install

# Start the development server
bun run dev
```

The frontend runs at **http://localhost:3000**

---

## 5. Verify Everything Works

```bash
# 1. Check the backend health endpoint
curl http://localhost:8000/api/health
# Expected: {"status":"healthy","app":"Grocery Sales Dashboard API","version":"1.0.0"}

# 2. Check the dashboard summary
curl http://localhost:8000/api/dashboard/summary
# Expected: JSON with KPIs (revenue, quantity, transactions...)

# 3. Open the frontend in your browser
# http://localhost:3000
```

---

## Quick Reference

| Service | URL | Command |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | `cd frontend && bun run dev` |
| **Backend API** | http://localhost:8000 | `cd backend && uvicorn app.main:app --reload` |
| **API Docs** | http://localhost:8000/api/docs | — |
| **PostgreSQL** | localhost:5432 | `sudo systemctl start postgresql` |

## Dashboard Pages

| Page | URL | Description |
|------|-----|-------------|
| Sales Dashboard | http://localhost:3000 | KPIs, revenue trends, category analysis |
| Product Analysis | http://localhost:3000/products | Product portfolio, price distribution |
| Customer Analysis | http://localhost:3000/customers | RFM segments, loyalty, geography |
| Employee Analysis | http://localhost:3000/employees | Team performance, demographics |
| Basket Analysis | http://localhost:3000/basket-analysis | Market basket / association rules |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `psycopg2` install fails | Install `libpq-dev`: `sudo apt install libpq-dev` |
| `pandas` no wheel for Python 3.14 | Use Python 3.12 or 3.13 instead |
| Port 8000 already in use | Change port: `--port 8001` |
| Database connection refused | Ensure PostgreSQL is running: `sudo systemctl start postgresql` |
| `mv_daily_baskets` not found | Run the CREATE MATERIALIZED VIEW command from step 3 |
| `basket_analysis_results` not found | Run the load script from step 3b |
| Frontend shows "Unable to load dashboard" | Ensure the backend is running on port 8000 |
