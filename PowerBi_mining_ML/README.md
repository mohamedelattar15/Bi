# Grocery Sales BI, Data Mining, and Machine Learning Project

This project is an end-to-end Business Intelligence and analytics solution for a grocery sales dataset. It combines data preprocessing, data warehouse modeling, Apache Hop ETL pipelines, Power BI dashboards, market basket analysis, and machine learning models for sales forecasting.

The goal is to transform raw grocery transaction data into business-ready insights: sales performance, product performance, customer behavior, employee performance, product associations, and revenue forecasts.

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
    └── models/
        ├── 01_Preprocessing.ipynb
        ├── 02_HoltWinters.ipynb
        ├── 03_XGBoost.ipynb
        ├── 04_RandomForest.ipynb
        ├── 05_Ensemble_Comparaison.ipynb
        └── 06_Forecast_2023.ipynb
```

> Note: Some screenshot file names contain accented characters on disk. If an image does not display in a Markdown viewer, open it directly from the `Images/` folder.

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

The project also uses a denormalized sales file for easier analysis and ETL loading. More details are available in [grocery_sales_denormalized_README.md](<Apache HOP/grocery_sales_denormalized_README.md>).

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

The SQL script for creating the warehouse tables is available in [SQL_Scripts.txt](<Apache HOP/SQL_Scripts.txt>).

## ETL Pipeline

The Apache Hop pipeline loads the denormalized grocery sales file into the star schema.

Pipeline file:

```text
Apache HOP/Dimension_Pipline.hpl
```

Detailed documentation:

[Dimension_Pipline_README.md](<Apache HOP/Dimension_Pipline_README.md>)

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

[powerbi.md](<Power bi/powerbi.md>)

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

[Basket_analysis_mining.md](<Power bi/Basket_analysis_mining.md>)

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

The `AI/` folder contains notebooks for revenue forecasting. The workflow is modular: preprocessing is done first, then each forecasting model is trained and compared.

Main dashboard notebook:

[grocery_forecasting_v3.ipynb](AI/grocery_forecasting_v3.ipynb)

Model notebooks:

| Notebook | Purpose |
| --- | --- |
| [01_Preprocessing.ipynb](AI/models/01_Preprocessing.ipynb) | Load daily revenue, aggregate monthly, correct COVID impact, engineer features, split train/test, define metrics. |
| [02_HoltWinters.ipynb](AI/models/02_HoltWinters.ipynb) | Train Holt-Winters forecasting models. |
| [03_XGBoost.ipynb](AI/models/03_XGBoost.ipynb) | Train XGBoost with engineered time-series features. |
| [04_RandomForest.ipynb](AI/models/04_RandomForest.ipynb) | Train Random Forest regression for revenue forecasting. |
| [05_Ensemble_Comparaison.ipynb](AI/models/05_Ensemble_Comparaison.ipynb) | Compare models and build a weighted ensemble. |
| [06_Forecast_2023.ipynb](AI/models/06_Forecast_2023.ipynb) | Generate 2023 forecasts with confidence intervals. |

The preprocessing notebook includes:

- Monthly revenue aggregation
- COVID-period correction using STL interpolation
- Lag features
- Rolling-window features
- Year-over-year features
- Time features
- Train/test split
- Walk-forward validation helpers
- Metrics: MAE, RMSE, MAPE, sMAPE, R2, MASE, Diebold-Mariano test

Model comparison results observed in the ensemble notebook:

| Rank | Model | MAPE | R2 |
| --- | --- | ---: | ---: |
| 1 | Holt-Winters | 4.92% | 0.8678 |
| 2 | Weighted Ensemble | 5.27% | 0.8111 |
| 3 | XGBoost | 5.56% | 0.8184 |
| 4 | Random Forest | 11.94% | 0.2128 |
| 5 | SARIMA | 46.76% | -9.2000 |

> Note: `grocery_forecasting_v3.ipynb` mentions SARIMA and Prophet in its dashboard text, but the current repository contains Holt-Winters, XGBoost, Random Forest, Ensemble Comparison, and Forecast 2023 notebooks.

## Screenshots

### Apache Hop Pipeline

![Apache Hop Pipeline](<Images/Capture d'écran 2026-06-03 012115.png>)

### Sales Dashboard

![Sales Dashboard](<Images/Capture d'écran 2026-06-03 020525.png>)

### Product Dashboard

![Product Dashboard](<Images/Capture d'écran 2026-06-03 020535.png>)

### Customer Dashboard

![Customer Dashboard](<Images/Capture d'écran 2026-06-03 020543.png>)

### Employee Dashboard

![Employee Dashboard](<Images/Capture d'écran 2026-06-03 020549.png>)

### Basket Analysis Dashboard

![Basket Analysis Dashboard](<Images/Capture d'écran 2026-06-03 020602.png>)

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
psql -d grocery_db -f "Apache HOP/SQL_Scripts.txt"
```

The script creates:

- `dim_category`
- `dim_product`
- `dim_customer`
- `dim_employee`
- `fact_sales`

### 4. Configure Apache Hop

In Apache Hop:

1. Open `Apache HOP/Dimension_Pipline.hpl`.
2. Configure the CSV file path.
3. Configure the PostgreSQL connection named `grocery_db`.
4. Confirm that the target schema is `public`.
5. Run the pipeline.

### 5. Open Power BI

Use the generated warehouse tables or the denormalized CSV file as the data source. Recreate or connect the model according to the documentation in [powerbi.md](<Power bi/powerbi.md>).

### 6. Run Forecasting Notebooks

Open the notebooks in Jupyter, VS Code, or another notebook environment.

Recommended order:

```text
AI/models/01_Preprocessing.ipynb
AI/models/02_HoltWinters.ipynb
AI/models/03_XGBoost.ipynb
AI/models/04_RandomForest.ipynb
AI/models/05_Ensemble_Comparaison.ipynb
AI/models/06_Forecast_2023.ipynb
```

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
| Data preprocessing | Python, pandas, Jupyter notebooks |
| ETL | Apache Hop |
| Database | PostgreSQL |
| BI and visualization | Power BI, DAX |
| Data mining | Market Basket Analysis, support, confidence, lift |
| Forecasting | Holt-Winters, XGBoost, Random Forest, weighted ensemble |
| Model evaluation | MAE, RMSE, MAPE, sMAPE, R2, MASE, Diebold-Mariano |

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

Run `01_Preprocessing.ipynb` first, then run the model notebooks.

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
