from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import SelectedAccessRequest, Employee
from ..schemas import (
    CreateApprovalRequest, ApprovalDecisionRequest, ApprovalResponse,
)
from ..services.approval_service import (
    create_approval, get_approval, approve_approval,
    reject_approval, expire_approval,
)
from ..services.audit_service import log_event

router = APIRouter()


def _build_approval_response(approval, correlation_id: str) -> ApprovalResponse:
    is_approved = approval.status.value == "APPROVED"
    next_action = {
        "APPROVED": "CREATE_ITSM_TICKET",
        "REJECTED": "NO_TICKET",
        "EXPIRED": "NO_TICKET",
        "PENDING": "WAIT_FOR_MANAGER_DECISION",
    }.get(approval.status.value, "WAIT_FOR_MANAGER_DECISION")
    return ApprovalResponse(
        ok=True, status=approval.status.value,
        approval_status=approval.status.value,
        approval_is_approved=is_approved,
        approval_id=approval.approval_id,
        request_id=str(approval.request_id),
        employee_id=approval.employee_id,
        manager_id=approval.manager_id,
        correlation_id=correlation_id,
        next_action=next_action,
    )


@router.post("/mock/approvals", response_model=ApprovalResponse)
def create_approval_endpoint(request: CreateApprovalRequest,
                             db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(
        Employee.employee_id == request.employee_id
    ).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    if not emp.manager_id:
        raise HTTPException(status_code=409, detail={
            "ok": False, "error_code": "MISSING_MANAGER",
            "message": "Employee has no manager assigned",
            "employee_id": request.employee_id,
        })
    if request.manager_id != emp.manager_id:
        log_event(db, request.correlation_id, request.employee_id,
                  "manager", request.manager_id,
                  "wrong_manager_blocked", "approval", None,
                  "BLOCKED", "WRONG_MANAGER",
                  {"expected_manager": emp.manager_id})
        raise HTTPException(status_code=403, detail={
            "ok": False, "error_code": "WRONG_MANAGER",
            "message": f"Expected manager {emp.manager_id}, got {request.manager_id}",
            "employee_id": request.employee_id,
        })

    request_id = int(request.request_id) if request.request_id.isdigit() else request.request_id
    selection = db.query(SelectedAccessRequest).filter(
        SelectedAccessRequest.request_id == request_id
    ).first()
    if not selection:
        raise HTTPException(status_code=404, detail="Selection request not found")

    approval = create_approval(db, request.employee_id, selection.request_id,
                               request.manager_id)
    if isinstance(approval, dict) and "error" in approval:
        raise HTTPException(status_code=400, detail=approval["error"])

    selection.approval_id = approval.approval_id
    db.commit()

    log_event(db, request.correlation_id, request.employee_id,
              "system", "approval-service",
              "approval_requested", "approval", approval.approval_id,
              "PENDING", None)

    return _build_approval_response(approval, request.correlation_id)


@router.get("/mock/approvals/{approval_id}", response_model=ApprovalResponse)
def get_approval_endpoint(approval_id: str, correlation_id: str = None,
                          db: Session = Depends(get_db)):
    approval = get_approval(db, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return _build_approval_response(approval, correlation_id or "")


@router.post("/mock/approvals/{approval_id}/approve", response_model=ApprovalResponse)
def approve(approval_id: str, request: ApprovalDecisionRequest,
            db: Session = Depends(get_db)):
    approval = approve_approval(db, approval_id, request.decided_by,
                                request.decision_reason)
    if not approval:
        raise HTTPException(status_code=403, detail={
            "ok": False, "error_code": "NOT_AUTHORIZED",
            "message": "Not authorized or approval not found",
        })
    log_event(db, request.correlation_id, approval.employee_id,
              "manager", request.decided_by,
              "approval_approved", "approval", approval_id,
              approval.status.value, None)
    db.commit()
    return _build_approval_response(approval, request.correlation_id)


@router.post("/mock/approvals/{approval_id}/reject", response_model=ApprovalResponse)
def reject(approval_id: str, request: ApprovalDecisionRequest,
           db: Session = Depends(get_db)):
    approval = reject_approval(db, approval_id, request.decided_by,
                               request.decision_reason)
    if not approval:
        raise HTTPException(status_code=403, detail={
            "ok": False, "error_code": "NOT_AUTHORIZED",
            "message": "Not authorized or approval not found",
        })
    log_event(db, request.correlation_id, approval.employee_id,
              "manager", request.decided_by,
              "approval_rejected", "approval", approval_id,
              approval.status.value, None)
    db.commit()
    return _build_approval_response(approval, request.correlation_id)


@router.post("/mock/approvals/{approval_id}/expire", response_model=ApprovalResponse)
def expire(approval_id: str, request: ApprovalDecisionRequest = None,
           db: Session = Depends(get_db)):
    correlation_id = request.correlation_id if request else ""
    approval = expire_approval(db, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if correlation_id:
        log_event(db, correlation_id, approval.employee_id,
                  "system", "system",
                  "approval_expired", "approval", approval_id,
                  approval.status.value, None)
    db.commit()
    return _build_approval_response(approval, correlation_id)



