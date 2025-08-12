from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base, get_db

# shared in-memory DB
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_db
client = TestClient(app)

HEADERS = {"X-Test-Auth": "ok"}

def test_add_browse_read_update_delete_cycle():
    r = client.post("/calculations/", json={"operation":"add","operands":[2,3]}, headers=HEADERS)
    assert r.status_code == 201, r.text

    r = client.get("/calculations/", headers=HEADERS)
    assert r.status_code == 200
    assert isinstance(r.json(), list)

def test_negative_inputs():
    r = client.post("/calculations/", json={"operation":"add","operands":[1]}, headers=HEADERS)
    assert r.status_code in (400, 422)

    r = client.post("/calculations/", json={"operation":"divide","operands":[1,0]}, headers=HEADERS)
    assert r.status_code == 400

    # no headers -> 401
    r = client.get("/calculations/")
    assert r.status_code == 401
