"""Product analytics API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import ProductDetail, ProductList, PriceDistribution, ProductPerformance

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("/", response_model=list[ProductList])
def get_all_products(db: Session = Depends(get_db)):
    """Get all products with revenue info."""
    service = ProductService(db)
    return service.get_all_products()


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
