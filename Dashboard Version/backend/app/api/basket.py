"""Basket analysis API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.services.basket_service import BasketService
from app.schemas.basket import BasketAnalysisResult

router = APIRouter(prefix="/api/basket", tags=["Basket Analysis"])


@router.get("/analysis", response_model=BasketAnalysisResult)
def get_basket_analysis(
    min_support: float = Query(0.000001, ge=0.0, le=1.0, description="Minimum support threshold"),
    min_lift: float = Query(0.0, ge=0.0, description="Minimum lift threshold"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of rules"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
):
    """Get basket (market basket) analysis with association rules."""
    service = BasketService(db)
    return service.get_basket_analysis(min_support, min_lift, limit, start_date, end_date)
