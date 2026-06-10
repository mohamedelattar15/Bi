"""Customer analytics API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.services.customer_service import CustomerService
from app.schemas.customer import (
    CustomerDetail, CustomerSegment, TopCustomer, CustomerActivity
)
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("/segments", response_model=list[CustomerSegment])
def get_customer_segments(db: Session = Depends(get_db)):
    """Get customer segmentation distribution."""
    service = CustomerService(db)
    return service.get_customer_segments()


@router.get("/top", response_model=list[TopCustomer])
def get_top_customers(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get top customers by revenue."""
    service = CustomerService(db)
    return service.get_top_customers(limit)


@router.get("/activity", response_model=list[CustomerActivity])
def get_customer_activity(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Get customer activity over time."""
    service = CustomerService(db)
    return service.get_customer_activity(start_date, end_date)


# ── New endpoints mapped from PBIX Customer page ──

class CustomerByTransactions(BaseModel):
    customer_id: int
    full_name: str
    city: str
    country: str
    total_transactions: int
    total_revenue: Decimal


class CustomerAvgBasketByCity(BaseModel):
    city: str
    customer_count: int
    total_revenue: Decimal
    avg_basket: Decimal
    total_transactions: int


class CustomerGrowthByCity(BaseModel):
    city: str
    revenue: Decimal
    transactions: int
    quantity: int
    customer_count: int
    ca_growth_pct: Decimal
    transa_growth_pct: Decimal
    quant_growth_pct: Decimal


class CustomerLoyaltyStats(BaseModel):
    total_customers: int
    active_customers: int
    ltv: Decimal
    avg_frequency: Decimal
    repurchase_rate: Decimal


@router.get("/by-transactions", response_model=list[CustomerByTransactions])
def get_customers_by_transactions(
    limit: int = Query(10, ge=1, le=100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Top customers by transaction count (for Bar chart)."""
    repo = DashboardRepository(db)
    data = repo.get_customers_by_transactions(limit, start_date, end_date)
    return [
        CustomerByTransactions(
            customer_id=int(row['customerid']),
            full_name=row['full_name'],
            city=row['city'],
            country=row['country'],
            total_transactions=int(row['total_transactions']),
            total_revenue=row['total_revenue'],
        )
        for row in data
    ]


@router.get("/avg-basket-by-city", response_model=list[CustomerAvgBasketByCity])
def get_avg_basket_by_city(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Average basket by city (for Map visual)."""
    repo = DashboardRepository(db)
    data = repo.get_customers_avg_basket_by_city(start_date, end_date)
    return [
        CustomerAvgBasketByCity(
            city=row['city'],
            customer_count=int(row['customer_count']),
            total_revenue=row['total_revenue'],
            avg_basket=row['avg_basket'],
            total_transactions=int(row['total_transactions']),
        )
        for row in data
    ]


@router.get("/growth-by-city", response_model=list[CustomerGrowthByCity])
def get_growth_by_city(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Growth metrics by city (for Pivot Table)."""
    repo = DashboardRepository(db)
    data = repo.get_customer_growth_by_city(start_date, end_date)
    return [
        CustomerGrowthByCity(
            city=row['city'],
            revenue=row['revenue'],
            transactions=int(row['transactions']),
            quantity=int(row['quantity']),
            customer_count=int(row['customer_count']),
            ca_growth_pct=Decimal(str(row['ca_growth_pct'])),
            transa_growth_pct=Decimal(str(row['transa_growth_pct'])),
            quant_growth_pct=Decimal(str(row['quant_growth_pct'])),
        )
        for row in data
    ]


@router.get("/loyalty-stats", response_model=CustomerLoyaltyStats)
def get_loyalty_stats(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Customer loyalty, frequency, and re-purchase rates."""
    repo = DashboardRepository(db)
    data = repo.get_customer_loyalty_stats(start_date, end_date)
    return CustomerLoyaltyStats(
        total_customers=int(data['total_customers']),
        active_customers=int(data['active_customers']),
        ltv=data['ltv'],
        avg_frequency=Decimal(str(data['avg_frequency'] or 0)),
        repurchase_rate=Decimal(str(data['repurchase_rate'] or 0)),
    )


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer_detail(customer_id: int, db: Session = Depends(get_db)):
    """Get detailed customer information."""
    service = CustomerService(db)
    result = service.get_customer_detail(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result
