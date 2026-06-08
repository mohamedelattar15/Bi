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
