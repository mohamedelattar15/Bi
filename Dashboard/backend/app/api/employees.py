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
from pydantic import BaseModel
from decimal import Decimal
from app.repositories.dashboard_repository import DashboardRepository

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


# ── New endpoints mapped from PBIX Employee page ──

class AgeCategoryDist(BaseModel):
    age_category: str
    employee_count: int


class AgeTrancheDist(BaseModel):
    age_tranche: str
    employee_count: int


class GenderDist(BaseModel):
    gender: str
    employee_count: int


class CaByAgeTranche(BaseModel):
    age_tranche: str
    employee_count: int
    total_revenue: Decimal


class EmployeePerfRow(BaseModel):
    employee_id: int
    full_name_emp: str
    gender: Optional[str] = None
    total_revenue: Decimal
    ca_growth: Decimal


@router.get("/demographics/age-category", response_model=list[AgeCategoryDist])
def get_age_category_distribution(db: Session = Depends(get_db)):
    """Employee count by age category (for Donut chart)."""
    repo = DashboardRepository(db)
    data = repo.get_employee_age_category_distribution()
    return [
        AgeCategoryDist(age_category=row['age_category'], employee_count=int(row['employee_count']))
        for row in data
    ]


@router.get("/demographics/age-tranche", response_model=list[AgeTrancheDist])
def get_age_tranche_distribution(db: Session = Depends(get_db)):
    """Employee count by detailed age tranche (for Pie chart)."""
    repo = DashboardRepository(db)
    data = repo.get_employee_age_tranche_distribution()
    return [
        AgeTrancheDist(age_tranche=row['age_tranche'], employee_count=int(row['employee_count']))
        for row in data
    ]


@router.get("/demographics/gender", response_model=list[GenderDist])
def get_gender_distribution(db: Session = Depends(get_db)):
    """Employee count by gender (for Donut chart)."""
    repo = DashboardRepository(db)
    data = repo.get_employee_gender_distribution()
    return [
        GenderDist(gender=row['gender'], employee_count=int(row['employee_count']))
        for row in data
    ]


@router.get("/ca-by-age-tranche", response_model=list[CaByAgeTranche])
def get_ca_by_age_tranche(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """CA total by age tranche (for Bar chart)."""
    repo = DashboardRepository(db)
    data = repo.get_employee_ca_by_age_tranche(start_date, end_date)
    return [
        CaByAgeTranche(
            age_tranche=row['age_tranche'],
            employee_count=int(row['employee_count']),
            total_revenue=row['total_revenue'],
        )
        for row in data
    ]


@router.get("/performance-table", response_model=list[EmployeePerfRow])
def get_employee_performance_table(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Employee table with CA total and CA Growth."""
    repo = DashboardRepository(db)
    data = repo.get_employee_performance_table(start_date, end_date)
    return [
        EmployeePerfRow(
            employee_id=int(row['employeeid']),
            full_name_emp=row['full_name_emp'],
            gender=row.get('gender'),
            total_revenue=row['total_revenue'],
            ca_growth=Decimal(str(row['ca_growth'])),
        )
        for row in data
    ]


@router.get("/{employee_id}", response_model=EmployeeDetail)
def get_employee_detail(employee_id: int, db: Session = Depends(get_db)):
    """Get detailed employee performance information."""
    service = EmployeeService(db)
    result = service.get_employee_detail(employee_id)
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result
