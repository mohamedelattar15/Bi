"""Filter and common schemas."""

from pydantic import BaseModel
from typing import Optional
from datetime import date


class DateRange(BaseModel):
    """Date range filter."""

    start_date: Optional[date] = None
    end_date: Optional[date] = None


class FilterOptions(BaseModel):
    """Available filter options for the dashboard."""

    categories: list[str]
    countries: list[str]
    cities: list[str]
    employees: list[str]
    date_range: tuple[Optional[date], Optional[date]]
    products: list[str]
    customer_segments: list[str]
    age_groups: list[str]
    seniority_groups: list[str]
