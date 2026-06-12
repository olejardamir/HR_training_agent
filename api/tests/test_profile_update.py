from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import setup_database, teardown_database

client = TestClient(app)


def setup_module():
    setup_database()


def teardown_module():
    teardown_database()


def test_salesforce_profile_get_valid_returns_profile():
    resp = client.get("/mock/salesforce/profile/emp_001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["employee_id"] == "emp_001"


def test_salesforce_profile_patch_valid_returns_updated():
    resp = client.patch("/mock/salesforce/profile/emp_001", json={
        "role_profile": "Enterprise Account Executive",
        "salesforce_profile_complete": True,
        "correlation_id": "corr_sf_01",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] == True
    assert data["setup_status"] == "completed"


def test_salesforce_profile_patch_unknown_returns_404():
    resp = client.patch("/mock/salesforce/profile/emp_999", json={
        "correlation_id": "corr_sf_02",
    })
    assert resp.status_code == 404
