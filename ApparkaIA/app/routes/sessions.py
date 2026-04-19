from fastapi import APIRouter, HTTPException
from app.schemas import SessionRequest
from app.services.session_manager import get_or_create_session, get_session, update_session

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("/get-or-create")
def create_or_get_session(payload: SessionRequest):
    session = get_or_create_session(payload.user_phone, payload.channel)
    return session


@router.get("/{session_id}")
def read_session(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return session


@router.patch("/{session_id}")
def patch_session(session_id: str, updates: dict):
    session = update_session(session_id, updates)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return session