from sqlalchemy.orm import Session
from ..models import SelectedAccessRequest, OnboardingSession
from .recommendation_service import get_recommendations


FORBIDDEN_SYSTEMS = [
    "Payroll Admin", "Production Database Admin", "Security Admin", "Finance Admin"
]


def _build_known_systems(db: Session, employee_id: str) -> set | None:
    rec, error = get_recommendations(db, employee_id)
    if error or not rec:
        return None
    known = set(FORBIDDEN_SYSTEMS)
    for r in rec.get("recommendations", []):
        known.add(r["system"])
    for b in rec.get("blocked_systems", []):
        known.add(b["system"])
    return known


def validate_selection(db: Session, employee_id: str, selected_systems: list):
    session = db.query(OnboardingSession).filter(
        OnboardingSession.employee_id == employee_id
    ).first()
    if not session:
        return {"error": "NO_ACTIVE_SESSION"}

    rec, error = get_recommendations(db, employee_id)
    if error:
        return {"error": "RECOMMENDATIONS_UNAVAILABLE", "reason": error}

    selected_systems = list(set(selected_systems))
    forbidden = FORBIDDEN_SYSTEMS
    for sys_name in selected_systems:
        if sys_name in forbidden:
            return {"error": "FORBIDDEN_SYSTEM_SELECTED", "system": sys_name}

    known = _build_known_systems(db, employee_id)
    if known is not None:
        for sys_name in selected_systems:
            if sys_name not in known:
                return {"error": "UNKNOWN_SYSTEM_SELECTED", "system": sys_name}

    return {"ok": True, "selected_systems": selected_systems}
