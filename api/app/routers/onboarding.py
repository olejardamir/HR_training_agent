import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Employee, OnboardingSession, SelectedAccessRequest
from ..schemas import (
    OnboardingStartRequest, OnboardingStatusResponse,
    SelectAccessRequest, SelectAccessResponse,
    OnboardingQuestionRequest, OnboardingQuestionResponse,
)
from ..services.audit_service import log_event
from ..services.selection_service import validate_selection
from ..services.recommendation_service import get_recommendations
from ..services.employee_service import get_employee

router = APIRouter()


@router.post("/onboarding/start/{employee_id}")
def start_onboarding(employee_id: str, request: OnboardingStartRequest,
                     db: Session = Depends(get_db)):
    emp = get_employee(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail={
            "ok": False, "error_code": "EMPLOYEE_NOT_FOUND",
            "message": f"Employee {employee_id} not found",
        })
    existing = db.query(OnboardingSession).filter(
        OnboardingSession.employee_id == employee_id
    ).first()
    if existing:
        existing.correlation_id = request.correlation_id
    else:
        session = OnboardingSession(
            employee_id=employee_id, correlation_id=request.correlation_id
        )
        db.add(session)
    log_event(db, request.correlation_id, employee_id, "system", "onboarding",
              "workflow_started", "session", employee_id, "STARTED", None)
    db.commit()
    return {
        "ok": True, "status": "STARTED", "message": "Onboarding session started.",
        "employee_id": employee_id, "correlation_id": request.correlation_id,
        "next_action": "FETCH_PROFILE",
    }


@router.get("/onboarding/status/{employee_id}", response_model=OnboardingStatusResponse)
def get_onboarding_status(employee_id: str, db: Session = Depends(get_db)):
    session = db.query(OnboardingSession).filter(
        OnboardingSession.employee_id == employee_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="No onboarding session found")
    return OnboardingStatusResponse(
        employee_id=session.employee_id,
        status="active",
        correlation_id=session.correlation_id,
        session_id=session.session_id,
    )


@router.post("/onboarding/select-access", response_model=SelectAccessResponse)
def select_access(request: SelectAccessRequest, db: Session = Depends(get_db)):
    validation = validate_selection(db, request.employee_id, request.selected_systems)
    if "error" in validation:
        error = validation["error"]
        if error == "NO_ACTIVE_SESSION":
            raise HTTPException(status_code=409, detail="No active onboarding session")
        if error == "FORBIDDEN_SYSTEM_SELECTED":
            log_event(db, request.correlation_id, request.employee_id,
                      "employee", request.employee_id,
                      "selection_blocked", "selection", None, "BLOCKED",
                      "FORBIDDEN_SYSTEM_SELECTED",
                      {"system": validation.get("system")})
            db.commit()
            raise HTTPException(status_code=403, detail={
                "ok": False, "error_code": "FORBIDDEN_SYSTEM_SELECTED",
                "message": f"System '{validation.get('system')}' is forbidden",
                "employee_id": request.employee_id,
                "correlation_id": request.correlation_id,
            })
        if error == "UNKNOWN_SYSTEM_SELECTED":
            log_event(db, request.correlation_id, request.employee_id,
                      "employee", request.employee_id,
                      "selection_blocked", "selection", None, "BLOCKED",
                      "UNKNOWN_SYSTEM_SELECTED",
                      {"system": validation.get("system")})
            db.commit()
            return JSONResponse(status_code=403, content={
                "ok": False, "status": "BLOCKED",
                "error_code": "UNKNOWN_SYSTEM_SELECTED",
                "message": f"System '{validation.get('system')}' is not a recognized system",
                "employee_id": request.employee_id,
                "correlation_id": request.correlation_id,
            })
        raise HTTPException(status_code=400, detail=error)

    selected = validation["selected_systems"]
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    selection = SelectedAccessRequest(
        request_id=request_id,
        employee_id=request.employee_id,
        selected_systems=selected,
        status="EMPLOYEE_SELECTED",
        idempotency_key=f"sel_{request.employee_id}_{uuid.uuid4().hex[:6]}",
    )
    db.add(selection)
    db.flush()

    log_event(db, request.correlation_id, request.employee_id,
              "employee", request.employee_id,
              "selection_validated", "selection", request.employee_id,
              "VALIDATED", None)

    log_event(db, request.correlation_id, request.employee_id,
              "employee", request.employee_id,
              "selection_received", "selection", selection.request_id,
              "SUCCESS", None, {"systems": selected})

    db.commit()
    db.refresh(selection)

    return SelectAccessResponse(
        ok=True, status="EMPLOYEE_SELECTED",
        employee_id=request.employee_id,
        request_id=selection.request_id,
        selected_systems=selected,
        correlation_id=request.correlation_id,
        next_action="REQUEST_MANAGER_APPROVAL",
    )


@router.post("/onboarding/questions", response_model=OnboardingQuestionResponse)
def onboarding_questions(request: OnboardingQuestionRequest,
                         db: Session = Depends(get_db)):
    from ..services.policy_service import get_policy, get_peer_pattern

    emp = get_employee(db, request.employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    training = db.query(SelectedAccessRequest).filter(
        SelectedAccessRequest.employee_id == request.employee_id
    ).all()

    question_lower = request.question.lower()

    forbidden_words = ["approve", "grant", "create ticket", "bypass", "override",
                       "change role", "change level", "change manager", "promote"]
    for word in forbidden_words:
        if word in question_lower:
            log_event(db, request.correlation_id, request.employee_id,
                      "employee", request.employee_id,
                      "question_blocked", "qna", None, "BLOCKED",
                      "QUESTION_OUT_OF_SCOPE",
                      {"question": request.question})
            return OnboardingQuestionResponse(
                ok=False, status="BLOCKED",
                error_code="QUESTION_OUT_OF_SCOPE",
                message="I can explain onboarding status and recommendations, "
                        "but I cannot approve or grant access.",
                correlation_id=request.correlation_id,
            )

    if "role" in question_lower or "level" in question_lower:
        answer = (f"Your role is {emp.role} (Level {emp.level}) "
                  f"in the {emp.department} department.")
    elif "training" in question_lower or "module" in question_lower:
        from ..services.training_service import get_training_status
        modules = get_training_status(db, request.employee_id)
        if not modules:
            answer = "No training records found."
        else:
            statuses = ", ".join(f"{m['module_id']}: {m['status']}" for m in modules)
            answer = f"Your training status: {statuses}."
    elif "recommend" in question_lower or "system" in question_lower or "access" in question_lower:
        rec, _ = get_recommendations(db, request.employee_id)
        if rec and rec.get("recommendations"):
            names = [r["system"] for r in rec["recommendations"]]
            codes = []
            policy = get_policy(db, emp.role, emp.level)
            if policy:
                codes = policy.reason_codes if hasattr(policy, 'reason_codes') else []
            answer = (f"Salesforce was recommended because it is listed in the "
                      f"{emp.role} L{emp.level} policy and appears in same-role "
                      f"peer access patterns.")
        else:
            answer = "No recommendations are available yet."
    elif "manager" in question_lower:
        answer = f"Your manager ID is {emp.manager_id or 'not assigned'}."
    else:
        answer = ("I can answer questions about your role, training, "
                  "recommendations, manager, or onboarding status.")

    log_event(db, request.correlation_id, request.employee_id,
              "employee", request.employee_id,
              "question_answered", "qna", None, "ANSWERED", None,
              {"question": request.question})

    return OnboardingQuestionResponse(
        ok=True, status="ANSWERED",
        employee_id=request.employee_id,
        answer=answer,
        source="deterministic_context",
        correlation_id=request.correlation_id,
    )
