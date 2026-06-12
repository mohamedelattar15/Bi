"""Basket analysis service."""

from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from typing import Optional

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.basket import BasketRule, HubProduct, LiftDistribution, ProductMatch, CategoryAffinity, BasketAnalysisResult


class BasketService:
    def __init__(self, db: Session):
        self.repo = DashboardRepository(db)

    def get_basket_analysis(self, min_support: float = 0.000001,
                             min_lift: float = 0.0,
                             limit: int = 50,
                             start_date: Optional[date] = None,
                             end_date: Optional[date] = None) -> BasketAnalysisResult:
        rules_data = self.repo.get_basket_rules(min_support, min_lift, limit,
                                                 start_date, end_date)

        rules = [
            BasketRule(
                product1=row['product1'],
                product2=row['product2'],
                basket_label=row['basket_label'],
                support=Decimal(str(row['support'])),
                confidence_p1=Decimal(str(row['confidence_p1'])),
                confidence_p2=Decimal(str(row['confidence_p2'])),
                lift=Decimal(str(row['lift'])),
            )
            for row in rules_data
        ]

        # Top 10 rules by lift
        top_rules = sorted(rules, key=lambda r: r.lift, reverse=True)[:10]

        # Matrix data for scatter plot
        matrix_data = [
            {"support": float(r.support), "lift": float(r.lift), "label": r.basket_label}
            for r in rules
        ]

        total_baskets = self.repo.get_basket_total_baskets(start_date, end_date)
        total_products = self.repo.get_basket_total_products()

        # Hub products
        hub_data = self.repo.get_basket_hub_products(10)
        hub_products = [
            HubProduct(product=row['product'], connection_count=row['connection_count'])
            for row in hub_data
        ]

        # Lift distribution
        lift_dist_data = self.repo.get_basket_lift_distribution()
        lift_distribution = [
            LiftDistribution(
                range_label=row['range_label'],
                rule_count=row['rule_count'],
                percentage=Decimal(str(row['percentage'])),
            )
            for row in lift_dist_data
        ]

        # Top matches
        top_matches_data = self.repo.get_basket_top_matches(5)
        top_matches = [
            ProductMatch(
                hub_product=row['hub_product'],
                total_connections=row['total_connections'],
                matched_product=row['matched_product'],
                lift=Decimal(str(row['lift'])),
                support=Decimal(str(row['support'])),
                nb_transactions=row['nb_transactions'],
            )
            for row in top_matches_data
        ]

        # Category affinities
        cat_data = self.repo.get_basket_category_affinities(15)
        category_affinities = [
            CategoryAffinity(
                category1=row['category1'],
                category2=row['category2'],
                pair_count=row['pair_count'],
                avg_lift=Decimal(str(row['avg_lift'])),
            )
            for row in cat_data
        ]

        return BasketAnalysisResult(
            total_transactions=total_baskets,
            total_products=total_products,
            min_support=Decimal(str(min_support)),
            min_lift=Decimal(str(min_lift)),
            rules=rules,
            top_rules_by_lift=top_rules,
            matrix_data=matrix_data,
            hub_products=hub_products,
            lift_distribution=lift_distribution,
            top_matches=top_matches,
            category_affinities=category_affinities,
        )
