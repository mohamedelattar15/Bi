"""Category dimension model."""

from sqlalchemy import Column, Integer, String
from app.core.database import Base


class DimCategory(Base):
    __tablename__ = "dim_category"

    categoryid = Column(Integer, primary_key=True)
    categoryname = Column(String(100), nullable=False)
