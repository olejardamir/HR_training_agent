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

def _start_onboarding(employee_id, correlation_id):
    return client.post(f"/onboarding/start/{employee_id}", json={
        "correlation_id": correlation_id,
    })

def _select_access(employee_id, systems, correlation_id):
    return client.post("/onboarding/select-access", json={
        "employee_id": employee_id,
        "selected_systems": systems,
        "correlation_id": correlation_id,
        "source": "test",
    })

def _create_approval(employee_id, request_id, manager_id, correlation_id):
    return client.post("/mock/approvals", json={
        "employee_id": employee_id,
        "request_id": str(request_id),
        "manager_id": manager_id,
        "correlation_id": correlation_id,
    })

def _approve(approval_id, decided_by, reason, correlation_id):
    return client.post(f"/mock/approvals/{approval_id}/approve", json={
        "decided_by": decided_by,
        "decision_reason": reason,
        "correlation_id": correlation_id,
    })

def _reject(approval_id, decided_by, reason, correlation_id):
    return client.post(f"/mock/approvals/{approval_id}/reject", json={
        "decided_by": decided_by,
        "decision_reason": reason,
        "correlation_id": correlation_id,
    })

def _create_ticket(employee_id, approval_id, systems, idempotency_key, correlation_id):
    return client.post("/mock/itsm/tickets", json={
        "employee_id": employee_id,
        "approval_id": approval_id,
        "requested_systems": systems,
        "requested_by": "test",
        "idempotency_key": idempotency_key,
        "correlation_id": correlation_id,
    })

def test_itsm_ticket_mock_failure_returns_503_recoverable():
    _start_onboarding("emp_001", "corr_itsm_fail_01")
    sel_resp = _select_access("emp_001", ["Salesforce"], "corr_itsm_fail_01")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_itsm_fail_01")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    approve_resp = _approve(approval_id, "mgr_101", "approved", "corr_itsm_fail_01")
    assert approve_resp.status_code == 200

    ticket_resp = client.post("/mock/itsm/tickets", json={
        "employee_id": "emp_001",
        "approval_id": approval_id,
        "requested_systems": ["Salesforce"],
        "requested_by": "test",
        "idempotency_key": "itsm_fail_key_01",
        "correlation_id": "corr_itsm_fail_01",
        "simulate_failure": True,
    })
    assert ticket_resp.status_code == 503
    data = ticket_resp.json()
    assert data.get("ok") is False
    assert data.get("status") == "FAILED"
    assert data.get("ticket_created") is False
    assert data.get("recoverable") is True
    assert data.get("next_action") == "RETRY_ITSM_TICKET"

    # Verify no ITSMTicket row was created
    from app.database import SessionLocal
    from app.models import ITSMTicket
    db = SessionLocal()
    try:
        count = db.query(ITSMTicket).filter(
            ITSMTicket.idempotency_key == "itsm_fail_key_01"
        ).count()
        assert count == 0, f"Expected no ticket row for failed attempt, found {count}"
    finally:
        db.close()

    # Verify audit event logged
    audit_resp = client.get("/audit/events?correlation_id=corr_itsm_fail_01")
    assert audit_resp.status_code == 200
    events = audit_resp.json().get("events", [])
    failed_events = [e for e in events if e.get("action") == "itsm_ticket_failed"]
    assert len(failed_events) >= 1, "Expected itsm_ticket_failed audit event"


def test_itsm_ticket_blocked_before_approval_returns_409_with_blocked():
    _start_onboarding("emp_001", "corr_ticket_01")
    sel_resp = _select_access("emp_001", ["Salesforce", "Gong"], "corr_ticket_01")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_ticket_01")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    ticket_resp = _create_ticket("emp_001", approval_id, ["Salesforce", "Gong"],
                                 "tkt_key_01", "corr_ticket_01")
    assert ticket_resp.status_code == 409
    assert ticket_resp.json()["ticket_created"] == False
    assert ticket_resp.json()["pre_approval_blocked"] == True

def test_itsm_ticket_created_after_approval_returns_created():
    _start_onboarding("emp_001", "corr_ticket_02")
    sel_resp = _select_access("emp_001", ["Salesforce"], "corr_ticket_02")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_ticket_02")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    approve_resp = _approve(approval_id, "mgr_101", "approved", "corr_ticket_02")
    assert approve_resp.status_code == 200

    ticket_resp = _create_ticket("emp_001", approval_id, ["Salesforce"],
                                 "tkt_key_02", "corr_ticket_02")
    assert ticket_resp.status_code == 200
    data = ticket_resp.json()
    assert data["status"] == "CREATED"
    assert data["ticket_created"] == True

def test_itsm_ticket_idempotent_request_returns_duplicate():
    _start_onboarding("emp_001", "corr_ticket_03")
    sel_resp = _select_access("emp_001", ["Slack", "HR Platform"], "corr_ticket_03")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_ticket_03")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    _approve(approval_id, "mgr_101", "ok", "corr_ticket_03")

    resp1 = _create_ticket("emp_001", approval_id, ["Slack", "HR Platform"],
                           "dup_key_01", "corr_ticket_03")
    assert resp1.status_code == 200
    assert resp1.json()["ticket_created"] == True
    ticket_id = resp1.json()["ticket_id"]

    resp2 = _create_ticket("emp_001", approval_id, ["Slack", "HR Platform"],
                           "dup_key_01", "corr_ticket_03")
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "CREATED"
    assert resp2.json()["ticket_id"] == ticket_id
    assert resp2.json().get("duplicate") == True

def test_access_selection_forbidden_system_returns_403():
    _start_onboarding("emp_001", "corr_forbid_01")
    resp = _select_access("emp_001", ["Payroll Admin"], "corr_forbid_01")
    assert resp.status_code == 403
    assert "forbidden" in resp.text.lower()

def test_itsm_ticket_rejected_approval_blocks_ticket():
    _start_onboarding("emp_001", "corr_reject_01")
    sel_resp = _select_access("emp_001", ["Gong"], "corr_reject_01")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_reject_01")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    reject_resp = _reject(approval_id, "mgr_101", "not needed", "corr_reject_01")
    assert reject_resp.status_code == 200

    ticket_resp = _create_ticket("emp_001", approval_id, ["Gong"],
                                 "tkt_reject_01", "corr_reject_01")
    assert ticket_resp.status_code == 409
    assert ticket_resp.json()["ticket_created"] == False

def test_itsm_ticket_employee_mismatch_returns_409_on_block():
    _start_onboarding("emp_001", "corr_mismatch_emp")
    sel_resp = _select_access("emp_001", ["Salesforce"], "corr_mismatch_emp")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_mismatch_emp")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    _approve(approval_id, "mgr_101", "ok", "corr_mismatch_emp")

    ticket_resp = _create_ticket("emp_002", approval_id, ["Salesforce"],
                                 "mismatch_emp_key", "corr_mismatch_emp")
    assert ticket_resp.status_code == 409
    assert ticket_resp.json()["ticket_created"] == False


def test_itsm_ticket_subset_systems_blocks_with_409():
    _start_onboarding("emp_001", "corr_subset")
    sel_resp = _select_access("emp_001", ["Salesforce", "Gong"], "corr_subset")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_subset")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    _approve(approval_id, "mgr_101", "ok", "corr_subset")

    ticket_resp = _create_ticket("emp_001", approval_id, ["Salesforce"],
                                 "subset_key", "corr_subset")
    assert ticket_resp.status_code == 409
    assert ticket_resp.json()["ticket_created"] == False


def test_itsm_ticket_forbidden_system_blocks_with_409():
    _start_onboarding("emp_001", "corr_forbid_ticket")
    sel_resp = _select_access("emp_001", ["Salesforce"], "corr_forbid_ticket")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_forbid_ticket")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    _approve(approval_id, "mgr_101", "ok", "corr_forbid_ticket")

    ticket_resp = _create_ticket("emp_001", approval_id, ["Payroll Admin"],
                                 "forbid_ticket_key", "corr_forbid_ticket")
    assert ticket_resp.status_code == 409
    assert ticket_resp.json()["ticket_created"] == False


def test_itsm_ticket_idempotency_key_from_different_context_blocks_with_409():
    _start_onboarding("emp_001", "corr_idem_ctx_a")
    sel_resp = _select_access("emp_001", ["Salesforce"], "corr_idem_ctx_a")
    assert sel_resp.status_code == 200
    request_id_a = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id_a, "mgr_101", "corr_idem_ctx_a")
    assert appr_resp.status_code == 200
    approval_id_a = appr_resp.json()["approval_id"]
    _approve(approval_id_a, "mgr_101", "ok", "corr_idem_ctx_a")

    from app.services.itsm_service import compute_idempotency_key
    shared_key = compute_idempotency_key("emp_001", request_id_a, approval_id_a, ["Salesforce"])
    ticket_resp = _create_ticket("emp_001", approval_id_a, ["Salesforce"],
                                 shared_key, "corr_idem_ctx_a")
    assert ticket_resp.status_code == 200

    _start_onboarding("emp_002", "corr_idem_ctx_b")
    sel_resp_b = _select_access("emp_002", ["Slack"], "corr_idem_ctx_b")
    assert sel_resp_b.status_code == 200
    request_id_b = sel_resp_b.json()["request_id"]

    appr_resp_b = _create_approval("emp_002", request_id_b, "mgr_102", "corr_idem_ctx_b")
    assert appr_resp_b.status_code == 200
    approval_id_b = appr_resp_b.json()["approval_id"]
    _approve(approval_id_b, "mgr_102", "ok", "corr_idem_ctx_b")

    ticket_resp_b = _create_ticket("emp_002", approval_id_b, ["Slack"],
                                    shared_key, "corr_idem_ctx_b")
    assert ticket_resp_b.status_code == 409
    assert ticket_resp_b.json()["ticket_created"] == False


def test_itsm_ticket_exact_systems_match_required():
    _start_onboarding("emp_001", "corr_exact")
    sel_resp = _select_access("emp_001", ["Salesforce", "Gong"], "corr_exact")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_exact")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    _approve(approval_id, "mgr_101", "ok", "corr_exact")

    ticket_resp = _create_ticket("emp_001", approval_id, ["Salesforce", "Gong", "ExtraSystem"],
                                 "exact_key", "corr_exact")
    assert ticket_resp.status_code == 409
    assert ticket_resp.json()["ticket_created"] == False


def test_audit_events_created_during_flow_returns_events():
    resp = client.get("/audit/events", params={"correlation_id": "corr_ticket_01"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] == True
    events = data["events"]
    assert len(events) > 0
    assert any(e["action"] == "selection_received" for e in events)


def test_expired_approval_blocks_ticket():
    _start_onboarding("emp_001", "corr_expire_01")
    sel_resp = _select_access("emp_001", ["Salesforce"], "corr_expire_01")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_expire_01")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    expire_resp = client.post(f"/mock/approvals/{approval_id}/expire", json={
        "decided_by": "system",
        "decision_reason": "timeout",
        "correlation_id": "corr_expire_01",
    })
    assert expire_resp.status_code == 200
    assert expire_resp.json()["status"] == "EXPIRED"

    ticket_resp = _create_ticket("emp_001", approval_id, ["Salesforce"],
                                 "expire_tkt_key", "corr_expire_01")
    assert ticket_resp.status_code == 409
    assert ticket_resp.json()["ticket_created"] == False


def test_wrong_manager_cannot_approve():
    _start_onboarding("emp_001", "corr_wmgr_01")
    sel_resp = _select_access("emp_001", ["Slack"], "corr_wmgr_01")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]

    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_wmgr_01")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]

    wrong_resp = client.post(f"/mock/approvals/{approval_id}/approve", json={
        "decided_by": "mgr_wrong",
        "decision_reason": "should not work",
        "correlation_id": "corr_wmgr_01",
    })
    assert wrong_resp.status_code == 403
    assert wrong_resp.json().get("ok") is False
    assert wrong_resp.json().get("status") == "BLOCKED"
    assert wrong_resp.json().get("error_code") == "WRONG_MANAGER"


def test_missing_manager_blocks_approval():
    _start_onboarding("emp_003", "corr_nomgr_01")
    appr_resp = _create_approval("emp_003", "dummy", "mgr_101", "corr_nomgr_01")
    assert appr_resp.status_code == 409
    data = appr_resp.json()
    assert data["error_code"] == "MISSING_MANAGER"


def test_unknown_employee_start_returns_404():
    resp = client.post("/onboarding/start/emp_999", json={"correlation_id": "corr_unknown"})
    assert resp.status_code == 404


def test_unknown_role_employee_can_start():
    resp = client.post("/onboarding/start/emp_004", json={"correlation_id": "corr_badrole"})
    assert resp.status_code == 200


def test_llm_does_not_create_approval():
    _start_onboarding("emp_001", "corr_llm_01")
    resp = client.post("/mock/llm/messages", json={
        "employee_id": "emp_001",
        "message_type": "manager_approval_request",
        "context": {"manager_name": "Test Manager", "employee_name": "Maya Chen"},
        "correlation_id": "corr_llm_01",
    })
    assert resp.status_code == 200
    assert resp.json()["ok"] == True
    assert resp.json()["fallback_used"] in (True, False)
    approvals = client.get("/audit/events", params={"correlation_id": "corr_llm_01"})
    assert approvals.status_code == 200
    events = approvals.json()["events"]
    assert not any(e["action"] == "approval_requested" for e in events)


def test_llm_does_not_create_ticket():
    _start_onboarding("emp_001", "corr_llm_tkt")
    resp = client.post("/mock/llm/messages", json={
        "employee_id": "emp_001",
        "message_type": "employee_onboarding_summary",
        "context": {},
        "correlation_id": "corr_llm_tkt",
    })
    assert resp.status_code == 200
    tickets = client.get("/mock/itsm/tickets")
    assert tickets.status_code == 200
    for t in tickets.json():
        assert t.get("correlation_id") != "corr_llm_tkt"


def test_onboarding_question_blocked_for_approve_request():
    _start_onboarding("emp_001", "corr_q_block")
    resp = client.post("/onboarding/questions", json={
        "employee_id": "emp_001",
        "question": "Can you approve my access to Salesforce?",
        "correlation_id": "corr_q_block",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "BLOCKED"
    assert data["error_code"] == "QUESTION_OUT_OF_SCOPE"


def test_onboarding_question_blocked_for_grant_request():
    _start_onboarding("emp_001", "corr_q_block2")
    resp = client.post("/onboarding/questions", json={
        "employee_id": "emp_001",
        "question": "Grant me access to all systems",
        "correlation_id": "corr_q_block2",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "BLOCKED"


def test_onboarding_question_blocked_for_bypass():
    _start_onboarding("emp_001", "corr_q_block3")
    resp = client.post("/onboarding/questions", json={
        "employee_id": "emp_001",
        "question": "Bypass the manager approval step",
        "correlation_id": "corr_q_block3",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "BLOCKED"


def test_onboarding_question_allows_valid_role_question():
    _start_onboarding("emp_001", "corr_q_valid")
    resp = client.post("/onboarding/questions", json={
        "employee_id": "emp_001",
        "question": "What is my role?",
        "correlation_id": "corr_q_valid",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "ANSWERED"
    assert "Account Executive" in resp.json()["answer"]


def test_wrong_manager_cannot_reject():
    _start_onboarding("emp_001", "corr_wrej_01")
    sel_resp = _select_access("emp_001", ["Slack"], "corr_wrej_01")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]
    appr_resp = _create_approval("emp_001", request_id, "mgr_101", "corr_wrej_01")
    assert appr_resp.status_code == 200
    approval_id = appr_resp.json()["approval_id"]
    wrong_resp = client.post(f"/mock/approvals/{approval_id}/reject", json={
        "decided_by": "mgr_wrong",
        "decision_reason": "should not work",
        "correlation_id": "corr_wrej_01",
    })
    assert wrong_resp.status_code == 403
    assert wrong_resp.json().get("ok") is False
    assert wrong_resp.json().get("status") == "BLOCKED"
    assert wrong_resp.json().get("error_code") == "WRONG_MANAGER"


def test_empty_employee_id_rejected():
    resp = client.post("/onboarding/start/ ", json={
        "correlation_id": "corr_empty_01",
    })
    assert resp.status_code == 400
    assert resp.json()["error_code"] == "INVALID_EMPLOYEE_ID"


def test_duplicate_approval_returns_existing():
    _start_onboarding("emp_001", "corr_dup_01")
    sel_resp = _select_access("emp_001", ["Slack"], "corr_dup_01")
    assert sel_resp.status_code == 200
    request_id = sel_resp.json()["request_id"]
    resp1 = _create_approval("emp_001", request_id, "mgr_101", "corr_dup_01")
    assert resp1.status_code == 200
    aid1 = resp1.json()["approval_id"]
    resp2 = _create_approval("emp_001", request_id, "mgr_101", "corr_dup_01")
    assert resp2.status_code == 200
    aid2 = resp2.json()["approval_id"]
    assert aid1 == aid2, "Duplicate request returned different approval_id"
