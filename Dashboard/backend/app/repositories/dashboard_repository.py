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
                           end_date: Optional[date] = None) -> str:
        """Append date filter to query if dates provided."""
        if start_date:
            base_query += " AND s.date >= :start_date"
            params["start_date"] = start_date
        if end_date:
            base_query += " AND s.date <= :end_date"
            params["end_date"] = end_date
        return base_query

    # ---- KPI QUERIES ----

    def get_total_revenue(self, start_date: Optional[date] = None,
                          end_date: Optional[date] = None) -> float:
        query = "SELECT COALESCE(SUM(totalprice), 0) FROM fact_sales s WHERE 1=1"
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date)
        return self.db.execute(text(query), params).scalar()

    def get_total_quantity(self, start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> int:
        query = "SELECT COALESCE(SUM(quantity), 0) FROM fact_sales s WHERE 1=1"
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date)
        return self.db.execute(text(query), params).scalar()

    def get_total_transactions(self, start_date: Optional[date] = None,
                                end_date: Optional[date] = None) -> int:
        query = """SELECT COUNT(DISTINCT transactionnumber) FROM fact_sales s WHERE 1=1"""
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date)
        return self.db.execute(text(query), params).scalar()

    def get_avg_basket(self, start_date: Optional[date] = None,
                       end_date: Optional[date] = None) -> float:
        query = """
            SELECT COALESCE(SUM(totalprice) / NULLIF(COUNT(DISTINCT transactionnumber), 0), 0)
            FROM fact_sales s WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date)
        return self.db.execute(text(query), params).scalar()

    def get_unique_customers(self, start_date: Optional[date] = None,
                              end_date: Optional[date] = None) -> int:
        query = "SELECT COUNT(DISTINCT customerid) FROM fact_sales s WHERE 1=1"
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date)
        return self.db.execute(text(query), params).scalar()

    def get_total_products(self) -> int:
        return self.db.execute(text("SELECT COUNT(*) FROM dim_product")).scalar()

    # ---- TIME SERIES ----

    def get_monthly_revenue(self, start_date: Optional[date] = None,
                            end_date: Optional[date] = None) -> list[dict]:
        query = """
            SELECT 
                d.year,
                d.month,
                d.month_name,
                d.quarter,
                SUM(s.totalprice) AS revenue,
                SUM(s.quantity) AS quantity,
                COUNT(DISTINCT s.transactionnumber) AS transaction_count,
                SUM(s.totalprice) / NULLIF(COUNT(DISTINCT s.transactionnumber), 0) AS avg_basket
            FROM fact_sales s
            JOIN dim_date d ON s.date = d.date_key
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date)
        query += """
            GROUP BY d.year, d.month, d.month_name, d.quarter
            ORDER BY d.year, d.month
        """
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    # ---- SALES BY CATEGORY ----

    def get_sales_by_category(self, start_date: Optional[date] = None,
                               end_date: Optional[date] = None) -> list[dict]:
        query = """
            SELECT 
                p.categoryname AS category,
                SUM(s.totalprice) AS revenue,
                SUM(s.quantity) AS quantity,
                COUNT(DISTINCT s.transactionnumber) AS transaction_count
            FROM fact_sales s
            JOIN dim_product p ON s.productid = p.productid
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date)
        query += """
            GROUP BY p.categoryname
            ORDER BY revenue DESC
        """
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    # ---- TOP PRODUCTS ----

    def get_top_products(self, limit: int = 10,
                         start_date: Optional[date] = None,
                         end_date: Optional[date] = None) -> list[dict]:
        query = """
            SELECT 
                p.productid,
                p.productname,
                p.categoryname AS category,
                SUM(s.totalprice) AS revenue,
                SUM(s.quantity) AS quantity_sold,
                COUNT(DISTINCT s.transactionnumber) AS times_sold
            FROM fact_sales s
            JOIN dim_product p ON s.productid = p.productid
            WHERE 1=1
        """
        params = {"limit": limit}
        query = self._apply_date_filter(query, params, start_date, end_date)
        query += """
            GROUP BY p.productid, p.productname, p.categoryname
            ORDER BY revenue DESC
            LIMIT :limit
        """
        result = self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result]

    # ---- PRODUCT ANALYTICS ----

    def get_product_detail(self, product_id: int) -> Optional[dict]:
        query = """
            SELECT 
                p.productid AS product_id,
                p.productname AS product_name,
                p.price,
                p.categoryname AS category,
                p.class AS class_,
                p.resistant,
                p.isallergic AS is_allergic,
                p.vitalitydays AS vitality_days,
                COALESCE(SUM(s.totalprice), 0) AS total_revenue,
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
        query = """
            SELECT 
                CASE 
                    WHEN price < 10 THEN '0-10€'
                    WHEN price < 20 THEN '10-20€'
                    WHEN price < 30 THEN '20-30€'
                    WHEN price < 50 THEN '30-50€'
                    WHEN price < 100 THEN '50-100€'
                    ELSE '100€+'
                END AS range_label,
                MIN(price) AS min_price,
                MAX(price) AS max_price,
                COUNT(*) AS product_count,
                COALESCE(SUM(s.totalprice), 0) AS total_revenue
            FROM dim_product p
            LEFT JOIN fact_sales s ON p.productid = s.productid
            GROUP BY range_label
            ORDER BY MIN(price)
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_price_volume_matrix(self) -> list[dict]:
        query = """
            SELECT 
                p.productid,
                p.productname,
                p.price,
                COALESCE(SUM(s.quantity), 0) AS total_quantity,
                COALESCE(SUM(s.totalprice), 0) AS total_revenue,
                p.categoryname AS category
            FROM dim_product p
            LEFT JOIN fact_sales s ON p.productid = s.productid
            GROUP BY p.productid, p.productname, p.price, p.categoryname
            ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    # ---- CUSTOMER ANALYTICS ----

    def get_customer_segments(self) -> list[dict]:
        query = """
            SELECT 
                customer_segment AS segment,
                COUNT(*) AS customer_count,
                SUM(total_spent) AS total_revenue,
                AVG(total_spent / NULLIF(purchase_frequency, 0)) AS avg_basket
            FROM mv_customer_segmentation
            GROUP BY customer_segment
            ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_top_customers(self, limit: int = 10) -> list[dict]:
        query = """
            SELECT 
                cs.customerid,
                c.full_name,
                c.city,
                c.country,
                cs.total_spent,
                cs.purchase_frequency AS total_transactions,
                cs.customer_segment AS segment
            FROM mv_customer_segmentation cs
            JOIN dim_customer c ON cs.customerid = c.customerid
            ORDER BY cs.total_spent DESC
            LIMIT :limit
        """
        result = self.db.execute(text(query), {"limit": limit})
        return [dict(row._mapping) for row in result]

    def get_customer_activity(self, start_date: Optional[date] = None,
                               end_date: Optional[date] = None) -> list[dict]:
        query = """
            SELECT 
                d.month_name AS month,
                d.year,
                COUNT(DISTINCT s.customerid) AS active_customers,
                SUM(s.totalprice) AS total_revenue
            FROM fact_sales s
            JOIN dim_date d ON s.date = d.date_key
            WHERE 1=1
        """
        params = {}
        query = self._apply_date_filter(query, params, start_date, end_date)
        query += """
            GROUP BY d.year, d.month, d.month_name
            ORDER BY d.year, d.month
        """
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
                gender,
                age_group
            FROM mv_employee_performance
            ORDER BY total_revenue DESC
            LIMIT :limit
        """
        result = self.db.execute(text(query), {"limit": limit})
        return [dict(row._mapping) for row in result]

    def get_employee_detail(self, employee_id: int) -> Optional[dict]:
        query = """
            SELECT 
                employeeid AS employee_id,
                full_name,
                gender,
                age_group,
                seniority_group,
                city,
                total_revenue_generated AS total_revenue,
                transactions_handled AS total_transactions,
                total_quantity_sold AS total_quantity,
                unique_customers_served AS unique_customers,
                avg_transaction_value,
                revenue_rank
            FROM mv_employee_performance
            WHERE employeeid = :employee_id
        """
        result = self.db.execute(text(query), {"employee_id": employee_id})
        row = result.first()
        return dict(row._mapping) if row else None

    def get_employee_performance_by_age(self) -> list[dict]:
        query = """
            SELECT 
                age_group AS group_name,
                COUNT(*) AS employee_count,
                SUM(total_revenue_generated) AS total_revenue,
                SUM(transactions_handled) AS total_transactions,
                AVG(total_revenue_generated) AS avg_revenue_per_employee
            FROM mv_employee_performance
            GROUP BY age_group
            ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    def get_employee_performance_by_seniority(self) -> list[dict]:
        query = """
            SELECT 
                seniority_group AS group_name,
                COUNT(*) AS employee_count,
                SUM(total_revenue_generated) AS total_revenue,
                SUM(transactions_handled) AS total_transactions,
                AVG(total_revenue_generated) AS avg_revenue_per_employee
            FROM mv_employee_performance
            GROUP BY seniority_group
            ORDER BY total_revenue DESC
        """
        result = self.db.execute(text(query))
        return [dict(row._mapping) for row in result]

    # ---- BASKET ANALYSIS ----

    def get_basket_rules(self, min_support: float = 0.01,
                         min_lift: float = 1.5,
                         limit: int = 50) -> list[dict]:
        """Get association rules from basket analysis.
        
        This computes product pairs by self-joining transactions.
        For production with 6.7M rows, pre-compute in a materialized view.
        """
        query = """
            WITH transaction_products AS (
                SELECT DISTINCT s.transactionnumber, s.productid, p.productname
                FROM fact_sales s
                JOIN dim_product p ON s.productid = p.productid
            ),
            total_trans AS (
                SELECT COUNT(DISTINCT transactionnumber) AS cnt 
                FROM fact_sales
            ),
            product_pairs AS (
                SELECT 
                    a.productname AS product1,
                    b.productname AS product2,
                    COUNT(DISTINCT a.transactionnumber) AS both_count,
                    COUNT(DISTINCT a.transactionnumber) OVER(
                        PARTITION BY a.productname
                    ) AS p1_count,
                    COUNT(DISTINCT b.transactionnumber) OVER(
                        PARTITION BY b.productname
                    ) AS p2_count
                FROM transaction_products a
                JOIN transaction_products b 
                    ON a.transactionnumber = b.transactionnumber
                    AND a.productname < b.productname
                GROUP BY a.productname, b.productname
            )
            SELECT 
                pp.product1,
                pp.product2,
                pp.product1 || ' - ' || pp.product2 AS basket_label,
                ROUND(pp.both_count::NUMERIC / tt.cnt, 6) AS support,
                ROUND(pp.both_count::NUMERIC / NULLIF(pp.p1_count, 0), 6) AS confidence_p1,
                ROUND(pp.both_count::NUMERIC / NULLIF(pp.p2_count, 0), 6) AS confidence_p2,
                ROUND(
                    (pp.both_count::NUMERIC / tt.cnt) / 
                    NULLIF((pp.p1_count::NUMERIC / tt.cnt) * (pp.p2_count::NUMERIC / tt.cnt), 0), 
                    6
                ) AS lift
            FROM product_pairs pp
            CROSS JOIN total_trans tt
            WHERE (pp.both_count::NUMERIC / tt.cnt) >= :min_support
            HAVING 
                (pp.both_count::NUMERIC / tt.cnt) / 
                NULLIF((pp.p1_count::NUMERIC / tt.cnt) * (pp.p2_count::NUMERIC / tt.cnt), 0) >= :min_lift
            ORDER BY lift DESC
            LIMIT :limit
        """
        result = self.db.execute(
            text(query),
            {"min_support": min_support, "min_lift": min_lift, "limit": limit}
        )
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
