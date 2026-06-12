import json
from .database import engine, SessionLocal
from .models import Base, Employee, TrainingStatusTable, RoleAccessPolicy, PeerAccessPattern, DepartmentStandard, EmploymentStatus

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
                employment_status=EmploymentStatus(emp["employment_status"])
            ))

        with open("app/fixtures/training_status.json") as f:
            trainings = json.load(f)
        for t in trainings:
            db.add(TrainingStatusTable(
                employee_id=t["employee_id"],
                modules=t["modules"]
            ))

        with open("app/fixtures/role_access_policies.json") as f:
            policies = json.load(f)
        for p in policies:
            db.add(RoleAccessPolicy(
                role=p["role"],
                level=p["level"],
                required_systems=p["required_systems"],
                recommended_systems=p["recommended_systems"],
                forbidden_systems=p["forbidden_systems"],
                policy_version=p.get("policy_version", "v1")
            ))

        with open("app/fixtures/peer_access_patterns.json") as f:
            peers = json.load(f)
        for peer in peers:
            db.add(PeerAccessPattern(
                role=peer["role"],
                level=peer["level"],
                peer_count=peer["peer_count"],
                common_access=peer["common_access"]
            ))

        with open("app/fixtures/department_standards.json") as f:
            dept_standards = json.load(f)
        for ds in dept_standards:
            db.add(DepartmentStandard(
                department=ds["department"],
                standard_systems=ds["standard_systems"]
            ))

        db.commit()
        print("Database seeded successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed()
