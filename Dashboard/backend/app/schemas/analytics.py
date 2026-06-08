"""Analytical insights schemas for the advanced analytics endpoints."""

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class RevenueConcentration(BaseModel):
    """Market concentration metrics (Herfindahl index)."""
    category_count: int
    top_category: str
    top_category_pct: Decimal
    herfindahl_index: Decimal


class DayOfWeekRevenue(BaseModel):
    """Revenue breakdown by day of week."""
    day_name: str
    is_weekend: bool
    transactions: int
    quantity: int
    revenue: Decimal
    avg_basket: Decimal


class MomGrowth(BaseModel):
    """Month-over-month growth metrics."""
    year: int
    month: int
    month_name: str
    revenue: Decimal
    quantity: int
    mom_growth_pct: Decimal
    monthly_run_rate: Decimal


class SalesByResistance(BaseModel):
    """Revenue by product resistance level."""
    resistance: str
    product_count: int
    quantity: int
    revenue: Decimal


class RFMSegment(BaseModel):
    """RFM customer segment."""
    rfm_segment: str
    customer_count: int
    avg_spent: Decimal
    total_revenue: Decimal
    avg_frequency: Decimal
    avg_categories: Decimal


class GeographicDistribution(BaseModel):
    """Customer and revenue by country."""
    country: str
    customer_count: int
    total_revenue: Decimal
    total_quantity: int
    avg_revenue_per_customer: Decimal


class EmployeeParity(BaseModel):
    """Employee performance distribution metrics."""
    employee_count: int
    avg_revenue: Decimal
    stddev_revenue: Decimal
    spread_pct: Decimal
    min_revenue: Decimal
    max_revenue: Decimal
    avg_transactions: int
    avg_customers: int


class EmployeeRanking(BaseModel):
    """Full employee ranking entry."""
    employee_id: int
    full_name: str
    gender: Optional[str] = None
    revenue: Decimal
    transactions: int
    customers_served: int
    quantity_sold: int
    avg_transaction_value: Decimal
    rank: int


class TopProductInsight(BaseModel):
    """Top product entry with detailed metrics."""
    rank: int
    product_id: int
    product_name: str
    category: str
    revenue: Decimal
    quantity_sold: int
    times_sold: int
    revenue_share: Optional[Decimal] = None
