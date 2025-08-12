from datetime import datetime, timedelta, UTC
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base, get_db

# Shared in-memory DB for this test module
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def seed_once():
    """Seed using the API so we hit the exact same stack and DB connection."""
    # only seed if empty
    r = client.get("/reports/metrics")
    if r.status_code == 200 and r.json().get("total_calculations"):
        return

    payloads = [
        {"operation": "add", "operands": [1, 2]},
        {"operation": "sub", "operands": [3, 1]},
        {"operation": "mul", "operands": [2, 5]},
        {"operation": "add", "operands": [10, 20]},
    ]
    for p in payloads:
        created = client.post("/calculations/", json=p)
        assert created.status_code == 201, created.text

def test_metrics_ok():
    seed_once()
    r = client.get("/reports/metrics")
    assert r.status_code == 200
    data = r.json()
    assert data["total_calculations"] == 4
    assert data["operations_breakdown"]["add"] == 2

def test_recent_ok():
    seed_once()
    r = client.get("/reports/recent?limit=3")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 3
