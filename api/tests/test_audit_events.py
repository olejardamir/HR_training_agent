from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import setup_database, teardown_database

client = TestClient(app)


def setup_module():
    setup_database()


def teardown_module():
    teardown_database()


def test_audit_events_by_employee_returns_events():
    resp = client.get("/audit/events", params={"employee_id": "emp_001", "limit": 10})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] == True
    assert "events" in data
    assert "count" in data


def test_audit_events_unknown_employee_returns_empty():
    resp = client.get("/audit/events", params={"employee_id": "emp_999"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 0
    assert data["events"] == []


def test_audit_events_no_filters_returns_all_events():
    resp = client.get("/audit/events")
    assert resp.status_code == 200
    assert resp.json()["ok"] == True
