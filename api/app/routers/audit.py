from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import AuditEvent
from ..schemas import AuditEventOut, AuditEventsResponse

router = APIRouter()


@router.get("/audit/events", response_model=AuditEventsResponse)
def get_audit_events(correlation_id: str = Query(None),
                     employee_id: str = Query(None),
                     action: str = Query(None),
                     db: Session = Depends(get_db)):
    q = db.query(AuditEvent)
    if correlation_id:
        q = q.filter(AuditEvent.correlation_id == correlation_id)
    if employee_id:
        q = q.filter(AuditEvent.employee_id == employee_id)
    if action:
        q = q.filter(AuditEvent.action == action)
    events = q.order_by(AuditEvent.event_id).all()

    return AuditEventsResponse(
        ok=True,
        events=[AuditEventOut(
            event_id=e.event_id,
            correlation_id=e.correlation_id,
            employee_id=e.employee_id,
            actor_type=e.actor_type,
            actor_id=e.actor_id,
            action=e.action,
            target_type=e.target_type,
            target_id=e.target_id,
            status=e.status,
            reason_code=e.reason_code,
            metadata_json=e.metadata_json,
            created_at=e.created_at,
        ) for e in events],
        count=len(events),
    )


@router.get("/audit/workflows/{correlation_id}", response_model=AuditEventsResponse)
def get_workflow_audit(correlation_id: str, db: Session = Depends(get_db)):
    events = db.query(AuditEvent).filter(
        AuditEvent.correlation_id == correlation_id
    ).order_by(AuditEvent.event_id).all()

    return AuditEventsResponse(
        ok=True,
        events=[AuditEventOut(
            event_id=e.event_id,
            correlation_id=e.correlation_id,
            employee_id=e.employee_id,
            actor_type=e.actor_type,
            actor_id=e.actor_id,
            action=e.action,
            target_type=e.target_type,
            target_id=e.target_id,
            status=e.status,
            reason_code=e.reason_code,
            metadata_json=e.metadata_json,
            created_at=e.created_at,
        ) for e in events],
        count=len(events),
    )
