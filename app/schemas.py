from pydantic import BaseModel, field_validator
from typing import List, Optional
from enum import Enum

class OperationType(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"

class CalculationBase(BaseModel):
    operation: OperationType
    operands: List[float]

    @field_validator("operands")
    @classmethod
    def check_operands(cls, v):
        if len(v) < 2:
            raise ValueError("Provide at least two operands")
        return v

class CalculationCreate(CalculationBase):
    pass

class CalculationUpdate(BaseModel):
    operation: Optional[OperationType] = None
    operands: Optional[List[float]] = None

class CalculationOut(CalculationBase):
    id: int
    result: Optional[float]
    user_id: str

    class Config:
        from_attributes = True
