import uuid
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import Employee, TrainingStatusTable, EmploymentStatus, SelectedAccessRequest, AuditEvent, OnboardingSession, SlackMessage
from .schemas import (
    EmployeeResponse, TrainingStatusResponse, AccessRecommendationResponse,
    AccessSelectionRequest, AccessSelectionResponse, ApprovalResponse,
    TicketRequest, TicketResponse, LLMMessageRequest, LLMMessageResponse,
    OnboardingStartRequest, SlackMessageRequest, SlackMessageResponse
)
from .logic.access_recommender import get_access_recommendations
from .services.approval_service import create_approval, get_approval, approve_approval, reject_approval, expire_approval
from .services.itsm_service import create_ticket
from .services.audit_service import log_event
from .services.llm_service import generate_message

app = FastAPI(title="HR Onboarding Agent API")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/mock/hr/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail={
            "ok": False, "error_code": "EMPLOYEE_NOT_FOUND",
            "message": f"Employee {employee_id} not found"
        })
    if emp.employment_status != EmploymentStatus.NEW_HIRE:
        raise HTTPException(status_code=403, detail={
            "ok": False, "error_code": "EMPLOYEE_NOT_ACTIVE",
            "message": "Employee is not active/new hire"
        })
    return emp


@app.get("/mock/training/status/{employee_id}", response_model=TrainingStatusResponse)
def get_training_status(employee_id: str, db: Session = Depends(get_db)):
    training = db.query(TrainingStatusTable).filter(TrainingStatusTable.employee_id == employee_id).first()
    if not training:
        return {"employee_id": employee_id, "modules": []}
    return training


@app.get("/mock/access/recommendations/{employee_id}", response_model=AccessRecommendationResponse)
def access_recommendations(employee_id: str, db: Session = Depends(get_db)):
    result, error = get_access_recommendations(employee_id, db)
    if error == "EMPLOYEE_NOT_FOUND":
        raise HTTPException(status_code=404, detail={
            "error_code": "EMPLOYEE_NOT_FOUND", "message": "Employee not found"
        })
    if error == "UNKNOWN_ROLE_LEVEL":
        raise HTTPException(status_code=409, detail={
            "error_code": "UNKNOWN_ROLE_LEVEL", "message": "Employee role or level is missing"
        })
    if error == "POLICY_NOT_FOUND":
        raise HTTPException(status_code=404, detail={
            "error_code": "POLICY_NOT_FOUND", "message": "No policy for this role/level"
        })
    return result


@app.post("/demo/reset")
def reset_demo():
    from .seed import reset_and_seed
    reset_and_seed()
    return {"status": "reset_complete"}


@app.post("/onboarding/select-access", response_model=AccessSelectionResponse)
def select_access(request: AccessSelectionRequest, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == request.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    rec, error = get_access_recommendations(request.employee_id, db)
    if error:
        raise HTTPException(status_code=400, detail="Cannot select access: recommendations unavailable")

    forbidden = [block["system"] for block in rec["blocked_systems"]]
    for sys in request.selected_systems:
        if sys in forbidden:
            log_event(db, request.correlation_id, request.employee_id, "employee", request.employee_id,
                      "SELECT_ACCESS", "selection", None, "BLOCKED", "FORBIDDEN_SYSTEM_SELECTED",
                      {"selected_system": sys})
            raise HTTPException(status_code=403, detail=f"System '{sys}' is forbidden for this role/level")

    request_id = db.query(SelectedAccessRequest).count() + 1
    selection = SelectedAccessRequest(
        request_id=request_id,
        employee_id=request.employee_id,
        selected_systems=request.selected_systems,
        status="EMPLOYEE_SELECTED",
        idempotency_key=f"sel_{request.employee_id}_{uuid.uuid4().hex[:6]}"
    )
    db.add(selection)
    db.commit()
    db.refresh(selection)

    log_event(db, request.correlation_id, request.employee_id, "employee", request.employee_id,
              "SELECT_ACCESS", "selection", str(request_id), "SUCCESS", None, {"systems": request.selected_systems})

    return AccessSelectionResponse(
        request_id=selection.request_id,
        employee_id=selection.employee_id,
        selected_systems=selection.selected_systems,
        status=selection.status
    )


@app.post("/mock/approvals", response_model=ApprovalResponse)
def create_approval_endpoint(employee_id: str, request_id: int, manager_id: str, correlation_id: str, db: Session = Depends(get_db)):
    selection = db.query(SelectedAccessRequest).filter(SelectedAccessRequest.request_id == request_id).first()
    if not selection:
        raise HTTPException(status_code=404, detail="Selection request not found")
    approval = create_approval(db, employee_id, request_id, manager_id)
    selection.approval_id = approval.approval_id
    db.commit()
    log_event(db, correlation_id, employee_id, "system", "approval-service",
              "CREATE_APPROVAL", "approval", approval.approval_id, "PENDING", None)
    return approval


@app.get("/mock/approvals/{approval_id}", response_model=ApprovalResponse)
def get_approval_endpoint(approval_id: str, db: Session = Depends(get_db)):
    approval = get_approval(db, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval


@app.post("/mock/approvals/{approval_id}/approve", response_model=ApprovalResponse)
def approve(approval_id: str, decided_by: str, decision_reason: str, correlation_id: str, db: Session = Depends(get_db)):
    approval = approve_approval(db, approval_id, decided_by, decision_reason)
    if not approval:
        raise HTTPException(status_code=403, detail="Not authorized or approval not found")
    log_event(db, correlation_id, approval.employee_id, "manager", decided_by,
              "APPROVE_APPROVAL", "approval", approval_id, approval.status.value, None)
    return approval


@app.post("/mock/approvals/{approval_id}/reject", response_model=ApprovalResponse)
def reject(approval_id: str, decided_by: str, decision_reason: str, correlation_id: str, db: Session = Depends(get_db)):
    approval = reject_approval(db, approval_id, decided_by, decision_reason)
    if not approval:
        raise HTTPException(status_code=403, detail="Not authorized or approval not found")
    log_event(db, correlation_id, approval.employee_id, "manager", decided_by,
              "REJECT_APPROVAL", "approval", approval_id, approval.status.value, None)
    return approval


@app.post("/mock/approvals/{approval_id}/expire", response_model=ApprovalResponse)
def expire(approval_id: str, db: Session = Depends(get_db)):
    approval = expire_approval(db, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval


@app.post("/mock/itsm/tickets", response_model=TicketResponse)
def create_ticket_endpoint(request: TicketRequest, db: Session = Depends(get_db)):
    result = create_ticket(db, request.employee_id, request.approval_id, request.requested_systems, request.idempotency_key)
    if "error" in result:
        status_code = 403 if result["error"] in ("APPROVAL_NOT_APPROVED",) else 404
        raise HTTPException(status_code=status_code, detail=result["error"])
    log_event(db, request.correlation_id, request.employee_id, "system", "itsm-mock",
              "CREATE_TICKET", "ticket", result.get("ticket_id"), "CREATED", None)
    return TicketResponse(ticket_id=result.get("ticket_id"), status=result["status"], created=result.get("created", False))


@app.get("/audit/events")
def get_audit_events(correlation_id: str = None, db: Session = Depends(get_db)):
    query = db.query(AuditEvent)
    if correlation_id:
        query = query.filter(AuditEvent.correlation_id == correlation_id)
    events = query.order_by(AuditEvent.event_id).all()
    return events


@app.post("/onboarding/start/{employee_id}")
def start_onboarding(employee_id: str, request: OnboardingStartRequest, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    existing = db.query(OnboardingSession).filter(OnboardingSession.employee_id == employee_id).first()
    if existing:
        existing.correlation_id = request.correlation_id
        existing.status = "STARTED"
    else:
        session = OnboardingSession(
            employee_id=employee_id,
            correlation_id=request.correlation_id,
            status="STARTED"
        )
        db.add(session)
    db.commit()
    log_event(db, request.correlation_id, employee_id, "system", "onboarding",
              "START_ONBOARDING", "session", employee_id, "STARTED", None)
    return {"status": "started", "employee_id": employee_id, "correlation_id": request.correlation_id}


@app.get("/onboarding/status/{employee_id}")
def get_onboarding_status(employee_id: str, db: Session = Depends(get_db)):
    session = db.query(OnboardingSession).filter(OnboardingSession.employee_id == employee_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="No onboarding session found")
    return {
        "employee_id": session.employee_id,
        "status": session.status,
        "correlation_id": session.correlation_id,
        "created_at": str(session.created_at) if session.created_at else None
    }


@app.post("/mock/slack/messages", response_model=SlackMessageResponse)
def store_slack_message(request: SlackMessageRequest, db: Session = Depends(get_db)):
    msg = SlackMessage(
        channel_or_user=request.channel_or_user,
        message_type=request.message_type,
        message=request.message,
        metadata_json=request.metadata
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return SlackMessageResponse(message_id=msg.message_id, status="stored")


@app.post("/mock/llm/messages", response_model=LLMMessageResponse)
async def llm_messages(request: LLMMessageRequest):
    context = request.context or {}
    if request.message_type == "employee_onboarding_summary":
        context.setdefault("employee_name", request.employee_id)
        context.setdefault("role", "Unknown")
        context.setdefault("level", "Unknown")
        context.setdefault("training_summary", "T1 incomplete, others pending")
        context.setdefault("recommended_systems_list", "No recommendations available")
        context.setdefault("optional_systems_list", "None")
        context.setdefault("manager_name", "your manager")
    elif request.message_type == "manager_approval_request":
        context.setdefault("manager_name", "Manager")
        context.setdefault("employee_name", request.employee_id)
        context.setdefault("role", "Unknown")
        context.setdefault("level", "Unknown")
        context.setdefault("selected_systems_list", "No systems selected")
        context.setdefault("correlation_id", request.correlation_id)
        context.setdefault("request_id", "unknown")

    message = await generate_message(
        message_type=request.message_type,
        context=context,
        fallback_enabled=True
    )
    return LLMMessageResponse(
        message=message,
        message_type=request.message_type,
        generated_by="ollama_fallback"
    )
