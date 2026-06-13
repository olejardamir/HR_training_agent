import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import SelectedAccessRequest, ManagerApproval, ITSMTicket, AuditEvent
from tests.helpers import setup_database, teardown_database
from app.rag.index_builder import build_index
from app.rag.retriever import retrieve, _lazy_load

client = TestClient(app)

APP_DIR = Path(__file__).resolve().parents[1] / "app"
INDEX_DIR = APP_DIR / "rag_index"


def setup_module():
    setup_database()
    build_index()
    _lazy_load()


def teardown_module():
    teardown_database()


def test_index_build_produces_required_files():
    chunks_path = INDEX_DIR / "content_chunks.json"
    vectors_path = INDEX_DIR / "content_vectors.json"
    meta_path = INDEX_DIR / "index_meta.json"
    assert chunks_path.exists()
    assert vectors_path.exists()
    assert meta_path.exists()
    chunks = json.loads(chunks_path.read_text())
    vectors = json.loads(vectors_path.read_text())
    meta = json.loads(meta_path.read_text())
    assert len(chunks) > 0, "chunk_count must be > 0"
    assert len(vectors) == len(chunks), "vector count must equal chunk count"
    assert "method" in meta, "index_meta must include method"


def test_retrieval_finds_t2_content():
    result = retrieve("What do I need to do for T2?", top_k=3, minimum_score=0.10)
    assert len(result["matches"]) > 0
    for m in result["matches"]:
        assert m.get("runtime_approved") is True
        assert "score" in m
    assert result.get("retrieval_method") in ("tfidf", "sentence-transformers")


def test_chat_uses_only_approved_content():
    resp = client.post("/agent/chat", json={
        "employee_id": "emp_001",
        "message": "What do I need to do for T2?",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["used_content_ids"]) > 0
    for cid in data["used_content_ids"]:
        assert isinstance(cid, str)


def test_faithfulness_grounding_smoke():
    resp = client.post("/agent/chat", json={
        "employee_id": "emp_001",
        "message": "What do I need to do for T2?",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert len(data["used_content_ids"]) > 0
    assert len(data["used_chunk_ids"]) > 0


def test_access_guidance_does_not_mutate_workflow():
    db = SessionLocal()
    try:
        before_selected = db.query(SelectedAccessRequest).count()
        before_approval = db.query(ManagerApproval).count()
        before_ticket = db.query(ITSMTicket).count()
    finally:
        db.close()

    resp = client.post("/agent/chat", json={
        "employee_id": "emp_001",
        "message": "Can I request Salesforce access?",
    })
    assert resp.status_code == 200

    db = SessionLocal()
    try:
        assert db.query(SelectedAccessRequest).count() == before_selected
        assert db.query(ManagerApproval).count() == before_approval
        assert db.query(ITSMTicket).count() == before_ticket
    finally:
        db.close()
