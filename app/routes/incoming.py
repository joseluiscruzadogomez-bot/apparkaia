from fastapi import APIRouter
from app.schemas import IncomingMessage
from app.services.normalizer import normalize_message
from app.services.session_manager import get_or_create_session
from app.database import MESSAGES_DB

router = APIRouter(prefix="/api/v1/incoming", tags=["incoming"])


@router.post("/test")
def incoming_test(payload: IncomingMessage):
    normalized = normalize_message(payload.model_dump(by_alias=True))
    MESSAGES_DB[normalized["message_id"]] = normalized

    session = get_or_create_session(
        user_phone=normalized["user_phone"],
        channel=normalized["channel"]
    )

    return {
        "ok": True,
        "normalized_message_id": normalized["message_id"],
        "session_id": session["session_id"],
        "normalized": normalized,
        "next_module": "conversation_engine"
    }