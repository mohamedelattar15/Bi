"""Customer dimension model."""

from sqlalchemy import Column, Integer, String
from app.core.database import Base


class DimCustomer(Base):
    __tablename__ = "dim_customer"

    customerid = Column(Integer, primary_key=True)
    customerfirstname = Column(String(100))
    middleinitial = Column(String(1))
    customerlastname = Column(String(100))
    address = Column(String(200))
    cityid = Column(Integer)
    city = Column(String(100))
    zipcode = Column(String(20))
    countryid = Column(Integer)
    country = Column(String(100))
    countrycode = Column(String(2))
