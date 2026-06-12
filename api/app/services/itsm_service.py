from sqlalchemy.orm import Session
from ..models import ITSMTicket, ManagerApproval, SelectedAccessRequest
import uuid

def create_ticket(db: Session, employee_id: str, approval_id: str, requested_systems: list, idempotency_key: str):
    existing = db.query(ITSMTicket).filter(ITSMTicket.idempotency_key == idempotency_key).first()
    if existing:
        return {"ticket_id": existing.ticket_id, "status": "EXISTING", "created": False}

    approval = db.query(ManagerApproval).filter(ManagerApproval.approval_id == approval_id).first()
    if not approval:
        return {"error": "APPROVAL_NOT_FOUND", "ticket_created": False}
    if approval.status.value != "APPROVED":
        return {"error": "APPROVAL_NOT_APPROVED", "status": approval.status.value, "ticket_created": False}

    access_request = db.query(SelectedAccessRequest).filter(SelectedAccessRequest.approval_id == approval_id).first()
    if not access_request:
        return {"error": "REQUEST_NOT_FOUND", "ticket_created": False}

    ticket_id = f"tkt_{uuid.uuid4().hex[:8]}"
    ticket = ITSMTicket(
        ticket_id=ticket_id,
        request_id=access_request.request_id,
        employee_id=employee_id,
        selected_systems=requested_systems,
        status="CREATED",
        idempotency_key=idempotency_key
    )
    db.add(ticket)
    access_request.ticket_id = ticket_id
    db.commit()

    return {"ticket_id": ticket_id, "status": "CREATED", "created": True}
