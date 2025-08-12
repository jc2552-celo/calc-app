from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from io import StringIO
import csv
from typing import Dict
from app.db import get_db
from app import models, schemas

router = APIRouter(prefix="/reports", tags=["reports"])

def _compute_metrics(db: Session) -> schemas.Metrics:
    total = db.query(models.Calculation).count()
    ops: Dict[str, int] = {}
    first_at = last_at = None

    rows = (
        db.query(models.Calculation.operation, models.Calculation.created_at)
          .order_by(models.Calculation.created_at.asc())
          .all()
    )
    for op, ts in rows:
        ops[op] = ops.get(op, 0) + 1
        if first_at is None: first_at = ts
        last_at = ts

    avg_gap = None
    if total > 1 and first_at and last_at:
        seconds = (last_at - first_at).total_seconds()
        avg_gap = seconds / (total - 1) if seconds >= 0 else None

    return schemas.Metrics(
        total_calculations=total,
        operations_breakdown=ops,
        first_calculation_at=first_at,
        last_calculation_at=last_at,
        average_time_between_seconds=avg_gap,
    )

@router.get("/metrics", response_model=schemas.Metrics)
def get_metrics(db: Session = Depends(get_db)):
    return _compute_metrics(db)

@router.get("/recent", response_model=schemas.RecentCalculations)
def get_recent(limit: int = 10, db: Session = Depends(get_db)):
    items = (
        db.query(models.Calculation)
          .order_by(models.Calculation.created_at.desc())
          .limit(limit)
          .all()
    )
    def coerce(x):
        return schemas.RecentCalculation(
            id=x.id, operation=str(x.operation),
            operand1=float(x.operand1), operand2=float(x.operand2),
            result=float(x.result), created_at=x.created_at,
        )
    return schemas.RecentCalculations(items=[coerce(i) for i in items])

@router.get("/metrics.csv")
def metrics_csv(db: Session = Depends(get_db)):
    m = _compute_metrics(db)
    buf = StringIO(); w = csv.writer(buf)
    w.writerow(["metric", "value"])
    w.writerow(["total_calculations", m.total_calculations])
    w.writerow(["first_calculation_at", m.first_calculation_at or ""])
    w.writerow(["last_calculation_at", m.last_calculation_at or ""])
    w.writerow(["average_time_between_seconds", m.average_time_between_seconds or ""])
    for k, v in m.operations_breakdown.items():
        w.writerow([f"operation:{k}", v])
    return Response(content=buf.getvalue(), media_type="text/csv")
