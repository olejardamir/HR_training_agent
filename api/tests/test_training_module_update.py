from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import setup_database, teardown_database

client = TestClient(app)


def setup_module():
    setup_database()


def teardown_module():
    teardown_database()


def test_training_status_get_valid_returns_modules():
    resp = client.get("/mock/training/status/emp_001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["employee_id"] == "emp_001"
    assert "modules" in data


def test_training_module_update_valid_returns_updated():
    resp = client.patch("/mock/training/status/emp_001/modules/T2", json={
        "status": "complete",
        "correlation_id": "corr_tr_01",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] == True


def test_training_module_update_unknown_module_returns_400():
    resp = client.patch("/mock/training/status/emp_001/modules/T5", json={
        "status": "complete",
        "correlation_id": "corr_tr_02",
    })
    assert resp.status_code == 400
