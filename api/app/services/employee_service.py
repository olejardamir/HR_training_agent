from sqlalchemy.orm import Session
from ..models import Employee, EmploymentStatus


def get_employee(db: Session, employee_id: str):
    return db.query(Employee).filter(Employee.employee_id == employee_id).first()


def is_new_hire(db: Session, employee_id: str) -> bool:
    emp = get_employee(db, employee_id)
    if not emp:
        return False
    return emp.employment_status == EmploymentStatus.NEW_HIRE
