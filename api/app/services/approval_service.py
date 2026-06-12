from sqlalchemy.orm import Session
from ..models import ManagerApproval, ApprovalStatus
import uuid
from datetime import datetime, timezone

def create_approval(db: Session, employee_id: str, request_id: int, manager_id: str):
    approval_id = f"apr_{uuid.uuid4().hex[:8]}"
    approval = ManagerApproval(
        approval_id=approval_id,
        request_id=request_id,
        employee_id=employee_id,
        manager_id=manager_id,
        status=ApprovalStatus.PENDING
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval

def get_approval(db: Session, approval_id: str):
    return db.query(ManagerApproval).filter(ManagerApproval.approval_id == approval_id).first()

def approve_approval(db: Session, approval_id: str, manager_id: str, reason: str = ""):
    approval = get_approval(db, approval_id)
    if not approval or approval.manager_id != manager_id:
        return None
    if approval.status != ApprovalStatus.PENDING:
        return approval
    approval.status = ApprovalStatus.APPROVED
    approval.approved_at = datetime.now(timezone.utc)
    approval.decision_reason = reason
    db.commit()
    db.refresh(approval)
    return approval

def reject_approval(db: Session, approval_id: str, manager_id: str, reason: str = ""):
    approval = get_approval(db, approval_id)
    if not approval or approval.manager_id != manager_id:
        return None
    if approval.status != ApprovalStatus.PENDING:
        return approval
    approval.status = ApprovalStatus.REJECTED
    approval.rejected_at = datetime.now(timezone.utc)
    approval.decision_reason = reason
    db.commit()
    db.refresh(approval)
    return approval

def expire_approval(db: Session, approval_id: str):
    approval = get_approval(db, approval_id)
    if not approval:
        return None
    if approval.status == ApprovalStatus.PENDING:
        approval.status = ApprovalStatus.EXPIRED
        db.commit()
        db.refresh(approval)
    return approval
