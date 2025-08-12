from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

# ===== Reports =====
class Metrics(BaseModel):
    total_calculations: int
    operations_breakdown: Dict[str, int]
    first_calculation_at: Optional[datetime] = None
    last_calculation_at: Optional[datetime] = None
    average_time_between_seconds: Optional[float] = None

class RecentCalculation(BaseModel):
    id: int
    operation: str
    operand1: float
    operand2: float
    result: float
    created_at: datetime

class RecentCalculations(BaseModel):
    items: List[RecentCalculation]

# ===== Calculations API =====
class CalculationCreate(BaseModel):
    operation: str
    # exactly two numbers required (works across Pydantic versions)
    operands: list[float] = Field(min_length=2, max_length=2)

class CalculationRead(BaseModel):
    id: int
    operation: str
    operand1: float
    operand2: float
    result: float

    class Config:
        from_attributes = True
