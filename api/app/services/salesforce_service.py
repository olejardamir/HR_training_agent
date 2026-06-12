from sqlalchemy.orm import Session
from ..models import SalesforceProfile
from datetime import datetime, timezone


def get_profile(db: Session, employee_id: str):
    return db.query(SalesforceProfile).filter(
        SalesforceProfile.employee_id == employee_id
    ).first()


def update_profile(db: Session, employee_id: str, profile_complete: bool = None,
                   role_profile: str = None):
    profile = get_profile(db, employee_id)
    if not profile:
        return {"error": "PROFILE_NOT_FOUND"}
    if profile_complete is not None:
        profile.profile_complete = profile_complete
        profile.setup_status = "completed" if profile_complete else "pending"
    profile.last_updated = datetime.now(timezone.utc)
    db.flush()
    return {
        "employee_id": employee_id,
        "profile_complete": profile.profile_complete,
        "setup_status": profile.setup_status,
    }
