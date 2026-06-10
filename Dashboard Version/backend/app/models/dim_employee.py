"""Employee dimension model."""

from sqlalchemy import Column, Integer, String, Date
from app.core.database import Base


class DimEmployee(Base):
    __tablename__ = "dim_employee"

    employeeid = Column(Integer, primary_key=True)
    employeefirstname = Column(String(100))
    employeelastname = Column(String(100))
    birthdate = Column(Date)
    gender = Column(String(20))
    hiredate = Column(Date)
    city = Column(String(100))
    cityid = Column(Integer)
