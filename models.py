from sqlalchemy import Column, Integer, String, Float
from database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, index=True)
    
    annual_income = Column(Float)
    loan_amount = Column(Float)
    credit_score = Column(Integer)
    employment_status = Column(Integer)
    housing_status = Column(Integer)
    loan_term = Column(Integer)
    
    status = Column(String) # Approved, Rejected, Error
    confidence = Column(Float) # Percentage 0-100
    remarks = Column(String)
