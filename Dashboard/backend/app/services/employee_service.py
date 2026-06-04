"""Employee analytics service."""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Optional

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.employee import (
    EmployeeDetail, EmployeePerformance, TopEmployee
)


class EmployeeService:
    def __init__(self, db: Session):
        self.repo = DashboardRepository(db)

    def get_top_employees(self, limit: int = 5) -> list[TopEmployee]:
        data = self.repo.get_top_employees(limit)
        return [
            TopEmployee(
                rank=i + 1,
                employee_id=row['employeeid'],
                full_name=row['full_name'],
                total_revenue=Decimal(str(row['total_revenue'])),
                total_transactions=int(row['total_transactions']),
                gender=row.get('gender'),
                age_group=row.get('age_group'),
            )
            for i, row in enumerate(data)
        ]

    def get_employee_detail(self, employee_id: int) -> Optional[EmployeeDetail]:
        data = self.repo.get_employee_detail(employee_id)
        if not data:
            return None
        return EmployeeDetail(**data)

    def get_performance_by_age(self) -> list[EmployeePerformance]:
        data = self.repo.get_employee_performance_by_age()
        return [EmployeePerformance(**row) for row in data]

    def get_performance_by_seniority(self) -> list[EmployeePerformance]:
        data = self.repo.get_employee_performance_by_seniority()
        return [EmployeePerformance(**row) for row in data]
