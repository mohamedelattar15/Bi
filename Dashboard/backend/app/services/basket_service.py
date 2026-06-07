"""Basket analysis service."""

from sqlalchemy.orm import Session
from decimal import Decimal

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.basket import BasketRule, BasketAnalysisResult


class BasketService:
    def __init__(self, db: Session):
        self.repo = DashboardRepository(db)

    def get_basket_analysis(self, min_support: float = 0.01,
                             min_lift: float = 1.5,
                             limit: int = 50) -> BasketAnalysisResult:
        rules_data = self.repo.get_basket_rules(min_support, min_lift, limit)

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

        total_transactions = int(
            self.repo.get_total_transactions()
        )

        return BasketAnalysisResult(
            total_transactions=total_transactions,
            total_products=0,  # would need separate query
            min_support=Decimal(str(min_support)),
            min_lift=Decimal(str(min_lift)),
            rules=rules,
            top_rules_by_lift=top_rules,
            matrix_data=matrix_data,
        )
