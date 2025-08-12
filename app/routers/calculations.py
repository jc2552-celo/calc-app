from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db
from ..deps import get_current_user_id
from .. import crud, schemas

router = APIRouter(prefix="/calculations", tags=["calculations"])

# Browse
@router.get("/", response_model=list[schemas.CalculationOut])
def browse_calculations(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return crud.list_calculations(db, user_id)

# Read
@router.get("/{calc_id}", response_model=schemas.CalculationOut)
def read_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    obj = crud.get_calculation(db, user_id, calc_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return obj

# Add
@router.post("/", response_model=schemas.CalculationOut, status_code=status.HTTP_201_CREATED)
def add_calculation(
    body: schemas.CalculationCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return crud.create_calculation(db, user_id, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Edit (PUT/PATCH)
@router.put("/{calc_id}", response_model=schemas.CalculationOut)
@router.patch("/{calc_id}", response_model=schemas.CalculationOut)
def edit_calculation(
    calc_id: int,
    body: schemas.CalculationUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        obj = crud.update_calculation(db, user_id, calc_id, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj

# Delete
@router.delete("/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    ok = crud.delete_calculation(db, user_id, calc_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return
