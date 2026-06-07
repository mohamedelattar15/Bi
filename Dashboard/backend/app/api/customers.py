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


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer_detail(customer_id: int, db: Session = Depends(get_db)):
    """Get detailed customer information."""
    service = CustomerService(db)
    result = service.get_customer_detail(customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result
