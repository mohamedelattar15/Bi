"""Dashboard business logic service."""

from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from typing import Optional

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardSummary, KPICard, SalesOverTime, 
    SalesByCategory, SalesByMonth, TopProduct
)


class DashboardService:
    """Orchestrates dashboard data retrieval and transformation."""

    def __init__(self, db: Session):
        self.repo = DashboardRepository(db)

    def get_dashboard_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> DashboardSummary:
        """Build complete dashboard summary with KPIs and chart data."""

        # --- KPIs ---
        revenue = Decimal(str(self.repo.get_total_revenue(start_date, end_date)))
        quantity = int(self.repo.get_total_quantity(start_date, end_date))
        transactions = int(self.repo.get_total_transactions(start_date, end_date))
        avg_basket = Decimal(str(self.repo.get_avg_basket(start_date, end_date)))
        customers = int(self.repo.get_unique_customers(start_date, end_date))
        total_products = int(self.repo.get_total_products())

        # --- Time Series ---
        monthly_data = self.repo.get_monthly_revenue(start_date, end_date)
        revenue_over_time = [
            SalesOverTime(
                date=f"{row['year']}-{row['month']:02d}-01",
                period=row['month_name'],
                revenue=Decimal(str(row['revenue'])),
                quantity=int(row['quantity']),
                transactions=int(row['transaction_count']),
                avg_basket=Decimal(str(row['avg_basket']))
            )
            for row in monthly_data
        ]

        # --- Sales by Category ---
        category_data = self.repo.get_sales_by_category(start_date, end_date)
        total_rev = sum(Decimal(str(c['revenue'])) for c in category_data) or Decimal(1)
        sales_by_category = [
            SalesByCategory(
                category=row['category'],
                revenue=Decimal(str(row['revenue'])),
                quantity=int(row['quantity']),
                percentage=(Decimal(str(row['revenue'])) / total_rev * 100).quantize(Decimal('0.01')),
                transaction_count=int(row['transaction_count'])
            )
            for row in category_data
        ]

        # --- Monthly Sales with YoY ---
        monthly_sales_raw = self.repo.get_monthly_revenue(start_date, end_date)
        # Build lookup for previous year comparison
        prev_year_map = {}
        for row in monthly_sales_raw:
            prev_year_map[(int(row['year']) - 1, int(row['month']))] = Decimal(str(row['revenue']))

        monthly_sales = [
            SalesByMonth(
                year=int(row['year']),
                month=int(row['month']),
                month_name=row['month_name'],
                quarter=int(row['quarter']),
                revenue=Decimal(str(row['revenue'])),
                quantity=int(row['quantity']),
                transaction_count=int(row['transaction_count']),
                prev_year_revenue=prev_year_map.get((int(row['year']), int(row['month']))),
                yoy_growth=(
                    (Decimal(str(row['revenue'])) - prev_year_map[(int(row['year']), int(row['month']))])
                    / prev_year_map[(int(row['year']), int(row['month']))] * 100
                    if (int(row['year']), int(row['month'])) in prev_year_map
                    else None
                )
            )
            for row in monthly_sales_raw
        ]

        # --- Top Products ---
        top_products_data = self.repo.get_top_products(10, start_date, end_date)
        top_products = [
            TopProduct(
                rank=i + 1,
                product_id=row['productid'],
                product_name=row['productname'],
                category=row['category'],
                revenue=Decimal(str(row['revenue'])),
                quantity_sold=int(row['quantity_sold']),
                times_sold=int(row['times_sold'])
            )
            for i, row in enumerate(top_products_data)
        ]

        return DashboardSummary(
            total_revenue=KPICard(
                label="Total Revenue",
                value=revenue,
                prefix="€",
                format="currency"
            ),
            total_quantity=KPICard(
                label="Total Quantity Sold",
                value=Decimal(str(quantity)),
                format="number"
            ),
            total_transactions=KPICard(
                label="Total Transactions",
                value=Decimal(str(transactions)),
                format="number"
            ),
            avg_basket=KPICard(
                label="Average Basket",
                value=avg_basket,
                prefix="€",
                format="currency"
            ),
            unique_customers=KPICard(
                label="Active Customers",
                value=Decimal(str(customers)),
                format="number"
            ),
            total_products=KPICard(
                label="Total Products",
                value=Decimal(str(total_products)),
                format="number"
            ),
            revenue_over_time=revenue_over_time,
            sales_by_category=sales_by_category,
            monthly_sales=monthly_sales,
            top_products=top_products,
        )
