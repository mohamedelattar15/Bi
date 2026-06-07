"""Employee analytics API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.employee_service import EmployeeService
from app.schemas.employee import (
    EmployeeDetail, EmployeePerformance, TopEmployee
)

router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.get("/top", response_model=list[TopEmployee])
def get_top_employees(
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get top performing employees."""
    service = EmployeeService(db)
    return service.get_top_employees(limit)


@router.get("/performance/by-age", response_model=list[EmployeePerformance])
def get_performance_by_age(db: Session = Depends(get_db)):
    """Get employee performance grouped by age group."""
    service = EmployeeService(db)
    return service.get_performance_by_age()


@router.get("/performance/by-seniority", response_model=list[EmployeePerformance])
def get_performance_by_seniority(db: Session = Depends(get_db)):
    """Get employee performance grouped by seniority."""
    service = EmployeeService(db)
    return service.get_performance_by_seniority()


@router.get("/{employee_id}", response_model=EmployeeDetail)
def get_employee_detail(employee_id: int, db: Session = Depends(get_db)):
    """Get detailed employee performance information."""
    service = EmployeeService(db)
    result = service.get_employee_detail(employee_id)
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result
