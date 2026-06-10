"""Filters API endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.filters import FilterOptions

router = APIRouter(prefix="/api/filters", tags=["Filters"])


@router.get("/", response_model=FilterOptions)
def get_filter_options(db: Session = Depends(get_db)):
    """Get all available filter options for the dashboard."""
    repo = DashboardRepository(db)
    data = repo.get_filter_options()
    return FilterOptions(**data)
