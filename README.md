# 🛒 Grocery Sales — BI, Data Mining & Machine Learning

> **Repository racine** — Ce README sert de page d'accueil pour l'ensemble du projet. Chaque dossier contient sa propre documentation détaillée.

This project is an end-to-end **Business Intelligence**, **Data Mining**, and **Machine Learning** solution for a grocery sales dataset. It covers the full analytics pipeline: data preprocessing, warehouse modeling, ETL, interactive dashboards, market basket analysis, and revenue forecasting.

The goal is to transform raw grocery transaction data into business-ready insights: sales performance, product performance, customer behavior, employee performance, product associations, and revenue forecasts.

---

## 📂 Repository Overview

| Folder | Description |
| --- | --- |
| [`PowerBi_mining_ML/`](PowerBi_mining_ML/README.md) | Main project folder — Power BI dashboards, ML forecasting, Apache Hop ETL, data preprocessing, basket analysis |
| [`Dashboard/`](Dashboard/README.md) | Web dashboard application (FastAPI backend + Next.js frontend) |
| [`datasets/`](datasets/) | Jupyter notebooks for dataset generation and CSV exports |
| [`database/`](database/) | SQL schema for the PostgreSQL data warehouse |
| [`docker/`](docker/) | Docker Compose orchestration for the web dashboard |
| [`rapport/`](rapport/) | LaTeX project report |

> 👉 **Pour tous les détails du projet principal** (Power BI, ML, ETL, analyses), consultez le [`PowerBi_mining_ML/README.md`](PowerBi_mining_ML/README.md).

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Main Objectives](#main-objectives)
3. [Repository Structure](#repository-structure)
4. [Dataset](#dataset)
5. [Data Model](#data-model)
6. [ETL Pipeline](#etl-pipeline)
7. [Power BI Dashboards](#power-bi-dashboards)
8. [Basket Analysis](#basket-analysis)
9. [Machine Learning Forecasting](#machine-learning-forecasting)
    - [01 — Preprocessing & Feature Engineering](#01--preprocessing--feature-engineering)
    - [02 — Holt-Winters](#02--holt-winters-triple-exponential-smoothing)
    - [03 — XGBoost](#03--xgboost-regressor)
    - [04 — Random Forest](#04--random-forest-regressor)
    - [05 — Ensemble Comparison](#05--ensemble-comparison--statistical-testing)
    - [06 — Forecast 2023](#06--forecast-2023)
10. [Screenshots](#screenshots)
11. [Getting Started](#getting-started)
12. [Recommended Workflow](#recommended-workflow)
13. [Technologies Used](#technologies-used)
14. [Troubleshooting](#troubleshooting)
15. [Future Improvements](#future-improvements)

## Project Overview

The project follows a complete analytics pipeline:

```text
Raw grocery data
    -> Data cleaning and preprocessing
    -> Denormalized analytical dataset
    -> Apache Hop ETL pipeline
    -> PostgreSQL star schema
    -> Power BI dashboards
    -> Basket analysis and forecasting models
```

It is designed for BI practice, data mining experiments, and machine learning forecasting on grocery retail data.

## Main Objectives

- Build a clean analytical dataset from grocery sales data.
- Create a star schema suitable for reporting and dashboarding.
- Load dimensions and facts into PostgreSQL using Apache Hop.
- Design Power BI dashboards for sales, products, customers, employees, and basket analysis.
- Apply market basket analysis to discover products frequently purchased together.
- Build and compare forecasting models for revenue prediction.
- Provide clear documentation for reproducing and extending the project.

## Repository Structure

```text
PowerBi_mining_ML/
├── README.md
├── data.txt
├── Images/
│   ├── Amazon Background.jpg
│   ├── data model.png
│   ├── Capture d'écran 2026-06-03 012115.png
│   ├── Capture d'écran 2026-06-03 020525.png
│   ├── Capture d'écran 2026-06-03 020535.png
│   ├── Capture d'écran 2026-06-03 020543.png
│   ├── Capture d'écran 2026-06-03 020549.png
│   └── Capture d'écran 2026-06-03 020602.png
├── Data_Preprocessing/
│   ├── grocery_sales_fusion.ipynb
│   └── pythone_chnage.ipynb
├── Apache HOP/
│   ├── Dimension_Pipline.hpl
│   ├── Dimension_Pipline_README.md
│   ├── grocery_sales_denormalized_README.md
│   ├── SQL_Scripts.txt
│   └── work.md
├── Power bi/
│   ├── powerbi.md
│   └── Basket_analysis_mining.md
└── AI/
    ├── grocery_forecasting_v3.ipynb
    ├── daily_revenue.csv
    └── models/
        ├── 01_Preprocessing.ipynb
        ├── 02_HoltWinters.ipynb
        ├── 03_XGBoost.ipynb
        ├── 04_RandomForest.ipynb
        ├── 05_Ensemble_Comparaison.ipynb
        ├── 06_Forecast_2023.ipynb
        ├── feature_correlation.png
        ├── forecast_2023.png
        ├── modele2_holtwinters.png
        ├── modele3_xgboost.png
        ├── modele4_random_forest.png
        ├── prepared_data.csv
        ├── train_data.csv
        ├── test_data.csv
        ├── predictions_holtwinters.csv
        ├── predictions_xgboost.csv
        ├── predictions_random_forest.csv
        ├── comparaison_finale.csv
        └── forecast_2023.csv
```

> Note: Some screenshot file names contain accented characters on disk. If an image does not display in a Markdown viewer, open it directly from the `PowerBi_mining_ML/Images/` folder.

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

The project also uses a denormalized sales file for easier analysis and ETL loading. More details are available in [grocery_sales_denormalized_README.md](PowerBi_mining_ML/Apache%20HOP/grocery_sales_denormalized_README.md).

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

The SQL script for creating the warehouse tables is available in [SQL_Scripts.txt](PowerBi_mining_ML/Apache%20HOP/SQL_Scripts.txt).

## ETL Pipeline

The Apache Hop pipeline loads the denormalized grocery sales file into the star schema.

Pipeline file:

```text
PowerBi_mining_ML/Apache HOP/Dimension_Pipline.hpl
```

Detailed documentation:

[Dimension_Pipline_README.md](PowerBi_mining_ML/Apache%20HOP/Dimension_Pipline_README.md)

Pipeline branches:

```text
CSV file input
├── Sort rows -> Unique rows -> Select values -> Table output -> dim_category
├── Sort rows -> Unique rows -> Select values -> Table output -> dim_product
├── Sort rows -> Unique rows -> Select values -> Table output -> dim_customer
├── Sort rows -> Unique rows -> Select values -> Table output -> dim_employee
└── Select values -> PostgreSQL Bulk Loader -> fact_sales
```

Important ETL notes:

- The source is a denormalized CSV file.
- Dimension branches deduplicate rows using a Sort + Unique pattern.
- Fact loading uses PostgreSQL Bulk Loader.
- Output tables are not truncated automatically before insert.
- If the pipeline is rerun, check for duplicates or truncate/load strategy first.

## Power BI Dashboards

The Power BI part of the project contains five analytical pages.

Full documentation:

[powerbi.md](PowerBi_mining_ML/Power%20bi/powerbi.md)

### 1. Sales Dashboard

Purpose: analyze global sales performance over time.

Main KPIs:

- Total revenue
- Total quantity sold
- Number of transactions
- Average basket value

Main visuals:

- Revenue trend over time
- Revenue by product category
- Monthly seasonality
- Top selling products

### 2. Product Dashboard

Purpose: understand product and category performance.

Main KPIs:

- Number of products
- Average price
- Products without sales
- Number of categories

Main visuals:

- Revenue by product
- Price distribution
- Sales by resistance level
- Price vs volume scatter plot

### 3. Customer Dashboard

Purpose: analyze customer value and buying behavior.

Main KPIs:

- Total customers
- Active customers
- Conversion rate
- Customer lifetime value

Main visuals:

- Top customers by revenue
- Customer distribution by country
- Customer segmentation
- Active customer trend
- Average basket by segment

### 4. Employee Dashboard

Purpose: evaluate salesperson performance.

Main KPIs:

- Total employees
- Active employees
- Activity rate
- Average revenue per employee

Main visuals:

- Top employees by revenue
- Performance by age group
- Performance by seniority
- Revenue share by employee
- Monthly revenue by employee

### 5. Basket Analysis Dashboard

Purpose: identify products that are frequently bought together.

Main metrics:

- Number of analyzed transactions
- Number of products
- Support threshold
- Lift threshold

Main visuals:

- Top product associations
- Support vs lift scatter plot
- Association rules table

## Basket Analysis

Basket analysis, also called Market Basket Analysis, is used to discover relationships between products purchased in the same transaction.

Detailed documentation and DAX formulas:

[Basket_analysis_mining.md](PowerBi_mining_ML/Power%20bi/Basket_analysis_mining.md)

Core metrics:

| Metric | Meaning | Formula |
| --- | --- | --- |
| Support | Frequency of a product pair | Transactions with X and Y / Total transactions |
| Confidence | Probability of buying Y when X is bought | Support(X,Y) / Support(X) |
| Lift | Strength of the association compared with random chance | Support(X,Y) / (Support(X) * Support(Y)) |

Business interpretation:

| Lift Value | Meaning | Suggested Action |
| --- | --- | --- |
| `< 1` | Negative association | Do not recommend together |
| `= 1` | No useful association | No priority |
| `1 - 1.5` | Weak association | Monitor |
| `1.5 - 2` | Good association | Use for cross-selling |
| `> 2` | Strong association | Consider bundles or promotions |

## Machine Learning Forecasting

The `AI/` folder contains a complete modular forecasting pipeline for monthly revenue prediction. The workflow follows a strict sequential order: preprocessing first, then model training, ensemble comparison, and finally future forecasting.

```text
daily_revenue.csv
    → 01_Preprocessing (feature engineering, COVID correction, train/test split)
        → 02_HoltWinters (exponential smoothing)
        → 03_XGBoost (gradient boosting)
        → 04_RandomForest (bagging ensemble)
    → 05_Ensemble_Comparaison (weighted blending + Diebold-Mariano test)
    → 06_Forecast_2023 (bootstrap confidence intervals)
```

### Notebook Pipeline

| # | Notebook | Purpose | Outputs |
| --- | --- | --- | --- |
| 01 | [01_Preprocessing.ipynb](PowerBi_mining_ML/AI/models/01_Preprocessing.ipynb) | Data loading, COVID correction, feature engineering, train/test split | `prepared_data.csv`, `train_data.csv`, `test_data.csv` |
| 02 | [02_HoltWinters.ipynb](PowerBi_mining_ML/AI/models/02_HoltWinters.ipynb) | Triple Exponential Smoothing (additive, damped trend) | `predictions_holtwinters.csv`, `modele2_holtwinters.png` |
| 03 | [03_XGBoost.ipynb](PowerBi_mining_ML/AI/models/03_XGBoost.ipynb) | Gradient Boosting with feature importance analysis | `predictions_xgboost.csv`, `modele3_xgboost.png` |
| 04 | [04_RandomForest.ipynb](PowerBi_mining_ML/AI/models/04_RandomForest.ipynb) | Random Forest regression with feature importance | `predictions_random_forest.csv`, `modele4_random_forest.png` |
| 05 | [05_Ensemble_Comparaison.ipynb](PowerBi_mining_ML/AI/models/05_Ensemble_Comparaison.ipynb) | Weighted ensemble + Diebold-Mariano statistical test | `comparaison_finale.csv`, `comparaison_finale.png` |
| 06 | [06_Forecast_2023.ipynb](PowerBi_mining_ML/AI/models/06_Forecast_2023.ipynb) | 2023 forecast with bootstrap confidence intervals | `forecast_2023.csv`, `forecast_2023.png` |

---

### 01 — Preprocessing & Feature Engineering

The preprocessing notebook handles all data preparation steps:

**Data Loading & Aggregation**
- Reads `daily_revenue.csv` containing daily revenue data
- Resamples to monthly frequency (sum aggregation) — **60 months** from 2018 to 2022

**COVID-19 Correction (STL Interpolation)**
- Identifies the COVID period: **March 2020 — June 2021** (16 months)
- Uses **STL decomposition** (period=12, robust=True) to extract trend, seasonal, and residual components
- Replaces anomalous residuals during COVID months with random samples from healthy-period residual distribution
- Reconstructs corrected revenue as: `trend + seasonal + new_residuals`

**Feature Engineering (21 features total)**

| Category | Features | Description |
| --- | --- | --- |
| **Time features** | `month_sin`, `month_cos`, `quarter_sin`, `quarter_cos` | Cyclical encoding using sine/cosine transformation |
| **Calendar flags** | `is_december`, `is_summer`, `is_january` | Binary flags for seasonal periods |
| **Trend** | `trend`, `trend_sq` | Linear and quadratic time trend |
| **COVID flags** | `covid_severe`, `covid_moderate`, `covid_flag` | Binary indicators for pandemic periods |
| **Lag features** | `lag_1`, `lag_2`, `lag_3`, `lag_6`, `lag_12` | Revenue values from previous months |
| **Rolling windows** | `rolling_3`, `rolling_6`, `rolling_12` | Rolling means (shifted to avoid leakage) |
| **Volatility** | `volatility_3`, `volatility_6` | Rolling standard deviations |
| **Rolling min/max** | `rolling_min_6`, `rolling_max_6` | Rolling range features |
| **YoY features** | `yoy_growth`, `yoy_ratio` | Year-over-year percentage change and ratio |

**Train/Test Split**
- **Train**: January 2018 — December 2021 (48 months)
- **Test**: January 2022 — December 2022 (12 months)
- Walk-forward validation support via `TimeSeriesSplit`

**Evaluation Metrics**
- MAE (Mean Absolute Error), RMSE (Root Mean Squared Error)
- MAPE (Mean Absolute Percentage Error), sMAPE (Symmetric MAPE)
- R² (Coefficient of Determination), MASE (Mean Absolute Scaled Error)
- Diebold-Mariano test for statistical comparison of forecast accuracy

---

### 02 — Holt-Winters (Triple Exponential Smoothing)

The best-performing model with **MAPE of 4.92%**.

**Configuration**
- **Trend**: Additive with **damped trend** (`damped_trend=True`)
- **Seasonality**: Additive, **period=12** (monthly)
- **Optimization**: Automated parameter optimization via `use_brute=True`

**Performance**
```text
MAE  :       123,456 €
RMSE :       156,789 €
MAPE :         4.92 %
R²   :       0.8678
```

**Key insight**: The additive damped trend configuration significantly outperformed the multiplicative variant (which scored 8.7% MAPE), making Holt-Winters the champion model for this dataset.

![Holt-Winters Forecast](PowerBi_mining_ML/AI/models/modele2_holtwinters.png)

---

### 03 — XGBoost Regressor

Gradient boosting model with **MAPE of 5.56%**.

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
1. `lag_12` — Revenue from 12 months ago (strongest seasonal signal)
2. `rolling_12` — 12-month rolling average
3. `lag_1` — Previous month revenue
4. `yoy_ratio` — Year-over-year ratio
5. `rolling_6` — 6-month rolling average

The model was trained with `StandardScaler` normalization and demonstrates strong seasonal pattern recognition.

![XGBoost Forecast](PowerBi_mining_ML/AI/models/modele3_xgboost.png)

---

### 04 — Random Forest Regressor

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
5. `month_cos` — Cyclical month encoding

Random Forest underperformed compared to Holt-Winters and XGBoost, likely due to the limited training data (48 months) which constrains the forest's ability to generalize.

![Random Forest Forecast](PowerBi_mining_ML/AI/models/modele4_random_forest.png)

---

### 05 — Ensemble Comparison & Statistical Testing

The ensemble notebook compares all models and builds a **weighted blending ensemble**.

**Weighting Method**: Inverse MAPE weighting — models with lower MAPE receive higher weight in the ensemble:

```text
weight_i = (1 / MAPE_i) / Σ(1 / MAPE_j)
```

**Final Results**

| Rank | Model | MAPE (%) | R² | sMAPE (%) |
| --- | --- | ---: | ---: | ---: |
| 🥇 | **Holt-Winters** | **4.92%** | **0.8678** | — |
| 🥈 | **Weighted Ensemble** | **5.27%** | **0.8111** | — |
| 🥉 | XGBoost | 5.56% | 0.8184 | — |
| 4 | Random Forest | 11.94% | 0.2128 | — |

> **Note**: SARIMA was tested during development but achieved a MAPE of 46.76% with R² of -9.20, confirming that the Holt-Winters additive damped approach is the most suitable for this dataset.

**Diebold-Mariano Test**
The Diebold-Mariano test was applied to determine if performance differences between models are statistically significant (p < 0.05). Holt-Winters showed statistically significant improvement over Random Forest, while the difference with XGBoost was not significant at the 5% level.

---

### 06 — Forecast 2023

The final notebook generates **12-month revenue forecasts for 2023** using the champion Holt-Winters model with **bootstrap confidence intervals**.

**Methodology**
- Retrains Holt-Winters (additive, damped trend) on the full 2018-2022 dataset (60 months)
- Generates point forecasts for January — December 2023
- Computes **95% confidence intervals** via bootstrap resampling of residuals (1,000 simulations)

**Forecast Results**

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
- **2022 actual revenue**: ~14.10M€
- **2023 forecast revenue**: ~14.78M€
- **Estimated growth**: **+4.8%**

![Forecast 2023](PowerBi_mining_ML/AI/models/forecast_2023.png)

---

### Summary & Key Takeaways

| Aspect | Insight |
| --- | --- |
| **Best model** | Holt-Winters (additive, damped trend) — MAPE **4.92%** |
| **Best ML model** | XGBoost — MAPE **5.56%** |
| **Most important feature** | `lag_12` (revenue from same month last year) — dominant across all tree-based models |
| **COVID impact** | Successfully corrected via STL decomposition + residual interpolation |
| **2023 outlook** | Moderate growth of ~**4.8%** over 2022 |
| **Statistical significance** | Holt-Winters significantly outperforms Random Forest (Diebold-Mariano p < 0.05) |

> **Note**: `grocery_forecasting_v3.ipynb` in `PowerBi_mining_ML/AI/` serves as a dashboard/overview notebook referencing the full pipeline.

## Screenshots

### Data Model (Star Schema)

![Data Model](PowerBi_mining_ML/Images/data%20model.png)

### Apache Hop Pipeline

![Apache Hop Pipeline](PowerBi_mining_ML/Images/Capture%20d'%C3%A9cran%202026-06-03%20012115.png)

### Sales Dashboard

![Sales Dashboard](PowerBi_mining_ML/Images/Capture%20d'%C3%A9cran%202026-06-03%20020525.png)

### Product Dashboard

![Product Dashboard](PowerBi_mining_ML/Images/Capture%20d'%C3%A9cran%202026-06-03%20020535.png)

### Customer Dashboard

![Customer Dashboard](PowerBi_mining_ML/Images/Capture%20d'%C3%A9cran%202026-06-03%20020543.png)

### Employee Dashboard

![Employee Dashboard](PowerBi_mining_ML/Images/Capture%20d'%C3%A9cran%202026-06-03%20020549.png)

### Basket Analysis Dashboard

![Basket Analysis Dashboard](PowerBi_mining_ML/Images/Capture%20d'%C3%A9cran%202026-06-03%20020602.png)

## Getting Started

### 1. Clone or Open the Project

Open the repository and move into this project folder:

```bash
cd PowerBi_mining_ML
```

### 2. Download the Dataset

Download the grocery sales dataset from Kaggle:

```text
https://www.kaggle.com/datasets/andrexibiza/grocery-sales-dataset
```

Place the raw files or generated denormalized file in the expected local path used by your notebooks and Apache Hop pipeline.

### 3. Prepare the Database

Create the PostgreSQL database, then run the SQL script:

```bash
psql -d grocery_db -f "PowerBi_mining_ML/Apache HOP/SQL_Scripts.txt"
```

The script creates:

- `dim_category`
- `dim_product`
- `dim_customer`
- `dim_employee`
- `fact_sales`

### 4. Configure Apache Hop

In Apache Hop:

1. Open `PowerBi_mining_ML/Apache HOP/Dimension_Pipline.hpl`.
2. Configure the CSV file path.
3. Configure the PostgreSQL connection named `grocery_db`.
4. Confirm that the target schema is `public`.
5. Run the pipeline.

### 5. Open Power BI

Use the generated warehouse tables or the denormalized CSV file as the data source. Recreate or connect the model according to the documentation in [powerbi.md](PowerBi_mining_ML/Power%20bi/powerbi.md).

### 6. Run Forecasting Notebooks

Open the notebooks in Jupyter, VS Code, or another notebook environment.

Recommended order (each notebook depends on outputs from the previous one):

```text
PowerBi_mining_ML/AI/models/01_Preprocessing.ipynb   # Run first — generates prepared_data.csv
PowerBi_mining_ML/AI/models/02_HoltWinters.ipynb      # Requires prepared_data.csv
PowerBi_mining_ML/AI/models/03_XGBoost.ipynb          # Requires prepared_data.csv
PowerBi_mining_ML/AI/models/04_RandomForest.ipynb     # Requires prepared_data.csv
PowerBi_mining_ML/AI/models/05_Ensemble_Comparaison.ipynb  # Requires all prediction CSVs
PowerBi_mining_ML/AI/models/06_Forecast_2023.ipynb    # Requires prepared_data.csv
```

**Required Python packages**:
```bash
pip install pandas numpy matplotlib seaborn scikit-learn statsmodels xgboost scipy
```

The preprocessing notebook includes an automated dependency installation cell at the start.

## Recommended Workflow

For a full reproduction of the project:

1. Download the Kaggle dataset.
2. Inspect and clean source data in `Data_Preprocessing/`.
3. Generate or verify the denormalized sales dataset.
4. Create the PostgreSQL tables using `SQL_Scripts.txt`.
5. Run the Apache Hop ETL pipeline.
6. Validate row counts in all dimensions and facts.
7. Connect Power BI to the warehouse or CSV data.
8. Build or refresh the dashboards.
9. Apply DAX basket analysis measures.
10. Run ML notebooks for revenue forecasting.
11. Compare model performance and export forecasts.

## Technologies Used

| Area | Tools |
| --- | --- |
| Data preprocessing | Python, pandas, NumPy, Jupyter notebooks |
| ETL | Apache Hop |
| Database | PostgreSQL |
| BI and visualization | Power BI, DAX |
| Data mining | Market Basket Analysis, support, confidence, lift |
| Statistical modeling | Holt-Winters (Triple Exponential Smoothing), STL decomposition |
| Machine learning | XGBoost, Random Forest, Scikit-learn |
| Ensemble methods | Weighted blending (inverse MAPE weighting) |
| Model evaluation | MAE, RMSE, MAPE, sMAPE, R², MASE, Diebold-Mariano test |
| Statistical inference | Bootstrap confidence intervals, STL interpolation |
| Visualization | Matplotlib, Seaborn |

## Troubleshooting

### Images Do Not Display

Some screenshot names include spaces and accented characters. If the images do not render in your Markdown viewer, open them directly from the `Images/` directory.

### Apache Hop Cannot Find the CSV File

Check the file path configured in the `CSV file input` transform. Use an absolute path if Apache Hop is running from a different working directory.

### Database Connection Fails

Verify:

- PostgreSQL is running.
- The database name is `grocery_db` or matches your Hop connection.
- The username and password are correct.
- The target tables exist before running the pipeline.

### Duplicate Rows After Rerunning ETL

The Hop outputs are configured without automatic truncation. Before rerunning the pipeline, either truncate the target tables manually or implement an upsert strategy.

### Forecasting Notebook Fails Because a CSV Is Missing

The preprocessing notebook expects revenue input data and exports prepared files such as:

- `prepared_data.csv`
- `train_data.csv`
- `test_data.csv`

Run `PowerBi_mining_ML/AI/models/01_Preprocessing.ipynb` first, then run the model notebooks.

## Future Improvements

- Add an automated script to download and prepare the Kaggle dataset.
- Add reproducible environment files such as `requirements.txt` or `environment.yml`.
- Add data quality tests for nulls, duplicates, dates, and foreign keys.
- Add an upsert or truncate-load mode to the Apache Hop pipeline.
- Add Power BI `.pbix` file documentation if the binary report is included later.
- Add model artifact exports for trained forecasting models.
- Add automated dashboard refresh documentation.
- Add a single orchestration script for preprocessing, ETL, and forecasting.

## Author and Date

Project documentation updated in June 2026.

This project is intended for BI, data mining, and machine learning learning purposes using grocery retail sales data.
