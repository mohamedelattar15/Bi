    -- ==========================================
    -- GROCERY SALES DATA WAREHOUSE - PostgreSQL Schema
    -- Based on Power BI Star Schema Design
    -- ==========================================

    -- Drop existing tables (for re-runs)
    DROP TABLE IF EXISTS fact_sales CASCADE;
    DROP TABLE IF EXISTS dim_product CASCADE;
    DROP TABLE IF EXISTS dim_customer CASCADE;
    DROP TABLE IF EXISTS dim_employee CASCADE;
    DROP TABLE IF EXISTS dim_category CASCADE;
    DROP TABLE IF EXISTS dim_date CASCADE;

    -- ==========================================
    -- 1. DIM_DATE (Time Intelligence dimension)
    -- ==========================================
    CREATE TABLE dim_date (
        date_key DATE PRIMARY KEY,
        year INTEGER NOT NULL,
        quarter INTEGER NOT NULL,
        month INTEGER NOT NULL,
        month_name VARCHAR(20) NOT NULL,
        day INTEGER NOT NULL,
        day_of_week INTEGER NOT NULL,
        day_name VARCHAR(20) NOT NULL,
        week_of_year INTEGER NOT NULL,
        is_weekend BOOLEAN NOT NULL DEFAULT FALSE,
        CONSTRAINT chk_quarter CHECK (quarter BETWEEN 1 AND 4),
        CONSTRAINT chk_month CHECK (month BETWEEN 1 AND 12)
    );

    CREATE INDEX idx_dim_date_year ON dim_date(year);
    CREATE INDEX idx_dim_date_month ON dim_date(month);
    CREATE INDEX idx_dim_date_quarter ON dim_date(quarter);

    -- ==========================================
    -- 2. DIM_CATEGORY
    -- ==========================================
    CREATE TABLE dim_category (
        categoryid INTEGER PRIMARY KEY,
        categoryname VARCHAR(100) NOT NULL
    );

    -- ==========================================
    -- 3. DIM_PRODUCT
    -- ==========================================
    CREATE TABLE dim_product (
        productid INTEGER PRIMARY KEY,
        productname VARCHAR(200) NOT NULL,
        price NUMERIC(12,2) NOT NULL DEFAULT 0,
        categoryid INTEGER NOT NULL,
        class VARCHAR(50),
        modifydate DATE,
        resistant VARCHAR(50),
        isallergic VARCHAR(10),
        vitalitydays NUMERIC(8,2),
        categoryname VARCHAR(100),
        CONSTRAINT fk_product_category FOREIGN KEY (categoryid) 
            REFERENCES dim_category(categoryid)
    );

    CREATE INDEX idx_dim_product_category ON dim_product(categoryid);
    CREATE INDEX idx_dim_product_resistant ON dim_product(resistant);
    CREATE INDEX idx_dim_product_class ON dim_product(class);

    -- ==========================================
    -- 4. DIM_CUSTOMER
    -- ==========================================
    CREATE TABLE dim_customer (
        customerid INTEGER PRIMARY KEY,
        customerfirstname VARCHAR(100),
        middleinitial VARCHAR(1),
        customerlastname VARCHAR(100),
        full_name VARCHAR(250) GENERATED ALWAYS AS (
            TRIM(COALESCE(customerfirstname, '') || ' ' || COALESCE(middleinitial || ' ', '') || COALESCE(customerlastname, ''))
        ) STORED,
        address VARCHAR(200),
        cityid INTEGER,
        city VARCHAR(100),
        zipcode VARCHAR(20),
        countryid INTEGER,
        country VARCHAR(100),
        countrycode VARCHAR(2)
    );

    CREATE INDEX idx_dim_customer_city ON dim_customer(city);
    CREATE INDEX idx_dim_customer_country ON dim_customer(country);
    CREATE INDEX idx_dim_customer_fullname ON dim_customer(full_name);

    -- ==========================================
    -- 5. DIM_EMPLOYEE
    -- ==========================================
    CREATE TABLE dim_employee (
        employeeid INTEGER PRIMARY KEY,
        employeefirstname VARCHAR(100),
        employeelastname VARCHAR(100),
        full_name VARCHAR(200) GENERATED ALWAYS AS (
            TRIM(COALESCE(employeefirstname, '') || ' ' || COALESCE(employeelastname, ''))
        ) STORED,
        birthdate DATE,
        gender VARCHAR(20),
        hiredate DATE,
        city VARCHAR(100),
        cityid INTEGER
    );

    CREATE INDEX idx_dim_employee_gender ON dim_employee(gender);

    -- ==========================================
    -- 6. FACT_SALES (Fact table, ~6.7M rows)
    -- ==========================================
    CREATE TABLE fact_sales (
        salesid BIGINT PRIMARY KEY,
        employeeid INTEGER NOT NULL,
        customerid INTEGER NOT NULL,
        productid INTEGER NOT NULL,
        date DATE NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 0,
        discount NUMERIC(10,2) NOT NULL DEFAULT 0,
        totalprice NUMERIC(14,2) NOT NULL DEFAULT 0,
        transactionnumber VARCHAR(50),
        time VARCHAR(10),
        -- Foreign keys
        CONSTRAINT fk_sales_employee FOREIGN KEY (employeeid) 
            REFERENCES dim_employee(employeeid),
        CONSTRAINT fk_sales_customer FOREIGN KEY (customerid) 
            REFERENCES dim_customer(customerid),
        CONSTRAINT fk_sales_product FOREIGN KEY (productid) 
            REFERENCES dim_product(productid),
        CONSTRAINT fk_sales_date FOREIGN KEY (date) 
            REFERENCES dim_date(date_key),
        -- Constraints
        CONSTRAINT chk_quantity CHECK (quantity >= 0),
        CONSTRAINT chk_totalprice CHECK (totalprice >= 0),
        CONSTRAINT chk_discount CHECK (discount >= 0)
    );

    -- Performance indexes for fact table
    CREATE INDEX idx_fact_sales_date ON fact_sales(date);
    CREATE INDEX idx_fact_sales_employee ON fact_sales(employeeid);
    CREATE INDEX idx_fact_sales_customer ON fact_sales(customerid);
    CREATE INDEX idx_fact_sales_product ON fact_sales(productid);
    CREATE INDEX idx_fact_sales_transaction ON fact_sales(transactionnumber);

    -- Composite indexes for common query patterns
    CREATE INDEX idx_fact_sales_date_product ON fact_sales(date, productid);
    CREATE INDEX idx_fact_sales_date_employee ON fact_sales(date, employeeid);
    CREATE INDEX idx_fact_sales_date_customer ON fact_sales(date, customerid);

    -- ==========================================
    -- 7. MATERIALIZED VIEWS (Performance Optimization)
    -- ==========================================

    -- 7.1 Daily Sales Aggregation
    -- Uses s.quantity * p.price (not s.totalprice) for defense-in-depth:
    -- even if totalprice is somehow zero, the MV stays correct.
    CREATE MATERIALIZED VIEW mv_daily_sales AS
    SELECT 
        s.date,
        d.year,
        d.month,
        d.quarter,
        d.month_name,
        d.day_name,
        d.is_weekend,
        s.productid,
        p.productname,
        p.categoryid,
        p.categoryname,
        p.resistant,
        p.class,
        s.employeeid,
        e.gender,
        s.customerid,
        c.country,
        c.city,
        SUM(s.quantity) AS total_quantity,
        SUM(s.quantity * p.price) AS total_revenue,
        COUNT(DISTINCT s.transactionnumber) AS transaction_count,
        COUNT(DISTINCT s.customerid) AS unique_customers,
        AVG(p.price) AS avg_unit_price,
        SUM(s.discount) AS total_discount
    FROM fact_sales s
    JOIN dim_date d ON s.date = d.date_key
    JOIN dim_product p ON s.productid = p.productid
    JOIN dim_employee e ON s.employeeid = e.employeeid
    JOIN dim_customer c ON s.customerid = c.customerid
    GROUP BY 
        s.date, d.year, d.month, d.quarter, d.month_name, d.day_name, d.is_weekend,
        s.productid, p.productname, p.categoryid, p.categoryname, p.resistant, p.class,
        s.employeeid, e.gender,
        s.customerid, c.country, c.city;

    CREATE INDEX idx_mv_daily_sales_unique 
    ON mv_daily_sales(date, productid, employeeid, customerid);
    CREATE INDEX idx_mv_daily_sales_date ON mv_daily_sales(date);
    CREATE INDEX idx_mv_daily_sales_category ON mv_daily_sales(categoryid);
    CREATE INDEX idx_mv_daily_sales_country ON mv_daily_sales(country);

    -- 7.2 Monthly Aggregation
    -- Uses s.quantity * p.price (not s.totalprice) for defense-in-depth.
    CREATE MATERIALIZED VIEW mv_monthly_sales AS
    SELECT 
        d.year,
        d.month,
        d.month_name,
        d.quarter,
        p.categoryid,
        p.categoryname,
        p.resistant,
        p.class,
        e.gender,
        c.country,
        COUNT(DISTINCT s.transactionnumber) AS transaction_count,
        COUNT(DISTINCT s.customerid) AS unique_customers,
        COUNT(DISTINCT s.employeeid) AS active_employees,
        SUM(s.quantity) AS total_quantity,
        SUM(s.quantity * p.price) AS total_revenue,
        AVG(p.price) AS avg_unit_price,
        SUM(s.discount) AS total_discount,
        SUM(s.quantity * p.price) / NULLIF(COUNT(DISTINCT s.transactionnumber), 0) AS avg_basket_size
    FROM fact_sales s
    JOIN dim_date d ON s.date = d.date_key
    JOIN dim_product p ON s.productid = p.productid
    JOIN dim_employee e ON s.employeeid = e.employeeid
    JOIN dim_customer c ON s.customerid = c.customerid
    GROUP BY 
        d.year, d.month, d.month_name, d.quarter,
        p.categoryid, p.categoryname, p.resistant, p.class,
        e.gender,
        c.country;

    CREATE INDEX idx_mv_monthly_sales_unique 
    ON mv_monthly_sales(year, month, categoryid, gender, country);
    CREATE INDEX idx_mv_monthly_sales_year_month ON mv_monthly_sales(year, month);

    -- 7.3 Customer Segmentation View
    CREATE MATERIALIZED VIEW mv_customer_segmentation AS
    WITH customer_stats AS (
        SELECT 
            customerid,
            COUNT(DISTINCT transactionnumber) AS purchase_frequency,
            SUM(totalprice) AS total_spent,
            COUNT(DISTINCT productid) AS unique_products_bought,
            MIN(date) AS first_purchase_date,
            MAX(date) AS last_purchase_date,
            SUM(quantity) AS total_quantity_bought,
            AVG(totalprice) AS avg_transaction_value
        FROM fact_sales
        GROUP BY customerid
    )
    SELECT 
        cs.customerid,
        c.full_name,
        c.city,
        c.country,
        cs.purchase_frequency,
        cs.total_spent,
        cs.unique_products_bought,
        cs.avg_transaction_value,
        cs.first_purchase_date,
        cs.last_purchase_date,
        CASE 
            WHEN cs.total_spent > 10000 AND cs.purchase_frequency > 20 THEN 'VIP'
            WHEN cs.total_spent > 5000 AND cs.purchase_frequency > 10 THEN 'Regular'
            WHEN cs.purchase_frequency > 0 THEN 'Occasional'
            ELSE 'New'
        END AS customer_segment
    FROM customer_stats cs
    JOIN dim_customer c ON cs.customerid = c.customerid;

    CREATE UNIQUE INDEX idx_mv_customer_segmentation ON mv_customer_segmentation(customerid);
    CREATE INDEX idx_mv_customer_segment ON mv_customer_segmentation(customer_segment);
    CREATE INDEX idx_mv_customer_country ON mv_customer_segmentation(country);

    -- 7.4 Top Products View
    CREATE MATERIALIZED VIEW mv_top_products AS
    SELECT 
        p.productid,
        p.productname,
        p.price,
        p.categoryname,
        p.resistant,
        p.class,
        COUNT(DISTINCT s.transactionnumber) AS times_sold,
        SUM(s.quantity) AS total_quantity_sold,
        SUM(s.quantity * p.price) AS total_revenue,
        COUNT(DISTINCT s.customerid) AS unique_customers,
        AVG(s.quantity) AS avg_quantity_per_sale,
        RANK() OVER (ORDER BY SUM(s.quantity * p.price) DESC) AS revenue_rank,
        RANK() OVER (ORDER BY SUM(s.quantity) DESC) AS volume_rank
    FROM fact_sales s
    JOIN dim_product p ON s.productid = p.productid
    GROUP BY p.productid, p.productname, p.price, p.categoryname, p.resistant, p.class;

    CREATE UNIQUE INDEX idx_mv_top_products ON mv_top_products(productid);
    CREATE INDEX idx_mv_top_products_category ON mv_top_products(categoryname);

    -- 7.5 Employee Performance View
    -- Joins dim_product for revenue computation (quantity*price, not totalprice)
    CREATE MATERIALIZED VIEW mv_employee_performance AS
    SELECT 
        e.employeeid,
        e.full_name,
        e.gender,
        e.city,
        COUNT(DISTINCT s.transactionnumber) AS transactions_handled,
        SUM(s.quantity * p.price) AS total_revenue_generated,
        SUM(s.quantity) AS total_quantity_sold,
        COUNT(DISTINCT s.customerid) AS unique_customers_served,
        SUM(s.quantity * p.price) / NULLIF(COUNT(DISTINCT s.transactionnumber), 0) AS avg_transaction_value,
        RANK() OVER (ORDER BY SUM(s.quantity * p.price) DESC) AS revenue_rank
    FROM fact_sales s
    JOIN dim_employee e ON s.employeeid = e.employeeid
    JOIN dim_product p ON s.productid = p.productid
    GROUP BY e.employeeid, e.full_name, e.gender, e.city;

    CREATE UNIQUE INDEX idx_mv_employee_perf ON mv_employee_performance(employeeid);
    CREATE INDEX idx_mv_employee_perf_city ON mv_employee_performance(city);

    -- ==========================================
    -- 8. FUNCTIONS & STORED PROCEDURES
    -- ==========================================

    -- Refresh all materialized views
    CREATE OR REPLACE FUNCTION refresh_materialized_views()
    RETURNS void AS $$
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_sales;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_segmentation;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_top_products;
        REFRESH MATERIALIZED VIEW CONCURRENTLY mv_employee_performance;
    END;
    $$ LANGUAGE plpgsql;

    -- ==========================================
    -- 9. INDEXES OPTIMIZATION NOTES
    -- ==========================================
    -- 
    -- QUERY PATTERN                    INDEX USED
    -- --------------                   ----------
    -- Sales by date range             idx_fact_sales_date
    -- Sales by product + date         idx_fact_sales_date_product
    -- Sales by employee               idx_fact_sales_employee
    -- Customer purchase history       idx_fact_sales_customer
    -- Category analysis               idx_mv_daily_sales_category
    -- Geographic analysis             idx_mv_daily_sales_country
    -- Time intelligence (YoY, MoM)    idx_mv_monthly_sales_year_month
    -- Customer segments               idx_mv_customer_segment
    -- Employee rankings               idx_mv_employee_perf_age_group
    -- 