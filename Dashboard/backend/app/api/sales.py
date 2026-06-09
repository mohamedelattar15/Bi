"""Sales analytics API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import SalesOverTime, SalesByCategory, SalesByMonth

router = APIRouter(prefix="/api/sales", tags=["Sales"])


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
