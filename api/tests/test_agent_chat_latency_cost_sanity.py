import inspect
from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import setup_database, teardown_database
from app.rag.index_builder import build_index
from app.rag.retriever import _lazy_load, retrieve

client = TestClient(app)


def setup_module():
    setup_database()
    build_index()
    _lazy_load()


def teardown_module():
    teardown_database()


def test_chat_does_not_build_index():
    import app.routers.agent_chat as mod
    source = inspect.getsource(mod)
    assert "build_index" not in source, "agent_chat must not call build_index"


def test_default_top_k_is_small():
    sig = inspect.signature(retrieve)
    default_top_k = sig.parameters["top_k"].default
    assert default_top_k <= 3, f"default top_k should be <= 3, got {default_top_k}"


def test_response_length_is_bounded():
    resp = client.post("/agent/chat", json={
        "employee_id": "emp_001",
        "message": "What do I need to do for T2?",
    })
    assert resp.status_code == 200
    answer = resp.json()["answer"]
    assert len(answer) < 2000, f"answer too long: {len(answer)} chars"
