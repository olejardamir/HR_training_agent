from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import SlackMessageRequest, SlackMessageResponse
from ..services.slack_service import store_message, get_messages
from ..services.audit_service import log_event

router = APIRouter()


@router.post("/mock/slack/messages", response_model=SlackMessageResponse)
def store_slack_message(request: SlackMessageRequest,
                        db: Session = Depends(get_db)):
    channel = request.channel_or_user or request.channel or "general"
    result = store_message(
        db, channel, request.message_type,
        request.message, request.metadata, request.simulate_failure,
    )
    if not result.get("ok"):
        if result.get("error") == "SIMULATED_FAILURE":
            return SlackMessageResponse(ok=False, status="FAILED", message_id="0")
        return SlackMessageResponse(ok=False, status="FAILED", message_id="0")

    cid = request.metadata.get("correlation_id") if request.metadata else None
    log_event(db, cid or "unknown", None, "system", "slack-mock",
              "message_stored", "slack", str(result["message_id"]),
              "STORED", None)

    return SlackMessageResponse(
        ok=True, status="STORED",
        message_id=str(result["message_id"]),
        correlation_id=cid,
    )


@router.get("/mock/slack/messages")
def list_slack_messages(employee_id: str = None,
                        db: Session = Depends(get_db)):
    messages = get_messages(db, employee_id)
    return [
        {
            "message_id": m.message_id,
            "channel_or_user": m.channel_or_user,
            "message_type": m.message_type,
            "message": m.message,
            "metadata": m.metadata_json,
            "created_at": str(m.created_at) if m.created_at else None,
        }
        for m in messages
    ]
