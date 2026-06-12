from sqlalchemy.orm import Session
from ..models import SlackMessage


def store_message(db: Session, channel_or_user: str, message_type: str,
                  message: str, metadata: dict = None,
                  simulate_failure: bool = False):
    if simulate_failure:
        return {"ok": False, "error": "SIMULATED_FAILURE", "message_id": None}
    msg = SlackMessage(
        channel_or_user=channel_or_user,
        message_type=message_type,
        message=message,
        metadata_json=metadata,
        simulate_failure=simulate_failure,
    )
    db.add(msg)
    db.flush()
    return {"ok": True, "message_id": msg.message_id}


def get_messages(db: Session, employee_id: str = None):
    q = db.query(SlackMessage)
    if employee_id:
        q = q.filter(SlackMessage.channel_or_user == employee_id)
    return q.order_by(SlackMessage.created_at).all()
