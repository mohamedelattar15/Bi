"""Product analytics API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.services.product_service import ProductService
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.product import ProductDetail, ProductList, PriceDistribution, ProductPerformance
from app.schemas.analytics import TopProductInsight, SalesByResistance
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("/", response_model=list[ProductList])
def get_all_products(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
):
    """Get all products with revenue info."""
    service = ProductService(db)
    return service.get_all_products(start_date, end_date)


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
def get_price_distribution(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
):
    """Get price distribution of products."""
    service = ProductService(db)
    return service.get_price_distribution(start_date, end_date)


@router.get("/analytics/price-volume-matrix", response_model=list[ProductPerformance])
def get_price_volume_matrix(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
):
    """Get price vs volume scatter plot data."""
    service = ProductService(db)
    return service.get_price_volume_matrix(start_date, end_date)


# ── New endpoints mapped from PBIX Product page ──

class AllergenDistribution(BaseModel):
    isallergic: str
    product_count: int


class ResistanceDistribution(BaseModel):
    resistance: str
    product_count: int


class CategoryGrowth(BaseModel):
    category: str
    revenue: Decimal
    quantity: int
    transactions: int
    ca_growth_pct: Decimal
    quant_growth_pct: Decimal
    transa_growth_pct: Decimal


class ProductQuantitySummary(BaseModel):
    product_id: int
    product_name: str
    category: str
    total_quantity: int
    total_revenue: Decimal


@router.get("/analytics/allergen-distribution", response_model=list[AllergenDistribution])
def get_allergen_distribution(db: Session = Depends(get_db)):
    """Product count by allergen status (for Pie chart)."""
    repo = DashboardRepository(db)
    data = repo.get_products_by_allergen()
    return [
        AllergenDistribution(isallergic=row['isallergic'], product_count=int(row['product_count']))
        for row in data
    ]


@router.get("/analytics/resistance-distribution", response_model=list[ResistanceDistribution])
def get_resistance_distribution(db: Session = Depends(get_db)):
    """Product count by resistance level (for Pie chart)."""
    repo = DashboardRepository(db)
    data = repo.get_products_by_resistance()
    return [
        ResistanceDistribution(resistance=row['resistance'], product_count=int(row['product_count']))
        for row in data
    ]


@router.get("/analytics/category-growth", response_model=list[CategoryGrowth])
def get_category_growth(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Growth rates by category (for Pivot Table)."""
    repo = DashboardRepository(db)
    data = repo.get_category_growth_rates(start_date, end_date)
    return [
        CategoryGrowth(
            category=row['category'],
            revenue=row['revenue'],
            quantity=int(row['quantity']),
            transactions=int(row['transactions']),
            ca_growth_pct=Decimal(str(row['ca_growth_pct'])),
            quant_growth_pct=Decimal(str(row['quant_growth_pct'])),
            transa_growth_pct=Decimal(str(row['transa_growth_pct'])),
        )
        for row in data
    ]


@router.get("/analytics/quantity-summary", response_model=list[ProductQuantitySummary])
def get_product_quantity_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Quantity sold by product (for Bar chart)."""
    repo = DashboardRepository(db)
    data = repo.get_products_quantity_summary(start_date, end_date)
    return [
        ProductQuantitySummary(
            product_id=int(row['productid']),
            product_name=row['productname'],
            category=row['category'],
            total_quantity=int(row['total_quantity']),
            total_revenue=row['total_revenue'],
        )
        for row in data
    ]
