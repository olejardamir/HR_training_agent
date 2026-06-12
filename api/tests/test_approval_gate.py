import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from app.models import Base
from app.seed import reset_and_seed

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup():
    Base.metadata.drop_all(bind=engine)
    reset_and_seed()
    yield
    Base.metadata.drop_all(bind=engine)

def _select_access(employee_id, systems, correlation_id):
    return client.post("/onboarding/select-access", json={
        "employee_id": employee_id,
        "selected_systems": systems,
        "correlation_id": correlation_id,
        "source": "test"
    })

def _create_approval(employee_id, request_id, manager_id, correlation_id):
    return client.post("/mock/approvals", params={
        "employee_id": employee_id,
        "request_id": request_id,
        "manager_id": manager_id,
        "correlation_id": correlation_id
    })

def _approve(approval_id, decided_by, reason, correlation_id):
    return client.post(f"/mock/approvals/{approval_id}/approve", params={
        "decided_by": decided_by,
        "decision_reason": reason,
        "correlation_id": correlation_id
    })

def _create_ticket(employee_id, approval_id, systems, idempotency_key, correlation_id):
    return client.post("/mock/itsm/tickets", json={
        "employee_id": employee_id,
        "approval_id": approval_id,
        "requested_systems": systems,
        "requested_by": "test",
        "idempotency_key": idempotency_key,
        "correlation_id": correlation_id
    })

def test_ticket_blocked_before_approval():
    sel_resp = _select_access("emp_001", ["Salesforce", "Gong"], "corr_ticket_01")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_ticket_01")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    ticket_resp = _create_ticket("emp_001", approval_id, ["Salesforce", "Gong"], "tkt_key_01", "corr_ticket_01")
    assert ticket_resp.status_code == 403
    assert "APPROVAL_NOT_APPROVED" in ticket_resp.json()["detail"]

def test_ticket_created_after_approval():
    sel_resp = _select_access("emp_001", ["Salesforce"], "corr_ticket_02")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_ticket_02")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    approve_resp = _approve(approval_id, "mgr_101", "approved", "corr_ticket_02")
    assert approve_resp.status_code == 200

    ticket_resp = _create_ticket("emp_001", approval_id, ["Salesforce"], "tkt_key_02", "corr_ticket_02")
    assert ticket_resp.status_code == 200
    assert ticket_resp.json()["status"] == "CREATED"
    assert ticket_resp.json()["created"] == True

def test_idempotency_prevents_duplicate():
    sel_resp = _select_access("emp_001", ["Slack", "HR Platform"], "corr_ticket_03")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_ticket_03")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    _approve(approval_id, "mgr_101", "ok", "corr_ticket_03")

    resp1 = _create_ticket("emp_001", approval_id, ["Slack", "HR Platform"], "dup_key_01", "corr_ticket_03")
    assert resp1.status_code == 200
    assert resp1.json()["created"] == True
    ticket_id = resp1.json()["ticket_id"]

    resp2 = _create_ticket("emp_001", approval_id, ["Slack", "HR Platform"], "dup_key_01", "corr_ticket_03")
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "EXISTING"
    assert resp2.json()["ticket_id"] == ticket_id

def test_forbidden_system_blocked():
    resp = _select_access("emp_001", ["Payroll Admin"], "corr_forbid_01")
    assert resp.status_code == 403
    assert "forbidden" in resp.json()["detail"].lower()

def test_rejected_approval_blocks_ticket():
    sel_resp = _select_access("emp_001", ["Gong"], "corr_reject_01")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_reject_01")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    reject_resp = client.post(f"/mock/approvals/{approval_id}/reject", params={
        "decided_by": "mgr_101", "decision_reason": "not needed", "correlation_id": "corr_reject_01"
    })
    assert reject_resp.status_code == 200

    ticket_resp = _create_ticket("emp_001", approval_id, ["Gong"], "tkt_reject_01", "corr_reject_01")
    assert ticket_resp.status_code == 403
    assert "APPROVAL_NOT_APPROVED" in ticket_resp.json()["detail"]

def test_audit_events_created():
    resp = client.get("/audit/events", params={"correlation_id": "corr_ticket_01"})
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) > 0
    assert any(e["action"] == "SELECT_ACCESS" for e in events)
    assert any(e["action"] == "CREATE_APPROVAL" for e in events)
