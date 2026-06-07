"""Product analytics schemas."""

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class ProductDetail(BaseModel):
    """Detailed product information."""

    product_id: int
    product_name: str
    price: Decimal
    category: str
    class_: Optional[str] = None
    resistant: Optional[str] = None
    is_allergic: Optional[str] = None
    vitality_days: Optional[Decimal] = None
    total_revenue: Decimal
    total_quantity: int
    times_sold: int
    unique_customers: int


class ProductList(BaseModel):
    """Product list item."""

    product_id: int
    product_name: str
    price: Decimal
    category: str
    total_revenue: Decimal
    total_quantity: int
    revenue_rank: int


class PriceDistribution(BaseModel):
    """Price distribution bucket."""

    range_label: str  # e.g. "0-10€", "10-20€"
    min_price: Decimal
    max_price: Decimal
    product_count: int
    total_revenue: Decimal
    percentage: Optional[Decimal] = None


class ProductPerformance(BaseModel):
    """Product price vs volume analysis."""

    product_id: int
    product_name: str
    price: Decimal
    total_quantity: int
    total_revenue: Decimal
    category: str
