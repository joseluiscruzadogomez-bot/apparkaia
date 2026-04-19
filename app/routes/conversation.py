from fastapi import APIRouter, HTTPException
from app.schemas import IntentRequest, ContextResolveRequest, ConversationNextRequest
from app.services.intent_classifier import classify_intent
from app.services.context_resolver import resolve_context
from app.services.conversation_engine import get_next_response

router = APIRouter(prefix="/api/v1/conversation", tags=["conversation"])


@router.post("/classify-intent")
def classify_intent_route(payload: IntentRequest):
    return classify_intent(payload.text, payload.conversation_state, payload.flow_origin)


@router.post("/resolve-context")
def resolve_context_route(payload: ContextResolveRequest):
    return resolve_context(
        session_id=payload.session_id,
        intent=payload.intent,
        flow_origin=payload.flow_origin,
        user_phone=payload.user_phone,
        qr_context=payload.qr_context,
        text=payload.text
    )


@router.post("/next")
def conversation_next(payload: ConversationNextRequest):
    if not payload.session:
        raise HTTPException(status_code=400, detail="Session requerida")
    return get_next_response(
        session=payload.session,
        intent=payload.intent,
        backend_result=payload.backend_result
    )