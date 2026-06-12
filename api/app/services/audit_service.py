from ..models import AuditEvent
from ..database import SessionLocal


def log_event(db, correlation_id, employee_id, actor_type, actor_id,
              action, target_type=None, target_id=None, status=None,
              reason_code=None, metadata_json=None):
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
        metadata_json=metadata_json,
    )
    db.add(event)
    db.flush()
    return event
