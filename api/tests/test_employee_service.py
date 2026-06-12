from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import setup_database, teardown_database

client = TestClient(app)


def setup_module():
    setup_database()


def teardown_module():
    teardown_database()


def test_hr_profile_patch_valid_update_returns_updated():
    resp = client.patch("/mock/hr/employees/emp_001/profile", json={
        "preferred_name": "Alex",
        "correlation_id": "corr_hr_01",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] == True
    assert data["status"] == "UPDATED"


def test_hr_profile_patch_unknown_employee_returns_404():
    resp = client.patch("/mock/hr/employees/emp_999/profile", json={
        "preferred_name": "Ghost",
        "correlation_id": "corr_hr_02",
    })
    assert resp.status_code == 404


def test_hr_profile_get_valid_employee_returns_profile():
    resp = client.get("/mock/hr/employees/emp_001/profile")
    assert resp.status_code == 200
    data = resp.json()
    assert data["employee_id"] == "emp_001"


def test_hr_profile_patch_ignores_role_level_manager_changes():
    resp = client.patch("/mock/hr/employees/emp_001/profile", json={
        "correlation_id": "corr_hr_03",
        "role": "CEO", "level": "L5", "manager_id": "mgr_999",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] == True
    assert data["profile_status"]["hr_profile_complete"] == True


def test_hr_manager_lookup_valid_returns_manager():
    resp = client.get("/mock/hr/managers/mgr_101")
    assert resp.status_code == 200
    data = resp.json()
    assert data["manager_id"] == "mgr_101"
    assert data["is_active"] == True


def test_hr_manager_lookup_unknown_returns_404():
    resp = client.get("/mock/hr/managers/mgr_999")
    assert resp.status_code == 404
