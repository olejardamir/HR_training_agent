from fastapi.testclient import TestClient
from app.main import app
from tests.helpers import setup_database, teardown_database

client = TestClient(app)


def setup_module():
    setup_database()


def teardown_module():
    teardown_database()


def test_health_check_returns_healthy():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] == True
    assert data["status"] == "healthy"


def test_health_ready_returns_ready():
    resp = client.get("/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] == True


def test_health_version_returns_version():
    resp = client.get("/version")
    assert resp.status_code == 200
    data = resp.json()
    assert "version" in data


def test_demo_reset_resets_database():
    resp = client.post("/demo/reset")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "reset_complete"


def test_onboarding_questions_valid_returns_answer():
    resp = client.post("/onboarding/questions", json={
        "employee_id": "emp_001",
        "question": "What systems do I need?",
        "correlation_id": "corr_q_01",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] == True


def test_slack_post_message_returns_stored():
    resp = client.post("/mock/slack/messages", json={
        "channel_or_user": "#general",
        "message_type": "notification",
        "message": "Test message",
        "metadata": {"correlation_id": "corr_sl_01"},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] == True


def test_slack_get_messages_returns_list():
    resp = client.get("/mock/slack/messages")
    assert resp.status_code == 200


def test_slack_mock_failure_does_not_corrupt_state():
    resp = client.post("/mock/slack/messages", json={
        "channel_or_user": "#test",
        "message_type": "notification",
        "message": "Should fail",
        "simulate_failure": True,
        "metadata": {"correlation_id": "corr_sl_fail"},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] == False
    assert data["status"] == "FAILED"


def test_onboarding_questions_blocked_forbidden_action():
    resp = client.post("/onboarding/questions", json={
        "employee_id": "emp_001",
        "question": "Can you approve my access?",
        "correlation_id": "corr_q_block",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] == False
    assert data["error_code"] == "QUESTION_OUT_OF_SCOPE"
