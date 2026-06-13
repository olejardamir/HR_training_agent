import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Employee, TrainingStatusTable, SalesforceProfile
from ..services.agent_response import build_answer
from ..services.agent_guardrails import (
    filter_approved_matches,
    has_approved_context,
    is_state_only_question,
    is_on_topic,
    build_no_context_answer,
    summarize_retrieval,
)
from ..services.audit_service import log_event
from ..rag import retriever

router = APIRouter(prefix="/agent", tags=["agent"])


class ChatRequest(BaseModel):
    employee_id: str
    message: str


class ChatResponse(BaseModel):
    employee_id: str
    answer: str
    used_content_ids: list
    used_chunk_ids: list
    source_ids: list
    retrieval_scores: list
    retrieval_method: str
    fallback_used: bool
    llm_used: bool
    suggested_actions: list
    state_summary: dict


@router.post("/chat", response_model=ChatResponse)
def agent_chat(req: ChatRequest, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.employee_id == req.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if not is_on_topic(req.message):
        raise HTTPException(
            status_code=400,
            detail="I can only answer HR and onboarding questions.",
        )

    training_statuses = db.query(TrainingStatusTable).filter(
        TrainingStatusTable.employee_id == req.employee_id
    ).all()
    sf_profile = db.query(SalesforceProfile).filter(
        SalesforceProfile.employee_id == req.employee_id
    ).first()

    state = {
        "role": employee.role,
        "level": employee.level,
        "department": employee.department,
        "training": [
            {"module_id": t.module_id, "status": t.status}
            for t in training_statuses
        ],
        "salesforce_setup_status": sf_profile.setup_status if sf_profile else "not_started",
        "profile_status": employee.profile_status,
    }

    retrieval = retriever.retrieve(req.message)
    raw_matches = retrieval.get("matches", [])

    approved_matches = filter_approved_matches(raw_matches)
    trace = summarize_retrieval(approved_matches, retrieval)

    has_llm = bool(os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY"))
    trace["llm_used"] = has_llm and has_approved_context(approved_matches)

    if not has_approved_context(approved_matches):
        if is_state_only_question(req.message):
            answer = _build_state_only_answer(state)
        else:
            answer = build_no_context_answer()
    else:
        answer = build_answer(req.message, state, approved_matches)

    suggested_actions = _suggest_actions(state)

    log_event(db, "agent_chat", None, req.employee_id, "employee",
              "agent_chat", "agent", None, "SUCCESS", None, {
                  "message": req.message,
                  "used_content_ids": trace["used_content_ids"],
                  "used_chunk_ids": trace["used_chunk_ids"],
                  "source_ids": trace["source_ids"],
                  "retrieval_scores": trace["retrieval_scores"],
                  "retrieval_method": trace["retrieval_method"],
                  "fallback_used": trace["fallback_used"],
                  "llm_used": trace["llm_used"],
              })
    db.commit()

    return ChatResponse(
        employee_id=req.employee_id,
        answer=answer,
        used_content_ids=trace["used_content_ids"],
        used_chunk_ids=trace["used_chunk_ids"],
        source_ids=trace["source_ids"],
        retrieval_scores=trace["retrieval_scores"],
        retrieval_method=trace["retrieval_method"],
        fallback_used=trace["fallback_used"],
        llm_used=trace["llm_used"],
        suggested_actions=suggested_actions,
        state_summary={
            "role": state["role"],
            "level": state["level"],
            "training": state["training"],
            "salesforce_setup_status": state["salesforce_setup_status"],
        },
    )


def _build_state_only_answer(state):
    parts = []
    role = state.get("role", "unknown")
    level = state.get("level", "unknown")
    parts.append(f"Your role is {role} and your level is {level}.")
    pending = [t for t in state.get("training", []) if t["status"] != "complete"]
    if pending:
        mods = ", ".join(t["module_id"] for t in pending)
        parts.append(f"Pending training: {mods}.")
    else:
        complete = [t for t in state.get("training", []) if t["status"] == "complete"]
        if complete:
            parts.append("All assigned training is complete.")
    sf = state.get("salesforce_setup_status", "not_started")
    parts.append(f"Salesforce setup status: {sf}.")
    return " ".join(parts)


def _suggest_actions(state):
    actions = []
    for t in state.get("training", []):
        if t["status"] != "complete":
            actions.append(f"complete_training_{t['module_id']}")
    if state.get("salesforce_setup_status") != "complete":
        actions.append("setup_salesforce_profile")
    if state.get("profile_status") == "active":
        actions.append("review_profile_settings")
    return actions[:3]
