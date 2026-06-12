from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import LLMMessageRequest, LLMMessageResponse
from ..services.llm_service import generate_message
from ..services.audit_service import log_event

router = APIRouter()


@router.post("/mock/llm/messages", response_model=LLMMessageResponse)
async def llm_messages(request: LLMMessageRequest,
                       db: Session = Depends(get_db)):
    allowed_types = {
        "employee_onboarding_summary", "manager_approval_request",
        "recommendation_explanation", "status_update",
        "onboarding_question_answer",
    }
    if request.message_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unknown message type: {request.message_type}")

    context = request.context or {}
    defaults = {
        "employee_onboarding_summary": {
            "employee_name": request.employee_id,
            "role": "Unknown", "level": "Unknown",
            "training_summary": "T1 incomplete, others pending",
            "recommended_systems_list": "No recommendations available",
            "optional_systems_list": "None",
            "manager_name": "your manager",
        },
        "manager_approval_request": {
            "manager_name": "Manager",
            "employee_name": request.employee_id,
            "role": "Unknown", "level": "Unknown",
            "selected_systems_list": "No systems selected",
            "correlation_id": request.correlation_id,
            "request_id": "unknown",
        },
        "recommendation_explanation": {
            "role": "Unknown",
            "systems": "None",
        },
        "status_update": {
            "status": "in progress",
            "employee_name": request.employee_id,
        },
        "onboarding_question_answer": {
            "answer": "No additional information available.",
        },
    }

    for k, v in defaults.get(request.message_type, {}).items():
        context.setdefault(k, v)

    message, provider = await generate_message(
        request.message_type, context, fallback_enabled=True,
    )
    fallback_used = provider == "fallback"

    action = "llm_fallback_used" if fallback_used else "message_generated"
    status_str = "FALLBACK" if fallback_used else "GENERATED"
    log_event(db, request.correlation_id, request.employee_id,
              "system", "llm-mock",
              action, "llm", request.correlation_id,
              status_str, None, {"provider": provider})
    db.commit()

    return LLMMessageResponse(
        ok=True, status="GENERATED",
        message=message,
        generated_message=message,
        llm_provider=provider,
        fallback_used=fallback_used,
        correlation_id=request.correlation_id,
    )
