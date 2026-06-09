"""Employee analytics API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.services.employee_service import EmployeeService
from app.schemas.employee import (
    EmployeeDetail, EmployeePerformance, TopEmployee
)

router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.get("/top", response_model=list[TopEmployee])
def get_top_employees(
    limit: int = Query(5, ge=1, le=50),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
):
    """Get top performing employees."""
    service = EmployeeService(db)
    return service.get_top_employees(limit, start_date, end_date)


@router.get("/performance/by-age", response_model=list[EmployeePerformance])
def get_performance_by_age(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
):
    """Get employee performance grouped by age group."""
    service = EmployeeService(db)
    return service.get_performance_by_age(start_date, end_date)


@router.get("/performance/by-seniority", response_model=list[EmployeePerformance])
def get_performance_by_seniority(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
):
    """Get employee performance grouped by seniority."""
    service = EmployeeService(db)
    return service.get_performance_by_seniority(start_date, end_date)


@router.get("/{employee_id}", response_model=EmployeeDetail)
def get_employee_detail(employee_id: int, db: Session = Depends(get_db)):
    """Get detailed employee performance information."""
    service = EmployeeService(db)
    result = service.get_employee_detail(employee_id)
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result
