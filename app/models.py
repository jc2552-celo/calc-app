from sqlalchemy import Column, Integer, Float, String, DateTime, func
from app.db import Base

class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, nullable=False, index=True)
    operand1 = Column(Float, nullable=False)
    operand2 = Column(Float, nullable=False)
    result   = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
