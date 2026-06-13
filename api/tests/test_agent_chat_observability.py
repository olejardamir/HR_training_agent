from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import AuditEvent
from tests.helpers import setup_database, teardown_database
from app.rag.index_builder import build_index
from app.rag.retriever import _lazy_load

client = TestClient(app)


def setup_module():
    setup_database()
    build_index()
    _lazy_load()


def teardown_module():
    teardown_database()


def test_audit_metadata_includes_retrieval_context():
    resp = client.post("/agent/chat", json={
        "employee_id": "emp_001",
        "message": "What do I need to do for T2?",
    })
    assert resp.status_code == 200

    db = SessionLocal()
    try:
        event = db.query(AuditEvent).filter(
            AuditEvent.action == "agent_chat"
        ).order_by(AuditEvent.event_id.desc()).first()
    finally:
        db.close()

    assert event is not None, "No agent_chat audit event found"
    meta = event.metadata_json or {}

    assert "used_content_ids" in meta
    assert "used_chunk_ids" in meta
    assert "retrieval_method" in meta
    assert "fallback_used" in meta
    assert "llm_used" in meta
    assert "latency_ms" in meta
    assert "match_count" in meta

    assert isinstance(meta["latency_ms"], (int, float)), "latency_ms must be numeric"
    assert isinstance(meta["match_count"], int), "match_count must be int"
    assert isinstance(meta["used_content_ids"], list)
    assert isinstance(meta["used_chunk_ids"], list)
    assert isinstance(meta["fallback_used"], bool)
    assert isinstance(meta["llm_used"], bool)
