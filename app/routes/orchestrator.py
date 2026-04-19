from fastapi import APIRouter

from app.schemas import IncomingMessage
from app.services.normalizer import normalize_message
from app.services.session_manager import (
    get_or_create_session,
    get_session,
    update_session,
)
from app.services.intent_classifier import classify_intent
from app.services.context_resolver import resolve_context
from app.services.backend_adapter import (
    get_ticket_status,
    get_ticket_debt,
    get_ticket_time,
    get_payment_link,
    create_support_case,
)
from app.services.conversation_engine import get_next_response
from app.services.response_builder import build_response
from app.database import MESSAGES_DB


router = APIRouter(prefix="/api/v1/orchestrator", tags=["orchestrator"])


@router.post("/process")
def orchestrator_process(payload: IncomingMessage):
    # 1. Normalizar mensaje
    normalized = normalize_message(payload.model_dump(by_alias=True))
    MESSAGES_DB[normalized["message_id"]] = normalized

    # 2. Obtener o crear sesión
    session = get_or_create_session(
        user_phone=normalized["user_phone"],
        channel=normalized["channel"]
    )

    qr_context = normalized.get("qr_context") or {}
    has_qr_ref = bool(qr_context.get("ref"))
    raw_text = (normalized.get("text") or "").strip().upper()

    # 3. Si viene desde QR, fijamos origen contextual
    if has_qr_ref:
        update_session(
            session["session_id"],
            {
                "flow_origin": "qr_exit"
            }
        )
        session = get_session(session["session_id"])

    # 4. Determinar intención
    current_state = session.get("conversation_state", "awaiting_intent")
    previous_intent = session.get("last_intent")

    # Caso A: flujo QR siempre tiene prioridad
    if has_qr_ref:
        intent_result = {
            "intent": "exit_problem",
            "confidence": 0.99,
            "requires_ticket_context": True,
            "requires_human": False,
        }
        intent = "exit_problem"

    else:
        # Clasificación normal
        intent_result = classify_intent(
            text=normalized.get("text"),
            conversation_state=current_state,
            flow_origin=session.get("flow_origin", "direct_whatsapp")
        )
        intent = intent_result["intent"]

        # Caso B: si estamos esperando ticket y llega TK..., reutilizar la intención previa
        if current_state == "awaiting_ticket_code" and raw_text.startswith("TK"):
            if previous_intent in [
                "pay_ticket",
                "check_status",
                "check_debt",
                "check_time",
                "exit_problem",
                "send_payment_link",
            ]:
                intent = previous_intent
                intent_result["intent"] = previous_intent
                intent_result["confidence"] = 0.99
                intent_result["requires_ticket_context"] = True
                intent_result["requires_human"] = False

    # 5. Guardar última intención en sesión
    update_session(session["session_id"], {"last_intent": intent})
    session = get_session(session["session_id"])

    # 6. Resolver contexto
    context_result = resolve_context(
        session_id=session["session_id"],
        intent=intent,
        flow_origin=session.get("flow_origin", "direct_whatsapp"),
        user_phone=normalized["user_phone"],
        qr_context=qr_context,
        text=normalized.get("text")
    )

    session = get_session(session["session_id"])

    # 7. Consultar backend si ya hay ticket/contexto suficiente
    backend_result = None
    ticket_code = context_result.get("ticket_code") or session.get("ticket_code")
    site_id = session.get("site_id")

    if context_result.get("context_status") == "resolved" and ticket_code:
        if intent in ["pay_ticket", "check_status", "exit_problem", "send_payment_link"]:
            backend_result = get_ticket_status(
                ticket_code=ticket_code,
                user_phone=normalized["user_phone"],
                site_id=site_id
            )

        elif intent == "check_debt":
            backend_result = get_ticket_debt(
                ticket_code=ticket_code,
                user_phone=normalized["user_phone"],
                site_id=site_id
            )

        elif intent == "check_time":
            backend_result = get_ticket_time(
                ticket_code=ticket_code,
                user_phone=normalized["user_phone"],
                site_id=site_id
            )

        elif intent == "pay_ticket_link":
            backend_result = get_payment_link(
                ticket_code=ticket_code,
                user_phone=normalized["user_phone"],
                site_id=site_id
            )

        if backend_result and backend_result.get("status"):
            update_session(
                session["session_id"],
                {"last_backend_status": backend_result.get("status")}
            )
            session = get_session(session["session_id"])

    # 8. Decidir respuesta conversacional
    final_decision = get_next_response(
        session=session,
        intent=intent,
        backend_result=backend_result
    )

    # 9. Ejecutar acciones automáticas
    action_results = []
    for action in final_decision.get("actions", []):
        action_type = action.get("type")
        action_payload = action.get("payload", {})

        if action_type == "create_support_case":
            support_result = create_support_case(
                ticket_code=action_payload.get("ticket_code", ""),
                category=action_payload.get("category", "general")
            )
            action_results.append({
                "type": action_type,
                "result": support_result
            })

    # 10. Actualizar estado final de la sesión
    update_session(
        session["session_id"],
        {
            "conversation_state": final_decision.get(
                "next_state",
                session["conversation_state"]
            )
        }
    )
    session = get_session(session["session_id"])

    # 11. Construir payload del canal
    final_response = build_response(
        reply_type=final_decision.get("reply_type", "text"),
        message=final_decision.get("message", ""),
        buttons=final_decision.get("buttons", []),
        list_sections=final_decision.get("list_sections", [])
    )

    # 12. Respuesta consolidada
    return {
        "ok": True,
        "normalized_message": normalized,
        "session": session,
        "intent": intent_result,
        "context": context_result,
        "backend_result": backend_result,
        "decision": final_decision,
        "action_results": action_results,
        "final_response": final_response
    }