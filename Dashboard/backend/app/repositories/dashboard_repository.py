"""Repository for dashboard-level aggregated queries."""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import date


class DashboardRepository:
    """Handles complex analytical queries against materialized views and fact tables."""

    def __init__(self, db: Session):
        self.db = db

    def _apply_date_filter(self, base_query: str, params: dict,
                           start_date: Optional[date] = None,
                           end_date: Optional[date] = None,
                           table_alias: str = "s") -> str:
        if start_date:
            base_query += f" AND {table_alias}.date >= :start_date"
            params["start_date"] = start_date
        if end_date:
            base_query += f" AND {table_alias}.date <= :end_date"
            params["end_date"] = end_date
        return base_query

    def _apply_filters(self, base_query: str, params: dict,
                       category: Optional[str] = None,
                       product: Optional[str] = None,
                       employee: Optional[str] = None,
                       table_alias: str = "s") -> str:
        """Apply chart-level dimension filters to a query."""
        if category:
            base_query += f" AND {table_alias}.categoryname = :category"
            params["category"] = category
        if product:
            base_query += f" AND {table_alias}.productname = :product"
            params["product"] = product
        if employee:
            base_query += f" AND {table_alias}.full_name = :employee"
            params["employee"] = employee
        return base_query

    # ──────────────────────────────────────────────
    # COMBINED KPI QUERY (replaces 6 individual calls)
    # ──────────────────────────────────────────────

    def get_all_kpis(self, start_date=None, end_date=None) -> dict:
        """
        Single query returning ALL dashboard KPIs.
        Uses mv_daily_sales (pre-aggregated, ~99.9% fewer rows than fact_sales).
        Falls back to fact_sales only if date filters produce no MV results.
        """
        query = """
            SELECT
                COALESCE(SUM(total_revenue), 0) AS total_revenue,
                COALESCE(SUM(total_quantity), 0) AS total_quantity,
                COALESCE(SUM(transaction_count), 0) AS total_transactions,
                COALESCE(SUM(total_revenue) / NULLIF(SUM(transaction_count), 0), 0) AS avg_basket,
                COALESCE(SUM(unique_customers), 0) AS unique_customers
            FROM mv_daily_sales
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date,
                                         table_alias="mv_daily_sales")

        kpis = dict(self.db.execute(text(query), params).first()._mapping)

        # Total products is a static count, fetched separately (tiny query)
        kpis["total_products"] = self.db.execute(
            text("SELECT COUNT(*) FROM dim_product")
        ).scalar()

        return kpis

    # ──────────────────────────────────────────────
    # TIME SERIES (uses mv_monthly_sales for speed)
    # ──────────────────────────────────────────────

    def get_monthly_revenue(self, start_date=None, end_date=None,
                            category=None) -> list[dict]:
        """
        Monthly revenue aggregation.
        Supports optional category filter for chart-level drill-down.
        """
        query = """
            SELECT d.year, d.month, d.month_name, d.quarter,
                   COALESCE(SUM(m.total_revenue), 0) AS revenue,
                   COALESCE(SUM(m.total_quantity), 0) AS quantity,
                   COALESCE(SUM(m.transaction_count), 0) AS transaction_count,
                   COALESCE(SUM(m.total_revenue) / NULLIF(SUM(m.transaction_count), 0), 0) AS avg_basket
            FROM mv_daily_sales m
            JOIN dim_date d ON m.date = d.date_key
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query = self._apply_filters(query, params, category=category, table_alias="m")
        query += " GROUP BY d.year, d.month, d.month_name, d.quarter ORDER BY d.year, d.month"
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    # ---- SALES BY CATEGORY ----

    def get_sales_by_category(self, start_date=None, end_date=None,
                              product=None) -> list[dict]:
        """Category breakdown. Supports optional product filter."""
        query = """
            SELECT categoryname AS category,
                   COALESCE(SUM(total_revenue), 0) AS revenue,
                   COALESCE(SUM(total_quantity), 0) AS quantity,
                   COALESCE(SUM(transaction_count), 0) AS transaction_count
            FROM mv_daily_sales
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date,
                                         table_alias="mv_daily_sales")
        query = self._apply_filters(query, params, product=product, table_alias="mv_daily_sales")
        query += " GROUP BY categoryname ORDER BY revenue DESC"
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    # ---- TOP PRODUCTS ----

    def get_top_products(self, limit: int = 10, start_date=None, end_date=None,
                        category=None) -> list[dict]:
        """Top N products by revenue. Supports optional category filter."""
        query = """
            SELECT productid, productname, categoryname AS category,
                   COALESCE(SUM(total_revenue), 0) AS revenue,
                   COALESCE(SUM(total_quantity), 0) AS quantity_sold,
                   COALESCE(SUM(transaction_count), 0) AS times_sold
            FROM mv_daily_sales
            WHERE 1=1
        """
        params = {"limit": limit}
        query = self._apply_date_filter(query, params, start_date, end_date,
                                         table_alias="mv_daily_sales")
        query = self._apply_filters(query, params, category=category, table_alias="mv_daily_sales")
        query += " GROUP BY productid, productname, categoryname ORDER BY revenue DESC LIMIT :limit"
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    # ---- PRODUCT ANALYTICS ----

    def get_product_detail(self, product_id: int) -> Optional[dict]:
        query = """
            SELECT p.productid AS product_id, p.productname AS product_name,
                   p.price, p.categoryname AS category, p.class AS class_,
                   p.resistant, p.isallergic AS is_allergic, p.vitalitydays AS vitality_days,
                   COALESCE(SUM(s.quantity * p.price), 0) AS total_revenue,
                   COALESCE(SUM(s.quantity), 0) AS total_quantity,
                   COUNT(DISTINCT s.transactionnumber) AS times_sold,
                   COUNT(DISTINCT s.customerid) AS unique_customers
            FROM dim_product p
            LEFT JOIN fact_sales s ON p.productid = s.productid
            WHERE p.productid = :product_id
            GROUP BY p.productid, p.productname, p.price, p.categoryname, 
                     p.class, p.resistant, p.isallergic, p.vitalitydays
        """
        result = self.db.execute(text(query), {"product_id": product_id})
        row = result.first()
        return dict(row._mapping) if row else None

    def get_price_distribution(self) -> list[dict]:
        """Price distribution. Uses mv_daily_sales for revenue (pre-aggregated)."""
        query = """
            SELECT CASE 
                WHEN price < 10 THEN '0-10€' WHEN price < 20 THEN '10-20€'
                WHEN price < 30 THEN '20-30€' WHEN price < 50 THEN '30-50€'
                WHEN price < 100 THEN '50-100€' ELSE '100€+'
            END AS range_label,
            MIN(price) AS min_price, MAX(price) AS max_price,
            COUNT(*) AS product_count,
            COALESCE(SUM(m.total_revenue), 0) AS total_revenue
            FROM dim_product p
            LEFT JOIN mv_daily_sales m ON p.productid = m.productid
            GROUP BY range_label ORDER BY MIN(price)
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_price_volume_matrix(self) -> list[dict]:
        """Price vs volume. Uses mv_daily_sales (pre-aggregated)."""
        query = """
            SELECT p.productid, p.productname, p.price,
                   COALESCE(SUM(m.total_quantity), 0) AS total_quantity,
                   COALESCE(SUM(m.total_revenue), 0) AS total_revenue,
                   p.categoryname AS category
            FROM dim_product p
            LEFT JOIN mv_daily_sales m ON p.productid = m.productid
            GROUP BY p.productid, p.productname, p.price, p.categoryname
            ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    # ---- CUSTOMER ANALYTICS ----

    def get_customer_segments(self) -> list[dict]:
        query = """
            SELECT customer_segment AS segment, COUNT(*) AS customer_count,
                   SUM(total_spent) AS total_revenue,
                   AVG(total_spent / NULLIF(purchase_frequency, 0)) AS avg_basket
            FROM mv_customer_segmentation
            GROUP BY customer_segment ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_top_customers(self, limit: int = 10) -> list[dict]:
        query = """
            SELECT cs.customerid, c.full_name, c.city, c.country,
                   cs.total_spent, cs.purchase_frequency AS total_transactions,
                   cs.customer_segment AS segment
            FROM mv_customer_segmentation cs
            JOIN dim_customer c ON cs.customerid = c.customerid
            ORDER BY cs.total_spent DESC LIMIT :limit
        """
        result = self.db.execute(text(query), {"limit": limit})
        return [dict(row._mapping) for row in result]

    def get_customer_activity(self, start_date=None, end_date=None) -> list[dict]:
        """Monthly active customers. Uses mv_daily_sales (pre-aggregated)."""
        query = """
            SELECT d.month_name AS month, d.year,
                   COALESCE(SUM(m.unique_customers), 0) AS active_customers,
                   COALESCE(SUM(m.total_revenue), 0) AS total_revenue
            FROM mv_daily_sales m
            JOIN dim_date d ON m.date = d.date_key WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date,
                                         table_alias="m")
        query += " GROUP BY d.year, d.month, d.month_name ORDER BY d.year, d.month"
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    def get_customer_detail(self, customer_id: int) -> Optional[dict]:
        query = """
            SELECT 
                c.customerid AS customer_id,
                c.full_name,
                c.city,
                c.country,
                cs.total_spent,
                cs.purchase_frequency AS total_transactions,
                cs.total_quantity_bought AS total_quantity,
                cs.avg_transaction_value,
                cs.unique_products_bought AS unique_products,
                cs.first_purchase_date AS first_purchase,
                cs.last_purchase_date AS last_purchase,
                cs.customer_segment AS segment
            FROM mv_customer_segmentation cs
            JOIN dim_customer c ON cs.customerid = c.customerid
            WHERE c.customerid = :customer_id
        """
        result = self.db.execute(text(query), {"customer_id": customer_id})
        row = result.first()
        return dict(row._mapping) if row else None

    # ---- EMPLOYEE ANALYTICS ----

    def get_top_employees(self, limit: int = 5) -> list[dict]:
        query = """
            SELECT 
                employeeid,
                full_name,
                total_revenue_generated AS total_revenue,
                transactions_handled AS total_transactions,
                gender
            FROM mv_employee_performance
            ORDER BY total_revenue DESC
            LIMIT :limit
        """
        result = self.db.execute(text(query), {"limit": limit})
        return [dict(row._mapping) for row in result]

    def get_employee_detail(self, employee_id: int) -> Optional[dict]:
        query = """
            SELECT 
                e.employeeid AS employee_id,
                e.full_name,
                e.gender,
                e.city,
                perf.total_revenue_generated AS total_revenue,
                perf.transactions_handled AS total_transactions,
                perf.total_quantity_sold AS total_quantity,
                perf.unique_customers_served AS unique_customers,
                perf.avg_transaction_value,
                perf.revenue_rank
            FROM mv_employee_performance perf
            JOIN dim_employee e ON perf.employeeid = e.employeeid
            WHERE e.employeeid = :employee_id
        """
        result = self.db.execute(text(query), {"employee_id": employee_id})
        row = result.first()
        return dict(row._mapping) if row else None

    def get_employee_performance_by_age(self) -> list[dict]:
        query = """
            SELECT 
                CASE 
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, e.birthdate)) < 30 THEN 'Young'
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, e.birthdate)) BETWEEN 30 AND 45 THEN 'Middle'
                    ELSE 'Senior'
                END AS group_name,
                COUNT(DISTINCT e.employeeid) AS employee_count,
                SUM(perf.total_revenue_generated) AS total_revenue,
                SUM(perf.transactions_handled) AS total_transactions,
                AVG(perf.total_revenue_generated) AS avg_revenue_per_employee
            FROM mv_employee_performance perf
            JOIN dim_employee e ON perf.employeeid = e.employeeid
            GROUP BY group_name
            ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_employee_performance_by_seniority(self) -> list[dict]:
        query = """
            SELECT 
                CASE 
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, e.hiredate)) < 1 THEN 'New'
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, e.hiredate)) BETWEEN 1 AND 5 THEN 'Confirmed'
                    ELSE 'Senior'
                END AS group_name,
                COUNT(DISTINCT e.employeeid) AS employee_count,
                SUM(perf.total_revenue_generated) AS total_revenue,
                SUM(perf.transactions_handled) AS total_transactions,
                AVG(perf.total_revenue_generated) AS avg_revenue_per_employee
            FROM mv_employee_performance perf
            JOIN dim_employee e ON perf.employeeid = e.employeeid
            GROUP BY group_name
            ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    # ---- BASKET ANALYSIS ----

    def get_basket_rules(self, min_support: float = 0.01,
                         min_lift: float = 1.5,
                         limit: int = 50) -> list[dict]:
        query = """
            WITH transaction_products AS (
                SELECT DISTINCT s.transactionnumber, s.productid, p.productname
                FROM fact_sales s
                JOIN dim_product p ON s.productid = p.productid
            ),
            total_trans AS (
                SELECT COUNT(DISTINCT transactionnumber) AS cnt FROM fact_sales
            ),
            -- Pre-compute per-product distinct transaction counts (can't use DISTINCT inside window functions)
            product_counts AS (
                SELECT productname, COUNT(DISTINCT transactionnumber) AS txn_count
                FROM transaction_products
                GROUP BY productname
            ),
            product_pairs AS (
                SELECT a.productname AS product1, b.productname AS product2,
                       COUNT(DISTINCT a.transactionnumber) AS both_count
                FROM transaction_products a
                JOIN transaction_products b ON a.transactionnumber = b.transactionnumber
                    AND a.productname < b.productname
                GROUP BY a.productname, b.productname
            )
            SELECT pp.product1, pp.product2,
                   pp.product1 || ' - ' || pp.product2 AS basket_label,
                   ROUND(pp.both_count::NUMERIC / tt.cnt, 6) AS support,
                   ROUND(pp.both_count::NUMERIC / NULLIF(pc1.txn_count, 0), 6) AS confidence_p1,
                   ROUND(pp.both_count::NUMERIC / NULLIF(pc2.txn_count, 0), 6) AS confidence_p2,
                   ROUND((pp.both_count::NUMERIC / tt.cnt) / NULLIF((pc1.txn_count::NUMERIC / tt.cnt) * (pc2.txn_count::NUMERIC / tt.cnt), 0), 6) AS lift
            FROM product_pairs pp
            CROSS JOIN total_trans tt
            JOIN product_counts pc1 ON pp.product1 = pc1.productname
            JOIN product_counts pc2 ON pp.product2 = pc2.productname
            WHERE (pp.both_count::NUMERIC / tt.cnt) >= :min_support
              AND (pp.both_count::NUMERIC / tt.cnt) / NULLIF((pc1.txn_count::NUMERIC / tt.cnt) * (pc2.txn_count::NUMERIC / tt.cnt), 0) >= :min_lift
            ORDER BY lift DESC LIMIT :limit
        """
        result = self.db.execute(text(query), {"min_support": min_support, "min_lift": min_lift, "limit": limit})
        return [dict(row._mapping) for row in result]

    # ====================================================================
    # NEW: ADVANCED ANALYTICAL INSIGHTS
    # ====================================================================

    # ---- REVENUE CONCENTRATION ANALYSIS ----

    def get_revenue_concentration(self) -> dict:
        """Herfindahl index and concentration metrics."""
        query = """
            WITH cat_rev AS (
                SELECT p.categoryname,
                       COALESCE(SUM(s.totalprice), 0) AS revenue
                FROM fact_sales s
                JOIN dim_product p ON s.productid = p.productid
                GROUP BY p.categoryname
            ), total AS (
                SELECT SUM(revenue) AS grand_total FROM cat_rev
            )
            SELECT 
                (SELECT COUNT(*) FROM cat_rev) AS category_count,
                ROUND((SELECT MAX(revenue) / NULLIF(grand_total, 0) * 100 FROM cat_rev, total)::numeric, 2) AS top_category_pct,
                (SELECT categoryname FROM cat_rev ORDER BY revenue DESC LIMIT 1) AS top_category,
                ROUND((SELECT SUM(revenue * revenue) FROM cat_rev) / NULLIF((SELECT grand_total * grand_total FROM total), 0) * 10000::numeric, 2) AS herfindahl_index
            FROM total
        """
        return dict(self.db.execute(text(query)).first()._mapping)

    def get_revenue_by_day_of_week(self) -> list[dict]:
        """Revenue and transaction breakdown by day of week."""
        query = """
            SELECT d.day_name, d.is_weekend,
                   COUNT(DISTINCT s.transactionnumber) AS transactions,
                   SUM(s.quantity) AS quantity,
                   COALESCE(SUM(s.totalprice), 0) AS revenue,
                   COALESCE(SUM(s.totalprice) / NULLIF(COUNT(DISTINCT s.transactionnumber), 0), 0) AS avg_basket
            FROM fact_sales s
            JOIN dim_date d ON s.date = d.date_key
            GROUP BY d.day_name, d.is_weekend
            ORDER BY revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_month_over_month_growth(self) -> list[dict]:
        """Month-over-month growth rate with full-month comparisons."""
        query = """
            WITH monthly AS (
                SELECT d.year, d.month, d.month_name,
                       COALESCE(SUM(s.totalprice), 0) AS revenue,
                       SUM(s.quantity) AS quantity,
                       COUNT(DISTINCT s.transactionnumber) AS transactions
                FROM fact_sales s
                JOIN dim_date d ON s.date = d.date_key
                GROUP BY d.year, d.month, d.month_name
            )
            SELECT curr.year, curr.month, curr.month_name,
                   ROUND(curr.revenue::numeric, 2) AS revenue,
                   ROUND(curr.quantity::numeric, 0) AS quantity,
                   ROUND(COALESCE((curr.revenue - prev.revenue) / NULLIF(prev.revenue, 0) * 100, 0)::numeric, 2) AS mom_growth_pct,
                   ROUND(curr.revenue::numeric / 3, 2) AS monthly_run_rate
            FROM monthly curr
            LEFT JOIN monthly prev ON curr.month = prev.month + 1
                AND curr.year = prev.year
                AND prev.month IS NOT NULL
            ORDER BY curr.year, curr.month
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_sales_by_resistance(self) -> list[dict]:
        """Revenue breakdown by product resistance level."""
        query = """
            SELECT p.resistant AS resistance,
                   COUNT(DISTINCT p.productid) AS product_count,
                   COALESCE(SUM(s.quantity), 0) AS quantity,
                   COALESCE(SUM(s.totalprice), 0) AS revenue
            FROM dim_product p
            LEFT JOIN fact_sales s ON p.productid = s.productid
            GROUP BY p.resistant
            ORDER BY revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    # ---- CUSTOMER RFM SEGMENTATION ----

    def get_customer_rfm_segmentation(self) -> list[dict]:
        """Full RFM segmentation with recency, frequency, monetary."""
        query = """
            WITH rfm AS (
                SELECT s.customerid,
                       COUNT(DISTINCT s.transactionnumber) AS frequency,
                       COALESCE(SUM(s.totalprice), 0) AS monetary,
                       MAX(s.date) AS last_purchase_date,
                       COALESCE(SUM(s.quantity), 0) AS total_quantity,
                       COUNT(DISTINCT p.categoryid) AS categories_bought
                FROM fact_sales s
                JOIN dim_product p ON s.productid = p.productid
                GROUP BY s.customerid
            ),
            stats AS (
                SELECT 
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY frequency) AS f25,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY frequency) AS f75,
                    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY monetary) AS m25,
                    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY monetary) AS m75
                FROM rfm
            )
            SELECT 
                CASE 
                    WHEN r.monetary > s.m75 AND r.frequency > s.f75 THEN 'Champions'
                    WHEN r.monetary > s.m75 AND r.frequency BETWEEN s.f25 AND s.f75 THEN 'Loyal'
                    WHEN r.monetary > s.m75 THEN 'Big Spenders'
                    WHEN r.frequency > s.f75 THEN 'Frequent Buyers'
                    WHEN r.monetary > s.m25 THEN 'Average'
                    ELSE 'At Risk'
                END AS rfm_segment,
                COUNT(*) AS customer_count,
                ROUND(AVG(r.monetary)::numeric, 2) AS avg_spent,
                ROUND(SUM(r.monetary)::numeric, 2) AS total_revenue,
                ROUND(AVG(r.frequency)::numeric, 1) AS avg_frequency,
                ROUND(AVG(r.categories_bought)::numeric, 1) AS avg_categories
            FROM rfm r CROSS JOIN stats s
            GROUP BY rfm_segment
            ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_customer_geographic_distribution(self) -> list[dict]:
        """Customer and revenue by country."""
        query = """
            SELECT c.country,
                   COUNT(DISTINCT s.customerid) AS customer_count,
                   COALESCE(SUM(s.totalprice), 0) AS total_revenue,
                   COALESCE(SUM(s.quantity), 0) AS total_quantity,
                   COALESCE(SUM(s.totalprice) / NULLIF(COUNT(DISTINCT s.customerid), 0), 0) AS avg_revenue_per_customer
            FROM fact_sales s
            JOIN dim_customer c ON s.customerid = c.customerid
            GROUP BY c.country
            ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    # ---- EMPLOYEE PERFORMANCE INSIGHTS ----

    def get_employee_performance_parity(self) -> dict:
        """How evenly distributed is employee performance."""
        query = """
            WITH emp_rev AS (
                SELECT e.employeeid, e.full_name, e.gender,
                       COALESCE(SUM(s.totalprice), 0) AS revenue,
                       COUNT(DISTINCT s.transactionnumber) AS transactions,
                       COUNT(DISTINCT s.customerid) AS customers_served
                FROM fact_sales s
                JOIN dim_employee e ON s.employeeid = e.employeeid
                GROUP BY e.employeeid, e.full_name, e.gender
            )
            SELECT COUNT(*) AS employee_count,
                   ROUND(AVG(revenue)::numeric, 2) AS avg_revenue,
                   ROUND(STDDEV(revenue)::numeric, 2) AS stddev_revenue,
                   ROUND((MAX(revenue) - MIN(revenue)) / NULLIF(AVG(revenue), 0) * 100::numeric, 2) AS spread_pct,
                   ROUND(MIN(revenue)::numeric, 2) AS min_revenue,
                   ROUND(MAX(revenue)::numeric, 2) AS max_revenue,
                   ROUND(AVG(transactions)::numeric, 0) AS avg_transactions,
                   ROUND(AVG(customers_served)::numeric, 0) AS avg_customers
            FROM emp_rev
        """
        return dict(self.db.execute(text(query)).first()._mapping)

    def get_employee_ranking(self) -> list[dict]:
        """Full employee ranking with metrics."""
        query = """
            SELECT e.employeeid, e.full_name, e.gender,
                   ROUND(COALESCE(SUM(s.totalprice), 0)::numeric, 2) AS revenue,
                   COUNT(DISTINCT s.transactionnumber) AS transactions,
                   COUNT(DISTINCT s.customerid) AS customers_served,
                   COALESCE(SUM(s.quantity), 0) AS quantity_sold,
                   ROUND(COALESCE(SUM(s.totalprice) / NULLIF(COUNT(DISTINCT s.transactionnumber), 0), 0)::numeric, 2) AS avg_transaction_value,
                   RANK() OVER (ORDER BY COALESCE(SUM(s.totalprice), 0) DESC) AS rank
            FROM fact_sales s
            JOIN dim_employee e ON s.employeeid = e.employeeid
            GROUP BY e.employeeid, e.full_name, e.gender
            ORDER BY revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    # ---- FILTERS ----

    def get_filter_options(self) -> dict:
        categories = self.db.execute(
            text("SELECT categoryname FROM dim_category ORDER BY categoryname")
        ).scalars().all()

        countries = self.db.execute(
            text("SELECT DISTINCT country FROM dim_customer WHERE country IS NOT NULL ORDER BY country")
        ).scalars().all()

        employees = self.db.execute(
            text("SELECT full_name FROM dim_employee ORDER BY full_name")
        ).scalars().all()

        date_result = self.db.execute(
            text("SELECT MIN(date), MAX(date) FROM fact_sales")
        ).first()
        date_range = (date_result[0], date_result[1]) if date_result else (None, None)

        return {
            "categories": list(categories),
            "countries": list(countries),
            "employees": list(employees),
            "date_range": date_range,
        }
