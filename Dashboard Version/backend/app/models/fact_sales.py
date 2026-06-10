"""Sales fact table model."""

from sqlalchemy import Column, BigInteger, Integer, Numeric, Date, String, ForeignKey
from app.core.database import Base


class FactSales(Base):
    __tablename__ = "fact_sales"

    salesid = Column(BigInteger, primary_key=True)
    employeeid = Column(Integer, ForeignKey("dim_employee.employeeid"), nullable=False)
    customerid = Column(Integer, ForeignKey("dim_customer.customerid"), nullable=False)
    productid = Column(Integer, ForeignKey("dim_product.productid"), nullable=False)
    date = Column(Date, ForeignKey("dim_date.date_key"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    discount = Column(Numeric(10, 2), nullable=False, default=0)
    totalprice = Column(Numeric(14, 2), nullable=False, default=0)
    transactionnumber = Column(String(50))
    time = Column(String(10))
