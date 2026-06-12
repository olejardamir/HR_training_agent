from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import setup_database, teardown_database

client = TestClient(app)


def setup_module():
    setup_database()


def teardown_module():
    teardown_database()


def test_itsm_ticket_idempotent_key_returns_existing_ticket():
    client.post("/onboarding/start/emp_001", json={"correlation_id": "corr_idem_01"})
    sel = client.post("/onboarding/select-access", json={
        "employee_id": "emp_001",
        "selected_systems": ["Slack"],
        "correlation_id": "corr_idem_01",
        "source": "test",
    })
    request_id = sel.json()["request_id"]
    appr = client.post("/mock/approvals", json={
        "employee_id": "emp_001",
        "request_id": request_id,
        "manager_id": "mgr_101",
        "correlation_id": "corr_idem_01",
    })
    approval_id = appr.json()["approval_id"]
    client.post(f"/mock/approvals/{approval_id}/approve", json={
        "decided_by": "mgr_101",
        "decision_reason": "ok",
        "correlation_id": "corr_idem_01",
    })

    resp1 = client.post("/mock/itsm/tickets", json={
        "employee_id": "emp_001",
        "approval_id": approval_id,
        "requested_systems": ["Slack"],
        "requested_by": "test",
        "idempotency_key": "idem_key_01",
        "correlation_id": "corr_idem_01",
    })
    assert resp1.status_code == 200
    ticket_id = resp1.json()["ticket_id"]

    resp2 = client.post("/mock/itsm/tickets", json={
        "employee_id": "emp_001",
        "approval_id": approval_id,
        "requested_systems": ["Slack"],
        "requested_by": "test",
        "idempotency_key": "idem_key_01",
        "correlation_id": "corr_idem_01",
    })
    assert resp2.status_code == 200
    assert resp2.json()["ticket_id"] == ticket_id
    assert resp2.json().get("duplicate") == True
