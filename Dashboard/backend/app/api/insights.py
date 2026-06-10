"""
Advanced analytical insights API endpoints.
Exposes all the deeper business logic from ANALYSIS_INSIGHTS.md.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.analytics import (
    RevenueConcentration,
    DayOfWeekRevenue,
    MomGrowth,
    SalesByResistance,
    RFMSegment,
    GeographicDistribution,
    EmployeeParity,
    EmployeeRanking,
)
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.get("/revenue-concentration", response_model=RevenueConcentration)
def get_revenue_concentration(db: Session = Depends(get_db)):
    """Revenue concentration (Herfindahl index, top category %)."""
    repo = DashboardRepository(db)
    return repo.get_revenue_concentration()


@router.get("/revenue-by-day", response_model=list[DayOfWeekRevenue])
def get_revenue_by_day_of_week(db: Session = Depends(get_db)):
    """Revenue breakdown by day of week (peak days, weekend vs weekday)."""
    repo = DashboardRepository(db)
    return repo.get_revenue_by_day_of_week()


@router.get("/month-over-month", response_model=list[MomGrowth])
def get_month_over_month_growth(db: Session = Depends(get_db)):
    """Month-over-month revenue growth and run rate."""
    repo = DashboardRepository(db)
    return repo.get_month_over_month_growth()


@router.get("/sales-by-resistance", response_model=list[SalesByResistance])
def get_sales_by_resistance(db: Session = Depends(get_db)):
    """Sales performance by product resistance level."""
    repo = DashboardRepository(db)
    return repo.get_sales_by_resistance()


@router.get("/customer-rfm", response_model=list[RFMSegment])
def get_customer_rfm(db: Session = Depends(get_db)):
    """Customer RFM segmentation (Champions, Loyal, At Risk, etc.)."""
    repo = DashboardRepository(db)
    return repo.get_customer_rfm_segmentation()


@router.get("/geographic-distribution", response_model=list[GeographicDistribution])
def get_geographic_distribution(db: Session = Depends(get_db)):
    """Customer count and revenue by country."""
    repo = DashboardRepository(db)
    return repo.get_customer_geographic_distribution()


@router.get("/employee-parity", response_model=EmployeeParity)
def get_employee_parity(db: Session = Depends(get_db)):
    """Employee performance distribution and parity stats."""
    repo = DashboardRepository(db)
    return repo.get_employee_performance_parity()


@router.get("/employee-ranking", response_model=list[EmployeeRanking])
def get_employee_ranking(db: Session = Depends(get_db)):
    """Full employee ranking with all performance metrics."""
    repo = DashboardRepository(db)
    return repo.get_employee_ranking()


# ── New advanced chart endpoints ──

class MonthlyRevenueByCategory(BaseModel):
    year: int
    month: int
    month_name: str
    category: str
    revenue: Decimal
    quantity: int
    transaction_count: int


class ProfitSummary(BaseModel):
    gross_revenue: Decimal
    total_discounts: Decimal
    total_orders: int
    net_profit: Decimal
    avg_profit_per_transaction: Decimal


class CategoryWaterfall(BaseModel):
    category: str
    revenue: Decimal
    quantity: int
    transaction_count: int


class ParetoProduct(BaseModel):
    product_id: int
    product_name: str
    category: str
    revenue: Decimal
    quantity_sold: int
    pct_of_total: Decimal
    cumulative_pct: Decimal


class GrowthMetrics(BaseModel):
    total_revenue: Decimal
    total_profit: Decimal
    total_orders: int
    total_discounts: Decimal
    profit_margin_pct: Decimal
    avg_profit_per_order: Decimal


@router.get("/monthly-by-category", response_model=list[MonthlyRevenueByCategory])
def get_monthly_revenue_by_category(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Monthly revenue by category (for Stacked Bar / Heatmap)."""
    repo = DashboardRepository(db)
    data = repo.get_monthly_revenue_by_category(start_date, end_date)
    return [
        MonthlyRevenueByCategory(
            year=int(row['year']), month=int(row['month']),
            month_name=row['month_name'], category=row['category'],
            revenue=row['revenue'], quantity=int(row['quantity']),
            transaction_count=int(row['transaction_count']),
        )
        for row in data
    ]


@router.get("/profit-summary", response_model=ProfitSummary)
def get_profit_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Gross revenue, discounts, net profit."""
    repo = DashboardRepository(db)
    data = repo.get_profit_summary(start_date, end_date)
    return ProfitSummary(**data)


@router.get("/category-waterfall", response_model=list[CategoryWaterfall])
def get_category_waterfall(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Category contribution waterfall."""
    repo = DashboardRepository(db)
    data = repo.get_category_waterfall(start_date, end_date)
    return [
        CategoryWaterfall(
            category=row['category'], revenue=row['revenue'],
            quantity=int(row['quantity']), transaction_count=int(row['transaction_count']),
        )
        for row in data
    ]


@router.get("/pareto-products", response_model=list[ParetoProduct])
def get_pareto_products(
    limit: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Product revenue with cumulative % for Pareto chart."""
    repo = DashboardRepository(db)
    data = repo.get_top_product_pareto(limit, start_date, end_date)
    return [
        ParetoProduct(
            product_id=int(row['productid']), product_name=row['productname'],
            category=row['category'], revenue=row['revenue'],
            quantity_sold=int(row['quantity_sold']),
            pct_of_total=Decimal(str(row['pct_of_total'])),
            cumulative_pct=Decimal(str(row['cumulative_pct'])),
        )
        for row in data
    ]


@router.get("/growth-metrics", response_model=GrowthMetrics)
def get_growth_metrics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Growth %, profit margin, and key financial metrics."""
    repo = DashboardRepository(db)
    data = repo.get_growth_metrics(start_date, end_date)
    return GrowthMetrics(**data)
