import uuid
import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import exc as sa_exc
from ..models import ITSMTicket, ManagerApproval, ApprovalStatus, SelectedAccessRequest

FORBIDDEN_SYSTEMS = [
    "Payroll Admin", "Production Database Admin", "Security Admin", "Finance Admin"
]


def _generate_ticket_id():
    return f"itsm_{uuid.uuid4().hex}"


def compute_idempotency_key(employee_id: str, request_id: str, approval_id: str, systems: list):
    raw = f"{employee_id}|{request_id}|{approval_id}|{','.join(sorted(systems))}"
    return hashlib.sha256(raw.encode()).hexdigest()


def create_ticket(db: Session, employee_id: str, approval_id: str,
                  requested_systems: list, idempotency_key: str = None,
                  simulate_failure: bool = False):
    approval = db.query(ManagerApproval).filter(
        ManagerApproval.approval_id == approval_id
    ).first()
    if not approval:
        return {
            "ok": False, "status": "BLOCKED",
            "error_code": "APPROVAL_NOT_FOUND",
            "reason_code": "MANAGER_APPROVAL_REQUIRED",
            "pre_approval_blocked": True,
            "ticket_created": False,
        }
    if approval.status != ApprovalStatus.APPROVED:
        return {
            "ok": False, "status": "BLOCKED",
            "error_code": "MANAGER_APPROVAL_REQUIRED",
            "reason_code": "MANAGER_APPROVAL_REQUIRED",
            "pre_approval_blocked": True,
            "ticket_created": False,
        }
    if approval.employee_id != employee_id:
        return {
            "ok": False, "status": "BLOCKED",
            "error_code": "EMPLOYEE_MISMATCH",
            "reason_code": "EMPLOYEE_MISMATCH",
            "pre_approval_blocked": True,
            "ticket_created": False,
        }

    for sys_name in (requested_systems or []):
        if sys_name in FORBIDDEN_SYSTEMS:
            return {
                "ok": False, "status": "BLOCKED",
                "error_code": "FORBIDDEN_SYSTEM_SELECTED",
                "reason_code": "FORBIDDEN_SYSTEM_SELECTED",
                "pre_approval_blocked": True,
                "ticket_created": False,
            }

    selection = db.query(SelectedAccessRequest).filter(
        SelectedAccessRequest.request_id == approval.request_id
    ).first()
    if selection:
        approved_systems = set(selection.selected_systems or [])
        req_systems = set(requested_systems or [])
        if req_systems != approved_systems:
            return {
                "ok": False, "status": "BLOCKED",
                "error_code": "SYSTEM_MISMATCH",
                "reason_code": "REQUESTED_SYSTEMS_MISMATCH",
                "pre_approval_blocked": True,
                "ticket_created": False,
            }

    if simulate_failure:
        return {
            "ok": False, "status": "FAILED",
            "error_code": "ITSM_MOCK_FAILURE",
            "reason_code": "ITSM_MOCK_FAILURE",
            "ticket_created": False,
            "recoverable": True,
            "next_action": "RETRY_ITSM_TICKET",
        }

    if not idempotency_key:
        idempotency_key = compute_idempotency_key(
            employee_id, approval.request_id, approval_id, requested_systems
        )

    existing = db.query(ITSMTicket).filter(
        ITSMTicket.idempotency_key == idempotency_key
    ).first()
    if existing:
        if (existing.employee_id != employee_id
                or existing.approval_id != approval_id
                or set(existing.selected_systems or []) != set(requested_systems or [])):
            return {
                "ok": False, "status": "BLOCKED",
                "error_code": "IDEMPOTENCY_KEY_MISMATCH",
                "reason_code": "IDEMPOTENCY_KEY_MISMATCH",
                "pre_approval_blocked": True,
                "ticket_created": False,
            }
        return {
            "ok": True, "status": "CREATED",
            "ticket_id": existing.ticket_id,
            "duplicate": True,
            "ticket_created": True,
        }

    ticket_id = _generate_ticket_id()
    ticket = ITSMTicket(
        ticket_id=ticket_id,
        request_id=approval.request_id,
        employee_id=employee_id,
        approval_id=approval_id,
        selected_systems=requested_systems,
        status="CREATED",
        idempotency_key=idempotency_key,
    )
    db.add(ticket)
    try:
        db.flush()
    except sa_exc.IntegrityError:
        db.rollback()
        existing = db.query(ITSMTicket).filter(
            ITSMTicket.idempotency_key == idempotency_key
        ).first()
        if existing:
            if (existing.employee_id != employee_id
                    or existing.approval_id != approval_id
                    or set(existing.selected_systems or []) != set(requested_systems or [])):
                return {
                    "ok": False, "status": "BLOCKED",
                    "error_code": "IDEMPOTENCY_KEY_MISMATCH",
                    "reason_code": "IDEMPOTENCY_KEY_MISMATCH",
                    "pre_approval_blocked": True,
                    "ticket_created": False,
                }
            return {
                "ok": True, "status": "CREATED",
                "ticket_id": existing.ticket_id,
                "duplicate": True,
                "ticket_created": True,
            }
        return {"error": "DUPLICATE_TICKET"}
    return {
        "ok": True, "status": "CREATED",
        "ticket_id": ticket_id,
        "request_id": approval.request_id,
        "approval_id": approval_id,
        "employee_id": employee_id,
        "requested_systems": requested_systems,
        "ticket_created": True,
    }
