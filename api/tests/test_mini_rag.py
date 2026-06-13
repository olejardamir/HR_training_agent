from pathlib import Path
import json
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, SessionLocal
from app.models import Base, TrainingContent, OnboardingContent, AuditEvent
from tests.helpers import setup_database, teardown_database
from app.rag.index_builder import load_runtime_content, build_chunks
from app.rag.retriever import retrieve, _lazy_load

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
    result = retrieve("What do I need to do for T2?", top_k=3, minimum_score=0.05)
    assert len(result["matches"]) > 0
    for m in result["matches"]:
        assert "chunk_id" in m
        assert "content_id" in m
        assert "score" in m


def test_retriever_returns_profile_content_for_profile_question():
    result = retrieve("How do I update my profile?", top_k=3, minimum_score=0.05)
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
