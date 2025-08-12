from fastapi import FastAPI, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .routers import calculations as calc_router
from . import crud, schemas
from .deps import get_current_user_id

app = FastAPI(title="Calc BREAD App")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Create tables on startup (SQLite)
Base.metadata.create_all(bind=engine)

# API
app.include_router(calc_router.router)

# ---- Minimal login just for demo/testing ----
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(username: str = Form(...)):
    resp = RedirectResponse(url="/", status_code=303)
    resp.set_cookie("x_user", username, httponly=False)
    return resp

# ---- UI pages ----
@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    user = request.cookies.get("x_user")
    if not user:
        return RedirectResponse(url="/login")
    rows = crud.list_calculations(db, user)
    return templates.TemplateResponse("index.html", {"request": request, "user": user, "rows": rows})

# ---- HTMX partial endpoints ----
@app.post("/ui/calculations")
def ui_add_calc(
    request: Request,
    operation: schemas.OperationType = Form(...),
    a: float = Form(...),
    b: float = Form(...),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    obj = crud.create_calculation(db, user_id, schemas.CalculationCreate(operation=operation, operands=[a, b]))
    return templates.TemplateResponse("partials/calc_row.html", {"request": request, "row": obj})

@app.post("/ui/calculations/{calc_id}")
def ui_edit_calc(
    request: Request,
    calc_id: int,
    operation: schemas.OperationType = Form(...),
    a: float = Form(...),
    b: float = Form(...),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    obj = crud.update_calculation(db, user_id, calc_id, schemas.CalculationUpdate(operation=operation, operands=[a, b]))
    if not obj:
        return Response("Not found", status_code=404)
    return templates.TemplateResponse("partials/calc_row.html", {"request": request, "row": obj})

@app.delete("/ui/calculations/{calc_id}")
def ui_delete_calc(
    calc_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    ok = crud.delete_calculation(db, user_id, calc_id)
    return Response(status_code=204 if ok else 404)
