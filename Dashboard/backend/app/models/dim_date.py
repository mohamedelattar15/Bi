"""Date dimension model."""

from sqlalchemy import Column, Date, Integer, String, Boolean
from app.core.database import Base


class DimDate(Base):
    __tablename__ = "dim_date"

    date_key = Column(Date, primary_key=True)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    month_name = Column(String(20), nullable=False)
    day = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    day_name = Column(String(20), nullable=False)
    week_of_year = Column(Integer, nullable=False)
    is_weekend = Column(Boolean, nullable=False, default=False)
