from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse
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
        return JSONResponse(status_code=404, content={
            "ok": False, "status": "ERROR",
            "error_code": "EMPLOYEE_NOT_FOUND",
            "message": "Employee not found",
            "employee_id": request.employee_id,
        })
    if not emp.manager_id:
        return JSONResponse(status_code=409, content={
            "ok": False, "status": "BLOCKED",
            "error_code": "MISSING_MANAGER",
            "message": "Employee has no manager assigned",
            "employee_id": request.employee_id,
        })
    if request.manager_id != emp.manager_id:
        log_event(db, request.correlation_id, request.employee_id,
                  "manager", request.manager_id,
                  "wrong_manager_blocked", "approval", None,
                  "BLOCKED", "WRONG_MANAGER",
                  {"expected_manager": emp.manager_id})
        return JSONResponse(status_code=403, content={
            "ok": False, "status": "BLOCKED",
            "error_code": "WRONG_MANAGER",
            "message": f"Expected manager {emp.manager_id}, got {request.manager_id}",
            "employee_id": request.employee_id,
        })

    request_id = int(request.request_id) if request.request_id.isdigit() else request.request_id
    selection = db.query(SelectedAccessRequest).filter(
        SelectedAccessRequest.request_id == request_id
    ).first()
    if not selection:
        return JSONResponse(status_code=404, content={
            "ok": False, "status": "ERROR",
            "error_code": "SELECTION_NOT_FOUND",
            "message": "Selection request not found",
            "request_id": str(request_id),
        })

    approval = create_approval(db, request.employee_id, selection.request_id,
                               request.manager_id)
    if isinstance(approval, dict) and "error" in approval:
        return JSONResponse(status_code=400, content={
            "ok": False, "status": "ERROR",
            "error_code": approval["error"],
            "message": f"Approval creation failed: {approval['error']}",
        })

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
        return JSONResponse(status_code=404, content={
            "ok": False, "status": "ERROR",
            "error_code": "APPROVAL_NOT_FOUND",
            "message": f"Approval {approval_id} not found",
        })
    return _build_approval_response(approval, correlation_id or "")


@router.post("/mock/approvals/{approval_id}/approve", response_model=ApprovalResponse)
def approve(approval_id: str, request: ApprovalDecisionRequest,
            db: Session = Depends(get_db)):
    approval = approve_approval(db, approval_id, request.decided_by,
                                request.decision_reason)
    if not approval:
        return JSONResponse(status_code=404, content={
            "ok": False, "status": "ERROR",
            "error_code": "APPROVAL_NOT_FOUND",
            "message": f"Approval {approval_id} not found",
        })
    if isinstance(approval, dict) and "error" in approval:
        return JSONResponse(status_code=403, content={
            "ok": False, "status": "BLOCKED",
            "error_code": "WRONG_MANAGER",
            "message": f"Wrong manager. Expected {approval['expected_manager']}, got {approval['decided_by']}",
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
        return JSONResponse(status_code=404, content={
            "ok": False, "status": "ERROR",
            "error_code": "APPROVAL_NOT_FOUND",
            "message": f"Approval {approval_id} not found",
        })
    if isinstance(approval, dict) and "error" in approval:
        return JSONResponse(status_code=403, content={
            "ok": False, "status": "BLOCKED",
            "error_code": "WRONG_MANAGER",
            "message": f"Wrong manager. Expected {approval['expected_manager']}, got {approval['decided_by']}",
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
        return JSONResponse(status_code=404, content={
            "ok": False, "status": "ERROR",
            "error_code": "APPROVAL_NOT_FOUND",
            "message": f"Approval {approval_id} not found",
        })
    if correlation_id:
        log_event(db, correlation_id, approval.employee_id,
                  "system", "system",
                  "approval_expired", "approval", approval_id,
                  approval.status.value, None)
    db.commit()
    return _build_approval_response(approval, correlation_id)



