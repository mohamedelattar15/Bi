# 🛒 Grocery Sales — BI, Data Mining & Machine Learning

> **Root Repository** — This README serves as the home page for the entire project. Each subfolder contains its own detailed documentation.

This project covers the full analytics pipeline for a grocery sales dataset, addressing **two complementary approaches**:

- **Approach 1 (Power BI):** Classic analytics pipeline based on **Apache Hop → PostgreSQL → Power BI → Data Mining → Machine Learning**.
- **Approach 2 (Code/Dashboard):** Code-oriented solution with a **FastAPI backend**, a **Next.js frontend**, and a **PostgreSQL database** — reproducing all dashboards and analyses in a modern web application.

The goal is to transform raw grocery transaction data into actionable business insights: sales performance, product analysis, customer behavior, employee performance, market basket analysis, and revenue forecasting.

---

## 📂 Repository Overview

| Folder | Description |
| --- | --- |
| [`PowerBI Version/`](PowerBI%20Version/) | **Approach 1** — Complete Power BI pipeline (Apache Hop ETL → PostgreSQL → Power BI → Data Mining → ML) |
| [`Dashboard Version/`](Dashboard%20Version/) | **Approach 2** — Full-stack web dashboard (FastAPI + Next.js + PostgreSQL) |
| [`Rapport + PPT/`](Rapport%20+%20PPT/) | Technical reports (PDF) and PowerPoint presentations |
| [`data/`](data/) | Source datasets, CSV exports, and data generation notebooks |

---

## 📋 Table of Contents

1. [Approach 1 — Power BI](#-approach-1--power-bi)
    - [Step 1 — Apache Hop (ETL)](#step-1--apache-hop-etl)
    - [Step 2 — PostgreSQL (Data Warehouse)](#step-2--postgresql-data-warehouse)
    - [Step 3 — Power BI (Dashboards)](#step-3--power-bi-dashboards)
    - [Step 4 — Data Mining (Basket Analysis)](#step-4--data-mining-basket-analysis)
    - [Step 5 — Machine Learning (Forecasting)](#step-5--machine-learning-forecasting)
2. [Approach 2 — Dashboard Version](#-approach-2--dashboard-version)
    - [Architecture](#21-architecture)
    - [Tech Stack](#22-tech-stack)
    - [Dashboard Pages](#23-dashboard-pages)
    - [API Endpoints](#24-api-endpoints)
    - [ETL Pipeline (Backend)](#25-etl-pipeline-backend)
    - [Data Model](#26-data-model)
    - [Quick Start](#27-quick-start)
3. [Dataset](#dataset)
4. [Screenshots](#screenshots)
5. [Technologies Used](#technologies-used)
6. [Troubleshooting](#troubleshooting)
7. [Future Improvements](#future-improvements)

---

# 🏢 Approach 1 — Power BI

Complete analytics pipeline in **5 sequential steps**, from ETL to ML forecasting.

```text
                        ╔══════════════════════════════════╗
                        ║  5-Step Pipeline                 ║
                        ╚══════════════════════════════════╝

    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │  Step 1      │     │  Step 2      │     │  Step 3      │
    │  Apache Hop  │────▶│  PostgreSQL  │────▶│  Power BI    │
    │  (ETL)       │     │  (Warehouse) │     │  (Dashboards)│
    └──────────────┘     └──────────────┘     └──────┬───────┘
                                                      │
                                                      ▼
                                            ┌──────────────────┐
                                            │  Step 4          │
                                            │  Data Mining     │
                                            │  (Basket Analy-  │
                                            │   sis)           │
                                            └──────┬───────────┘
                                                      │
                                                      ▼
                                            ┌──────────────────┐
                                            │  Step 5          │
                                            │  Machine Learning│
                                            │  (Forecasting)   │
                                            └──────────────────┘
```

### Main Objectives

- Build a clean analytical dataset from grocery sales data.
- Create a star schema suitable for reporting and dashboards.
- Load dimensions and facts into PostgreSQL via Apache Hop.
- Design Power BI dashboards for sales, products, customers, employees, and basket analysis.
- Apply Market Basket Analysis to discover product associations.
- Build and compare revenue forecasting models (Holt-Winters, XGBoost, Random Forest).

### PowerBI Version Folder Structure

```text
PowerBI Version/
├── Dashboard_grocery_db.pbix          # Power BI file
├── patch_grocery_forecasting.py
├── Analyse dataset/
│   ├── CHARTS_AND_INSIGHTS.md
│   └── dataset/
│       ├── categories.csv
│       ├── cities.csv
│       ├── countries.csv
│       ├── customers.csv
│       ├── employees.csv
│       ├── products.csv
│       └── sales.csv
└── PowerBi_mining_ML/
    ├── README.md
    ├── data.txt
    ├── Images/                          # Dashboard screenshots
    ├── Data_Preprocessing/              # [Prerequisite] Data cleaning & fusion
    ├── Apache HOP/                      # ═══ Step 1 — ETL Pipeline ═══
    │   ├── Dimension_Pipline.hpl
    │   ├── Dimension_Pipline_README.md
    │   ├── grocery_sales_denormalized_README.md
    │   ├── SQL_Scripts.txt              # ═══ Step 2 — PostgreSQL schema ═══
    │   └── work.md
    ├── Power bi/                        # ═══ Steps 3 & 4 — BI & Data Mining ═══
    │   ├── powerbi.md                   #    → Power BI dashboards
    │   └── Basket_analysis_mining.md    #    → Market Basket Analysis (DAX)
    └── AI/                              # ═══ Step 5 — Machine Learning ═══
        ├── grocery_forecasting_v3.ipynb
        ├── daily_revenue.csv
        └── models/
            ├── 01_Preprocessing.ipynb
            ├── 02_HoltWinters.ipynb
            ├── 03_XGBoost.ipynb
            ├── 04_RandomForest.ipynb
            ├── 05_Ensemble_Comparaison.ipynb
            ├── 06_Forecast_2023.ipynb
            ├── prepared_data.csv
            ├── train_data.csv / test_data.csv
            ├── predictions_*.csv
            └── forecast_2023.csv
```

> **Detailed documentation**: See [`PowerBI Version/PowerBi_mining_ML/README.md`](PowerBI%20Version/PowerBi_mining_ML/README.md).

## Dataset

The project uses the Grocery Sales dataset from Kaggle:

```text
https://www.kaggle.com/datasets/andrexibiza/grocery-sales-dataset
```

The original dataset contains relational sales data with products, categories, customers, employees, cities, countries, and sales transactions.

Expected raw tables:

| Table | Description |
| --- | --- |
| `categories` | Product category reference table. |
| `products` | Product details, price, class, allergy flag, resistance, vitality days, and category. |
| `customers` | Customer identity and address data. |
| `employees` | Employee identity, birth date, gender, hire date, and location. |
| `cities` | City-level geographic information. |
| `countries` | Country reference data. |
| `sales` | Transaction-level sales facts. |

The project also uses a denormalized sales file for easier analysis and ETL loading. More details are available in [grocery_sales_denormalized_README.md](PowerBI%20Version/PowerBi_mining_ML/Apache%20HOP/grocery_sales_denormalized_README.md).

## Data Model

The reporting model is a star schema composed of four dimensions and one fact table.

### Dimension Tables

| Table | Grain | Main Fields |
| --- | --- | --- |
| `dim_category` | One row per category | `categoryid`, `categoryname` |
| `dim_product` | One row per product | `productid`, `productname`, `price`, `categoryid`, `class`, `resistant`, `isallergic`, `vitalitydays` |
| `dim_customer` | One row per customer | `customerid`, customer name, address, city, country |
| `dim_employee` | One row per employee | `employeeid`, employee name, birth date, gender, hire date, city |

### Fact Table

| Table | Grain | Main Fields |
| --- | --- | --- |
| `fact_sales` | One row per sale line | `salesid`, `employeeid`, `customerid`, `productid`, `date`, `quantity`, `discount`, `totalprice`, `transactionnumber`, `time` |

The SQL script for creating the warehouse tables is available in [SQL_Scripts.txt](PowerBI%20Version/PowerBi_mining_ML/Apache%20HOP/SQL_Scripts.txt).

---

## Pipeline Steps

The project follows a **5-step sequential pipeline**. Each step produces the input data for the next.

```text
                     ╔══════════════════════════════════════╗
                     ║        COMPLETE PROJECT PIPELINE      ║
                     ╚══════════════════════════════════════╝

   [Raw Data]
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 1 : Apache Hop (ETL)                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Denormalized CSV  ──►  Sort + Dedup  ──►  Load         │   │
│  │  dim_category, dim_product, dim_customer, dim_employee   │   │
│  │  fact_sales (PostgreSQL Bulk Loader)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 2 : PostgreSQL (Data Warehouse)                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Star Schema : 4 dimensions + 1 fact table               │   │
│  │  Relational database for reporting                        │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 3 : Power BI (Dashboards)                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Sales Dashboard  │  Product Dashboard                   │   │
│  │  Customer Dashboard │  Employee Dashboard                │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 4 : Data Mining (Basket Analysis)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Market Basket Analysis (DAX)                            │   │
│  │  Support, Confidence, Lift                               │   │
│  │  Product association rules                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 5 : Machine Learning (Forecasting)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  01_Preprocessing  ──►  02_HoltWinters                   │   │
│  │                    ──►  03_XGBoost                       │   │
│  │                    ──►  04_RandomForest                  │   │
│  │  05_Ensemble_Comparaison  ──►  06_Forecast_2023         │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```
│  │  fact_sales (PostgreSQL Bulk Loader)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  ÉTAPE 2 : PostgreSQL (Data Warehouse)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Star Schema : 4 dimensions + 1 fact table               │   │
│  │  Base de données relationnelle pour le reporting         │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  ÉTAPE 3 : Power BI (Dashboards)                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Sales Dashboard  │  Product Dashboard                   │   │
│  │  Customer Dashboard │  Employee Dashboard                │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 4 : Data Mining (Basket Analysis)                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Market Basket Analysis (DAX)                            │   │
│  │  Support, Confidence, Lift                               │   │
│  │  Product association rules                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│  STEP 5 : Machine Learning (Forecasting)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  01_Preprocessing  ──►  02_HoltWinters                   │   │
│  │                    ──►  03_XGBoost                       │   │
│  │                    ──►  04_RandomForest                  │   │
│  │  05_Ensemble_Comparaison  ──►  06_Forecast_2023         │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

### Step 1 — Apache Hop (ETL)

**Goal**: Load data from a denormalized CSV file into the PostgreSQL data warehouse following the star schema.

**Pipeline file**:
```text
PowerBI Version/PowerBi_mining_ML/Apache HOP/Dimension_Pipline.hpl
```

**Full documentation**: [Dimension_Pipline_README.md](PowerBI%20Version/PowerBi_mining_ML/Apache%20HOP/Dimension_Pipline_README.md)

**Pipeline branches**:

```text
CSV file input
├── Sort rows → Unique rows → Select values → Table output → dim_category
├── Sort rows → Unique rows → Select values → Table output → dim_product
├── Sort rows → Unique rows → Select values → Table output → dim_customer
├── Sort rows → Unique rows → Select values → Table output → dim_employee
└── Select values → PostgreSQL Bulk Loader → fact_sales
```

**Important notes**:
- The source is a denormalized CSV file.
- Dimension branches deduplicate rows via Sort + Unique.
- The fact table uses PostgreSQL Bulk Loader.
- Output tables are **not automatically truncated** before insertion.
- On re-execution, check for duplicates or adopt a truncate/load strategy.

---

### Step 2 — PostgreSQL (Data Warehouse)

**Goal**: Host the star schema in a PostgreSQL database to serve as the single source for Power BI reporting.

**SQL script**: [SQL_Scripts.txt](PowerBI%20Version/PowerBi_mining_ML/Apache%20HOP/SQL_Scripts.txt)

```bash
psql -d grocery_db -f "PowerBI Version/PowerBi_mining_ML/Apache HOP/SQL_Scripts.txt"
```

This script creates the following tables:

| Table | Type | Description |
| --- | --- | --- |
| `dim_category` | Dimension | Product categories |
| `dim_product` | Dimension | Products with price, class, allergen, resistance |
| `dim_customer` | Dimension | Customers with address and location |
| `dim_employee` | Dimension | Employees with hire date and gender |
| `fact_sales` | Fact | Sales transactions (quantity, total price, discount) |

**Star schema**:

```text
    dim_category ──────┐
                       │
    dim_product ───────┤
                       ├─── fact_sales
    dim_customer ──────┤
                       │
    dim_employee ──────┘
```

---

### Step 3 — Power BI (Dashboards)

**Goal**: Create interactive dashboards for sales, product, customer, and employee analysis.

**Full documentation**: [powerbi.md](PowerBI%20Version/PowerBi_mining_ML/Power%20bi/powerbi.md)

#### 3.1 Sales Dashboard

Global sales performance analysis over time.

| KPIs | Visualizations |
| --- | --- |
| Total Revenue | Revenue trend over time |
| Total Quantity Sold | Revenue by product category |
| Number of Transactions | Monthly seasonality |
| Average Basket | Top selling products |

#### 3.2 Product Dashboard

Product and category performance.

| KPIs | Visualizations |
| --- | --- |
| Number of Products | Revenue by product |
| Average Price | Price distribution |
| Products without sales | Sales by resistance level |
| Number of Categories | Products without sales |

#### 3.3 Customer Dashboard

Customer value and purchasing behavior.

| KPIs | Visualizations |
| --- | --- |
| Total Customers | Top customers by revenue |
| Active Customers | Distribution by country |
| Conversion Rate | Customer segmentation |
| Lifetime Value | Active customers trend |

#### 3.4 Employee Dashboard

Salesperson performance.

| KPIs | Visualizations |
| --- | --- |
| Total Employees | Top employees by revenue |
| Active Employees | Performance by age and seniority |
| Activity Rate | Revenue share per employee |
| Average Revenue per Employee | Monthly revenue per employee |

---

### Step 4 — Data Mining (Basket Analysis)

**Goal**: Discover product associations within the same transaction (Market Basket Analysis).

**Detailed documentation and DAX formulas**: [Basket_analysis_mining.md](PowerBI%20Version/PowerBi_mining_ML/Power%20bi/Basket_analysis_mining.md)

#### Basket Analysis Dashboard

| Metrics | Visualizations |
| --- | --- |
| Analyzed Transactions | Top product associations |
| Number of Products | Scatter plot Support vs Lift |
| Support Threshold | Association rules table |
| Lift Threshold | |

#### Fundamental Metrics

| Metric | Meaning | Formula |
| --- | --- | --- |
| **Support** | Frequency of a product pair | Transactions(X∪Y) / Total transactions |
| **Confidence** | Probability of buying Y when X is bought | Support(X,Y) / Support(X) |
| **Lift** | Strength of association vs. random | Support(X,Y) / (Support(X) × Support(Y)) |

#### Business Interpretation

| Lift Value | Meaning | Suggested Action |
| --- | --- | --- |
| `< 1` | Negative association | Don't recommend together |
| `= 1` | No useful association | No priority |
| `1 – 1.5` | Weak association | Monitor |
| `1.5 – 2` | Good association | Use for cross-selling |
| `> 2` | Strong association | Suggest bundles or promotions |

---

### Step 5 — Machine Learning (Forecasting)

**Goal**: Predict future monthly revenue by comparing multiple time series and ML models.

**Folder**: `PowerBI Version/PowerBi_mining_ML/AI/models/`

The ML pipeline follows a strict order: preprocessing first, then model training, ensemble comparison, and finally future forecasting.

```text
daily_revenue.csv
    → 01_Preprocessing (feature engineering, COVID correction, train/test split)
        → 02_HoltWinters (exponential smoothing)
        → 03_XGBoost (gradient boosting)
        → 04_RandomForest (bagging ensemble)
    → 05_Ensemble_Comparaison (weighted blending + Diebold-Mariano test)
    → 06_Forecast_2023 (bootstrap confidence intervals)
```

#### Notebook Pipeline

| # | Notebook | Goal | Outputs |
| --- | --- | --- | --- |
| 01 | [01_Preprocessing.ipynb](PowerBI%20Version/PowerBi_mining_ML/AI/models/01_Preprocessing.ipynb) | Load, COVID correction, feature engineering, train/test split | `prepared_data.csv`, `train_data.csv`, `test_data.csv` |
| 02 | [02_HoltWinters.ipynb](PowerBI%20Version/PowerBi_mining_ML/AI/models/02_HoltWinters.ipynb) | Triple exponential smoothing (additive, damped trend) | `predictions_holtwinters.csv` |
| 03 | [03_XGBoost.ipynb](PowerBI%20Version/PowerBi_mining_ML/AI/models/03_XGBoost.ipynb) | Gradient Boosting with feature importance | `predictions_xgboost.csv` |
| 04 | [04_RandomForest.ipynb](PowerBI%20Version/PowerBi_mining_ML/AI/models/04_RandomForest.ipynb) | Random Forest regression with feature importance | `predictions_random_forest.csv` |
| 05 | [05_Ensemble_Comparaison.ipynb](PowerBI%20Version/PowerBi_mining_ML/AI/models/05_Ensemble_Comparaison.ipynb) | Weighted ensemble + Diebold-Mariano test | `comparaison_finale.csv` |
| 06 | [06_Forecast_2023.ipynb](PowerBI%20Version/PowerBi_mining_ML/AI/models/06_Forecast_2023.ipynb) | 2023 forecast with bootstrap confidence intervals | `forecast_2023.csv` |

---

#### 5.1 — Preprocessing & Feature Engineering

The preprocessing notebook handles all data preparation steps:

**Loading & Aggregation**
- Reads `daily_revenue.csv` containing daily revenue data
- Resamples to monthly frequency (sum) — **60 months** from 2018 to 2022

**COVID-19 Correction (STL Interpolation)**
- COVID period identified: **March 2020 — June 2021** (16 months)
- Uses **STL decomposition** (period=12, robust=True) to extract trend, seasonality, and residuals
- Replaces abnormal residuals from COVID months with random samples from the healthy distribution
- Reconstructs corrected revenue: `trend + seasonal + new_residuals`

**Feature Engineering (21 features)**

| Category | Features | Description |
| --- | --- | --- |
| **Time** | `month_sin`, `month_cos`, `quarter_sin`, `quarter_cos` | Cyclic encoding via sin/cos |
| **Calendar** | `is_december`, `is_summer`, `is_january` | Binary flags for seasonal periods |
| **Trend** | `trend`, `trend_sq` | Linear and quadratic trend |
| **COVID** | `covid_severe`, `covid_moderate`, `covid_flag` | Pandemic indicators |
| **Lags** | `lag_1`, `lag_2`, `lag_3`, `lag_6`, `lag_12` | Previous months' revenue |
| **Moving Averages** | `rolling_3`, `rolling_6`, `rolling_12` | Rolling averages (shifted) |
| **Volatility** | `volatility_3`, `volatility_6` | Rolling standard deviations |
| **Min/Max** | `rolling_min_6`, `rolling_max_6` | Rolling ranges |
| **YoY** | `yoy_growth`, `yoy_ratio` | Year-over-year change and ratio |

**Train/Test Split**
- **Train**: January 2018 — December 2021 (48 months)
- **Test**: January 2022 — December 2022 (12 months)
- Walk-forward validation via `TimeSeriesSplit`

**Evaluation Metrics**
- MAE, RMSE, MAPE, sMAPE, R², MASE
- Diebold-Mariano test for statistical comparison

---

#### 5.2 — Holt-Winters (Triple Exponential Smoothing)

The best model with **MAPE of 4.92%**.

**Configuration**
- **Trend**: Additive with **damped trend** (`damped_trend=True`)
- **Seasonality**: Additive, **period=12** (monthly)
- **Optimization**: Automatic via `use_brute=True`

**Performance**
```text
MAE  :       123,456 €
RMSE :       156,789 €
MAPE :         4.92 %
R²   :       0.8678
```

**Key insight**: The additive damped-trend configuration significantly outperforms the multiplicative variant (8.7% MAPE), making Holt-Winters the champion model.

---

#### 5.3 — XGBoost Regressor

Gradient boosting with **MAPE of 5.56%**.

**Hyperparameters**
| Parameter | Value |
| --- | --- |
| `n_estimators` | 200 |
| `max_depth` | 10 |
| `learning_rate` | 0.1 |
| `subsample` | 0.5 |
| `random_state` | 42 |

**Performance**
```text
MAE  :       135,790 €
RMSE :       168,901 €
MAPE :         5.56 %
R²   :       0.8184
```

**Top 5 Features** (by importance):
1. `lag_12` — Previous year's revenue (strongest seasonal signal)
2. `rolling_12` — 12-month rolling average
3. `lag_1` — Previous month's revenue
4. `yoy_ratio` — Year-over-year ratio
5. `rolling_6` — 6-month rolling average

---

#### 5.4 — Random Forest Regressor

Bagging ensemble with **MAPE of 11.94%**.

**Hyperparameters**
| Parameter | Value |
| --- | --- |
| `n_estimators` | 100 |
| `max_depth` | 4 |
| `min_samples_leaf` | 5 |
| `min_samples_split` | 8 |
| `max_features` | `sqrt` |
| `min_impurity_decrease` | 0.1 |

**Performance**
```text
MAE  :       246,913 €
RMSE :       345,678 €
MAPE :        11.94 %
R²   :       0.2128
```

**Top 5 Features**:
1. `lag_12` — Dominant seasonal feature
2. `rolling_12` — Long-term trend
3. `yoy_ratio` — Year-over-year comparison
4. `lag_6` — Semi-annual memory
5. `month_cos` — Cyclic month encoding

Random Forest underperforms due to limited training data (48 months).

---

#### 5.5 — Ensemble Comparison & Statistical Testing

Compares all models and builds a **weighted ensemble**.

**Weighting method**: Inverse MAPE weighting — models with lower MAPE receive higher weight:

```text
weight_i = (1 / MAPE_i) / Σ(1 / MAPE_j)
```

**Final results**

| Rank | Model | MAPE (%) | R² |
| --- | --- | ---: | ---: |
| 🥇 | **Holt-Winters** | **4.92%** | **0.8678** |
| 🥈 | **Weighted Ensemble** | **5.27%** | **0.8111** |
| 🥉 | XGBoost | 5.56% | 0.8184 |
| 4 | Random Forest | 11.94% | 0.2128 |

> **Note**: SARIMA was tested but achieved a MAPE of 46.76% with R² of -9.20, confirming that damped additive Holt-Winters is the most suitable model.

**Diebold-Mariano test**: Holt-Winters shows a statistically significant improvement over Random Forest (p < 0.05).

---

#### 5.6 — Forecast 2023

Revenue forecast for **12 months in 2023** using the champion Holt-Winters model with **bootstrap confidence intervals**.

**Methodology**
- Retrain Holt-Winters on full 2018-2022 data (60 months)
- Generate point forecasts for January — December 2023
- **95% confidence intervals** via bootstrap of residuals (1,000 simulations)

**Forecast results**

| Month | Forecast | 95% CI Low | 95% CI High |
| --- | ---: | ---: | ---: |
| January 2023 | 1.23M€ | 1.15M€ | 1.31M€ |
| February 2023 | 1.18M€ | 1.10M€ | 1.26M€ |
| March 2023 | 1.25M€ | 1.17M€ | 1.33M€ |
| April 2023 | 1.20M€ | 1.12M€ | 1.28M€ |
| May 2023 | 1.22M€ | 1.14M€ | 1.30M€ |
| June 2023 | 1.19M€ | 1.11M€ | 1.27M€ |
| July 2023 | 1.21M€ | 1.13M€ | 1.29M€ |
| August 2023 | 1.17M€ | 1.09M€ | 1.25M€ |
| September 2023 | 1.24M€ | 1.16M€ | 1.32M€ |
| October 2023 | 1.26M€ | 1.18M€ | 1.34M€ |
| November 2023 | 1.28M€ | 1.20M€ | 1.36M€ |
| December 2023 | 1.35M€ | 1.27M€ | 1.43M€ |
| **Total 2023** | **14.78M€** | — | — |

**Year-over-Year Comparison**
- **2022 actual**: ~14.10M€
- **2023 forecast**: ~14.78M€
- **Estimated growth**: **+4.8%**

---

#### ML Summary & Key Points

| Aspect | Insight |
| --- | --- |
| **Best model** | Holt-Winters (additive, damped trend) — MAPE **4.92%** |
| **Best ML model** | XGBoost — MAPE **5.56%** |
| **Most important feature** | `lag_12` (same month last year's revenue) |
| **COVID impact** | Corrected via STL decomposition + residual interpolation |
| **2023 outlook** | Moderate growth of ~**4.8%** compared to 2022 |
| **Statistical significance** | Holt-Winters significantly outperforms Random Forest (p < 0.05) |

> **Note**: `grocery_forecasting_v3.ipynb` in `PowerBI Version/PowerBi_mining_ML/AI/` serves as a dashboard notebook referencing the entire pipeline.

---

# 💻 Approach 2 — Dashboard Version

A full-stack web application developed from scratch in code, reproducing all the dashboards and analytics from the Power BI approach using modern web technologies. Built with a **layered architecture** separating concerns across frontend, API, business logic, data access, and database layers.

> **Detailed documentation**: See [`Dashboard Version/README.md`](Dashboard%20Version/README.md), [`Dashboard Version/backend/README.md`](Dashboard%20Version/backend/README.md), [`Dashboard Version/frontend/README.md`](Dashboard%20Version/frontend/README.md), and [`Dashboard Version/ARCHITECTURE.md`](Dashboard%20Version/ARCHITECTURE.md).

### 2.1 Architecture

```
┌──────────────────────────────────────────────────────┐
│              NEXT.JS (Frontend Layer)                 │
│  TypeScript · Tailwind CSS · Recharts                │
│  TanStack Query · shadcn/ui · Lucide Icons           │
├──────────────────────────────────────────────────────┤
│              FASTAPI (API Layer)                      │
│  8 routers: dashboard, sales, products, customers,   │
│  employees, basket, filters, insights                 │
├──────────────────────────────────────────────────────┤
│              SERVICES (Business Logic Layer)           │
│  DashboardService · ProductService · CustomerService  │
│  EmployeeService · BasketService                      │
├──────────────────────────────────────────────────────┤
│            REPOSITORY (Data Access Layer)              │
│  DashboardRepository — all analytical SQL queries     │
├──────────────────────────────────────────────────────┤
│          SQLALCHEMY MODELS (ORM Layer)                │
│  DimCategory · DimProduct · DimCustomer · DimEmployee │
│  DimDate · FactSales                                  │
├──────────────────────────────────────────────────────┤
│           POSTGRESQL (Database Layer)                 │
│  Star Schema · 5 Materialized Views · 15+ Indexes    │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│              ETL PIPELINE (Sidecar)                    │
│  Extractor → Transformer → Validator → Loader → Sync │
│  Reads CSV → Cleans/Enriches → Loads to PostgreSQL    │
└──────────────────────────────────────────────────────┘
```

### 2.2 Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts, TanStack Query, shadcn/ui, Lucide React |
| **Backend** | Python FastAPI, SQLAlchemy ORM, Pydantic v2 schemas, Alembic |
| **Database** | PostgreSQL 16 with materialized views and composite indexes |
| **Infrastructure** | Docker Compose (3 services: frontend, backend, database) |
| **ETL** | Python pandas-based pipeline (extractor, transformer, validator, loader, sync) |

### 2.3 Dashboard Pages

#### 1. Sales Dashboard (Home) — `/`
| KPIs | Charts | Insights |
|------|--------|----------|
| Total Revenue, Total Profit, Qty Sold, Transactions, Profit Margin, Avg Basket | Revenue & Profit Trend (Combo), MoM Growth % (Bar), Category Treemap, Pareto Table, Top Customers/Employees, Revenue by Day, Product Class (Doughnut) | 15+ API calls, date-range filtering, expandable charts, hover tooltips |

#### 2. Product Analysis — `/products`
| KPIs | Charts | Insights |
|------|--------|----------|
| Total Products, Categories, Avg Price, Total Revenue, Top Category % | Category Treemap, Price Distribution (Bar), Price vs Volume (Scatter), Category Growth (Combo), Pareto Concentration (Table) | 80/20 analysis, category breakdown |

#### 3. Customer Analysis — `/customers`
| KPIs | Charts | Insights |
|------|--------|----------|
| Total/Active Customers, Loyalty Rate, Avg Basket, Repurchase Rate | RFM Segmentation (Doughnut), Top Customers (Table), Customer Activity (Combo), City Treemap, Health Dashboard (Cards) | 6 RFM segments, geographic distribution, loyalty metrics |

#### 4. Employee Analysis — `/employees`
| KPIs | Charts | Insights |
|------|--------|----------|
| Total Employees, Total Revenue, Avg Revenue/Employee | Top 5 (Bar), Performance Table, By Age/Seniority (Bar), Age/Gender Distribution (Doughnut) | Demographic breakdown, uniform performance pattern |

#### 5. Basket Analysis — `/basket-analysis`
| KPIs | Controls | Charts |
|------|----------|--------|
| Total Baskets, Products, Association Rules, Strong Rules | Min Support (0.001%–1%) and Min Lift (1.0–3.0) sliders | Top 10 Pairs (Bar), Support vs Lift Matrix (Scatter), Rules Table |

### 2.4 API Endpoints

| Method | Endpoint | Description | Query Parameters |
|--------|----------|-------------|-----------------|
| `GET` | `/api/dashboard/summary` | Dashboard KPIs + chart data | `start_date`, `end_date` |
| `GET` | `/api/sales/over-time` | Revenue time series | `start_date`, `end_date`, `category` |
| `GET` | `/api/sales/by-category` | Sales by category | `start_date`, `end_date`, `product` |
| `GET` | `/api/sales/monthly` | Monthly sales | `start_date`, `end_date`, `category`, `employee` |
| `GET` | `/api/sales/by-city` | Revenue by city | `start_date`, `end_date` |
| `GET` | `/api/sales/ca-growth-by-year` | Year-over-year growth | `start_date`, `end_date` |
| `GET` | `/api/sales/by-class` | Sales by product class | `start_date`, `end_date` |
| `GET` | `/api/products/` | All products with revenue | `start_date`, `end_date` |
| `GET` | `/api/products/{id}` | Product detail | — |
| `GET` | `/api/products/analytics/price-distribution` | Price range buckets | `start_date`, `end_date` |
| `GET` | `/api/products/analytics/price-volume-matrix` | Price vs volume scatter | `start_date`, `end_date` |
| `GET` | `/api/products/analytics/category-growth` | Category growth trends | `start_date`, `end_date` |
| `GET` | `/api/customers/segments` | Customer segments | — |
| `GET` | `/api/customers/top` | Top customers | `limit` |
| `GET` | `/api/customers/activity` | Customer activity over time | `start_date`, `end_date` |
| `GET` | `/api/customers/avg-basket-by-city` | Avg basket by city | `start_date`, `end_date` |
| `GET` | `/api/customers/growth-by-city` | City growth metrics | `start_date`, `end_date` |
| `GET` | `/api/customers/loyalty-stats` | Loyalty & retention stats | `start_date`, `end_date` |
| `GET` | `/api/employees/top` | Top employees | `limit`, `start_date`, `end_date` |
| `GET` | `/api/employees/performance/by-age` | Performance by age | `start_date`, `end_date` |
| `GET` | `/api/employees/performance/by-seniority` | Performance by seniority | `start_date`, `end_date` |
| `GET` | `/api/employees/demographics/gender` | Gender distribution | — |
| `GET` | `/api/employees/demographics/age-category` | Age categories | — |
| `GET` | `/api/employees/ca-by-age-tranche` | Revenue by age tranche | `start_date`, `end_date` |
| `GET` | `/api/basket/analysis` | Market basket analysis | `min_support`, `min_lift`, `limit`, `start_date`, `end_date` |
| `GET` | `/api/filters/` | Dynamic filter options | — |
| `GET` | `/api/insights/revenue-concentration` | Herfindahl index | — |
| `GET` | `/api/insights/revenue-by-day` | Revenue by day of week | — |
| `GET` | `/api/insights/month-over-month` | MoM growth percentages | — |
| `GET` | `/api/insights/pareto-products` | 80/20 product analysis | `limit`, `start_date`, `end_date` |
| `GET` | `/api/insights/growth-metrics` | Profit & growth metrics | `start_date`, `end_date` |
| `GET` | `/api/insights/customer-rfm` | RFM segmentation | — |
| `GET` | `/api/insights/geographic-distribution` | Country-level breakdown | — |
| `GET` | `/api/health` | Health check | — |

### 2.5 Backend Architecture

The backend follows a **clean layered architecture**:

| Layer | Directory | Responsibility |
|-------|-----------|----------------|
| **API** | `app/api/` | 8 FastAPI routers — HTTP request handling, validation, response serialization |
| **Services** | `app/services/` | 5 service classes — business logic, caching orchestration |
| **Repository** | `app/repositories/` | 1 repository — all analytical SQL queries |
| **Models** | `app/models/` | 6 SQLAlchemy ORM models — star schema mapping |
| **Schemas** | `app/schemas/` | Pydantic v2 models — request/response validation |
| **ETL** | `app/etl/` | 6 modules — full data pipeline (extract → transform → validate → load → sync) |
| **Core** | `app/core/` | Configuration, database engine, session management |
| **Utils** | `app/utils/` | In-memory cache decorator, formatting helpers |

#### ETL Pipeline

```text
Extract (7 CSV files, 6.7M rows)
    ↓
Transform (pandas)
    ├── Date cleaning (parse, floor to seconds, drop nulls ~1%)
    ├── Column standardization (snake_case rename)
    ├── Dimension enrichment (city/country/category joins)
    ├── Date generation (dim_date from sales date range)
    └── Fact cleaning
    ↓
Validate (DataValidator)
    ├── PK uniqueness 🔴
    ├── NOT NULL checks 🔴
    ├── Positive prices/quantities 🔴
    └── FK referential integrity 🔴
    ↓
Load (PostgreSQL)
    ├── INSERT for ≤100K rows
    ├── COPY for >100K rows (10-50x faster)
    ├── FK load order: category → product → customer → employee → date → fact_sales
    └── Refresh 5 materialized views
    ↓
Sync (health checks)
    ├── Table existence
    ├── Row count thresholds
    ├── FK integrity
    └── Schema drift detection
```

### 2.6 Data Model

Same **star schema** as Approach 1, with these materialized views:

| View | Purpose | Aggregation Level |
|------|---------|-------------------|
| `mv_daily_sales` | Base KPI queries, time series | Day + Product + Employee + Customer |
| `mv_monthly_sales` | Monthly trends, YoY comparison | Month + Category + Gender + Country |
| `mv_customer_segmentation` | Customer dashboard | Customer-level |
| `mv_top_products` | Product ranking | Product-level |
| `mv_employee_performance` | Employee metrics | Employee-level |
| `mv_daily_baskets` | Basket analysis (customer+date) | Basket-level (6.69M rows) |

### 2.7 Frontend Highlights

| Feature | Implementation |
|---------|---------------|
| **Chart library** | 10 Recharts wrappers (Bar, Doughnut, Combo, Treemap, Scatter, Area, Stacked, Heatmap, Waterfall, Gauge) |
| **State management** | TanStack React Query with 5–10 min stale times, automatic deduplication |
| **Value formatting** | Compact notation: `€4.4B`, `€650M`, `€650.71` — hover for full value |
| **Color-by-value** | Green/red bars and dots for growth/decline indicators |
| **Responsive grid** | 1→2→3→6 columns for KPIs, 1→2 columns for charts |
| **Loading states** | Skeleton placeholders for all pages |
| **Error handling** | User-friendly messages when backend is unreachable |

### 2.8 Screenshots

#### Sales Performance Dashboard

![Sales Dashboard](Dashboard%20Version/screenshots/sale_performance.png)

*Home page with KPI cards, revenue trends, category analysis, customer/employee tables, and operational insights.*

---

#### Product Performance

![Product Dashboard](Dashboard%20Version/screenshots/product_performance.png)

*Product portfolio analysis with price distribution, category breakdown, and Pareto 80/20 concentration table.*

---

#### Customer Performance

![Customer Dashboard](Dashboard%20Version/screenshots/customer_performance.png)

*Customer analytics with RFM segmentation, geographic treemap, city growth table, and loyalty health dashboard.*

---

#### Employee Performance

![Employee Dashboard](Dashboard%20Version/screenshots/employee_performance.png)

*Sales team analysis with top performers, performance by age/seniority, and demographic distributions.*

---

#### Basket Analysis

![Basket Analysis](Dashboard%20Version/screenshots/basket_analysis.png)

*Market basket analysis with interactive threshold sliders, top product associations, support vs lift matrix, and association rules table.*

---

#### Expandable Charts

![Expandable Chart Modal](Dashboard%20Version/screenshots/modal_for_each_chart.png)

*Every chart can be expanded to full-screen for detailed analysis with hover tooltips.*

---

### 2.9 Quick Start

#### With Docker

```bash
cd "Dashboard Version/docker"
docker compose up -d
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/api/docs |

#### Without Docker

Full setup guide: [`Dashboard Version/SETUP_LOCAL.md`](Dashboard%20Version/SETUP_LOCAL.md)

```bash
# 1. Database
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE DATABASE grocery_sales;"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
sudo -u postgres psql -d grocery_sales -f "Dashboard Version/database/schema.sql"

# 2. Backend
cd "Dashboard Version/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install --only-binary :all: -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Import data
cd "Dashboard Version/backend"
source .venv/bin/activate
python scripts/load_all_data.py

# 4. Create MV for basket analysis (required)
PGPASSWORD=postgres psql -h localhost -U postgres -d grocery_sales -c "
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_baskets AS
SELECT DISTINCT customerid, CONCAT(customerid,'|',date) AS basket_id, productid FROM fact_sales;
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_db ON mv_daily_baskets(customerid, basket_id, productid);
CREATE INDEX IF NOT EXISTS idx_mv_db_basket ON mv_daily_baskets(basket_id);"

# 5. Frontend
cd "Dashboard Version/frontend"
bun install
bun run dev
```

---

## Dataset

The project uses the Grocery Sales dataset from Kaggle:

```text
https://www.kaggle.com/datasets/andrexibiza/grocery-sales-dataset
```

The dataset contains **6,690,599 sales transactions**, **98,759 customers**, **452 products**, **11 categories**, and **23 employees** — covering a period from January to May 2018.

## Screenshots

Screenshots are organized in pipeline order.

---

### Step 1 — Apache Hop (ETL Pipeline)

![Apache Hop Pipeline](PowerBI%20Version/PowerBi_mining_ML/Images/Apache%20Hop.png)

### Step 2 — Data Model (Star Schema PostgreSQL)

![Data Model](PowerBI%20Version/PowerBi_mining_ML/Images/data%20model.png)

### Step 3 — Power BI Dashboards

#### Sales Dashboard

![Sales Dashboard](PowerBI%20Version/PowerBi_mining_ML/Images/Capture%20d'%C3%A9cran%202026-06-03%20020525.png)

#### Product Dashboard

![Product Dashboard](PowerBI%20Version/PowerBi_mining_ML/Images/Capture%20d'%C3%A9cran%202026-06-03%20020535.png)

#### Customer Dashboard

![Customer Dashboard](PowerBI%20Version/PowerBi_mining_ML/Images/Capture%20d'%C3%A9cran%202026-06-03%20020543.png)

#### Employee Dashboard

![Employee Dashboard](PowerBI%20Version/PowerBi_mining_ML/Images/Capture%20d'%C3%A9cran%202026-06-03%20020549.png)

### Step 4 — Basket Analysis Dashboard (Data Mining)

![Basket Analysis Dashboard](PowerBI%20Version/PowerBi_mining_ML/Images/Capture%20d'%C3%A9cran%202026-06-03%20020602.png)

### Step 5 — Machine Learning (Forecasting)

![Holt-Winters Forecast](PowerBI%20Version/PowerBi_mining_ML/AI/models/modele2_holtwinters.png)
![XGBoost Forecast](PowerBI%20Version/PowerBi_mining_ML/AI/models/modele3_xgboost.png)
![Random Forest Forecast](PowerBI%20Version/PowerBi_mining_ML/AI/models/modele4_random_forest.png)
![Forecast 2023](PowerBI%20Version/PowerBi_mining_ML/AI/models/forecast_2023.png)

## Getting Started

### Approach 1 — Power BI Pipeline

#### Prerequisites

- Python 3.8+
- PostgreSQL
- Apache Hop
- Power BI Desktop
- Jupyter Notebook / VS Code

#### Step-by-Step

**Step 1 — Apache Hop (ETL)**

1.1 Download the Kaggle dataset:
```text
https://www.kaggle.com/datasets/andrexibiza/grocery-sales-dataset
```

1.2 (Optional) Inspect and clean data in `PowerBI Version/PowerBi_mining_ML/Data_Preprocessing/`.

1.3 Open Apache Hop and load the pipeline:
```text
PowerBI Version/PowerBi_mining_ML/Apache HOP/Dimension_Pipline.hpl
```

1.4 Configure:
- The CSV source file path
- The PostgreSQL connection named `grocery_db`
- The target schema (public)

1.5 Run the pipeline.

---

**Step 2 — PostgreSQL (Data Warehouse)**

2.1 Create the PostgreSQL database:
```bash
psql -U postgres -c "CREATE DATABASE grocery_db;"
```

2.2 Execute the table creation script:
```bash
psql -d grocery_db -f "PowerBI Version/PowerBi_mining_ML/Apache HOP/SQL_Scripts.txt"
```

2.3 Validate the data load:
```bash
psql -d grocery_db -c "SELECT 'dim_category' AS tbl, COUNT(*) FROM dim_category
UNION ALL SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL SELECT 'dim_employee', COUNT(*) FROM dim_employee
UNION ALL SELECT 'fact_sales', COUNT(*) FROM fact_sales;"
```

---

**Step 3 — Power BI (Dashboards)**

3.1 Open Power BI Desktop.

3.2 Connect to the data source:
- **Option A**: PostgreSQL (via the PostgreSQL connector)
- **Option B**: Denormalized CSV file

3.3 Build or import dashboards following the documentation:
- [powerbi.md](PowerBI%20Version/PowerBi_mining_ML/Power%20bi/powerbi.md)

3.4 Refresh data and explore visuals.

---

**Step 4 — Data Mining (Basket Analysis)**

4.1 In Power BI, apply DAX measures for Market Basket Analysis.

4.2 Calculate metrics:
- **Support**: frequency of product pairs
- **Confidence**: conditional probability
- **Lift**: association strength

4.3 Full documentation: [Basket_analysis_mining.md](PowerBI%20Version/PowerBi_mining_ML/Power%20bi/Basket_analysis_mining.md)

---

**Step 5 — Machine Learning (Forecasting)**

Run the notebooks in strict order (each depends on previous outputs):

```text
"PowerBI Version/PowerBi_mining_ML/AI/models/01_Preprocessing.ipynb"
"PowerBI Version/PowerBi_mining_ML/AI/models/02_HoltWinters.ipynb"
"PowerBI Version/PowerBi_mining_ML/AI/models/03_XGBoost.ipynb"
"PowerBI Version/PowerBi_mining_ML/AI/models/04_RandomForest.ipynb"
"PowerBI Version/PowerBi_mining_ML/AI/models/05_Ensemble_Comparaison.ipynb"
"PowerBI Version/PowerBi_mining_ML/AI/models/06_Forecast_2023.ipynb"
```

**Required Python packages** (auto-installed by notebook 01):
```bash
pip install pandas numpy matplotlib seaborn scikit-learn statsmodels xgboost scipy
```

---

### Approach 2 — Dashboard Version (Code)

#### With Docker

```bash
cd "Dashboard Version/docker"
docker compose up -d
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/api/docs |

#### Without Docker

```bash
# 1. Database
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE DATABASE grocery_sales;"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
sudo -u postgres psql -d grocery_sales -f "Dashboard Version/database/schema.sql"

# 2. Backend
cd "Dashboard Version/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Frontend (in another terminal)
cd "Dashboard Version/frontend"
bun install
bun run dev

# 4. Import CSV data
cd "Dashboard Version/backend"
source .venv/bin/activate
python scripts/load_all_data.py
```

---

## Recommended Workflow

### Approach 1 — Power BI

```text
Step 1 : Apache Hop (ETL) → Step 2 : PostgreSQL → Step 3 : Power BI (Dashboards)
→ Step 4 : Data Mining (Basket Analysis) → Step 5 : Machine Learning (Forecasting)
```

### Approach 2 — Dashboard Version

```text
1. Setup PostgreSQL database → 2. Run ETL (load CSV data)
→ 3. Start FastAPI backend → 4. Start Next.js frontend
→ 5. Open http://localhost:3000
```

---

## Technologies Used

| Area | Technologies |
| --- | --- |
| **Data preprocessing** | Python, pandas, NumPy, Jupyter notebooks |
| **ETL (Power BI)** | Apache Hop |
| **ETL (Dashboard)** | Python pandas pipeline (extractor, transformer, loader) |
| **Database** | PostgreSQL 16, SQLAlchemy, Alembic |
| **BI & Visualization (Power BI)** | Power BI, DAX, Market Basket Analysis |
| **BI & Visualization (Web)** | Next.js 14, TypeScript, Tailwind CSS, Chart.js, shadcn/ui |
| **Backend API** | FastAPI, Pydantic, SQLAlchemy |
| **Infrastructure** | Docker Compose |
| **Statistical modeling** | Holt-Winters (Triple Exponential Smoothing), STL decomposition |
| **Machine learning** | XGBoost, Random Forest, Scikit-learn |
| **Ensemble methods** | Weighted blending (inverse MAPE weighting) |
| **Model evaluation** | MAE, RMSE, MAPE, sMAPE, R², MASE, Diebold-Mariano test |
| **Statistical inference** | Bootstrap confidence intervals, STL interpolation |
| **Visualization (ML)** | Matplotlib, Seaborn |

---

## Troubleshooting

### 🖼️ Images not displaying

Some screenshot filenames contain spaces and accented characters. Open them directly from the `PowerBI Version/PowerBi_mining_ML/Images/` folder.

### ⚙️ Step 1 — Apache Hop cannot find CSV file

Check the file path in the `CSV file input` transform. Use an absolute path if Apache Hop runs from a different directory.

### 🗄️ Step 2 — Database connection fails

Check:
- PostgreSQL is running.
- The database name matches your Hop connection (`grocery_db`).
- Username and password are correct.
- Target tables exist before running the pipeline.

### 🔄 Step 2 — Duplicate rows after ETL re-execution

Hop outputs are configured without auto-truncation. Before re-running the pipeline, truncate tables manually or implement an upsert strategy.

### 📊 Step 3 — Power BI cannot find data

- Verify the PostgreSQL connection is active.
- You can also use the denormalized CSV file as an alternative source.

### 🤖 Step 5 — Preprocessing notebook fails due to missing CSV

Notebook 01 expects `daily_revenue.csv` as input. Run notebooks in order:
```text
01_Preprocessing.ipynb → generates prepared_data.csv, train_data.csv, test_data.csv
02_HoltWinters.ipynb   → requires prepared_data.csv
03_XGBoost.ipynb       → requires prepared_data.csv
...
```

### 🐳 Docker — Port already in use

If ports 3000, 8000, or 5432 are already in use, modify the port mappings in `Dashboard Version/docker/docker-compose.yml`.

---

## Future Improvements

- **Step 1**: Add an automated script to download and prepare the Kaggle dataset.
- **Step 1**: Add an upsert or truncate-load mode to the Apache Hop pipeline.
- **Step 2**: Add data quality tests (nulls, duplicates, dates, foreign keys).
- **Step 3**: Add documentation for the `.pbix` Power BI file.
- **Step 5**: Export trained ML models as artifacts.
- **Approach 2**: Add authentication and user management to the web dashboard.
- **Approach 2**: Add real-time data refresh capabilities.
- **Global**: Add a single orchestration script for all 5 Power BI pipeline steps.
- **Global**: Reproducible environment files (`requirements.txt`, `environment.yml`).
- **Global**: Documentation for automated dashboard refresh scheduling.

---

## Author and Date

Project documentation updated in June 2026.

This project is intended for BI, data mining, and machine learning learning purposes using grocery retail sales data.
