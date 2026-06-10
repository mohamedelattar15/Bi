"""Dashboard summary and KPI schemas."""

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date, datetime


class KPICard(BaseModel):
    """KPI card value with optional trend."""

    label: str
    value: Decimal
    prefix: str = ""
    suffix: str = ""
    format: str = "number"  # number, currency, percentage
    trend: Optional[Decimal] = None  # percentage change vs previous period
    trend_direction: Optional[str] = None  # up, down, stable


class SalesOverTime(BaseModel):
    """Sales data point for time series charts."""

    date: str  # ISO date string
    period: str  # month, quarter, year label
    revenue: Decimal
    quantity: int
    transactions: int
    avg_basket: Optional[Decimal] = None


class SalesByCategory(BaseModel):
    """Sales aggregated by product category."""

    category: str
    revenue: Decimal
    quantity: int
    percentage: Optional[Decimal] = None
    transaction_count: Optional[int] = None


class SalesByMonth(BaseModel):
    """Monthly sales with seasonality info."""

    year: int
    month: int
    month_name: str
    quarter: int
    revenue: Decimal
    quantity: int
    transaction_count: int
    prev_year_revenue: Optional[Decimal] = None
    yoy_growth: Optional[Decimal] = None


class TopProduct(BaseModel):
    """Top selling product entry."""

    rank: int
    product_id: int
    product_name: str
    category: str
    revenue: Decimal
    quantity_sold: int
    times_sold: int


class DashboardSummary(BaseModel):
    """Complete dashboard summary response."""

    # KPI Cards
    total_revenue: KPICard
    total_quantity: KPICard
    total_transactions: KPICard
    avg_basket: KPICard
    unique_customers: Optional[KPICard] = None
    total_products: Optional[KPICard] = None

    # Charts data
    revenue_over_time: list[SalesOverTime]
    sales_by_category: list[SalesByCategory]
    monthly_sales: list[SalesByMonth]
    top_products: list[TopProduct]

    # Metadata
    period: str = "All Time"
    generated_at: datetime = datetime.now()
