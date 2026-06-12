import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

def test_llm_employee_summary_fallback_returns_message():
    response = client.post("/mock/llm/messages", json={
        "message_type": "employee_onboarding_summary",
        "employee_id": "emp_001",
        "correlation_id": "test_001",
        "context": {
            "employee_name": "Test User",
            "role": "Engineer",
            "level": "L2",
            "training_summary": "All complete",
            "recommended_systems_list": "GitHub, AWS",
            "manager_name": "Test Manager",
        },
    })
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data.get("llm_provider") in ("ollama", "fallback")
    assert data.get("fallback_used") == (data.get("llm_provider") == "fallback")
    assert "Test User" in data["message"] or "Engineer" in data["message"]

def test_llm_manager_message_fallback_returns_message():
    response = client.post("/mock/llm/messages", json={
        "message_type": "manager_approval_request",
        "employee_id": "emp_001",
        "correlation_id": "test_002",
        "context": {
            "manager_name": "Alice",
            "employee_name": "Bob",
            "role": "Sales",
            "level": "L2",
            "selected_systems_list": "Salesforce",
            "correlation_id": "corr_123",
            "request_id": "req_456",
        },
    })
    assert response.status_code == 200
    data = response.json()
    assert "Salesforce" in data["message"] or "access" in data["message"]
    assert data.get("fallback_used") == (data.get("llm_provider") == "fallback")

def test_llm_invalid_message_type_returns_400():
    response = client.post("/mock/llm/messages", json={
        "message_type": "invalid_type_xyz",
        "employee_id": "emp_001",
        "correlation_id": "test_004",
        "context": {},
    })
    assert response.status_code == 400
    data = response.json()
    assert data.get("ok") is False
    assert data.get("status") == "ERROR"
    assert data.get("error_code") == "INVALID_MESSAGE_TYPE"

from unittest.mock import patch as _patch, Mock as _Mock, AsyncMock as _AsyncMock

def test_ollama_provider_returns_ollama_response():
    import app.services.llm_service as llm_svc
    mock_response = _Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "Mock Ollama response for employee."}
    original_provider = llm_svc.settings.llm_provider
    llm_svc.settings.llm_provider = "ollama"
    try:
        with _patch.object(llm_svc.httpx, "AsyncClient") as mock_client:
            mock_instance = mock_client.return_value
            mock_context = _AsyncMock()
            mock_instance.__aenter__.return_value = mock_context
            mock_context.post = _AsyncMock(return_value=mock_response)
            response = client.post("/mock/llm/messages", json={
                "message_type": "employee_onboarding_summary",
                "employee_id": "emp_001",
                "correlation_id": "ollama_test_001",
                "context": {"employee_name": "Ollama User", "role": "Engineer", "level": "L2"},
            })
        assert response.status_code == 200
        data = response.json()
        assert data.get("llm_provider") == "ollama", f"Expected ollama, got {data.get('llm_provider')}"
        assert data.get("fallback_used") is False
    finally:
        llm_svc.settings.llm_provider = original_provider


def test_llm_fallback_missing_context_uses_defaults():
    response = client.post("/mock/llm/messages", json={
        "message_type": "employee_onboarding_summary",
        "employee_id": "emp_002",
        "correlation_id": "test_003",
        "context": {},
    })
    assert response.status_code == 200
    data = response.json()
    assert "emp_002" in data["message"] or "your manager" in data["message"]
