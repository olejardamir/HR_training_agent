from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import setup_database, teardown_database
from app import logic

client = TestClient(app)

ALLOWED_PII_KEYS = {
    "employee_id", "role", "level", "department", "manager_id",
    "request_id", "approval_id", "ticket_id", "selected_systems",
    "reason_codes", "status", "error_code", "policy_version",
    "peer_count", "correlation_id",
}

BLOCKED_PII_KEYS = {
    "phone_number", "home_address", "birth_date", "government_id",
    "ssn", "passport", "full_email_body", "secret", "token",
    "raw_prompt", "password", "api_key",
}


def setup_module():
    setup_database()


def teardown_module():
    teardown_database()


def test_audit_events_no_blocked_pii_in_audit():
    client.post("/onboarding/start/emp_001", json={"correlation_id": "corr_pii_test"})
    resp = client.get("/audit/events", params={"correlation_id": "corr_pii_test"})
    assert resp.status_code == 200
    data = resp.json()
    body = str(data).lower()
    for blocked in BLOCKED_PII_KEYS:
        assert blocked not in body, f"Found blocked PII key: {blocked}"
