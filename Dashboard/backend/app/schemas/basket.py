"""Basket analysis schemas."""

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class BasketRule(BaseModel):
    """Association rule between two products."""

    product1: str
    product2: str
    basket_label: str  # "Product1 - Product2"
    support: Decimal
    confidence_p1: Decimal
    confidence_p2: Decimal
    lift: Decimal


class BasketAnalysisResult(BaseModel):
    """Basket analysis result with metadata."""

    total_transactions: int
    total_products: int
    min_support: Decimal = Decimal("0.01")
    min_lift: Decimal = Decimal("1.5")
    rules: list[BasketRule]
    top_rules_by_lift: list[BasketRule]
    matrix_data: list[dict]  # For Support vs Lift scatter plot
