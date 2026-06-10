"""Sales analytics API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import SalesOverTime, SalesByCategory, SalesByMonth
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/api/sales", tags=["Sales"])


# Additional schemas for new endpoints
class SalesByCity(BaseModel):
    city: str
    revenue: Decimal
    quantity: int
    transaction_count: int


class SalesFunnel(BaseModel):
    city: str
    quantity: int
    revenue: Decimal


class CaGrowthByYear(BaseModel):
    year: int
    revenue: Decimal
    quantity: int
    transaction_count: int
    growth: Optional[Decimal] = None


class SalesByClass(BaseModel):
    class_: str
    revenue: Decimal
    quantity: int


@router.get("/over-time", response_model=list[SalesOverTime])
def get_sales_over_time(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category: Optional[str] = Query(None, description="Filter by product category"),
    db: Session = Depends(get_db),
):
    """Get revenue over time (monthly)."""
    repo = DashboardRepository(db)
    data = repo.get_monthly_revenue(start_date, end_date, category=category)
    return [
        SalesOverTime(
            date=f"{row['year']}-{row['month']:02d}-01",
            period=row['month_name'],
            revenue=row['revenue'],
            quantity=int(row['quantity']),
            transactions=int(row['transaction_count']),
            avg_basket=row['avg_basket'],
        )
        for row in data
    ]


@router.get("/by-category", response_model=list[SalesByCategory])
def get_sales_by_category(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    product: Optional[str] = Query(None, description="Filter by product name"),
    db: Session = Depends(get_db),
):
    """Get sales aggregated by product category."""
    repo = DashboardRepository(db)
    data = repo.get_sales_by_category(start_date, end_date, product=product)
    total = sum(r['revenue'] for r in data) or 1
    return [
        SalesByCategory(
            category=row['category'],
            revenue=row['revenue'],
            quantity=int(row['quantity']),
            percentage=(row['revenue'] / total * 100),
            transaction_count=int(row['transaction_count']),
        )
        for row in data
    ]


@router.get("/monthly", response_model=list[SalesByMonth])
def get_monthly_sales(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category: Optional[str] = Query(None, description="Filter by product category"),
    db: Session = Depends(get_db),
):
    """Get monthly sales with YoY comparison."""
    repo = DashboardRepository(db)
    data = repo.get_monthly_revenue(start_date, end_date, category=category)
    return [
        SalesByMonth(
            year=int(row['year']),
            month=int(row['month']),
            month_name=row['month_name'],
            quarter=int(row['quarter']),
            revenue=row['revenue'],
            quantity=int(row['quantity']),
            transaction_count=int(row['transaction_count']),
        )
        for row in data
    ]


@router.get("/by-city", response_model=list[SalesByCity])
def get_sales_by_city(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Get CA total by city (for Map visual)."""
    repo = DashboardRepository(db)
    data = repo.get_sales_by_city(start_date, end_date)
    return [
        SalesByCity(
            city=row['city'],
            revenue=row['revenue'],
            quantity=int(row['quantity']),
            transaction_count=int(row['transaction_count']),
        )
        for row in data
    ]


@router.get("/funnel-by-city", response_model=list[SalesFunnel])
def get_sales_funnel(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Get funnel data: quantity by city."""
    repo = DashboardRepository(db)
    data = repo.get_sales_funnel_by_city(start_date, end_date)
    return [
        SalesFunnel(
            city=row['city'],
            quantity=int(row['quantity']),
            revenue=row['revenue'],
        )
        for row in data
    ]


@router.get("/ca-growth-by-year", response_model=list[CaGrowthByYear])
def get_ca_growth_by_year(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Get CA Growth by year (for Area Chart)."""
    repo = DashboardRepository(db)
    data = repo.get_ca_growth_by_year(start_date, end_date)
    return [
        CaGrowthByYear(
            year=int(row['year']),
            revenue=row['revenue'],
            quantity=int(row['quantity']),
            transaction_count=int(row['transaction_count']),
            growth=row['growth'],
        )
        for row in data
    ]


@router.get("/by-class", response_model=list[SalesByClass])
def get_sales_by_class(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Get CA by product class (for Donut chart)."""
    repo = DashboardRepository(db)
    data = repo.get_sales_by_class(start_date, end_date)
    return [
        SalesByClass(
            class_=row['class'],
            revenue=row['revenue'],
            quantity=int(row['quantity']),
        )
        for row in data
    ]
