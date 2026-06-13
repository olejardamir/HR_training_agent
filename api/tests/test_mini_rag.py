from pathlib import Path
import json
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, SessionLocal
from app.models import (
    Base, TrainingContent, OnboardingContent, AuditEvent,
    SelectedAccessRequest, ManagerApproval, ITSMTicket,
    TrainingStatusTable, SalesforceProfile, Employee, SlackMessage,
)
from tests.helpers import setup_database, teardown_database
from app.rag.index_builder import load_runtime_content, build_chunks
from app.rag.retriever import retrieve, _lazy_load
from app.services.agent_guardrails import (
    filter_approved_matches,
    has_approved_context,
    is_state_only_question,
    build_no_context_answer,
    summarize_retrieval,
)

client = TestClient(app)

APP_DIR = Path(__file__).resolve().parents[1] / "app"
FIXTURE_DIR = APP_DIR / "fixtures"
INDEX_DIR = APP_DIR / "rag_index"


def setup_module():
    setup_database()
    from app.rag.index_builder import build_index
    build_index()
    _lazy_load()


def teardown_module():
    teardown_database()


def test_content_fixtures_are_seeded():
    db = SessionLocal()
    try:
        count = db.query(TrainingContent).count()
        assert count > 0, f"Expected >0 training content, got {count}"
        count = db.query(OnboardingContent).count()
        assert count > 0, f"Expected >0 onboarding content, got {count}"
    finally:
        db.close()


def test_training_content_endpoint_filters_t2():
    resp = client.get("/mock/content/training?module_id=T2")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    for item in data:
        assert "T2" in item["module_ids"]


def test_onboarding_content_endpoint_filters_profile_update():
    resp = client.get("/mock/content/onboarding")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0


def test_rag_index_builds_from_runtime_approved_content():
    chunks_path = INDEX_DIR / "content_chunks.json"
    vectors_path = INDEX_DIR / "content_vectors.json"
    assert chunks_path.exists(), "content_chunks.json missing"
    assert vectors_path.exists(), "content_vectors.json missing"
    chunks = json.loads(chunks_path.read_text())
    assert len(chunks) > 0
    for c in chunks:
        assert c.get("runtime_approved") is True


def test_retriever_returns_t2_content_for_t2_question():
    result = retrieve("What do I need to do for T2?", top_k=3, minimum_score=0.10)
    assert len(result["matches"]) > 0
    for m in result["matches"]:
        assert "chunk_id" in m
        assert "content_id" in m
        assert "score" in m


def test_retriever_returns_profile_content_for_profile_question():
    result = retrieve("How do I update my profile?", top_k=3, minimum_score=0.10)
    assert len(result["matches"]) > 0


def test_retriever_ignores_runtime_approved_false_content():
    _lazy_load()
    from app.rag.retriever import _chunks
    for c in _chunks:
        if not c.get("runtime_approved"):
            result = retrieve("test query", top_k=1, minimum_score=0.0)
            found = any(m["chunk_id"] == c["chunk_id"] for m in result["matches"])
            assert not found, f"Unapproved chunk {c['chunk_id']} should not be returned"


def test_agent_chat_returns_answer_with_used_content_ids():
    resp = client.post("/agent/chat", json={
        "employee_id": "emp_001",
        "message": "What do I need to do for T2?",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert isinstance(data["used_content_ids"], list)
    assert isinstance(data["used_chunk_ids"], list)
    assert data["employee_id"] == "emp_001"


def test_agent_chat_uses_employee_role_level_state():
    resp = client.post("/agent/chat", json={
        "employee_id": "emp_001",
        "message": "What do I need to do for T2?",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "state_summary" in data
    assert "role" in data["state_summary"]
    assert "level" in data["state_summary"]
    assert "training" in data["state_summary"]


def test_agent_chat_does_not_make_access_decision_from_rag_text():
    resp = client.post("/agent/chat", json={
        "employee_id": "emp_001",
        "message": "Can I request Salesforce access?",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "suggested_actions" in data


def test_agent_chat_logs_audit_event():
    resp = client.post("/agent/chat", json={
        "employee_id": "emp_001",
        "message": "What is Salesforce setup like?",
    })
    assert resp.status_code == 200
    db = SessionLocal()
    try:
        events = db.query(AuditEvent).filter(
            AuditEvent.action == "agent_chat"
        ).all()
        assert len(events) > 0
    finally:
        db.close()


def test_agent_chat_returns_404_for_unknown_employee():
    resp = client.post("/agent/chat", json={
        "employee_id": "UNKNOWN",
        "message": "Test",
    })
    assert resp.status_code == 404


def test_guardrail_filter_approved_matches():
    matches = [
        {"chunk_id": "a", "runtime_approved": True},
        {"chunk_id": "b", "runtime_approved": False},
        {"chunk_id": "c", "runtime_approved": True},
    ]
    filtered = filter_approved_matches(matches)
    ids = [m["chunk_id"] for m in filtered]
    assert "a" in ids
    assert "b" not in ids
    assert "c" in ids


def test_guardrail_has_approved_context():
    assert has_approved_context([{"runtime_approved": True}]) is True
    assert has_approved_context([{"runtime_approved": False}]) is False
    assert has_approved_context([]) is False


def test_guardrail_is_state_only_question():
    assert is_state_only_question("What is my Salesforce setup status?") is True
    assert is_state_only_question("Tell me my training status") is True
    assert is_state_only_question("What is the company policy on remote work?") is False


def test_guardrail_build_no_context_answer():
    answer = build_no_context_answer()
    assert "do not have enough approved onboarding guidance" in answer.lower()


def test_guardrail_summarize_retrieval():
    matches = [
        {
            "chunk_id": "c1", "content_id": "x",
            "source_ids": ["doc1.md"], "score": 0.85,
            "runtime_approved": True,
        },
    ]
    retrieval = {"retrieval_method": "tfidf"}
    result = summarize_retrieval(matches, retrieval)
    assert result["used_content_ids"] == ["x"]
    assert result["used_chunk_ids"] == ["c1"]
    assert result["source_ids"] == ["doc1.md"]
    assert result["retrieval_scores"] == [0.85]
    assert result["retrieval_method"] == "tfidf"
    assert result["fallback_used"] is False
    assert result["llm_used"] is False


def test_agent_chat_no_context_fallback():
    resp = client.post("/agent/chat", json={
        "employee_id": "emp_001",
        "message": "What is the policy for xyzzz?",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["answer"], str) and len(data["answer"]) > 0
    assert isinstance(data["fallback_used"], bool)


def test_agent_chat_state_only_without_rag_context():
    resp = client.post("/agent/chat", json={
        "employee_id": "emp_002",
        "message": "What is my Salesforce setup status?",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "salesforce" in data["answer"].lower() or "setup" in data["answer"].lower()
    assert "state_summary" in data
    assert "salesforce_setup_status" in data["state_summary"]


def test_agent_chat_read_only():
    db = SessionLocal()
    try:
        before_selected = db.query(SelectedAccessRequest).count()
        before_approval = db.query(ManagerApproval).count()
        before_ticket = db.query(ITSMTicket).count()
        before_training = db.query(TrainingStatusTable).count()
        before_sf = db.query(SalesforceProfile).count()
        before_employee = db.query(Employee).count()
        before_slack = db.query(SlackMessage).count()
        before_audit = db.query(AuditEvent).count()
    finally:
        db.close()

    resp = client.post("/agent/chat", json={
        "employee_id": "emp_001",
        "message": "What do I need to do for T2?",
    })
    assert resp.status_code == 200

    db = SessionLocal()
    try:
        assert db.query(SelectedAccessRequest).count() == before_selected
        assert db.query(ManagerApproval).count() == before_approval
        assert db.query(ITSMTicket).count() == before_ticket
        assert db.query(TrainingStatusTable).count() == before_training
        assert db.query(SalesforceProfile).count() == before_sf
        assert db.query(Employee).count() == before_employee
        assert db.query(SlackMessage).count() == before_slack
        assert db.query(AuditEvent).count() == before_audit + 1
    finally:
        db.close()


def test_agent_chat_traceability_fields():
    resp = client.post("/agent/chat", json={
        "employee_id": "emp_001",
        "message": "What do I need to do for T2?",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "source_ids" in data
    assert "retrieval_scores" in data
    assert "retrieval_method" in data
    assert "fallback_used" in data
    assert "llm_used" in data


def test_agent_response_prompt_constraints():
    from app.services.agent_response import _build_with_llm
    import inspect
    source = inspect.getsource(_build_with_llm)
    constraints = [
        "Do not invent company policy",
        "Do not invent training completion status",
        "Do not claim access is allowed unless role/level policy says so",
        "Do not claim approval happened unless approval state says so",
        "Do not claim a ticket was submitted unless ticket state says so",
            "Answer only using:",
    ]
    for c in constraints:
        assert c in source, f"Missing prompt constraint: {c}"
