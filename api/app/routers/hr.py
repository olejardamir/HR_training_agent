from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Employee, Manager
from ..schemas import EmployeeProfile, EmployeeProfilePatchRequest, ManagerProfile
from ..services.employee_service import get_employee
from ..services.audit_service import log_event

router = APIRouter()


@router.get("/mock/hr/employees/{employee_id}", response_model=EmployeeProfile)
@router.get("/mock/hr/employees/{employee_id}/profile", response_model=EmployeeProfile)
def get_employee_profile(employee_id: str, db: Session = Depends(get_db)):
    emp = get_employee(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail={
            "ok": False, "error_code": "EMPLOYEE_NOT_FOUND",
            "message": f"Employee {employee_id} not found",
        })
    log_event(db, None, employee_id, "system", "hr-mock",
              "employee_profile_loaded", "employee", employee_id, "LOADED", None)

    return EmployeeProfile(
        employee_id=emp.employee_id,
        name=emp.name,
        email=emp.email,
        role=emp.role,
        level=emp.level,
        department=emp.department,
        manager_id=emp.manager_id,
        start_date=emp.start_date,
        employment_status=emp.employment_status.value if hasattr(emp.employment_status, 'value') else emp.employment_status,
        profile_status=emp.profile_status or "active",
    )


@router.patch("/mock/hr/employees/{employee_id}/profile")
def patch_employee_profile(employee_id: str, request: EmployeeProfilePatchRequest,
                           db: Session = Depends(get_db)):
    emp = get_employee(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    ignored_fields = []
    for field in ("role", "level", "manager_id", "employment_status", "department"):
        incoming = getattr(request, field, None)
        if incoming is not None:
            ignored_fields.append(field)
            setattr(request, field, None)

    if request.preferred_name:
        emp.name = request.preferred_name

    if ignored_fields:
        reason_code = "untrusted_profile_field_ignored"
        log_event(db, request.correlation_id, employee_id, "employee", employee_id,
                  "profile_updated", "employee", employee_id, "UPDATED",
                  reason_code, {"ignored_fields": ignored_fields})
    else:
        log_event(db, request.correlation_id, employee_id, "employee", employee_id,
                  "profile_updated", "employee", employee_id, "UPDATED", None)

    profile_status = {
        "hr_profile_complete": True,
        "slack_profile_complete": False,
        "salesforce_profile_complete": False,
    }

    db.flush()

    return {
        "ok": True, "status": "UPDATED",
        "employee_id": employee_id,
        "profile_status": profile_status,
        "correlation_id": request.correlation_id,
    }


@router.get("/mock/hr/managers/{manager_id}", response_model=ManagerProfile)
def get_manager(manager_id: str, db: Session = Depends(get_db)):
    mgr = db.query(Manager).filter(Manager.manager_id == manager_id).first()
    if not mgr:
        raise HTTPException(status_code=404, detail="Manager not found")
    return ManagerProfile(
        manager_id=mgr.manager_id,
        name=mgr.name,
        email=mgr.email,
        is_active=mgr.is_active,
        has_contact=mgr.has_contact,
    )
