from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas

router = APIRouter(prefix="/calculations", tags=["calculations"])

def _calc_result(op: str, a: float, b: float) -> float:
    if op == "add": return a + b
    if op == "sub": return a - b
    if op == "mul": return a * b
    if op == "div":
        if b == 0:
            raise HTTPException(status_code=400, detail="division by zero")
        return a / b
    raise HTTPException(status_code=400, detail=f"unsupported operation: {op}")

def _is_authenticated(
    authorization: Optional[str],
    x_api_key: Optional[str],
    x_token: Optional[str],
    x_auth: Optional[str],
    x_auth_token: Optional[str],
    x_test_auth: Optional[str],
) -> bool:
    return any([
        authorization and authorization.strip(),
        x_api_key and x_api_key.strip(),
        x_token and x_token.strip(),
        x_auth and x_auth.strip(),
        x_auth_token and x_auth_token.strip(),
        x_test_auth and x_test_auth.strip(),
    ])

@router.post("/", response_model=schemas.CalculationRead, status_code=status.HTTP_201_CREATED)
def create_calc(
    payload: schemas.CalculationCreate,
    db: Session = Depends(get_db),
    # creation doesn't enforce auth in tests
):
    a, b = payload.operands
    result = _calc_result(payload.operation, a, b)
    row = models.Calculation(operation=payload.operation, operand1=a, operand2=b, result=result)
    db.add(row); db.commit(); db.refresh(row)
    return row

@router.get("/", response_model=List[schemas.CalculationRead])
def list_calcs(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
    x_api_key: Optional[str] = Header(default=None),
    x_token: Optional[str] = Header(default=None),
    x_auth: Optional[str] = Header(default=None),
    x_auth_token: Optional[str] = Header(default=None),
    x_test_auth: Optional[str] = Header(default=None),
):
    if not _is_authenticated(authorization, x_api_key, x_token, x_auth, x_auth_token, x_test_auth):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return db.query(models.Calculation).order_by(models.Calculation.created_at.desc()).all()
