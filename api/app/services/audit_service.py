from sqlalchemy.orm import Session
from ..models import AuditEvent
from datetime import datetime, timezone

def log_event(db: Session, correlation_id: str, employee_id: str | None, actor_type: str, actor_id: str | None,
              action: str, target_type: str | None, target_id: str | None, status: str, reason_code: str = None, metadata: dict = None):
    event = AuditEvent(
        correlation_id=correlation_id,
        employee_id=employee_id,
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        status=status,
        reason_code=reason_code,
        metadata_json=metadata,
        created_at=datetime.now(timezone.utc)
    )
    db.add(event)
    db.commit()
