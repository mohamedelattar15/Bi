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

    def get_price_distribution(self, start_date=None, end_date=None) -> list[dict]:
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
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += " GROUP BY range_label ORDER BY MIN(price)"
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    def get_price_volume_matrix(self, start_date=None, end_date=None) -> list[dict]:
        """Price vs volume. Uses mv_daily_sales (pre-aggregated)."""
        query = """
            SELECT p.productid, p.productname, p.price,
                   COALESCE(SUM(m.total_quantity), 0) AS total_quantity,
                   COALESCE(SUM(m.total_revenue), 0) AS total_revenue,
                   p.categoryname AS category
            FROM dim_product p
            LEFT JOIN mv_daily_sales m ON p.productid = m.productid
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += """
            GROUP BY p.productid, p.productname, p.price, p.categoryname
            ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query), params)
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

    def get_top_employees(self, limit: int = 5, start_date=None, end_date=None) -> list[dict]:
        query = """
            SELECT e.employeeid, e.full_name, e.gender,
                   COALESCE(SUM(m.total_revenue), 0) AS total_revenue,
                   COALESCE(SUM(m.transaction_count), 0) AS total_transactions
            FROM dim_employee e
            LEFT JOIN mv_daily_sales m ON e.employeeid = m.employeeid
            WHERE 1=1
        """
        params = {"limit": limit}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += """
            GROUP BY e.employeeid, e.full_name, e.gender
            ORDER BY total_revenue DESC
            LIMIT :limit
        """
        result = self.db.execute(text(query), params)
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

    def get_employee_performance_by_age(self, start_date=None, end_date=None) -> list[dict]:
        query = """
            SELECT 
                CASE 
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, e.birthdate)) < 30 THEN 'Young'
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, e.birthdate)) BETWEEN 30 AND 45 THEN 'Middle'
                    ELSE 'Senior'
                END AS group_name,
                COUNT(DISTINCT e.employeeid) AS employee_count,
                COALESCE(SUM(m.total_revenue), 0) AS total_revenue,
                COALESCE(SUM(m.transaction_count), 0) AS total_transactions,
                COALESCE(SUM(m.total_revenue) / NULLIF(COUNT(DISTINCT e.employeeid), 0), 0) AS avg_revenue_per_employee
            FROM dim_employee e
            LEFT JOIN mv_daily_sales m ON e.employeeid = m.employeeid
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += """
            GROUP BY group_name
            ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    def get_employee_performance_by_seniority(self, start_date=None, end_date=None) -> list[dict]:
        query = """
            SELECT 
                CASE 
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, e.hiredate)) < 1 THEN 'New'
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, e.hiredate)) BETWEEN 1 AND 5 THEN 'Confirmed'
                    ELSE 'Senior'
                END AS group_name,
                COUNT(DISTINCT e.employeeid) AS employee_count,
                COALESCE(SUM(m.total_revenue), 0) AS total_revenue,
                COALESCE(SUM(m.transaction_count), 0) AS total_transactions,
                COALESCE(SUM(m.total_revenue) / NULLIF(COUNT(DISTINCT e.employeeid), 0), 0) AS avg_revenue_per_employee
            FROM dim_employee e
            LEFT JOIN mv_daily_sales m ON e.employeeid = m.employeeid
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += """
            GROUP BY group_name
            ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    # ---- BASKET ANALYSIS ----

    def get_basket_rules(self, min_support: float = 0.00001,
                         min_lift: float = 0.5,
                         limit: int = 50,
                         start_date=None, end_date=None) -> list[dict]:
        """
        Market Basket Analysis using mv_daily_baskets (customer+date grouping).
        
        Note: 98% of baskets contain only 1 product → support values are very
        low (0.0001-0.0002%) and lift values are typically < 1.0 (random pairing).
        Thresholds are set to show the most frequent pairs regardless of lift.
        """
        query = """
            WITH product_pairs AS (
                SELECT a.productid AS pid1, b.productid AS pid2,
                       COUNT(DISTINCT a.basket_id) AS both_count
                FROM mv_daily_baskets a
                JOIN mv_daily_baskets b ON a.basket_id = b.basket_id
                    AND a.productid < b.productid
                GROUP BY a.productid, b.productid
            ),
            total_baskets AS (
                SELECT COUNT(DISTINCT basket_id) AS cnt FROM mv_daily_baskets
            ),
            product_counts AS (
                SELECT productid, COUNT(DISTINCT basket_id) AS basket_count
                FROM mv_daily_baskets
                GROUP BY productid
            )
            SELECT p1.productname AS product1, p2.productname AS product2,
                   p1.productname || ' - ' || p2.productname AS basket_label,
                   ROUND(pp.both_count::NUMERIC / tb.cnt, 6) AS support,
                   ROUND(pp.both_count::NUMERIC / NULLIF(pc1.basket_count, 0), 6) AS confidence_p1,
                   ROUND(pp.both_count::NUMERIC / NULLIF(pc2.basket_count, 0), 6) AS confidence_p2,
                   ROUND((pp.both_count::NUMERIC / tb.cnt) / NULLIF((pc1.basket_count::NUMERIC / tb.cnt) * (pc2.basket_count::NUMERIC / tb.cnt), 0), 6) AS lift
            FROM product_pairs pp
            CROSS JOIN total_baskets tb
            JOIN product_counts pc1 ON pp.pid1 = pc1.productid
            JOIN product_counts pc2 ON pp.pid2 = pc2.productid
            JOIN dim_product p1 ON pp.pid1 = p1.productid
            JOIN dim_product p2 ON pp.pid2 = p2.productid
            WHERE (pp.both_count::NUMERIC / tb.cnt) >= :min_support
              AND (pp.both_count::NUMERIC / tb.cnt) / NULLIF((pc1.basket_count::NUMERIC / tb.cnt) * (pc2.basket_count::NUMERIC / tb.cnt), 0) >= :min_lift
            ORDER BY pp.both_count DESC, lift DESC LIMIT :limit
        """
        params = {"min_support": min_support, "min_lift": min_lift, "limit": limit}
        result = self.db.execute(text(query), params)
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
                COALESCE((SELECT COUNT(*) FROM cat_rev), 0) AS category_count,
                COALESCE(ROUND((SELECT MAX(revenue) / NULLIF((SELECT grand_total FROM total), 0) * 100 FROM cat_rev)::numeric, 2), 0) AS top_category_pct,
                COALESCE((SELECT categoryname FROM cat_rev ORDER BY revenue DESC LIMIT 1), '') AS top_category,
                COALESCE(ROUND((SELECT SUM(revenue * revenue) FROM cat_rev) / NULLIF((SELECT grand_total * grand_total FROM total), 0) * 10000::numeric, 2), 0) AS herfindahl_index
        """
        result = self.db.execute(text(query)).first()
        return dict(result._mapping) if result else {
            "category_count": 0,
            "top_category": "",
            "top_category_pct": 0,
            "herfindahl_index": 0,
        }

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

    # ====================================================================
    # PAGE 1: SALES - Additional queries
    # ====================================================================

    def get_sales_by_city(self, start_date=None, end_date=None) -> list[dict]:
        """CA total by city (for Map visual)."""
        query = """
            SELECT c.city,
                   COALESCE(SUM(m.total_revenue), 0) AS revenue,
                   COALESCE(SUM(m.total_quantity), 0) AS quantity,
                   COALESCE(SUM(m.transaction_count), 0) AS transaction_count
            FROM mv_daily_sales m
            JOIN dim_customer c ON m.customerid = c.customerid
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += " GROUP BY c.city ORDER BY revenue DESC"
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    def get_sales_funnel_by_city(self, start_date=None, end_date=None) -> list[dict]:
        """Funnel data: quantity by city."""
        query = """
            SELECT c.city,
                   COALESCE(SUM(m.total_quantity), 0) AS quantity,
                   COALESCE(SUM(m.total_revenue), 0) AS revenue
            FROM mv_daily_sales m
            JOIN dim_customer c ON m.customerid = c.customerid
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += " GROUP BY c.city ORDER BY quantity DESC"
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    def get_ca_growth_by_year(self, start_date=None, end_date=None) -> list[dict]:
        """CA Growth by year (for Area Chart)."""
        query = """
            SELECT d.year,
                   COALESCE(SUM(m.total_revenue), 0) AS revenue,
                   COALESCE(SUM(m.total_quantity), 0) AS quantity,
                   COALESCE(SUM(m.transaction_count), 0) AS transaction_count
            FROM mv_daily_sales m
            JOIN dim_date d ON m.date = d.date_key
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += " GROUP BY d.year ORDER BY d.year"
        result = self.db.execute(text(query), params)
        rows = [dict(row._mapping) for row in result]
        # Calculate growth
        for i, row in enumerate(rows):
            if i > 0 and rows[i-1]['revenue']:
                row['growth'] = round((row['revenue'] - rows[i-1]['revenue']) / rows[i-1]['revenue'] * 100, 2)
            else:
                row['growth'] = None
        return rows

    def get_sales_by_class(self, start_date=None, end_date=None) -> list[dict]:
        """CA total by product class (for Donut chart)."""
        query = """
            SELECT p.class,
                   COALESCE(SUM(m.total_revenue), 0) AS revenue,
                   COALESCE(SUM(m.total_quantity), 0) AS quantity
            FROM mv_daily_sales m
            JOIN dim_product p ON m.productid = p.productid
            WHERE p.class IS NOT NULL AND 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += " GROUP BY p.class ORDER BY revenue DESC"
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    # ====================================================================
    # PAGE 2: PRODUCTS - Additional queries
    # ====================================================================

    def get_products_by_allergen(self) -> list[dict]:
        """Product count by allergen status (for Pie chart)."""
        query = """
            SELECT COALESCE(isallergic, 'Unknown') AS isallergic,
                   COUNT(*) AS product_count
            FROM dim_product
            GROUP BY isallergic
            ORDER BY product_count DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_products_by_resistance(self) -> list[dict]:
        """Product count by resistance level (for Pie chart)."""
        query = """
            SELECT COALESCE(resistant, 'Unknown') AS resistance,
                   COUNT(*) AS product_count
            FROM dim_product
            GROUP BY resistant
            ORDER BY product_count DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_category_growth_rates(self, start_date=None, end_date=None) -> list[dict]:
        """Growth rates (CA, Quantity, Transactions) by category."""
        query = """
            SELECT m.categoryname AS category,
                   COALESCE(SUM(m.total_revenue), 0) AS revenue,
                   COALESCE(SUM(m.total_quantity), 0) AS quantity,
                   COALESCE(SUM(m.transaction_count), 0) AS transactions
            FROM mv_daily_sales m
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += " GROUP BY m.categoryname ORDER BY revenue DESC"
        result = self.db.execute(text(query), params)
        rows = [dict(row._mapping) for row in result]
        # Calculate growth vs total
        total_rev = sum(r['revenue'] for r in rows) or 1
        total_qty = sum(r['quantity'] for r in rows) or 1
        total_txn = sum(r['transactions'] for r in rows) or 1
        for row in rows:
            row['ca_growth_pct'] = round((row['revenue'] / total_rev) * 100, 2)
            row['quant_growth_pct'] = round((row['quantity'] / total_qty) * 100, 2)
            row['transa_growth_pct'] = round((row['transactions'] / total_txn) * 100, 2)
        return rows

    def get_products_quantity_summary(self, start_date=None, end_date=None) -> list[dict]:
        """Quantity sold by product (for Bar chart)."""
        query = """
            SELECT m.productid, m.productname, m.categoryname AS category,
                   COALESCE(SUM(m.total_quantity), 0) AS total_quantity,
                   COALESCE(SUM(m.total_revenue), 0) AS total_revenue
            FROM mv_daily_sales m
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += " GROUP BY m.productid, m.productname, m.categoryname ORDER BY total_quantity DESC"
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    # ====================================================================
    # PAGE 3: CUSTOMERS - Additional queries
    # ====================================================================

    def get_customers_by_transactions(self, limit=10, start_date=None, end_date=None) -> list[dict]:
        """Top customers by transaction count."""
        query = """
            SELECT c.customerid,
                   c.full_name,
                   c.city,
                   c.country,
                   COALESCE(SUM(m.transaction_count), 0) AS total_transactions,
                   COALESCE(SUM(m.total_revenue), 0) AS total_revenue
            FROM mv_daily_sales m
            JOIN dim_customer c ON m.customerid = c.customerid
            WHERE 1=1
        """
        params = {"limit": limit}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += """
            GROUP BY c.customerid, c.full_name, c.city, c.country
            ORDER BY total_transactions DESC
            LIMIT :limit
        """
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    def get_customers_avg_basket_by_city(self, start_date=None, end_date=None) -> list[dict]:
        """Average basket by city (for Map visual)."""
        query = """
            SELECT c.city,
                   COUNT(DISTINCT m.customerid) AS customer_count,
                   COALESCE(SUM(m.total_revenue), 0) AS total_revenue,
                   COALESCE(SUM(m.total_revenue) / NULLIF(SUM(m.transaction_count), 0), 0) AS avg_basket,
                   COALESCE(SUM(m.transaction_count), 0) AS total_transactions
            FROM mv_daily_sales m
            JOIN dim_customer c ON m.customerid = c.customerid
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += " GROUP BY c.city ORDER BY total_revenue DESC"
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    def get_customer_growth_by_city(self, start_date=None, end_date=None) -> list[dict]:
        """Growth metrics by city (for Pivot Table)."""
        query = """
            SELECT c.city,
                   COALESCE(SUM(m.total_revenue), 0) AS revenue,
                   COALESCE(SUM(m.transaction_count), 0) AS transactions,
                   COALESCE(SUM(m.total_quantity), 0) AS quantity,
                   COUNT(DISTINCT m.customerid) AS customer_count
            FROM mv_daily_sales m
            JOIN dim_customer c ON m.customerid = c.customerid
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += " GROUP BY c.city ORDER BY revenue DESC"
        result = self.db.execute(text(query), params)
        rows = [dict(row._mapping) for row in result]
        total_rev = sum(r['revenue'] for r in rows) or 1
        total_txn = sum(r['transactions'] for r in rows) or 1
        total_qty = sum(r['quantity'] for r in rows) or 1
        for row in rows:
            row['ca_growth_pct'] = round((row['revenue'] / total_rev) * 100, 2)
            row['transa_growth_pct'] = round((row['transactions'] / total_txn) * 100, 2)
            row['quant_growth_pct'] = round((row['quantity'] / total_qty) * 100, 2)
        return rows

    def get_customer_loyalty_stats(self, start_date=None, end_date=None) -> dict:
        """Customer loyalty, frequency, and re-purchase rates."""
        query = """
            SELECT 
                COUNT(DISTINCT customerid) AS total_customers,
                COUNT(DISTINCT CASE WHEN transaction_count > 0 THEN customerid END) AS active_customers,
                COALESCE(SUM(total_revenue) / NULLIF(COUNT(DISTINCT customerid), 0), 0) AS ltv
            FROM mv_daily_sales
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="mv_daily_sales")
        result = self.db.execute(text(query), params)
        stats = dict(result.first()._mapping)
        
        # Frequency and re-purchase rate from fact_sales
        freq_query = """
            SELECT 
                COUNT(DISTINCT transactionnumber) / NULLIF(COUNT(DISTINCT customerid), 0) AS avg_frequency,
                COUNT(DISTINCT customerid) FILTER (WHERE customerid IN (
                    SELECT customerid FROM fact_sales GROUP BY customerid HAVING COUNT(DISTINCT transactionnumber) > 1
                ))::NUMERIC / NULLIF(COUNT(DISTINCT customerid), 0) * 100 AS repurchase_rate
            FROM fact_sales
            WHERE 1=1
        """
        freq_params = {}
        freq_query = self._apply_date_filter(freq_query, freq_params, start_date, end_date, table_alias="fact_sales")
        freq_result = self.db.execute(text(freq_query), freq_params).first()
        
        stats['avg_frequency'] = freq_result[0] if freq_result else 0
        stats['repurchase_rate'] = freq_result[1] if freq_result else 0
        return stats

    # ====================================================================
    # PAGE 4: EMPLOYEES - Additional queries
    # ====================================================================

    def get_employee_age_category_distribution(self) -> list[dict]:
        """Employee count by age category (for Donut chart)."""
        query = """
            SELECT 
                CASE 
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, birthdate)) < 30 THEN 'Young'
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, birthdate)) BETWEEN 30 AND 45 THEN 'Middle'
                    ELSE 'Senior'
                END AS age_category,
                COUNT(*) AS employee_count
            FROM dim_employee
            GROUP BY age_category
            ORDER BY employee_count DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_employee_age_tranche_distribution(self) -> list[dict]:
        """Employee count by detailed age tranche (for Pie chart)."""
        query = """
            SELECT 
                CASE 
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, birthdate)) < 25 THEN 'Under 25'
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, birthdate)) BETWEEN 25 AND 34 THEN '25-34'
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, birthdate)) BETWEEN 35 AND 44 THEN '35-44'
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, birthdate)) BETWEEN 45 AND 54 THEN '45-54'
                    ELSE '55+'
                END AS age_tranche,
                COUNT(*) AS employee_count
            FROM dim_employee
            GROUP BY age_tranche
            ORDER BY age_tranche
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_employee_gender_distribution(self) -> list[dict]:
        """Employee count by gender (for Donut chart)."""
        query = """
            SELECT COALESCE(gender, 'Unknown') AS gender,
                   COUNT(*) AS employee_count
            FROM dim_employee
            GROUP BY gender
            ORDER BY employee_count DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_employee_ca_by_age_tranche(self, start_date=None, end_date=None) -> list[dict]:
        """CA total by age tranche (for Bar chart)."""
        query = """
            SELECT 
                CASE 
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, e.birthdate)) < 25 THEN 'Under 25'
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, e.birthdate)) BETWEEN 25 AND 34 THEN '25-34'
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, e.birthdate)) BETWEEN 35 AND 44 THEN '35-44'
                    WHEN EXTRACT(YEAR FROM age(CURRENT_DATE, e.birthdate)) BETWEEN 45 AND 54 THEN '45-54'
                    ELSE '55+'
                END AS age_tranche,
                COUNT(DISTINCT e.employeeid) AS employee_count,
                COALESCE(SUM(m.total_revenue), 0) AS total_revenue
            FROM dim_employee e
            LEFT JOIN mv_daily_sales m ON e.employeeid = m.employeeid
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += " GROUP BY age_tranche ORDER BY age_tranche"
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    def get_employee_performance_table(self, start_date=None, end_date=None) -> list[dict]:
        """Employee performance table with CA total and growth."""
        query = """
            SELECT e.employeeid, e.full_name AS full_name_emp, e.gender,
                   COALESCE(SUM(m.total_revenue), 0) AS total_revenue
            FROM dim_employee e
            LEFT JOIN mv_daily_sales m ON e.employeeid = m.employeeid
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += " GROUP BY e.employeeid, e.full_name, e.gender ORDER BY total_revenue DESC"
        result = self.db.execute(text(query), params)
        rows = [dict(row._mapping) for row in result]
        # Calculate growth vs average
        avg_rev = sum(r['total_revenue'] for r in rows) / len(rows) if rows else 1
        for row in rows:
            row['ca_growth'] = round((row['total_revenue'] - avg_rev) / avg_rev * 100, 2) if avg_rev else 0
        return rows

    # ====================================================================
    # PAGE 5: BASKET - Additional queries
    # ====================================================================

    def get_basket_total_products(self) -> int:
        """Total distinct products available for basket analysis."""
        return self.db.execute(
            text("SELECT COUNT(DISTINCT productname) FROM dim_product")
        ).scalar() or 0

    def get_basket_total_baskets(self, start_date=None, end_date=None) -> int:
        """Total distinct baskets (customer+date) for basket analysis.
        
        Note: mv_daily_baskets has no date column (uses basket_id = CONCAT(customerid,'|',date)).
        Date filtering is handled at the basket_rules query level instead.
        """
        return self.db.execute(
            text("SELECT COUNT(DISTINCT basket_id) FROM mv_daily_baskets")
        ).scalar() or 0

    # ====================================================================
    # ADVANCED CHARTS - New repository methods
    # ====================================================================

    def get_monthly_revenue_by_category(self, start_date=None, end_date=None) -> list[dict]:
        """Monthly revenue broken down by category (for Stacked Bar / Heatmap)."""
        query = """
            SELECT d.year, d.month, d.month_name,
                   m.categoryname AS category,
                   COALESCE(SUM(m.total_revenue), 0) AS revenue,
                   COALESCE(SUM(m.total_quantity), 0) AS quantity,
                   COALESCE(SUM(m.transaction_count), 0) AS transaction_count
            FROM mv_daily_sales m
            JOIN dim_date d ON m.date = d.date_key
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += """
            GROUP BY d.year, d.month, d.month_name, m.categoryname
            ORDER BY d.year, d.month, m.categoryname
        """
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    def get_profit_summary(self, start_date=None, end_date=None) -> dict:
        """Profit = SUM(qty × price) - discount. Returns profit metrics."""
        query = """
            SELECT 
                COALESCE(SUM(s.quantity * p.price), 0) AS gross_revenue,
                COALESCE(SUM(s.discount), 0) AS total_discounts,
                COUNT(DISTINCT s.transactionnumber) AS total_orders,
                COALESCE(SUM(s.quantity * p.price) - COALESCE(SUM(s.discount), 0), 0) AS net_profit,
                AVG(s.quantity * p.price - COALESCE(s.discount, 0)) AS avg_profit_per_transaction
            FROM fact_sales s
            JOIN dim_product p ON s.productid = p.productid
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="s")
        result = self.db.execute(text(query), params)
        return dict(result.first()._mapping)

    def get_category_waterfall(self, start_date=None, end_date=None) -> list[dict]:
        """Category contribution in waterfall format (largest → smallest)."""
        query = """
            SELECT categoryname AS category,
                   COALESCE(SUM(total_revenue), 0) AS revenue,
                   COALESCE(SUM(total_quantity), 0) AS quantity,
                   COALESCE(SUM(transaction_count), 0) AS transaction_count
            FROM mv_daily_sales
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="mv_daily_sales")
        query += " GROUP BY categoryname ORDER BY revenue DESC"
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    def get_top_product_pareto(self, limit=20, start_date=None, end_date=None) -> list[dict]:
        """Product revenue with cumulative percentage (for Pareto chart)."""
        query = """
            SELECT m.productid, m.productname, m.categoryname AS category,
                   COALESCE(SUM(m.total_revenue), 0) AS revenue,
                   COALESCE(SUM(m.total_quantity), 0) AS quantity_sold
            FROM mv_daily_sales m
            WHERE 1=1
        """
        params = {"limit": limit}
        query = self._apply_date_filter(query, params, start_date, end_date, table_alias="m")
        query += """
            GROUP BY m.productid, m.productname, m.categoryname
            ORDER BY revenue DESC
            LIMIT :limit
        """
        result = self.db.execute(text(query), params)
        rows = [dict(row._mapping) for row in result]
        total = sum(r['revenue'] for r in rows) or 1
        cumulative = 0
        for row in rows:
            cumulative += row['revenue']
            row['cumulative_pct'] = round(cumulative / total * 100, 2)
            row['pct_of_total'] = round(row['revenue'] / total * 100, 2)
        return rows

    def get_growth_metrics(self, start_date=None, end_date=None) -> dict:
        """Growth % and profit margin."""
        profit = self.get_profit_summary(start_date, end_date)
        kpis = self.get_all_kpis(start_date, end_date)
        return {
            "total_revenue": kpis["total_revenue"],
            "total_profit": profit["net_profit"],
            "total_orders": profit["total_orders"],
            "total_discounts": profit["total_discounts"],
            "profit_margin_pct": round(
                (profit["net_profit"] / kpis["total_revenue"] * 100) if kpis["total_revenue"] else 0, 2
            ),
            "avg_profit_per_order": round(
                (profit["net_profit"] / profit["total_orders"]) if profit["total_orders"] else 0, 2
            ),
        }
