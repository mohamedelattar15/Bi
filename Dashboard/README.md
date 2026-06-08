# 🛒 Grocery Sales Dashboard

A modern full-stack web application rebuilt from a Power BI dashboard. Provides interactive analytics for grocery sales data across 5 dashboard pages.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  Next.js (Frontend)              │
│     TypeScript · Tailwind CSS · Chart.js         │
│     TanStack Query · shadcn/ui                   │
├─────────────────────────────────────────────────┤
│                  FastAPI (Backend)                │
│     SQLAlchemy · Pydantic · Alembic              │
├─────────────────────────────────────────────────┤
│                PostgreSQL (Database)              │
│     Star Schema · Materialized Views · Indexes    │
└─────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose

### Run with Docker

```bash
cd docker
docker compose up -d
```

### Access

| Service     | URL                      |
|-------------|--------------------------|
| Frontend    | http://localhost:3000     |
| Backend API | http://localhost:8000     |
| API Docs    | http://localhost:8000/api/docs |
| PostgreSQL  | localhost:5432            |

## 🗂️ Project Structure

```
Dashboard/
├── database/
│   └── schema.sql              # PostgreSQL schema (tables, views, indexes)
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI route handlers
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic layer
│   │   ├── repositories/       # Data access layer
│   │   ├── core/               # Config, database connection
│   │   └── utils/              # Helper functions
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router pages
│   │   │   ├── page.tsx        # Sales Dashboard (home)
│   │   │   ├── products/       # Product Analysis page
│   │   │   ├── customers/      # Customer Analysis page
│   │   │   ├── employees/      # Employee Analysis page
│   │   │   └── basket-analysis/# Basket Analysis page
│   │   ├── components/         # Reusable UI components
│   │   │   └── charts/         # Chart.js wrapper components
│   │   ├── hooks/              # React Query hooks
│   │   ├── services/           # API client
│   │   ├── types/              # TypeScript type definitions
│   │   └── lib/                # Utility functions
│   ├── Dockerfile
│   └── package.json
└── docker/
    └── docker-compose.yml
```

## 📊 Dashboard Pages

### 1. Sales Dashboard (Home)
- KPI Cards: Revenue, Quantity, Transactions, Avg Basket, Customers, Products
- Revenue Over Time (Line Chart)
- Sales by Category (Doughnut Chart)
- Monthly Seasonality (Bar Chart)
- Top 10 Products (Horizontal Bar Chart)

### 2. Product Analysis
- Product KPIs
- Price Distribution
- Revenue by Category
- Price vs Volume Matrix (Scatter Chart)

### 3. Customer Analysis
- Customer Segmentation (VIP, Regular, Occasional, New)
- Top Customers
- Active Customers Over Time
- Avg Basket by Segment

### 4. Employee Analysis
- Top Employees
- Performance by Age Group
- Performance by Seniority
- Revenue Distribution

### 5. Basket Analysis
- Association Rules (Support, Confidence, Lift)
- Adjustable threshold sliders
- Support vs Lift Matrix
- Top Rules by Lift
- Sortable Rules Table

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/summary` | Complete dashboard data |
| GET | `/api/sales/over-time` | Revenue time series |
| GET | `/api/sales/by-category` | Sales by category |
| GET | `/api/sales/monthly` | Monthly sales |
| GET | `/api/products/` | All products |
| GET | `/api/products/{id}` | Product detail |
| GET | `/api/products/analytics/price-distribution` | Price distribution |
| GET | `/api/products/analytics/price-volume-matrix` | Price vs volume |
| GET | `/api/customers/segments` | Customer segments |
| GET | `/api/customers/top` | Top customers |
| GET | `/api/customers/activity` | Customer activity |
| GET | `/api/customers/{id}` | Customer detail |
| GET | `/api/employees/top` | Top employees |
| GET | `/api/employees/performance/by-age` | Performance by age |
| GET | `/api/employees/performance/by-seniority` | Performance by seniority |
| GET | `/api/employees/{id}` | Employee detail |
| GET | `/api/basket/analysis` | Basket analysis rules |
| GET | `/api/filters/` | Filter options |
| GET | `/api/health` | Health check |

## 🔧 Development

### Backend (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (without Docker)

```bash
cd frontend
bun install
bun run dev
```

## 📋 Data Import

To load the CSV data into PostgreSQL:

```bash
# Using the provided Python script
cd backend
python scripts/load_data.py
```

Or manually:

```bash
# Copy CSV files to Docker container
docker cp dataset/. grocery-sales-db:/tmp/

# Import using psql
docker exec -it grocery-sales-db psql -U postgres -d grocery_sales \
  -c "\COPY dim_category FROM '/tmp/categories.csv' CSV HEADER"
```

## 🧪 Performance Optimizations

- **Materialized Views**: Pre-aggregated `mv_daily_sales`, `mv_monthly_sales`, `mv_customer_segmentation`, `mv_top_products`, `mv_employee_performance`
- **Composite Indexes**: On `fact_sales(date, productid)`, `fact_sales(date, employeeid)`, etc.
- **React Query Caching**: 5-10 minute stale times on slow-changing data
- **Connection Pooling**: SQLAlchemy pool with 20 connections
- **Refresh Function**: `refresh_materialized_views()` to update aggregations
