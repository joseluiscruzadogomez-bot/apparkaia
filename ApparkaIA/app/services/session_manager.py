from datetime import datetime
from uuid import uuid4
from app.database import SESSIONS_DB
from app.constants import CONVERSATION_STATES, FLOW_ORIGINS


def get_or_create_session(user_phone: str, channel: str = "whatsapp") -> dict:
    existing = None
    for session in SESSIONS_DB.values():
        if session["user_phone"] == user_phone and session["channel"] == channel:
            existing = session
            break

    if existing:
        existing["updated_at"] = datetime.now().isoformat()
        return existing

    session_id = f"ses_{uuid4().hex[:8]}"
    now = datetime.now().isoformat()

    session = {
        "session_id": session_id,
        "user_phone": user_phone,
        "channel": channel,
        "flow_origin": FLOW_ORIGINS["direct_whatsapp"],
        "conversation_state": CONVERSATION_STATES["awaiting_intent"],
        "ticket_id": None,
        "ticket_code": None,
        "site_id": None,
        "site_name": None,
        "lane_id": None,
        "last_intent": None,
        "last_backend_status": None,
        "context_prevalidated": False,
        "created_at": now,
        "updated_at": now,
    }

    SESSIONS_DB[session_id] = session
    return session


def get_session(session_id: str) -> dict | None:
    return SESSIONS_DB.get(session_id)


def update_session(session_id: str, updates: dict) -> dict | None:
    session = SESSIONS_DB.get(session_id)
    if not session:
        return None

    session.update(updates)
    session["updated_at"] = datetime.now().isoformat()
    return session