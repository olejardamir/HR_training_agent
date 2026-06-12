from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import setup_database, teardown_database

client = TestClient(app)


def setup_module():
    setup_database()


def teardown_module():
    teardown_database()


def test_itsm_ticket_full_lifecycle_from_start_to_ticket():
    cid = "corr_itsm_life"
    client.post(f"/onboarding/start/emp_001", json={"correlation_id": cid})
    sel = client.post("/onboarding/select-access", json={
        "employee_id": "emp_001",
        "selected_systems": ["Slack"],
        "correlation_id": cid,
        "source": "test",
    })
    request_id = sel.json()["request_id"]

    appr = client.post("/mock/approvals", json={
        "employee_id": "emp_001",
        "request_id": request_id,
        "manager_id": "mgr_101",
        "correlation_id": cid,
    })
    approval_id = appr.json()["approval_id"]

    client.post(f"/mock/approvals/{approval_id}/approve", json={
        "decided_by": "mgr_101",
        "decision_reason": "approved",
        "correlation_id": cid,
    })

    ticket = client.post("/mock/itsm/tickets", json={
        "employee_id": "emp_001",
        "approval_id": approval_id,
        "requested_systems": ["Slack"],
        "requested_by": "test",
        "idempotency_key": "lifecycle_key",
        "correlation_id": cid,
    })
    assert ticket.status_code == 200
    data = ticket.json()
    assert data["ticket_id"].startswith("itsm_")
    assert data["status"] == "CREATED"
    assert data["ticket_created"] == True
