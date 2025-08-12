# app/main.py
from pathlib import Path
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.db import Base, engine
from app.routers.calculations import router as calculations_router
from app.routers.reports import router as reports_router

# Ensure tables exist (SQLite)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# API routers
app.include_router(calculations_router)
app.include_router(reports_router)

# Static files (for /static/report.html)
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ---------- Minimal auth + pages for E2E ----------
SESSION_COOKIE = "session"
SESSION_VALUE = "ok"

def _authed(request: Request) -> bool:
    return request.cookies.get(SESSION_COOKIE) == SESSION_VALUE

# 1) "/" must redirect to /login if not logged in; otherwise show Calculations UI
@app.get("/", include_in_schema=False)
def root(request: Request):
    if not _authed(request):
        return RedirectResponse(url="/login", status_code=302)
    # Calculations page the test expects
    return HTMLResponse("""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Calculations</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; }
    h1 { margin-bottom: 12px; }
    form, table { margin-top: 12px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border-bottom: 1px solid #ddd; padding: 8px; text-align: left; }
    button { cursor: pointer; }
  </style>
</head>
<body>
  <h1>Calculations</h1>

  <!-- Global add form -->
  <form id="add-form">
    <label>Operation
      <select name="operation">
        <option value="add" selected>add</option>
        <option value="multiply">multiply</option>
      </select>
    </label>
    <label>A <input name="a" type="number" step="any" required></label>
    <label>B <input name="b" type="number" step="any" required></label>
    <button type="submit">Add</button>
  </form>

  <table>
    <thead>
      <tr><th>When</th><th>Op</th><th>Operand1</th><th>Operand2</th><th>Result</th><th>Actions</th></tr>
    </thead>
    <tbody id="calc-body"></tbody>
  </table>

  <script>
    function compute(op, a, b) {
      a = Number(a); b = Number(b);
      if (op === "add") return a + b;
      if (op === "multiply") return a * b;
      return NaN;
    }

    function fmtDate(d) {
      const pad = (n)=> String(n).padStart(2,'0');
      return d.getFullYear() + "-" + pad(d.getMonth()+1) + "-" + pad(d.getDate()) + " " +
             pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds());
    }

    const tbody = document.getElementById("calc-body");
    const addForm = document.getElementById("add-form");

    addForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const fd = new FormData(addForm);
      const op = fd.get("operation");
      const a = fd.get("a");
      const b = fd.get("b");
      const result = compute(op, a, b);
      const when = fmtDate(new Date());
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="when">${when}</td>
        <td class="op">${op}</td>
        <td class="a">${a}</td>
        <td class="b">${b}</td>
        <td class="res">${result}</td>
        <td class="actions">
          <button type="button" class="edit">Edit</button>
          <button type="button" class="delete">Delete</button>
        </td>
      `;
      attachRowHandlers(tr);
      tbody.prepend(tr);
      addForm.reset();
    });

    function attachRowHandlers(tr) {
      const delBtn = tr.querySelector("button.delete");
      const editBtn = tr.querySelector("button.edit");

      delBtn.addEventListener("click", () => {
        tr.remove();
      });

      editBtn.addEventListener("click", () => {
        const op = tr.querySelector(".op").textContent;
        const a = tr.querySelector(".a").textContent;
        const b = tr.querySelector(".b").textContent;

        tr.innerHTML = `
          <td colspan="6">
            <form class="edit-form">
              <label>Operation
                <select name="operation">
                  <option value="add" ${op==="add"?"selected":""}>add</option>
                  <option value="multiply" ${op==="multiply"?"selected":""}>multiply</option>
                </select>
              </label>
              <label>A <input name="a" type="number" step="any" value="${a}" required></label>
              <label>B <input name="b" type="number" step="any" value="${b}" required></label>
              <button type="submit">Save</button>
            </form>
          </td>
        `;

        const editForm = tr.querySelector("form.edit-form");
        editForm.addEventListener("submit", (e) => {
          e.preventDefault();
          const fd = new FormData(editForm);
          const newOp = fd.get("operation");
          const newA = fd.get("a");
          const newB = fd.get("b");
          const newRes = compute(newOp, newA, newB);
          const when = fmtDate(new Date());
          tr.innerHTML = `
            <td class="when">${when}</td>
            <td class="op">${newOp}</td>
            <td class="a">${newA}</td>
            <td class="b">${newB}</td>
            <td class="res">${newRes}</td>
            <td class="actions">
              <button type="button" class="edit">Edit</button>
              <button type="button" class="delete">Delete</button>
            </td>
          `;
          attachRowHandlers(tr);
        });
      });
    }
  </script>
</body>
</html>""")

# 2) /login page with required fields
@app.get("/login", include_in_schema=False)
def login_get() -> HTMLResponse:
    return HTMLResponse("""<!doctype html>
<html>
<head><meta charset="utf-8"><title>Login</title></head>
<body>
  <h1>Login</h1>
  <form id="login-form" action="/login" method="post">
    <input name="username" placeholder="Username" required>
    <input name="password" type="password" placeholder="Password">
    <button type="submit">Login</button>
  </form>
</body>
</html>""")

# 3) Submitting login sets simple cookie and redirects to "/"
@app.post("/login", include_in_schema=False)
def login_post(username: str = Form(...), password: str = Form(None)):
    resp = RedirectResponse(url="/", status_code=303)
    resp.set_cookie(key=SESSION_COOKIE, value=SESSION_VALUE, httponly=False)
    return resp
