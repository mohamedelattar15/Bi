"""Product dimension model."""

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from app.core.database import Base


class DimProduct(Base):
    __tablename__ = "dim_product"

    productid = Column(Integer, primary_key=True)
    productname = Column(String(200), nullable=False)
    price = Column(Numeric(12, 2), nullable=False, default=0)
    categoryid = Column(Integer, ForeignKey("dim_category.categoryid"), nullable=False)
    class_ = Column("class", String(50))
    modifydate = Column(Date)
    resistant = Column(String(50))
    isallergic = Column(String(10))
    vitalitydays = Column(Numeric(8, 2))
    categoryname = Column(String(100))
