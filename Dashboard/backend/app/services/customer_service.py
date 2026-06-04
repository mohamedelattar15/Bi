"""Customer analytics service."""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Optional
from datetime import date

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.customer import (
    CustomerDetail, CustomerSegment, TopCustomer, CustomerActivity
)


class CustomerService:
    def __init__(self, db: Session):
        self.repo = DashboardRepository(db)

    def get_customer_segments(self) -> list[CustomerSegment]:
        data = self.repo.get_customer_segments()
        total_customers = sum(d['customer_count'] for d in data) or 1
        return [
            CustomerSegment(
                segment=row['segment'],
                customer_count=int(row['customer_count']),
                total_revenue=Decimal(str(row['total_revenue'])),
                avg_basket=Decimal(str(row['avg_basket'] or 0)),
                percentage=(Decimal(str(row['customer_count'])) / total_customers * 100).quantize(Decimal('0.01'))
            )
            for row in data
        ]

    def get_top_customers(self, limit: int = 10) -> list[TopCustomer]:
        data = self.repo.get_top_customers(limit)
        return [
            TopCustomer(
                rank=i + 1,
                customer_id=row['customerid'],
                full_name=row['full_name'],
                city=row['city'],
                country=row['country'],
                total_spent=Decimal(str(row['total_spent'])),
                total_transactions=int(row['total_transactions']),
                segment=row['segment'],
            )
            for i, row in enumerate(data)
        ]

    def get_customer_activity(self, start_date: Optional[date] = None,
                               end_date: Optional[date] = None) -> list[CustomerActivity]:
        data = self.repo.get_customer_activity(start_date, end_date)
        return [
            CustomerActivity(
                month=row['month'],
                year=int(row['year']),
                active_customers=int(row['active_customers']),
                new_customers=0,  # Would need separate query
                total_revenue=Decimal(str(row['total_revenue'])),
            )
            for row in data
        ]

    def get_customer_detail(self, customer_id: int) -> Optional[CustomerDetail]:
        data = self.repo.get_customer_detail(customer_id)
        if not data:
            return None
        # Handle None dates
        if data.get('first_purchase'):
            data['first_purchase'] = data['first_purchase'].isoformat() if hasattr(data['first_purchase'], 'isoformat') else data['first_purchase']
        if data.get('last_purchase'):
            data['last_purchase'] = data['last_purchase'].isoformat() if hasattr(data['last_purchase'], 'isoformat') else data['last_purchase']
        return CustomerDetail(**data)
