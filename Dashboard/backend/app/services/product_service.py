"""Product analytics service."""

from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Optional
from datetime import date

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.product import (
    ProductDetail, ProductList, PriceDistribution, ProductPerformance
)


class ProductService:
    def __init__(self, db: Session):
        self.repo = DashboardRepository(db)

    def get_product_detail(self, product_id: int) -> Optional[ProductDetail]:
        data = self.repo.get_product_detail(product_id)
        if not data:
            return None
        return ProductDetail(**data)

    def get_all_products(self, start_date: Optional[date] = None,
                         end_date: Optional[date] = None) -> list[ProductList]:
        data = self.repo.get_price_volume_matrix(start_date, end_date)
        return [
            ProductList(
                product_id=row['productid'],
                product_name=row['productname'],
                price=Decimal(str(row['price'])),
                category=row['category'],
                total_revenue=Decimal(str(row['total_revenue'])),
                total_quantity=int(row['total_quantity']),
                revenue_rank=i + 1,
            )
            for i, row in enumerate(data)
        ]

    def get_price_distribution(self, start_date: Optional[date] = None,
                               end_date: Optional[date] = None) -> list[PriceDistribution]:
        data = self.repo.get_price_distribution(start_date, end_date)
        total = sum(Decimal(str(d['total_revenue'])) for d in data) or Decimal(1)
        return [
            PriceDistribution(
                range_label=row['range_label'],
                min_price=Decimal(str(row['min_price'])),
                max_price=Decimal(str(row['max_price'])),
                product_count=int(row['product_count']),
                total_revenue=Decimal(str(row['total_revenue'])),
                percentage=(Decimal(str(row['total_revenue'])) / total * 100).quantize(Decimal('0.01'))
            )
            for row in data
        ]

    def get_price_volume_matrix(self, start_date: Optional[date] = None,
                                end_date: Optional[date] = None) -> list[ProductPerformance]:
        data = self.repo.get_price_volume_matrix(start_date, end_date)
        return [
            ProductPerformance(
                product_id=row['productid'],
                product_name=row['productname'],
                price=Decimal(str(row['price'])),
                total_quantity=int(row['total_quantity']),
                total_revenue=Decimal(str(row['total_revenue'])),
                category=row['category'],
            )
            for row in data
        ]
