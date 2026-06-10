"""Utility helper functions."""

from decimal import Decimal
from datetime import date, datetime
from typing import Any


def decimal_to_float(value: Any) -> float:
    """Convert Decimal to float safely."""
    if isinstance(value, Decimal):
        return float(value)
    return value


def serialize_datetime(obj: Any) -> Any:
    """Serialize datetime/date objects to ISO string."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj


def format_currency(value: Decimal, currency: str = "€") -> str:
    """Format a Decimal as a currency string."""
    return f"{currency}{value:,.2f}"


def format_percentage(value: Decimal, decimals: int = 2) -> str:
    """Format a Decimal as a percentage string."""
    return f"{value:,.{decimals}f}%"
