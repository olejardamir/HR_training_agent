from sqlalchemy.orm import Session
from ..models import Employee, EmploymentStatus
from .policy_service import get_policy, get_peer_pattern, get_department_standard


FORBIDDEN_SYSTEMS = [
    "Payroll Admin", "Production Database Admin", "Security Admin", "Finance Admin"
]


def get_recommendations(db: Session, employee_id: str):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        return None, "EMPLOYEE_NOT_FOUND"
    if emp.employment_status != EmploymentStatus.NEW_HIRE:
        return None, "EMPLOYEE_NOT_ACTIVE"
    if not emp.role or not emp.level:
        return None, "UNKNOWN_ROLE_LEVEL"

    policy = get_policy(db, emp.role, emp.level)
    if not policy:
        return None, "POLICY_NOT_FOUND"

    peer = get_peer_pattern(db, emp.role, emp.level)
    dept_std = get_department_standard(db, emp.department)

    recommendations = []
    seen_systems = set()

    for sys_name in (policy.required_systems or []):
        if sys_name in FORBIDDEN_SYSTEMS:
            continue
        recommendations.append({
            "system": sys_name,
            "recommendation_type": "required",
            "reason_codes": ["BASE_ONBOARDING_REQUIRED", "ROLE_LEVEL_POLICY"],
            "requires_manager_approval": False,
        })
        seen_systems.add(sys_name)

    for sys_name in (policy.recommended_systems or []):
        if sys_name in FORBIDDEN_SYSTEMS or sys_name in seen_systems:
            continue
        codes = ["ROLE_LEVEL_POLICY"]
        freq = None
        if peer:
            for ca in (peer.common_access or []):
                if ca["system"] == sys_name:
                    codes.append("PEER_COMMON_ACCESS")
                    freq = ca["frequency"]
                    break
        if dept_std and sys_name in (dept_std.standard_systems or []):
            codes.append("DEPARTMENT_STANDARD")
        recommendations.append({
            "system": sys_name,
            "recommendation_type": "recommended",
            "reason_codes": codes,
            "requires_manager_approval": True,
            "peer_frequency": freq,
        })
        seen_systems.add(sys_name)

    for sys_name in (policy.optional_systems or []):
        if sys_name in FORBIDDEN_SYSTEMS or sys_name in seen_systems:
            continue
        recommendations.append({
            "system": sys_name,
            "recommendation_type": "optional",
            "reason_codes": ["ROLE_LEVEL_POLICY"],
            "requires_manager_approval": False,
        })
        seen_systems.add(sys_name)

    blocked = []
    for sys_name in FORBIDDEN_SYSTEMS:
        blocked.append({
            "system": sys_name,
            "reason_codes": ["FORBIDDEN_FOR_ROLE_LEVEL"],
        })

    result = {
        "employee_id": employee_id,
        "role": emp.role,
        "level": emp.level,
        "recommendations": recommendations,
        "blocked_systems": blocked,
        "policy_version": policy.policy_version,
    }
    return result, None
