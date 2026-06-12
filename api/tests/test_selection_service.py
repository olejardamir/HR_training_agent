from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import setup_database, teardown_database

client = TestClient(app)


def setup_module():
    setup_database()


def teardown_module():
    teardown_database()


def test_onboarding_select_access_no_session_returns_409():
    resp = client.post("/onboarding/select-access", json={
        "employee_id": "emp_001",
        "selected_systems": ["Slack"],
        "correlation_id": "corr_sel_no_session",
        "source": "test",
    })
    assert resp.status_code == 409


def test_onboarding_select_access_valid_returns_request_id():
    client.post("/onboarding/start/emp_001", json={"correlation_id": "corr_sel_01"})
    resp = client.post("/onboarding/select-access", json={
        "employee_id": "emp_001",
        "selected_systems": ["Slack", "Gong"],
        "correlation_id": "corr_sel_01",
        "source": "test",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "request_id" in data
    assert data["request_id"].startswith("req_")


def test_onboarding_select_unknown_system_is_blocked():
    resp = client.post("/onboarding/start/emp_001", json={"correlation_id": "corr_sel_unk"})
    resp = client.post("/onboarding/select-access", json={
        "employee_id": "emp_001",
        "selected_systems": ["TotallyUnknownSystem"],
        "correlation_id": "corr_sel_unk",
        "source": "test",
    })
    assert resp.status_code == 403
    data = resp.json()
    assert data["error_code"] == "UNKNOWN_SYSTEM_SELECTED"
