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


class HubProduct(BaseModel):
    """Product with its association connection count."""

    product: str
    connection_count: int


class LiftDistribution(BaseModel):
    """Lift value distribution bucket."""

    range_label: str
    rule_count: int
    percentage: Decimal


class ProductMatch(BaseModel):
    """A product matched with another product."""

    hub_product: str
    total_connections: int
    matched_product: str
    lift: Decimal
    support: Decimal
    nb_transactions: int


class CategoryAffinity(BaseModel):
    """Category-to-category affinity."""

    category1: str
    category2: str
    pair_count: int
    avg_lift: Decimal


class BasketAnalysisResult(BaseModel):
    """Basket analysis result with metadata."""

    total_transactions: int
    total_products: int
    min_support: Decimal = Decimal("0.000001")
    min_lift: Decimal = Decimal("0.0")
    rules: list[BasketRule]
    top_rules_by_lift: list[BasketRule]
    matrix_data: list[dict]  # For Support vs Lift scatter plot
    hub_products: list[HubProduct] = []
    lift_distribution: list[LiftDistribution] = []
    top_matches: list[ProductMatch] = []
    category_affinities: list[CategoryAffinity] = []
