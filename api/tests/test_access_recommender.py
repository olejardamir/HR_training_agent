import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from app.models import Base
from app.seed import reset_and_seed

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    reset_and_seed()
    yield
    Base.metadata.drop_all(bind=engine)

def test_recommendations_for_emp_001():
    response = client.get("/mock/access/recommendations/emp_001")
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == "emp_001"
    assert data["role"] == "Account Executive"
    assert data["level"] == "L2"

    required = [r for r in data["recommendations"] if r["recommendation_type"] == "required"]
    assert any(r["system"] == "Slack" for r in required)

    recommended = [r for r in data["recommendations"] if r["recommendation_type"] == "recommended"]
    salesforce = next((r for r in recommended if r["system"] == "Salesforce"), None)
    assert salesforce is not None
    assert "PEER_COMMON_ACCESS" in salesforce["reason_codes"]
    assert salesforce["peer_frequency"] == 8

    blocked = data["blocked_systems"]
    assert any(b["system"] == "Payroll Admin" for b in blocked)
    assert any(b["system"] == "Production Database Admin" for b in blocked)

def test_unknown_employee_returns_404():
    response = client.get("/mock/access/recommendations/emp_999")
    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == "EMPLOYEE_NOT_FOUND"

def test_unknown_role_level_returns_404():
    response = client.get("/mock/access/recommendations/emp_004")
    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == "POLICY_NOT_FOUND"

def test_department_standard_reason_code():
    response = client.get("/mock/access/recommendations/emp_001")
    data = response.json()
    recommended = [r for r in data["recommendations"] if r["recommendation_type"] == "recommended"]
    slack_channels = next((r for r in recommended if r["system"] == "Sales Slack Channels"), None)
    assert slack_channels is not None
    assert "DEPARTMENT_STANDARD" in slack_channels["reason_codes"]
