"""Product analytics API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal

from app.core.database import get_db
from app.services.product_service import ProductService
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.product import ProductDetail, ProductList, PriceDistribution, ProductPerformance
from app.schemas.analytics import TopProductInsight, SalesByResistance

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("/", response_model=list[ProductList])
def get_all_products(db: Session = Depends(get_db)):
    """Get all products with revenue info."""
    service = ProductService(db)
    return service.get_all_products()


@router.get("/top", response_model=list[TopProductInsight])
def get_top_products(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get top products by revenue with revenue share."""
    repo = DashboardRepository(db)
    data = repo.get_top_products(limit)
    total = sum(Decimal(str(r['revenue'])) for r in data) or Decimal(1)
    return [
        TopProductInsight(
            rank=i + 1,
            product_id=row['productid'],
            product_name=row['productname'],
            category=row['category'],
            revenue=row['revenue'],
            quantity_sold=int(row['quantity_sold']),
            times_sold=int(row['times_sold']),
            revenue_share=(Decimal(str(row['revenue'])) / total * 100).quantize(Decimal('0.01')),
        )
        for i, row in enumerate(data)
    ]


@router.get("/sales-by-resistance", response_model=list[SalesByResistance])
def get_sales_by_resistance(db: Session = Depends(get_db)):
    """Sales performance by product resistance level (Durable, Weak, etc.)."""
    repo = DashboardRepository(db)
    return repo.get_sales_by_resistance()


@router.get("/{product_id}", response_model=ProductDetail)
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    """Get detailed product information."""
    service = ProductService(db)
    result = service.get_product_detail(product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result


@router.get("/analytics/price-distribution", response_model=list[PriceDistribution])
def get_price_distribution(db: Session = Depends(get_db)):
    """Get price distribution of products."""
    service = ProductService(db)
    return service.get_price_distribution()


@router.get("/analytics/price-volume-matrix", response_model=list[ProductPerformance])
def get_price_volume_matrix(db: Session = Depends(get_db)):
    """Get price vs volume scatter plot data."""
    service = ProductService(db)
    return service.get_price_volume_matrix()
