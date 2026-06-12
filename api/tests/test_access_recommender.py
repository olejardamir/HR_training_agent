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

def test_access_recommendations_emp001_returns_recommendations():
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

def test_access_recommendations_unknown_employee_returns_404():
    response = client.get("/mock/access/recommendations/emp_999")
    assert response.status_code == 404
    assert response.json()["error_code"] == "EMPLOYEE_NOT_FOUND"

def test_access_recommendations_unsupported_role_level_returns_404():
    response = client.get("/mock/access/recommendations/emp_004")
    assert response.status_code == 404
    assert response.json()["error_code"] == "POLICY_NOT_FOUND"

def test_inactive_employee_blocked():
    from app.models import Employee
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        emp = db.query(Employee).filter(Employee.employee_id == "emp_inactive").first()
        if not emp:
            from app.models import EmploymentStatus
            emp = Employee(
                employee_id="emp_inactive",
                name="Inactive Employee",
                email="inactive@example.test",
                role="Account Executive",
                level="L2",
                department="Sales",
                manager_id="mgr_101",
                start_date="2026-01-01",
                employment_status=EmploymentStatus.INACTIVE,
            )
            db.add(emp)
            db.commit()
        response = client.get("/mock/access/recommendations/emp_inactive")
        assert response.status_code == 403
        assert response.json()["error_code"] == "EMPLOYEE_NOT_ACTIVE"
    finally:
        db.close()

def test_missing_role_level_returns_error():
    from app.models import Employee, EmploymentStatus
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        emp = db.query(Employee).filter(Employee.employee_id == "emp_999_norole").first()
        if not emp:
            emp = Employee(
                employee_id="emp_999_norole",
                name="No Role User",
                email="norole@example.test",
                role=None,
                level=None,
                department="Sales",
                manager_id="mgr_101",
                start_date="2026-01-01",
                employment_status=EmploymentStatus.NEW_HIRE,
            )
            db.add(emp)
            db.commit()
        response = client.get("/mock/access/recommendations/emp_999_norole")
        assert response.status_code == 409
        assert response.json()["error_code"] == "UNKNOWN_ROLE_LEVEL"
    finally:
        db.close()

def test_access_recommendations_department_standard_includes_reason_code():
    response = client.get("/mock/access/recommendations/emp_001")
    data = response.json()
    recommended = [r for r in data["recommendations"] if r["recommendation_type"] == "recommended"]
    slack_channels = next((r for r in recommended if r["system"] == "Sales Slack Channels"), None)
    assert slack_channels is not None
    assert "DEPARTMENT_STANDARD" in slack_channels["reason_codes"]
