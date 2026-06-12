import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models import ManagerApproval, SelectedAccessRequest, ApprovalStatus, Employee


def _generate_approval_id():
    return f"apr_{uuid.uuid4().hex}"


def create_approval(db: Session, employee_id: str, request_id: str, manager_id: str):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        return {"error": "EMPLOYEE_NOT_FOUND"}
    if manager_id != emp.manager_id:
        return {"error": "WRONG_MANAGER"}

    existing = db.query(ManagerApproval).filter(
        ManagerApproval.request_id == request_id
    ).first()
    if existing:
        return existing

    approval_id = _generate_approval_id()
    approval = ManagerApproval(
        approval_id=approval_id,
        request_id=request_id,
        employee_id=employee_id,
        manager_id=manager_id,
        status=ApprovalStatus.PENDING,
    )
    db.add(approval)
    db.flush()
    return approval


def get_approval(db: Session, approval_id: str):
    return db.query(ManagerApproval).filter(ManagerApproval.approval_id == approval_id).first()


def approve_approval(db: Session, approval_id: str, decided_by: str, decision_reason: str):
    approval = get_approval(db, approval_id)
    if not approval:
        return None
    if approval.status != ApprovalStatus.PENDING:
        return approval
    if decided_by != approval.manager_id:
        return {
            "error": "WRONG_MANAGER",
            "expected_manager": approval.manager_id,
            "decided_by": decided_by,
        }
    approval.status = ApprovalStatus.APPROVED
    approval.decided_by = decided_by
    approval.decision_reason = decision_reason
    approval.approved_at = datetime.now(timezone.utc)
    db.flush()
    return approval


def reject_approval(db: Session, approval_id: str, decided_by: str, decision_reason: str):
    approval = get_approval(db, approval_id)
    if not approval:
        return None
    if approval.status != ApprovalStatus.PENDING:
        return approval
    if decided_by != approval.manager_id:
        return {
            "error": "WRONG_MANAGER",
            "expected_manager": approval.manager_id,
            "decided_by": decided_by,
        }
    approval.status = ApprovalStatus.REJECTED
    approval.decided_by = decided_by
    approval.decision_reason = decision_reason
    approval.rejected_at = datetime.now(timezone.utc)
    db.flush()
    return approval


def expire_approval(db: Session, approval_id: str):
    approval = get_approval(db, approval_id)
    if not approval:
        return None
    if approval.status != ApprovalStatus.PENDING:
        return approval
    approval.status = ApprovalStatus.EXPIRED
    approval.expired_at = datetime.now(timezone.utc)
    db.flush()
    return approval
