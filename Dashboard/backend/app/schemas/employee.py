"""Employee analytics schemas."""

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class EmployeeDetail(BaseModel):
    """Detailed employee information."""

    employee_id: int
    full_name: str
    gender: Optional[str] = None
    age_group: Optional[str] = None
    seniority_group: Optional[str] = None
    city: Optional[str] = None
    total_revenue: Decimal
    total_transactions: int
    total_quantity: int
    unique_customers: int
    avg_transaction_value: Decimal
    revenue_rank: int


class EmployeePerformance(BaseModel):
    """Employee performance by demographic."""

    group_name: str  # e.g. age group or seniority
    employee_count: int
    total_revenue: Decimal
    total_transactions: int
    avg_revenue_per_employee: Decimal


class TopEmployee(BaseModel):
    """Top employee entry."""

    rank: int
    employee_id: int
    full_name: str
    total_revenue: Decimal
    total_transactions: int
    gender: Optional[str] = None
    age_group: Optional[str] = None
