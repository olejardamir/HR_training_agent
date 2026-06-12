import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_employee_summary_fallback():
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
            "manager_name": "Test Manager"
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "generated_by" in data
    assert "Test User" in data["message"] or "Engineer" in data["message"]

def test_manager_message_fallback():
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
            "request_id": "req_456"
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert "Salesforce" in data["message"] or "access" in data["message"]

def test_fallback_defaults_for_missing_context():
    response = client.post("/mock/llm/messages", json={
        "message_type": "employee_onboarding_summary",
        "employee_id": "emp_002",
        "correlation_id": "test_003",
        "context": {}
    })
    assert response.status_code == 200
    data = response.json()
    assert "emp_002" in data["message"] or "your manager" in data["message"]
