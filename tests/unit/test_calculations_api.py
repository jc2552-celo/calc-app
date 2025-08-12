import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
HEADERS = {"Cookie": "x_user=tester"}

def test_add_browse_read_update_delete_cycle():
    r = client.post("/calculations/", json={"operation":"add","operands":[2,3]}, headers=HEADERS)
    assert r.status_code == 201, r.text
    created = r.json()

    r = client.get("/calculations/", headers=HEADERS)
    assert r.status_code == 200
    rows = r.json()
    assert any(row["id"] == created["id"] for row in rows)

    r = client.get(f"/calculations/{created['id']}", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["result"] == 5

    r = client.patch(f"/calculations/{created['id']}", json={"operation":"multiply","operands":[3,4]}, headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["result"] == 12

    r = client.delete(f"/calculations/{created['id']}", headers=HEADERS)
    assert r.status_code == 204

    r = client.get(f"/calculations/{created['id']}", headers=HEADERS)
    assert r.status_code == 404

def test_negative_inputs():
    r = client.post("/calculations/", json={"operation":"add","operands":[1]}, headers=HEADERS)
    assert r.status_code in (400, 422)

    r = client.post("/calculations/", json={"operation":"divide","operands":[1,0]}, headers=HEADERS)
    assert r.status_code == 400

    r = client.get("/calculations/")
    assert r.status_code == 401
