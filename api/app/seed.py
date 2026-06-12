import json
import uuid
from .database import engine, SessionLocal
from .models import (
    Base, Employee, Manager, TrainingStatusTable, SalesforceProfile,
    RoleAccessPolicy, PeerAccessPattern, DepartmentStandard,
    OnboardingSession, SelectedAccessRequest, ManagerApproval,
    ITSMTicket, SlackMessage, AuditEvent, EmploymentStatus
)


def reset_and_seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        with open("app/fixtures/employees.json") as f:
            employees = json.load(f)
        for emp in employees:
            db.add(Employee(
                employee_id=emp["employee_id"],
                name=emp["name"],
                email=emp["email"],
                role=emp["role"],
                level=emp["level"],
                department=emp["department"],
                manager_id=emp.get("manager_id"),
                start_date=emp["start_date"],
                employment_status=EmploymentStatus(emp["employment_status"]),
                profile_status=emp.get("profile_status", "active"),
            ))

        with open("app/fixtures/managers.json") as f:
            managers = json.load(f)
        for mgr in managers:
            db.add(Manager(**mgr))

        with open("app/fixtures/training_status.json") as f:
            trainings = json.load(f)
        for t in trainings:
            db.add(TrainingStatusTable(
                employee_id=t["employee_id"],
                module_id=t["module_id"],
                status=t["status"],
            ))

        with open("app/fixtures/salesforce_profiles.json") as f:
            sf_profiles = json.load(f)
        for sf in sf_profiles:
            db.add(SalesforceProfile(
                employee_id=sf["employee_id"],
                profile_complete=sf.get("profile_complete", False),
                setup_status=sf.get("setup_status", "not_started"),
                assigned_licenses=sf.get("assigned_licenses", []),
            ))

        with open("app/fixtures/role_access_policies.json") as f:
            policies = json.load(f)
        for p in policies:
            db.add(RoleAccessPolicy(
                role=p["role"],
                level=p["level"],
                required_systems=p["required_systems"],
                recommended_systems=p["recommended_systems"],
                optional_systems=p.get("optional_systems", []),
                forbidden_systems=p["forbidden_systems"],
                policy_version=p.get("policy_version", "v1"),
            ))

        with open("app/fixtures/peer_access_patterns.json") as f:
            peers = json.load(f)
        for peer in peers:
            db.add(PeerAccessPattern(
                role=peer["role"],
                level=peer["level"],
                peer_count=peer["peer_count"],
                common_access=peer["common_access"],
            ))

        with open("app/fixtures/department_standards.json") as f:
            dept_standards = json.load(f)
        for ds in dept_standards:
            db.add(DepartmentStandard(
                department=ds["department"],
                standard_systems=ds["standard_systems"],
            ))

        db.commit()
        print("Database seeded successfully.")
    finally:
        db.close()
