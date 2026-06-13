from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Employee, TrainingStatusTable, SalesforceProfile
from ..services.agent_response import build_answer
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
    suggested_actions: list
    state_summary: dict


@router.post("/chat", response_model=ChatResponse)
def agent_chat(req: ChatRequest, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.employee_id == req.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

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
    matches = retrieval.get("matches", [])

    answer = build_answer(req.message, state, matches)

    used_content_ids = list(set(m["content_id"] for m in matches))
    used_chunk_ids = list(set(m["chunk_id"] for m in matches))

    suggested_actions = _suggest_actions(state)

    log_event(db, "agent_chat", None, req.employee_id, "employee",
              "agent_chat", "agent", None, "SUCCESS", None,
              {"message": req.message, "used_chunk_ids": used_chunk_ids})
    db.commit()

    return ChatResponse(
        employee_id=req.employee_id,
        answer=answer,
        used_content_ids=used_content_ids,
        used_chunk_ids=used_chunk_ids,
        suggested_actions=suggested_actions,
        state_summary={
            "role": state["role"],
            "level": state["level"],
            "training": state["training"],
            "salesforce_setup_status": state["salesforce_setup_status"],
        },
    )


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
