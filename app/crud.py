from sqlalchemy.orm import Session
from . import models, schemas

def compute_result(operation: schemas.OperationType, operands: list[float]) -> float:
    a, b = operands[0], operands[1]
    if operation == schemas.OperationType.add:
        return a + b
    if operation == schemas.OperationType.subtract:
        return a - b
    if operation == schemas.OperationType.multiply:
        return a * b
    if operation == schemas.OperationType.divide:
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    raise ValueError("Unsupported operation")

def create_calculation(db: Session, user_id: str, data: schemas.CalculationCreate) -> models.Calculation:
    result = compute_result(data.operation, data.operands)
    obj = models.Calculation(user_id=user_id, operation=data.operation, operands=data.operands, result=result)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_calculation(db: Session, user_id: str, calc_id: int) -> models.Calculation | None:
    return db.query(models.Calculation).filter_by(id=calc_id, user_id=user_id).first()

def list_calculations(db: Session, user_id: str) -> list[models.Calculation]:
    return (
        db.query(models.Calculation)
        .filter_by(user_id=user_id)
        .order_by(models.Calculation.created_at.desc())
        .all()
    )

def update_calculation(db: Session, user_id: str, calc_id: int, data: schemas.CalculationUpdate) -> models.Calculation | None:
    obj = get_calculation(db, user_id, calc_id)
    if not obj:
        return None
    if data.operation is not None:
        obj.operation = data.operation
    if data.operands is not None:
        obj.operands = data.operands
    if data.operation is not None or data.operands is not None:
        obj.result = compute_result(obj.operation, obj.operands)
    db.commit()
    db.refresh(obj)
    return obj

def delete_calculation(db: Session, user_id: str, calc_id: int) -> bool:
    obj = get_calculation(db, user_id, calc_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
