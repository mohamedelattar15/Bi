"""Customer analytics schemas."""

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import date


class CustomerDetail(BaseModel):
    """Detailed customer information."""

    customer_id: int
    full_name: str
    city: Optional[str] = None
    country: Optional[str] = None
    total_spent: Decimal
    total_transactions: int
    total_quantity: int
    avg_transaction_value: Decimal
    unique_products: int
    first_purchase: Optional[date] = None
    last_purchase: Optional[date] = None
    segment: Optional[str] = None


class CustomerSegment(BaseModel):
    """Customer segment data."""

    segment: str  # VIP, Regular, Occasional, New
    customer_count: int
    total_revenue: Decimal
    avg_basket: Decimal
    percentage: Optional[Decimal] = None


class TopCustomer(BaseModel):
    """Top customer entry."""

    rank: int
    customer_id: int
    full_name: str
    city: str
    country: str
    total_spent: Decimal
    total_transactions: int
    segment: str


class CustomerActivity(BaseModel):
    """Customer activity over time."""

    month: str
    year: int
    active_customers: int
    new_customers: int
    total_revenue: Decimal
