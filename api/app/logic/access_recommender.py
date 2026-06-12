from sqlalchemy.orm import Session
from ..models import Employee, RoleAccessPolicy, PeerAccessPattern, DepartmentStandard

def get_access_recommendations(employee_id: str, db: Session):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        return None, "EMPLOYEE_NOT_FOUND"

    if not emp.role or not emp.level:
        return None, "UNKNOWN_ROLE_LEVEL"

    policy = db.query(RoleAccessPolicy).filter(
        RoleAccessPolicy.role == emp.role,
        RoleAccessPolicy.level == emp.level
    ).first()
    if not policy:
        return None, "POLICY_NOT_FOUND"

    peer = db.query(PeerAccessPattern).filter(
        PeerAccessPattern.role == emp.role,
        PeerAccessPattern.level == emp.level
    ).first()

    dept_std = db.query(DepartmentStandard).filter(
        DepartmentStandard.department == emp.department
    ).first()
    dept_standard_systems = dept_std.standard_systems if dept_std else []

    recommendations = []

    for sys in policy.required_systems:
        reason_codes = ["BASE_ONBOARDING_REQUIRED"]
        if sys in dept_standard_systems:
            reason_codes.append("DEPARTMENT_STANDARD")
        recommendations.append({
            "system": sys,
            "recommendation_type": "required",
            "reason_codes": reason_codes,
            "requires_manager_approval": False,
            "peer_frequency": None
        })

    for sys in policy.recommended_systems:
        peer_freq = None
        if peer:
            for item in peer.common_access:
                if item["system"] == sys:
                    peer_freq = item["frequency"]
                    break
        reason_codes = ["ROLE_LEVEL_POLICY"]
        if peer_freq and peer_freq >= (peer.peer_count * 0.6):
            reason_codes.append("PEER_COMMON_ACCESS")
        if sys in dept_standard_systems:
            reason_codes.append("DEPARTMENT_STANDARD")
        recommendations.append({
            "system": sys,
            "recommendation_type": "recommended",
            "reason_codes": reason_codes,
            "requires_manager_approval": True,
            "peer_frequency": peer_freq
        })

    blocked_systems = [
        {"system": sys, "reason_codes": ["FORBIDDEN_FOR_ROLE_LEVEL"]}
        for sys in policy.forbidden_systems
    ]

    return {
        "employee_id": employee_id,
        "role": emp.role,
        "level": emp.level,
        "recommendations": recommendations,
        "blocked_systems": blocked_systems,
        "policy_version": policy.policy_version
    }, None
